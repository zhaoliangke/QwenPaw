# -*- coding: utf-8 -*-
"""UI Automation API routes at /api/test/ui-auto/."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/generate")
async def generate_script(body: dict):
    from mcp_tools.ui_auto_tool import generate_script_tool
    return await generate_script_tool(
        test_case=body["test_case"],
        page_name=body.get("page_name", ""),
        iteration_id=body.get("iteration_id", ""),
        base_url=body.get("base_url", ""),
        element_map=body.get("element_map"),
        mode=body.get("mode", "template"),
        project_id=body.get("project_id", ""),
    )


@router.post("/debug")
async def debug_script(body: dict):
    from mcp_tools.ui_auto_tool import debug_script_tool
    return await debug_script_tool(
        script_content=body["script_content"],
        test_case_id=body["test_case_id"],
    )


@router.get("/script/{script_id}")
async def get_script(script_id: str, iteration_id: str = ""):
    from storage.paths import get_script_dir
    from qwenpaw.constant import WORKING_DIR
    script_dir = get_script_dir(WORKING_DIR, iteration_id)
    f = script_dir / f"{script_id}.py"
    if f.exists():
        return {"script_id": script_id, "content": f.read_text()}
    return {"error": "Script not found"}


@router.put("/script/{script_id}")
async def update_script(script_id: str, body: dict):
    from storage.paths import get_script_dir
    from qwenpaw.constant import WORKING_DIR
    script_dir = get_script_dir(WORKING_DIR, body.get("iteration_id", ""))
    script_dir.mkdir(parents=True, exist_ok=True)
    f = script_dir / f"{script_id}.py"
    f.write_text(body.get("content", ""))
    return {"script_id": script_id, "status": "saved"}
