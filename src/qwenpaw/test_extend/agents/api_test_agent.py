# -*- coding: utf-8 -*-
"""API test agent — executes HTTP requests and validates responses."""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any

import httpx

from common.utils import read_json_file, write_json_file
from common.trace_id import generate_trace_id
from models.api_test import (
    ApiTestCase,
    ApiTestResult,
    ApiTestSuite,
    AssertionType,
    HttpMethod,
)
from storage.paths import get_api_test_dir

logger = logging.getLogger(__name__)


class ApiTestAgent:
    def __init__(self, workspace_dir: str | Path):
        self._workspace = Path(workspace_dir)
        self._case_dir = get_api_test_dir(self._workspace)
        self._result_dir = self._workspace / "test" / "api_results"
        self._case_dir.mkdir(parents=True, exist_ok=True)
        self._result_dir.mkdir(parents=True, exist_ok=True)

    async def execute_case(self, case: ApiTestCase) -> ApiTestResult:
        result = ApiTestResult(case_id=case.id)
        start = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=case.timeout, follow_redirects=True) as client:
                resp = await client.request(
                    method=case.method.value,
                    url=case.url,
                    headers=case.headers or None,
                    params=case.query_params or None,
                    json=case.body if isinstance(case.body, dict) else None,
                    content=json.dumps(case.body) if case.body and not isinstance(case.body, dict) else None,
                )
                result.status_code = resp.status_code
                result.response_body = resp.text[:5000]
                result.response_headers = dict(resp.headers)
                result.response_time_ms = (time.monotonic() - start) * 1000
                result.assertion_results, result.passed_assertions, result.total_assertions = \
                    self._evaluate_assertions(case.assertions, resp)
                result.status = "passed" if result.passed_assertions == result.total_assertions and result.total_assertions > 0 else "failed"
        except httpx.TimeoutException:
            result.status = "failed"
            result.error = f"Request timed out after {case.timeout}s"
            result.response_time_ms = (time.monotonic() - start) * 1000
        except Exception as e:
            result.status = "failed"
            result.error = str(e)[:300]
            result.response_time_ms = (time.monotonic() - start) * 1000

        self._save_result(result)
        return result

    async def execute_suite(self, suite: ApiTestSuite) -> list[ApiTestResult]:
        cases = self._load_cases(suite.case_ids)
        tasks = [self.execute_case(c) for c in cases]
        return await asyncio.gather(*tasks, return_exceptions=False)

    def _evaluate_assertions(
        self, assertions: list[dict], resp: httpx.Response
    ) -> tuple[list[dict], int, int]:
        results = []
        passed = 0
        for a in assertions:
            atype = a.get("type", "")
            expected = a.get("expected")
            actual = None
            ok = False
            if atype == AssertionType.STATUS_CODE.value:
                actual = resp.status_code
                ok = actual == expected
            elif atype == AssertionType.BODY_CONTAINS.value:
                actual = resp.text[:2000]
                ok = expected in resp.text if expected else False
            elif atype == AssertionType.BODY_EQUALS.value:
                actual = resp.text
                ok = resp.text == expected
            elif atype == AssertionType.JSON_PATH.value:
                path = a.get("path", "")
                try:
                    data = resp.json()
                    actual = self._extract_json_path(data, path)
                    ok = actual == expected
                except Exception:
                    ok = False
            elif atype == AssertionType.RESPONSE_TIME.value:
                actual = resp.elapsed.total_seconds() * 1000 if hasattr(resp, "elapsed") else 0
                ok = actual <= expected if expected else True
            elif atype == AssertionType.HEADER.value:
                header_name = a.get("name", "")
                actual = resp.headers.get(header_name, "")
                ok = actual == expected

            if ok:
                passed += 1
            results.append({"type": atype, "expected": expected, "actual": actual, "passed": ok})

        return results, passed, len(assertions)

    def _extract_json_path(self, data: Any, path: str) -> Any:
        parts = path.replace("$.", "").split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    current = current[int(part)]
                except (ValueError, IndexError):
                    return None
            else:
                return None
        return current

    def _load_cases(self, case_ids: list[str]) -> list[ApiTestCase]:
        cases = []
        for cid in case_ids:
            f = self._case_dir / f"{cid}.json"
            if f.exists():
                data = read_json_file(f)
                if data:
                    cases.append(ApiTestCase(**data))
        return cases

    def _save_result(self, result: ApiTestResult):
        f = self._result_dir / f"{result.id}.json"
        write_json_file(f, result.model_dump())

    def save_case(self, case: ApiTestCase):
        f = self._case_dir / f"{case.id}.json"
        write_json_file(f, case.model_dump())

    def get_result(self, result_id: str) -> ApiTestResult | None:
        f = self._result_dir / f"{result_id}.json"
        if f.exists():
            data = read_json_file(f)
            return ApiTestResult(**data) if data else None
        return None

    def list_results(self, case_id: str = "") -> list[ApiTestResult]:
        results = []
        for f in sorted(self._result_dir.glob("*.json")):
            data = read_json_file(f)
            if data:
                r = ApiTestResult(**data)
                if not case_id or r.case_id == case_id:
                    results.append(r)
        return results
