# -*- coding: utf-8 -*-
"""Story Agent - decomposes PRD requirements into user stories.

Generates structured stories with acceptance criteria in Gherkin format.
Stories are persisted as JSON files under the iteration storage.
"""

import json
import logging
from pathlib import Path

from storage.paths import get_story_dir
from models.story import Story, AcceptanceCriteria
from common.trace_id import generate_story_id

logger = logging.getLogger(__name__)


class StoryAgent:
    """Agent responsible for decomposing requirements into user stories."""

    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir

    async def generate_stories(
        self,
        parsed_prd: dict,
        iteration_id: str,
    ) -> dict:
        story_dir = get_story_dir(self._workspace_dir, iteration_id)
        story_dir.mkdir(parents=True, exist_ok=True)

        stories = []
        story_id = generate_story_id()
        story = Story(
            id=story_id,
            iteration_id=iteration_id,
            title=f"User Story for {parsed_prd.get('file', 'PRD')}",
            as_a="user",
            i_want="feature described in PRD",
            so_that="achieve expected outcome",
            acceptance_criteria=[
                AcceptanceCriteria(
                    scenario="Happy path",
                    gherkin="Given valid input\nWhen action is performed\nThen expected result is returned",
                )
            ],
        )

        f = story_dir / f"{story_id}.json"
        f.write_text(story.model_dump_json(indent=2))
        stories.append(story.model_dump())

        return {"stories": stories, "count": len(stories), "iteration_id": iteration_id}

    async def validate_story(self, story_id: str, iteration_id: str) -> dict:
        story_dir = get_story_dir(self._workspace_dir, iteration_id)
        story_file = story_dir / f"{story_id}.json"
        if not story_file.exists():
            return {"error": "Story not found"}

        data = json.loads(story_file.read_text())
        issues = []
        if not data.get("acceptance_criteria"):
            issues.append("Missing acceptance criteria")
        if not data.get("title"):
            issues.append("Missing story title")
        data["is_validated"] = True
        data["validation_issues"] = issues
        story_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return {"story_id": story_id, "is_valid": len(issues) == 0, "issues": issues}

    async def generate_traceability(self, story_id: str, iteration_id: str) -> dict:
        story_dir = get_story_dir(self._workspace_dir, iteration_id)
        story_file = story_dir / f"{story_id}.json"
        if not story_file.exists():
            return {"error": "Story not found"}

        data = json.loads(story_file.read_text())
        tid = data.get("traceability_id", story_id)
        return {
            "story_id": story_id,
            "traceability_id": tid,
            "parent_iteration": iteration_id,
        }
