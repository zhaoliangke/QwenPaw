# -*- coding: utf-8 -*-
"""Video recording API router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.recording_agent import RecordingAgent
from common.trace_id import generate_trace_id
from models.recording import RecordingStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recording", tags=["recording"])

_agent: RecordingAgent | None = None


def init_recording_agent(workspace_dir: str):
    global _agent
    _agent = RecordingAgent(workspace_dir)


@router.post("/start")
async def start_recording(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Recording agent not initialized")
    rec = _agent.start_recording(
        case_id=body.get("case_id", ""),
        run_id=body.get("run_id", ""),
        iteration_id=body.get("iteration_id", ""),
        script_id=body.get("script_id", ""),
    )
    return {
        "recording_id": rec.id,
        "trace_path": rec.trace_path,
        "status": rec.status.value,
        "trace_config": _agent.get_playwright_trace_config(rec.id),
    }


@router.post("/{rec_id}/stop")
async def stop_recording(rec_id: str, body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Recording agent not initialized")
    success = body.get("success", True)
    error = body.get("error", "")
    rec = _agent.stop_recording(rec_id, success, error)
    if not rec:
        raise HTTPException(status_code=404, detail=f"Recording {rec_id} not found")
    return {
        "recording_id": rec.id,
        "status": rec.status.value,
        "duration_ms": rec.duration_ms,
        "file_size_bytes": rec.file_size_bytes,
    }


@router.get("/{rec_id}")
async def get_recording(rec_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Recording agent not initialized")
    rec = _agent.get_recording(rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail=f"Recording {rec_id} not found")
    return rec.model_dump()


@router.get("/{rec_id}/report")
async def get_report_snippet(rec_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Recording agent not initialized")
    return _agent.generate_report_snippet(rec_id)


@router.get("/")
async def list_recordings(run_id: str = "", case_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Recording agent not initialized")
    recordings = _agent.list_recordings(run_id, case_id)
    return {"recordings": [r.model_dump() for r in recordings], "total": len(recordings)}
