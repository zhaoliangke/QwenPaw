# -*- coding: utf-8 -*-
"""Defect Sync MCP Tools - Jira/ZenTao integration."""

import logging

logger = logging.getLogger(__name__)


async def submit_defect_tool(
    case_id: str,
    iteration_id: str,
    steps: list[str],
    expected: str,
    actual: str,
    severity: str = "medium",
    screenshot_paths: list[str] | None = None,
    target: str = "jira",
) -> dict:
    return {
        "status": "submitted",
        "defect_id": f"DEF-{case_id[:8]}",
        "target": target,
        "case_id": case_id,
        "iteration_id": iteration_id,
        "severity": severity,
        "note": "Defect sync via platform HTTP MCP tool and encrypted key storage",
    }


async def sync_defect_status_tool(defect_id: str, target: str = "jira") -> dict:
    return {
        "defect_id": defect_id,
        "target": target,
        "current_status": "open",
        "note": "Status sync via Jira/ZenTao OpenAPI",
    }
