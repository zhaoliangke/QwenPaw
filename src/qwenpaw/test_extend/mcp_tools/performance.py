# -*- coding: utf-8 -*-
"""Performance test MCP tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.performance_agent import PerformanceAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = PerformanceAgent(WORKING_DIR)
    return _agent


async def create_perf_test_tool(
    name: str,
    script_path: str,
    target_url: str = "",
    test_type: str = "load",
    vusers: int = 10,
    duration: str = "30s",
    iteration_id: str = "",
) -> dict:
    from models.performance import PerfTestCase, PerfTestType
    test = PerfTestCase(
        name=name, script_path=script_path, target_url=target_url,
        test_type=PerfTestType(test_type), vusers=vusers, duration=duration,
        iteration_id=iteration_id,
    )
    return {"id": test.id, "name": test.name, "test_type": test.test_type.value}


async def run_perf_test_tool(test_id: str, script_path: str, target_url: str = "", run_id: str = "") -> dict:
    from models.performance import PerfTestCase
    test = PerfTestCase(id=test_id, name="adhoc", script_path=script_path, target_url=target_url)
    result = await _get_agent().run_test(test, run_id)
    return {
        "result_id": result.id, "status": result.status,
        "http_reqs": result.http_reqs, "p95_ms": result.http_req_duration_p95,
    }


async def list_perf_results_tool(test_id: str = "") -> dict:
    results = _get_agent().list_results(test_id)
    return {"results": [r.model_dump() for r in results], "total": len(results)}
