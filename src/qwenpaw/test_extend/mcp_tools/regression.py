# -*- coding: utf-8 -*-
"""Regression test selection MCP tools."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_agent = None
_plans = {}


def _get_agent():
    global _agent
    if _agent is None:
        from agents.regression_agent import RegressionAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = RegressionAgent(WORKING_DIR)
    return _agent


async def analyze_diff_tool(
    base_ref: str,
    head_ref: str,
    iteration_id: str = "",
    all_cases: list[dict] | None = None,
) -> dict:
    plan = await _get_agent().analyze_diff(base_ref, head_ref, iteration_id)
    if all_cases:
        plan = await _get_agent().select_cases(plan, all_cases)
    _plans[plan.id] = plan
    summary = await _get_agent().get_impact_summary(plan)
    return {"plan_id": plan.id, "changes_count": len(plan.changes), "summary": summary}


async def select_cases_tool(plan_id: str, all_cases: list[dict]) -> dict:
    plan = _plans.get(plan_id)
    if not plan:
        return {"error": f"Plan {plan_id} not found"}
    plan = await _get_agent().select_cases(plan, all_cases)
    _plans[plan.id] = plan
    return {
        "plan_id": plan.id,
        "selected": plan.selected_cases,
        "skipped": plan.skipped_cases,
        "total": plan.total_cases,
        "selected_count": plan.selected_count,
    }


async def list_regression_plans_tool(iteration_id: str = "") -> dict:
    plans = list(_plans.values())
    if iteration_id:
        plans = [p for p in plans if p.iteration_id == iteration_id]
    return {"plans": [p.model_dump() for p in plans], "total": len(plans)}


async def get_regression_plan_tool(plan_id: str) -> dict:
    plan = _plans.get(plan_id)
    if not plan:
        return {"error": f"Plan {plan_id} not found"}
    return plan.model_dump()
