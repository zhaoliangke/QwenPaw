# -*- coding: utf-8 -*-
"""Test Case Generation MCP Tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.case_gen_agent import CaseGenAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = CaseGenAgent(WORKING_DIR)
    return _agent


async def generate_cases_tool(story_id: str, iteration_id: str, dimensions: list[str] | None = None) -> dict:
    return await _get_agent().generate_cases(story_id, iteration_id, dimensions)


async def enhance_with_kb_tool(story_id: str, iteration_id: str) -> dict:
    return await _get_agent().enhance_with_knowledge_base(story_id, iteration_id)


async def calculate_coverage_tool(iteration_id: str) -> dict:
    return await _get_agent().calculate_coverage(iteration_id)


async def export_cases_tool(case_ids: list[str], format: str = "excel") -> dict:
    return await _get_agent().export_cases(case_ids, format)
