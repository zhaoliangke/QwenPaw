# -*- coding: utf-8 -*-
"""Story Generation MCP Tools - generates stories from structured PRD data."""

import logging
from datetime import datetime

from common.trace_id import generate_trace_id

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.story_agent import StoryAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = StoryAgent(WORKING_DIR)
    return _agent


def _build_story(parsed_prd: dict, iteration_id: str, title: str, as_a: str, i_want: str, so_that: str, priority: str, criteria: list[dict]) -> dict:
    """Build a structured story object."""
    return {
        "id": generate_trace_id("ST"),
        "iteration_id": iteration_id,
        "parent_story_id": None,
        "title": title,
        "as_a": as_a,
        "i_want": i_want,
        "so_that": so_that,
        "acceptance_criteria": criteria,
        "priority": priority,
        "traceability_id": "",
        "is_validated": False,
        "validation_issues": [],
        "created_at": datetime.now().isoformat(),
    }


async def generate_stories_tool(parsed_prd: dict, iteration_id: str) -> dict:
    stories = []

    modules = parsed_prd.get("functional_modules", [])
    flows = parsed_prd.get("business_flows", [])

    if modules:
        for module in modules:
            stories.append(_build_story(
                parsed_prd, iteration_id,
                title=f"Feature: {module}",
                as_a="user",
                i_want=f"use the {module} feature",
                so_that="accomplish my task efficiently",
                priority="medium",
                criteria=[{
                    "scenario": "Happy path",
                    "gherkin": "Given I am on " + module + "\nWhen I perform the main action\nThen I see the expected result"
                }, {
                    "scenario": "Validation",
                    "gherkin": "Given valid input is provided\nWhen the action is submitted\nThen it is processed successfully"
                }]
            ))

    if flows:
        for flow in flows:
            name = flow.get("name", "Business Flow")
            steps = flow.get("steps", [])
            if steps:
                gherkin_steps = "\n".join([
                    ("Given" if i == 0 else "And") + " " + s.lower()
                    for i, s in enumerate(steps[:3])
                ])
                stories.append(_build_story(
                    parsed_prd, iteration_id,
                    title=f"Flow: {name}",
                    as_a="user",
                    i_want=f"complete the {name} process",
                    so_that="my goal is achieved",
                    priority="high",
                    criteria=[{
                        "scenario": "Complete flow",
                        "gherkin": f"{gherkin_steps}\nWhen the final step completes\nThen the flow succeeds"
                    }]
                ))

    if not stories:
        return await _get_agent().generate_stories(parsed_prd, iteration_id)

    return {"stories": stories, "count": len(stories), "iteration_id": iteration_id}


async def validate_story_tool(story_id: str, iteration_id: str) -> dict:
    return await _get_agent().validate_story(story_id, iteration_id)


async def generate_traceability_tool(story_id: str, iteration_id: str) -> dict:
    return await _get_agent().generate_traceability(story_id, iteration_id)
