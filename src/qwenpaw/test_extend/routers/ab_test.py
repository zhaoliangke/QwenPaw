# -*- coding: utf-8 -*-
"""A/B test router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.ab_test_agent import ABObstestAgent
from common.trace_id import generate_trace_id
from models.ab_test import ABTest, Variant

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ab_test", tags=["ab_test"])

_agent: ABObstestAgent | None = None


def init_ab_test_agent(workspace_dir: str):
    global _agent
    _agent = ABObstestAgent(workspace_dir)


@router.post("/tests")
async def create_test(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="AB test agent not initialized")
    test = ABTest(
        id=generate_trace_id("AB"),
        name=body.get("name", ""),
        hypothesis=body.get("hypothesis", ""),
        control=Variant(**body.get("control", {"name": "control"})),
        treatment=Variant(**body.get("treatment", {"name": "treatment"})),
        metrics=body.get("metrics", ["conversion"]),
        significance_level=body.get("significance_level", 0.05),
        target_sample_size=body.get("target_sample_size", 1000),
        iteration_id=body.get("iteration_id", ""),
    )
    return {"id": test.id, "name": test.name, "status": test.status.value}


@router.post("/tests/{test_id}/analyze")
async def analyze(test_id: str, body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="AB test agent not initialized")
    test = ABTest(id=test_id, name="adhoc", metrics=body.get("metrics", ["conversion"]))
    control_data = body.get("control_data", [])
    treatment_data = body.get("treatment_data", [])
    result = await _agent.analyze(test, control_data, treatment_data)
    return {
        "result_id": result.id,
        "status": result.status.value,
        "winner": result.winner,
        "conclusion": result.conclusion,
        "metrics": [m.model_dump() for m in result.metric_results],
    }


@router.get("/results")
async def list_results(test_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="AB test agent not initialized")
    results = _agent.list_results(test_id)
    return {"results": [r.model_dump() for r in results], "total": len(results)}
