# -*- coding: utf-8 -*-
"""Test Execution Scheduling MCP Tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from ...agents.test_schedule_agent import TestScheduleAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = TestScheduleAgent(WORKING_DIR)
    return _agent


async def run_batch_tool(case_ids: list[str], iteration_id: str, concurrency: int = 4, environment: str = "test") -> dict:
    return await _get_agent().run_batch(case_ids, iteration_id, concurrency, environment)


async def run_single_tool(case_id: str, environment: str = "test", iteration_id: str = "") -> dict:
    return await _get_agent().run_single(case_id, environment, iteration_id)


async def retry_failed_tool(test_run_id: str) -> dict:
    return await _get_agent().retry_failed(test_run_id)


async def get_progress_tool(run_id: str) -> dict:
    return await _get_agent().get_execution_progress(run_id)
