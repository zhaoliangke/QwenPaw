# -*- coding: utf-8 -*-
"""Report Center API routes at /api/test/report/."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/generate")
async def generate_report(body: dict):
    from ..mcp_tools.report_builder import generate_report_tool
    return await generate_report_tool(
        test_run=body["test_run"],
        iteration_id=body["iteration_id"],
    )


@router.get("/{report_id}")
async def get_report(report_id: str, iteration_id: str = ""):
    from ..storage.paths import get_report_dir
    from ..common.utils import read_json_file
    from qwenpaw.constant import WORKING_DIR
    report_dir = get_report_dir(WORKING_DIR, iteration_id)
    f = report_dir / f"{report_id}.json"
    data = read_json_file(f)
    return data or {"error": "Report not found"}


@router.get("/export/{report_id}")
async def export_report(report_id: str, format: str = "html", iteration_id: str = ""):
    from ..mcp_tools.report_builder import export_report_tool
    return await export_report_tool(report_id, format, iteration_id)


@router.post("/push/{report_id}")
async def push_report(report_id: str, body: dict):
    from ..mcp_tools.report_builder import push_report_tool
    return await push_report_tool(
        report_id=report_id,
        channels=body.get("channels"),
    )
