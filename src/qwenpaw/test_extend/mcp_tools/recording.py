# -*- coding: utf-8 -*-
"""Video recording MCP tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.recording_agent import RecordingAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = RecordingAgent(WORKING_DIR)
    return _agent


async def start_recording_tool(
    case_id: str = "",
    run_id: str = "",
    iteration_id: str = "",
    script_id: str = "",
) -> dict:
    rec = _get_agent().start_recording(case_id, run_id, iteration_id, script_id)
    return {"recording_id": rec.id, "trace_path": rec.trace_path, "status": rec.status.value}


async def stop_recording_tool(recording_id: str, success: bool = True, error: str = "") -> dict:
    rec = _get_agent().stop_recording(recording_id, success, error)
    if not rec:
        return {"error": f"Recording {recording_id} not found"}
    return {"recording_id": rec.id, "status": rec.status.value, "duration_ms": rec.duration_ms}


async def get_recording_report_tool(recording_id: str) -> dict:
    return _get_agent().generate_report_snippet(recording_id)


async def list_recordings_tool(run_id: str = "", case_id: str = "") -> dict:
    recordings = _get_agent().list_recordings(run_id, case_id)
    return {"recordings": [r.model_dump() for r in recordings], "total": len(recordings)}
