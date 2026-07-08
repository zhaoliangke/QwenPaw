# -*- coding: utf-8 -*-
"""API test MCP tools."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.api_test_agent import ApiTestAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = ApiTestAgent(WORKING_DIR)
    return _agent


async def create_api_case_tool(
    name: str,
    method: str,
    url: str,
    headers: dict | None = None,
    query_params: dict | None = None,
    body: Any = None,
    assertions: list | None = None,
    timeout: int = 30,
    iteration_id: str = "",
) -> dict:
    from models.api_test import ApiTestCase, HttpMethod
    case = ApiTestCase(
        name=name, method=HttpMethod(method), url=url,
        headers=headers or {}, query_params=query_params or {},
        body=body, assertions=assertions or [], timeout=timeout,
        iteration_id=iteration_id,
    )
    _get_agent().save_case(case)
    return {"id": case.id, "name": case.name, "url": case.url}


async def run_api_case_tool(case_id: str) -> dict:
    cases = _get_agent()._load_cases([case_id])
    if not cases:
        return {"error": f"Case {case_id} not found"}
    result = await _get_agent().execute_case(cases[0])
    return {
        "result_id": result.id, "status": result.status,
        "status_code": result.status_code, "passed": result.passed_assertions,
        "total": result.total_assertions,
    }


async def run_api_suite_tool(suite_id: str, case_ids: list[str]) -> dict:
    from models.api_test import ApiTestSuite
    suite = ApiTestSuite(id=suite_id, name="adhoc", case_ids=case_ids)
    results = await _get_agent().execute_suite(suite)
    passed = sum(1 for r in results if r.status == "passed")
    return {"total": len(results), "passed": passed, "failed": len(results) - passed}


async def list_api_results_tool(case_id: str = "") -> dict:
    results = _get_agent().list_results(case_id)
    return {"results": [r.model_dump() for r in results], "total": len(results)}
