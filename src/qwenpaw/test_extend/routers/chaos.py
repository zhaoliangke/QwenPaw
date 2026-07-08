# -*- coding: utf-8 -*-
"""Chaos engineering router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.chaos_agent import ChaosAgent
from common.trace_id import generate_trace_id
from models.chaos import ChaosExperiment, ChaosTarget, ChaosType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chaos", tags=["chaos"])

_agent: ChaosAgent | None = None


def init_chaos_agent(workspace_dir: str):
    global _agent
    _agent = ChaosAgent(workspace_dir)


@router.post("/experiments")
async def create_experiment(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Chaos agent not initialized")
    target_body = body.get("target", {})
    experiment = ChaosExperiment(
        id=generate_trace_id("CE"),
        name=body.get("name", ""),
        chaos_type=ChaosType(body.get("chaos_type", "network_delay")),
        target=ChaosTarget(**target_body),
        duration_seconds=body.get("duration_seconds", 30),
        intensity=body.get("intensity", 1.0),
        parameters=body.get("parameters", {}),
        rollback_enabled=body.get("rollback_enabled", True),
        iteration_id=body.get("iteration_id", ""),
    )
    return {"id": experiment.id, "name": experiment.name, "chaos_type": experiment.chaos_type.value}


@router.post("/experiments/{exp_id}/run")
async def run_experiment(exp_id: str, body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Chaos agent not initialized")
    experiment = ChaosExperiment(
        id=exp_id, name="adhoc",
        chaos_type=ChaosType(body.get("chaos_type", "network_delay")),
        target=ChaosTarget(**body.get("target", {})),
        duration_seconds=body.get("duration_seconds", 30),
        parameters=body.get("parameters", {}),
    )
    result = await _agent.run_experiment(experiment)
    return {
        "result_id": result.id,
        "status": result.status.value,
        "impact_score": result.impact_score,
        "error_rate_before": result.error_rate_before,
        "error_rate_during": result.error_rate_during,
        "recovery_time_ms": result.recovery_time_ms,
        "findings": result.findings,
    }


@router.get("/results")
async def list_results(experiment_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Chaos agent not initialized")
    results = _agent.list_results(experiment_id)
    return {"results": [r.model_dump() for r in results], "total": len(results)}
