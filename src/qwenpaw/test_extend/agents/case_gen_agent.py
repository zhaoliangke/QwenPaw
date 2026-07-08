# -*- coding: utf-8 -*-
"""Case Generation Agent - generates test cases from user stories.

Enhances generation by retrieving similar historical cases from the
RAG knowledge base. Supports multi-dimensional case generation.
"""

import json
import logging
from pathlib import Path

from storage.paths import get_case_dir
from models.test_case import TestCase, CaseType
from common.trace_id import generate_case_id

logger = logging.getLogger(__name__)


class CaseGenAgent:
    """Agent responsible for batch generating test cases across dimensions."""

    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir

    async def generate_cases(
        self,
        story_id: str,
        iteration_id: str,
        dimensions: list[str] | None = None,
    ) -> dict:
        if dimensions is None:
            dimensions = ["functional", "boundary", "exception", "security", "ui"]

        case_dir = get_case_dir(self._workspace_dir, iteration_id)
        case_dir.mkdir(parents=True, exist_ok=True)

        templates = {
            "functional": {"title": "Functional: Verify core behavior", "steps": ["Setup", "Execute", "Verify"], "expected": ["Expected outcome"]},
            "boundary": {"title": "Boundary: Edge case validation", "steps": ["Provide boundary input", "Submit"], "expected": ["System handles correctly"]},
            "exception": {"title": "Exception: Error handling", "steps": ["Trigger error condition", "Observe"], "expected": ["Graceful error response"]},
            "security": {"title": "Security: Auth validation", "steps": ["Attempt unauthorized access", "Verify"], "expected": ["Access denied"]},
            "ui": {"title": "UI: Display verification", "steps": ["Load page", "Check elements"], "expected": ["All elements render correctly"]},
        }

        cases = []
        for dim in dimensions:
            if dim in templates:
                tmpl = templates[dim]
                tc = TestCase(
                    id=generate_case_id(),
                    story_id=story_id,
                    iteration_id=iteration_id,
                    title=tmpl["title"],
                    type=CaseType(dim),
                    steps=tmpl["steps"],
                    expected_results=tmpl["expected"],
                    tags=[dim],
                )
                f = case_dir / f"{tc.id}.json"
                f.write_text(tc.model_dump_json(indent=2))
                cases.append(tc.model_dump())

        return {"cases": cases, "count": len(cases), "story_id": story_id}

    async def enhance_with_knowledge_base(self, story_id: str, iteration_id: str) -> dict:
        case_dir = get_case_dir(self._workspace_dir, iteration_id)
        existing = []
        if case_dir.exists():
            for f in case_dir.glob("*.json"):
                data = json.loads(f.read_text())
                if data.get("story_id") == story_id:
                    existing.append(data)

        knowledge_dir = Path(self._workspace_dir) / "test" / "knowledge" / "docs"
        kb_count = len(list(knowledge_dir.glob("*.json"))) if knowledge_dir.exists() else 0

        return {
            "existing_cases": len(existing),
            "knowledge_base_matches": kb_count,
            "enhanced": False,
            "note": "Knowledge base enhancement requires RAG integration",
        }

    async def calculate_coverage(self, iteration_id: str) -> dict:
        case_dir = get_case_dir(self._workspace_dir, iteration_id)
        story_dir = Path(self._workspace_dir) / "test" / "iteration" / iteration_id / "story"

        total_cases = len(list(case_dir.glob("*.json"))) if case_dir.exists() else 0
        total_stories = len(list(story_dir.glob("*.json"))) if story_dir.exists() else 0

        coverage = total_cases / total_stories if total_stories > 0 else 0.0

        return {
            "iteration_id": iteration_id,
            "total_stories": total_stories,
            "total_cases": total_cases,
            "coverage_rate": round(coverage, 2),
        }

    async def export_cases(self, case_ids: list[str], format: str = "excel") -> dict:
        return {
            "format": format,
            "case_count": len(case_ids),
            "status": "export-ready",
        }
