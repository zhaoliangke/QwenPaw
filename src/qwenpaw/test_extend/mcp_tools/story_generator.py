# -*- coding: utf-8 -*-
"""Story Generation MCP Tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from ...agents.story_agent import StoryAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = StoryAgent(WORKING_DIR)
    return _agent


async def generate_stories_tool(parsed_prd: dict, iteration_id: str) -> dict:
    return await _get_agent().generate_stories(parsed_prd, iteration_id)


async def validate_story_tool(story_id: str, iteration_id: str) -> dict:
    return await _get_agent().validate_story(story_id, iteration_id)


async def generate_traceability_tool(story_id: str, iteration_id: str) -> dict:
    return await _get_agent().generate_traceability(story_id, iteration_id)
