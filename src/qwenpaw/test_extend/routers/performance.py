# -*- coding: utf-8 -*-
"""Performance test router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.performance_agent import PerformanceAgent
from common.trace_id import generate_trace_id
from models.performance import PerfTestCase, PerfTestType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/performance", tags=["performance"])

_agent: PerformanceAgent | None = None


def init_performance_agent(workspace_dir: str):
    global _agent
    _agent = PerformanceAgent(workspace_dir)


@router.post("/tests")
async def create_test(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Performance agent not initialized")
    test = PerfTestCase(
        id=generate_trace_id("PT"),
        name=body.get("name", ""),
        description=body.get("description", ""),
        test_type=PerfTestType(body.get("test_type", "load")),
        script_path=body.get("script_path", ""),
        target_url=body.get("target_url", ""),
        vusers=body.get("vusers", 10),
        duration=body.get("duration", "30s"),
        iteration_id=body.get("iteration_id", ""),
        env_vars=body.get("env_vars", {}),
    )
    return {"id": test.id, "name": test.name, "test_type": test.test_type.value}


@router.post("/tests/{test_id}/run")
async def run_test(test_id: str, body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Performance agent not initialized")
    test = PerfTestCase(id=test_id, name="adhoc", script_path=body.get("script_path", ""), target_url=body.get("target_url", ""))
    result = await _agent.run_test(test, run_id=body.get("run_id", ""))
    return {
        "result_id": result.id,
        "status": result.status,
        "http_reqs": result.http_reqs,
        "http_req_failed": result.http_req_failed,
        "http_req_duration_p95": result.http_req_duration_p95,
        "metrics_count": len(result.metrics),
        "error": result.error,
    }


@router.get("/results")
async def list_results(test_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Performance agent not initialized")
    results = _agent.list_results(test_id)
    return {"results": [r.model_dump() for r in results], "total": len(results)}


@router.get("/results/{result_id}")
async def get_result(result_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Performance agent not initialized")
    result = _agent.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Result {result_id} not found")
    return result.model_dump()
