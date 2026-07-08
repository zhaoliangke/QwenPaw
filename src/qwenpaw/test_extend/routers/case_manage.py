# -*- coding: utf-8 -*-
"""Case Management API routes at /api/test/case/."""

from fastapi import APIRouter, HTTPException

from qwenpaw.constant import WORKING_DIR

router = APIRouter()


@router.post("/generate")
async def generate_cases(body: dict):
    from mcp_tools.case_generator import generate_cases_tool

    # Support both story_id and full story object
    if "story" in body:
        story = body["story"]
        story_id = story.get("id", "")
        title = story.get("title", "")
        as_a = story.get("as_a", "")
        i_want = story.get("i_want", "")
        so_that = story.get("so_that", "")
        acceptance = story.get("acceptance_criteria", [])
        description = f"As a {as_a}, I want {i_want}, so that {so_that}"
        if acceptance:
            try:
                description += "\n验收标准：" + ", ".join(
                    str(a.get("scenario", a) if isinstance(a, dict) else a) for a in acceptance
                )
            except Exception:
                pass
        cases = [{
            "id": f"TC-{story_id}",
            "title": f"[用例] {title}",
            "story_id": story_id,
            "type": "functional",
            "priority": story.get("priority", "medium"),
            "steps": [f"触发条件：{as_a}", f"操作步骤：{i_want}", f"预期结果：{so_that}"],
            "expected": so_that,
        }]
        # Add edge case variation
        cases.append({
            "id": f"TC-{story_id}-EDGE",
            "title": f"[边界用例] {title}",
            "story_id": story_id,
            "type": "edge",
            "priority": story.get("priority", "medium"),
            "steps": [f"触发条件：{as_a}（异常场景）", f"操作步骤：{i_want}（非法输入）", "预期结果：提示错误信息"],
            "expected": "系统正确处理边界情况并给出友好提示",
        })
        return {"cases": cases, "count": len(cases)}

    return await generate_cases_tool(
        story_id=body.get("story_id", ""),
        iteration_id=body["iteration_id"],
        dimensions=body.get("dimensions"),
    )


@router.get("/{case_id}")
async def get_case(case_id: str, iteration_id: str):
    from storage.paths import get_case_dir
    from common.utils import read_json_file
    from qwenpaw.constant import WORKING_DIR
    case_dir = get_case_dir(WORKING_DIR, iteration_id)
    f = case_dir / f"{case_id}.json"
    data = read_json_file(f)
    return data or {"error": "Case not found"}


@router.put("/{case_id}")
async def update_case(case_id: str, body: dict):
    from storage.paths import get_case_dir
    from common.utils import write_json_file
    from qwenpaw.constant import WORKING_DIR
    case_dir = get_case_dir(WORKING_DIR, body.get("iteration_id", ""))
    write_json_file(case_dir / f"{case_id}.json", body)
    return body


@router.get("/export")
async def export_cases(case_ids: str = "", format: str = "excel", iteration_id: str = ""):
    from mcp_tools.case_generator import export_cases_tool
    ids = [i.strip() for i in case_ids.split(",") if i.strip()]
    return await export_cases_tool(ids, format)


@router.post("/save")
async def save_cases(body: dict):
    """Save generated test cases to storage."""
    from models.test_case import TestCase, CaseType
    from infra.storage_factory import StorageFactory

    cases = body.get("cases", [])
    iteration_id = body.get("iteration_id", "")
    if not cases:
        return {"saved": 0, "message": "No cases to save"}

    factory = StorageFactory(str(WORKING_DIR))
    store = factory.create_case_store()
    saved_count = 0
    for c in cases:
        try:
            case = TestCase(
                id=c.get("id", ""),
                story_id=c.get("story_id", ""),
                iteration_id=iteration_id,
                title=c.get("title", ""),
                type=CaseType(c.get("type", "functional")),
                priority=c.get("priority", "medium"),
                module=c.get("module", ""),
                preconditions=c.get("preconditions", []),
                steps=c.get("steps", []),
                expected_results=c.get("expected_results", [c.get("expected", "")]),
                tags=c.get("tags", []),
                is_active=True,
            )
            await store.create(case)
            saved_count += 1
        except Exception as e:
            import logging
            logging.warning(f"Failed to save case {c.get('id')}: {e}")
    return {"saved": saved_count, "message": f"Saved {saved_count} cases"}
