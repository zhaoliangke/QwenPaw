# -*- coding: utf-8 -*-
"""Chaos engineering MCP tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.chaos_agent import ChaosAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = ChaosAgent(WORKING_DIR)
    return _agent


async def create_chaos_experiment_tool(
    name: str,
    chaos_type: str,
    target: dict,
    duration_seconds: int = 30,
    parameters: dict | None = None,
) -> dict:
    from models.chaos import ChaosExperiment, ChaosTarget, ChaosType
    experiment = ChaosExperiment(
        name=name, chaos_type=ChaosType(chaos_type),
        target=ChaosTarget(**target),
        duration_seconds=duration_seconds,
        parameters=parameters or {},
    )
    return {"id": experiment.id, "name": experiment.name, "chaos_type": experiment.chaos_type.value}


async def run_chaos_experiment_tool(exp_id: str, chaos_type: str, target: dict, parameters: dict | None = None) -> dict:
    from models.chaos import ChaosExperiment, ChaosTarget, ChaosType
    experiment = ChaosExperiment(
        id=exp_id, name="adhoc", chaos_type=ChaosType(chaos_type),
        target=ChaosTarget(**target), parameters=parameters or {},
    )
    result = await _get_agent().run_experiment(experiment)
    return {"result_id": result.id, "status": result.status.value, "impact_score": result.impact_score, "findings": result.findings}


async def list_chaos_results_tool(experiment_id: str = "") -> dict:
    results = _get_agent().list_results(experiment_id)
    return {"results": [r.model_dump() for r in results], "total": len(results)}
