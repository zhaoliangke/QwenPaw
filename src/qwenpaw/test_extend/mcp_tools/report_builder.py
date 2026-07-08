# -*- coding: utf-8 -*-
"""Report Generation MCP Tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.report_agent import ReportAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = ReportAgent(WORKING_DIR)
    return _agent


async def generate_report_tool(test_run: dict, iteration_id: str) -> dict:
    return await _get_agent().generate_report(test_run, iteration_id)


async def analyze_failures_tool(test_run_id: str, iteration_id: str) -> dict:
    return await _get_agent().analyze_failures(test_run_id, iteration_id)


async def push_report_tool(report_id: str, channels: list[str] | None = None) -> dict:
    return await _get_agent().push_report(report_id, channels)


async def export_report_tool(report_id: str, format: str = "html", iteration_id: str = "") -> dict:
    return await _get_agent().export_report(report_id, format, iteration_id)
