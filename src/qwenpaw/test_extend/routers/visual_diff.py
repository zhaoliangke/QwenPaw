# -*- coding: utf-8 -*-
"""Visual regression test router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.visual_diff_agent import VisualDiffAgent
from common.trace_id import generate_trace_id
from models.visual_diff import VisualDiffTest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/visual_diff", tags=["visual_diff"])

_agent: VisualDiffAgent | None = None


def init_visual_diff_agent(workspace_dir: str):
    global _agent
    _agent = VisualDiffAgent(workspace_dir)


@router.post("/tests")
async def create_test(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Visual diff agent not initialized")
    test = VisualDiffTest(
        id=generate_trace_id("VD"),
        name=body.get("name", ""),
        url=body.get("url", ""),
        selector=body.get("selector", ""),
        viewport_width=body.get("viewport_width", 1280),
        viewport_height=body.get("viewport_height", 720),
        threshold=body.get("threshold", 0.1),
        iteration_id=body.get("iteration_id", ""),
    )
    return {"id": test.id, "name": test.name, "url": test.url}


@router.post("/tests/{test_id}/run")
async def run_test(test_id: str, body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Visual diff agent not initialized")
    test = VisualDiffTest(
        id=test_id, name="adhoc", url=body.get("url", ""),
        viewport_width=body.get("viewport_width", 1280),
        viewport_height=body.get("viewport_height", 720),
    )
    result = await _agent.run_test(test, run_id=body.get("run_id", ""))
    return {
        "result_id": result.id,
        "status": result.status.value,
        "diff_percentage": result.diff_percentage,
        "diff_pixels": result.diff_pixel_count,
        "regions_count": len(result.diff_regions),
        "baseline_path": result.baseline_path,
        "current_path": result.current_path,
        "diff_path": result.diff_path,
    }


@router.post("/tests/{test_id}/baseline")
async def update_baseline(test_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Visual diff agent not initialized")
    ok = _agent.update_baseline(test_id)
    return {"updated": ok}


@router.get("/results")
async def list_results(test_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Visual diff agent not initialized")
    results = _agent.list_results(test_id)
    return {"results": [r.model_dump() for r in results], "total": len(results)}
