# -*- coding: utf-8 -*-
"""Case Management API routes at /api/test/case/."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/generate")
async def generate_cases(body: dict):
    from ..mcp_tools.case_generator import generate_cases_tool
    return await generate_cases_tool(
        story_id=body["story_id"],
        iteration_id=body["iteration_id"],
        dimensions=body.get("dimensions"),
    )


@router.get("/{case_id}")
async def get_case(case_id: str, iteration_id: str):
    from ..storage.paths import get_case_dir
    from ..common.utils import read_json_file
    from qwenpaw.constant import WORKING_DIR
    case_dir = get_case_dir(WORKING_DIR, iteration_id)
    f = case_dir / f"{case_id}.json"
    data = read_json_file(f)
    return data or {"error": "Case not found"}


@router.put("/{case_id}")
async def update_case(case_id: str, body: dict):
    from ..storage.paths import get_case_dir
    from ..common.utils import write_json_file
    from qwenpaw.constant import WORKING_DIR
    case_dir = get_case_dir(WORKING_DIR, body.get("iteration_id", ""))
    write_json_file(case_dir / f"{case_id}.json", body)
    return body


@router.get("/export")
async def export_cases(case_ids: str = "", format: str = "excel", iteration_id: str = ""):
    from ..mcp_tools.case_generator import export_cases_tool
    ids = [i.strip() for i in case_ids.split(",") if i.strip()]
    return await export_cases_tool(ids, format)
