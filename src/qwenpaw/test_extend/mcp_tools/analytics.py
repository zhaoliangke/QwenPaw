# -*- coding: utf-8 -*-
"""Analytics dashboard MCP tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.analytics_agent import AnalyticsAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = AnalyticsAgent(WORKING_DIR)
    return _agent


async def get_dashboard_tool(iteration_id: str = "") -> dict:
    return await _get_agent().generate_dashboard(iteration_id)


async def get_asset_metrics_tool(iteration_id: str = "") -> dict:
    return await _get_agent()._compute_asset_metrics(iteration_id)


async def get_execution_trend_tool(iteration_id: str = "") -> dict:
    return await _get_agent()._compute_execution_trend(iteration_id)
