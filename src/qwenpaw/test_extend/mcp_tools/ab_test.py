# -*- coding: utf-8 -*-
"""A/B test MCP tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.ab_test_agent import ABObstestAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = ABObstestAgent(WORKING_DIR)
    return _agent


async def create_ab_test_tool(
    name: str,
    hypothesis: str,
    control: dict,
    treatment: dict,
    metrics: list[str],
    significance_level: float = 0.05,
) -> dict:
    from models.ab_test import ABTest, Variant
    test = ABTest(
        name=name, hypothesis=hypothesis,
        control=Variant(**control), treatment=Variant(**treatment),
        metrics=metrics, significance_level=significance_level,
    )
    return {"id": test.id, "name": test.name}


async def analyze_ab_test_tool(test_id: str, control_data: list[float], treatment_data: list[float]) -> dict:
    from models.ab_test import ABTest
    test = ABTest(id=test_id, name="adhoc", metrics=["conversion"])
    result = await _get_agent().analyze(test, control_data, treatment_data)
    return {"result_id": result.id, "winner": result.winner, "conclusion": result.conclusion}


async def list_ab_results_tool(test_id: str = "") -> dict:
    results = _get_agent().list_results(test_id)
    return {"results": [r.model_dump() for r in results], "total": len(results)}
