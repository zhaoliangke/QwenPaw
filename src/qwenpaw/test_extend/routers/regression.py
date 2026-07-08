# -*- coding: utf-8 -*-
"""Regression test selection API router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.regression_agent import RegressionAgent, RegressionPlan

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/regression", tags=["regression"])

_agent: RegressionAgent | None = None
# In-memory plan storage
_plans: dict[str, RegressionPlan] = {}


def init_regression_agent(workspace_dir: str):
    global _agent
    _agent = RegressionAgent(workspace_dir)


@router.post("/analyze")
async def analyze_diff(body: dict[str, Any]) -> dict[str, Any]:
    """Analyze git diff and generate regression plan."""
    if not _agent:
        raise HTTPException(status_code=503, detail="Regression agent not initialized")

    base_ref = body.get("base_ref", "HEAD~1")
    head_ref = body.get("head_ref", "HEAD")
    iteration_id = body.get("iteration_id", "")

    plan = await _agent.analyze_diff(base_ref, head_ref, iteration_id)

    # Select cases if provided
    all_cases = body.get("all_cases", [])
    if all_cases:
        plan = await _agent.select_cases(plan, all_cases)

    _plans[plan.id] = plan

    summary = await _agent.get_impact_summary(plan)
    return {
        "plan_id": plan.id,
        "changes_count": len(plan.changes),
        "summary": summary,
    }


@router.post("/select")
async def select_cases(body: dict[str, Any]) -> dict[str, Any]:
    """Select test cases from an existing plan."""
    if not _agent:
        raise HTTPException(status_code=503, detail="Regression agent not initialized")

    plan_id = body.get("plan_id", "")
    plan = _plans.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")

    all_cases = body.get("all_cases", [])
    if not all_cases:
        raise HTTPException(status_code=400, detail="all_cases required")

    plan = await _agent.select_cases(plan, all_cases)
    _plans[plan.id] = plan

    return {
        "plan_id": plan.id,
        "selected": plan.selected_cases,
        "skipped": plan.skipped_cases,
        "total": plan.total_cases,
        "selected_count": plan.selected_count,
        "estimated_time_saved": plan.estimated_time_saved,
    }


@router.get("/plans")
async def list_plans(iteration_id: str = "") -> dict[str, Any]:
    plans = list(_plans.values())
    if iteration_id:
        plans = [p for p in plans if p.iteration_id == iteration_id]
    return {
        "plans": [p.model_dump() for p in plans],
        "total": len(plans),
    }


@router.get("/plans/{plan_id}")
async def get_plan(plan_id: str) -> dict[str, Any]:
    plan = _plans.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    return plan.model_dump()


@router.get("/plans/{plan_id}/summary")
async def get_plan_summary(plan_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Regression agent not initialized")
    plan = _plans.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    return await _agent.get_impact_summary(plan)
