# -*- coding: utf-8 -*-
"""Coverage analysis MCP tools."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.coverage_agent import CoverageAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = CoverageAgent(WORKING_DIR)
    return _agent


async def run_coverage_tool(
    source_path: str,
    test_path: str,
    iteration_id: str = "",
    run_id: str = "",
) -> dict:
    return await _get_agent().run_coverage(source_path, test_path, iteration_id, run_id)


async def list_coverage_reports_tool(iteration_id: str = "") -> dict:
    reports = await _get_agent().list_reports(iteration_id)
    return {"reports": [r.model_dump() for r in reports], "total": len(reports)}


async def get_coverage_gaps_tool(report_id: str) -> dict:
    gaps = await _get_agent().get_uncovered_gaps(report_id)
    return {"report_id": report_id, "gaps": gaps, "gap_count": len(gaps)}
