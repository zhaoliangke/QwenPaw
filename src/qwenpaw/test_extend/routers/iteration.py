# -*- coding: utf-8 -*-
"""Iteration Management API routes at /api/test/iteration/."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/")
async def create_iteration(body: dict):
    from ..mcp_tools.iteration_mgr import create_iteration_tool
    return await create_iteration_tool(
        name=body["name"], version=body["version"], module=body["module"],
        start_date=body["start_date"], end_date=body["end_date"],
        description=body.get("description", ""),
        git_branch=body.get("git_branch", ""),
        test_environment=body.get("test_environment", ""),
    )


@router.get("/")
async def list_iterations(status: str = ""):
    from ..mcp_tools.iteration_mgr import list_iterations_tool
    return await list_iterations_tool(status or None)


@router.get("/{iteration_id}")
async def get_iteration(iteration_id: str):
    from ..mcp_tools.iteration_mgr import get_iteration_tool
    result = await get_iteration_tool(iteration_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.put("/{iteration_id}")
async def update_iteration(iteration_id: str, body: dict):
    from ..storage.iteration_store import IterationStore
    from qwenpaw.constant import WORKING_DIR
    store = IterationStore(WORKING_DIR)
    it = store.get(iteration_id)
    if not it:
        raise HTTPException(status_code=404, detail="Iteration not found")
    for k, v in body.items():
        if hasattr(it, k):
            setattr(it, k, v)
    store.update(it)
    return it.model_dump()


@router.post("/{iteration_id}/snapshot")
async def create_snapshot(iteration_id: str):
    from ..mcp_tools.iteration_mgr import create_snapshot_tool
    return await create_snapshot_tool(iteration_id)


@router.get("/diff")
async def diff_iterations(a: str, b: str):
    from ..mcp_tools.iteration_mgr import diff_iterations_tool
    return await diff_iterations_tool(a, b)
