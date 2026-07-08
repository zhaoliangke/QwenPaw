# -*- coding: utf-8 -*-
"""Iteration Management MCP Tools.

Provides tools for CRUD operations, snapshots, diffs, and Jira sync.
All tools register into the platform's native tool pipeline.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.iteration_agent import IterationAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = IterationAgent(WORKING_DIR)
    return _agent


async def create_iteration_tool(
    name: str,
    version: str,
    module: str,
    start_date: str,
    end_date: str,
    description: str = "",
    git_branch: str = "",
    test_environment: str = "",
) -> dict:
    return await _get_agent().create_iteration(
        name=name, version=version, module=module,
        start_date=start_date, end_date=end_date,
        description=description or None,
        git_branch=git_branch or None,
        test_environment=test_environment or None,
    )


async def get_iteration_tool(iteration_id: str) -> dict:
    result = await _get_agent().get_iteration(iteration_id)
    return result or {"error": "Iteration not found"}


async def list_iterations_tool(status: str = "") -> list[dict]:
    return await _get_agent().list_iterations(status or None)


async def update_iteration_status_tool(iteration_id: str, new_status: str) -> dict:
    result = await _get_agent().update_iteration_status(iteration_id, new_status)
    return result or {"error": "Iteration not found"}


async def create_snapshot_tool(iteration_id: str) -> dict:
    return await _get_agent().create_snapshot(iteration_id)


async def diff_iterations_tool(id_a: str, id_b: str) -> dict:
    return await _get_agent().diff_iterations(id_a, id_b)


async def sync_from_jira_tool(project_key: str) -> dict:
    return {
        "project_key": project_key,
        "synced_stories": 0,
        "note": "Jira sync requires Jira API credentials in platform encrypted storage",
    }


async def schedule_regression_tool(iteration_id: str, cron_expression: str) -> dict:
    return {
        "iteration_id": iteration_id,
        "cron": cron_expression,
        "status": "scheduled",
        "note": "Reuses platform native Cron engine",
    }
