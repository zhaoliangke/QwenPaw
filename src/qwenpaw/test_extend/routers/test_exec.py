# -*- coding: utf-8 -*-
"""Test Execution API routes at /api/test/exec/."""

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)


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


@router.websocket("/ws/{run_id}")
async def websocket_progress(websocket: WebSocket, run_id: str):
    """WebSocket endpoint for real-time execution progress.

    Clients connect to /api/test/exec/ws/{run_id} and receive JSON
    progress updates as the test run executes.
    """
    await websocket.accept()
    logger.info("WebSocket connected for run %s", run_id)

    from ..mcp_tools.test_scheduler import _get_agent

    agent = _get_agent()

    sentinel = asyncio.Event()

    def on_progress(payload: dict):
        async def send():
            try:
                await websocket.send_json(payload)
            except Exception:
                sentinel.set()
        asyncio.create_task(send())

    agent.on_progress(run_id, on_progress)

    try:
        # Send initial progress
        from ..mcp_tools.test_scheduler import get_progress_tool
        initial = await get_progress_tool(run_id)
        await websocket.send_json(initial)

        # Keep connection alive until done or disconnected
        while not sentinel.is_set():
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                run = agent._active_runs.get(run_id)
                if run and run.status in ("completed", "failed"):
                    await websocket.send_json({"run_id": run_id, "status": run.status, "completed": True})
                    break
                await websocket.send_json({"type": "heartbeat"})
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for run %s", run_id)
    except Exception as e:
        logger.warning("WebSocket error for run %s: %s", run_id, e)
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


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
