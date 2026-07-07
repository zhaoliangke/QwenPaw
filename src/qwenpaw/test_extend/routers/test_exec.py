# -*- coding: utf-8 -*-
"""Test Execution API routes at /api/test/exec/."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/run")
async def run_batch(body: dict):
    from ..mcp_tools.test_scheduler import run_batch_tool
    return await run_batch_tool(
        case_ids=body["case_ids"],
        iteration_id=body["iteration_id"],
        concurrency=body.get("concurrency", 4),
        environment=body.get("environment", "test"),
    )


@router.post("/run-single")
async def run_single(body: dict):
    from ..mcp_tools.test_scheduler import run_single_tool
    return await run_single_tool(
        case_id=body["case_id"],
        environment=body.get("environment", "test"),
        iteration_id=body.get("iteration_id", ""),
    )


@router.get("/progress/{run_id}")
async def get_progress(run_id: str):
    from ..mcp_tools.test_scheduler import get_progress_tool
    return await get_progress_tool(run_id)


@router.get("/history")
async def get_history(iteration_id: str):
    from ..storage.paths import get_exec_log_dir
    from qwenpaw.constant import WORKING_DIR
    log_dir = get_exec_log_dir(WORKING_DIR, iteration_id)
    runs = []
    if log_dir.exists():
        for f in sorted(log_dir.glob("run_*.log"), reverse=True):
            runs.append({"run_id": f.stem.replace("run_", ""), "log": f.read_text()[:500]})
    return {"iteration_id": iteration_id, "runs": runs}
