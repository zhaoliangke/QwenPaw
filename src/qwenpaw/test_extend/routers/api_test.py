# -*- coding: utf-8 -*-
"""API test router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.api_test_agent import ApiTestAgent
from common.trace_id import generate_trace_id
from models.api_test import ApiTestCase, ApiTestSuite, HttpMethod

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api_test", tags=["api_test"])

_agent: ApiTestAgent | None = None


def init_api_test_agent(workspace_dir: str):
    global _agent
    _agent = ApiTestAgent(workspace_dir)


@router.post("/cases")
async def create_case(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="API test agent not initialized")
    case = ApiTestCase(
        id=generate_trace_id("AT"),
        name=body.get("name", ""),
        method=HttpMethod(body.get("method", "GET")),
        url=body.get("url", ""),
        headers=body.get("headers", {}),
        query_params=body.get("query_params", {}),
        body=body.get("body"),
        assertions=body.get("assertions", []),
        timeout=body.get("timeout", 30),
        iteration_id=body.get("iteration_id", ""),
    )
    _agent.save_case(case)
    return {"id": case.id, "name": case.name, "method": case.method.value, "url": case.url}


@router.post("/cases/{case_id}/run")
async def run_case(case_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="API test agent not initialized")
    cases = _agent._load_cases([case_id])
    if not cases:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    result = await _agent.execute_case(cases[0])
    return {
        "result_id": result.id,
        "status": result.status,
        "status_code": result.status_code,
        "response_time_ms": result.response_time_ms,
        "passed": result.passed_assertions,
        "total": result.total_assertions,
        "error": result.error,
    }


@router.post("/suites")
async def create_suite(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="API test agent not initialized")
    suite = ApiTestSuite(
        id=generate_trace_id("AS"),
        name=body.get("name", ""),
        description=body.get("description", ""),
        iteration_id=body.get("iteration_id", ""),
        base_url=body.get("base_url", ""),
        case_ids=body.get("case_ids", []),
        env_vars=body.get("env_vars", {}),
    )
    return {"id": suite.id, "name": suite.name, "case_count": len(suite.case_ids)}


@router.post("/suites/{suite_id}/run")
async def run_suite(suite_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="API test agent not initialized")
    results = await _agent.execute_suite(ApiTestSuite(id=suite_id, name="adhoc", case_ids=[]))
    passed = sum(1 for r in results if r.status == "passed")
    return {"total": len(results), "passed": passed, "failed": len(results) - passed}


@router.get("/results")
async def list_results(case_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="API test agent not initialized")
    results = _agent.list_results(case_id)
    return {"results": [r.model_dump() for r in results], "total": len(results)}
