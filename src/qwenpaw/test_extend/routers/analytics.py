# -*- coding: utf-8 -*-
"""Analytics dashboard router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.analytics_agent import AnalyticsAgent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])

_agent: AnalyticsAgent | None = None


def init_analytics_agent(workspace_dir: str):
    global _agent
    _agent = AnalyticsAgent(workspace_dir)


@router.get("/dashboard")
async def get_dashboard(iteration_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Analytics agent not initialized")
    dashboard = await _agent.generate_dashboard(iteration_id)
    return dashboard.model_dump()


@router.get("/metrics")
async def get_asset_metrics(iteration_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Analytics agent not initialized")
    metrics = await _agent._compute_asset_metrics(iteration_id)
    return metrics.model_dump()


@router.get("/trend")
async def get_execution_trend(iteration_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Analytics agent not initialized")
    trend = await _agent._compute_execution_trend(iteration_id)
    return trend.model_dump()
