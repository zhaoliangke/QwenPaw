# -*- coding: utf-8 -*-
"""UI Automation MCP Tools - Playwright integration."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from ...agents.ui_auto_agent import UIAutoAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = UIAutoAgent(WORKING_DIR)
    return _agent


async def generate_script_tool(test_case: dict, page_name: str = "", iteration_id: str = "") -> dict:
    return await _get_agent().generate_script(test_case, page_name, iteration_id)


async def debug_script_tool(script_content: str, test_case_id: str) -> dict:
    return await _get_agent().debug_script(script_content, test_case_id)


async def execute_script_tool(script_content: str, env_config: dict | None = None, iteration_id: str = "") -> dict:
    return await _get_agent().execute_script(script_content, env_config, iteration_id)


async def capture_screenshot_tool(test_case_id: str, step: int, iteration_id: str = "") -> dict:
    return await _get_agent().capture_screenshot(test_case_id, step, iteration_id)
