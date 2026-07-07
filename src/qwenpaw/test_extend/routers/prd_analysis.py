# -*- coding: utf-8 -*-
"""Story Management API routes (extended on /api/test/ prefix)."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/story/generate")
async def generate_stories(body: dict):
    from ..mcp_tools.story_generator import generate_stories_tool
    return await generate_stories_tool(
        parsed_prd=body["parsed_prd"],
        iteration_id=body["iteration_id"],
    )


@router.get("/story/{story_id}")
async def get_story(story_id: str, iteration_id: str = ""):
    from ..storage.paths import get_story_dir
    from ..common.utils import read_json_file
    from qwenpaw.constant import WORKING_DIR
    story_dir = get_story_dir(WORKING_DIR, iteration_id)
    f = story_dir / f"{story_id}.json"
    data = read_json_file(f)
    return data or {"error": "Story not found"}


@router.put("/story/{story_id}")
async def update_story(story_id: str, body: dict):
    from ..storage.paths import get_story_dir
    from ..common.utils import write_json_file
    from qwenpaw.constant import WORKING_DIR
    story_dir = get_story_dir(WORKING_DIR, body.get("iteration_id", ""))
    story_dir.mkdir(parents=True, exist_ok=True)
    write_json_file(story_dir / f"{story_id}.json", body)
    return body


@router.post("/defect/submit")
async def submit_defect(body: dict):
    from ..mcp_tools.defect_sync import submit_defect_tool
    return await submit_defect_tool(
        case_id=body["case_id"],
        iteration_id=body.get("iteration_id", ""),
        steps=body.get("steps", []),
        expected=body.get("expected", ""),
        actual=body.get("actual", ""),
        severity=body.get("severity", "medium"),
        screenshot_paths=body.get("screenshot_paths"),
        target=body.get("target", "jira"),
    )
