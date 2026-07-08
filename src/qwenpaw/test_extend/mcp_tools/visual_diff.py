# -*- coding: utf-8 -*-
"""Visual regression MCP tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.visual_diff_agent import VisualDiffAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = VisualDiffAgent(WORKING_DIR)
    return _agent


async def create_visual_test_tool(name: str, url: str, threshold: float = 0.1, iteration_id: str = "") -> dict:
    from models.visual_diff import VisualDiffTest
    test = VisualDiffTest(name=name, url=url, threshold=threshold, iteration_id=iteration_id)
    return {"id": test.id, "name": test.name, "url": test.url}


async def run_visual_test_tool(test_id: str, url: str, run_id: str = "") -> dict:
    from models.visual_diff import VisualDiffTest
    test = VisualDiffTest(id=test_id, name="adhoc", url=url)
    result = await _get_agent().run_test(test, run_id)
    return {"result_id": result.id, "status": result.status.value, "diff_percentage": result.diff_percentage}


async def update_baseline_tool(test_id: str) -> dict:
    ok = _get_agent().update_baseline(test_id)
    return {"updated": ok}


async def list_visual_results_tool(test_id: str = "") -> dict:
    results = _get_agent().list_results(test_id)
    return {"results": [r.model_dump() for r in results], "total": len(results)}
