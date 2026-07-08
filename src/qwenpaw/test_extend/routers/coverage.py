# -*- coding: utf-8 -*-
"""Coverage analysis API router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.coverage_agent import CoverageAgent, CoverageReport

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/coverage", tags=["coverage"])

_agent: CoverageAgent | None = None


def init_coverage_agent(workspace_dir: str):
    global _agent
    _agent = CoverageAgent(workspace_dir)


@router.post("/run")
async def run_coverage(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Coverage agent not initialized")

    source_path = body.get("source_path", "")
    test_path = body.get("test_path", "")
    iteration_id = body.get("iteration_id", "")
    run_id = body.get("run_id", "")

    if not source_path or not test_path:
        raise HTTPException(status_code=400, detail="source_path and test_path required")

    report = await _agent.run_coverage(source_path, test_path, iteration_id, run_id)
    return {
        "id": report.id,
        "summary": report.summary,
        "line_rate": report.line_rate,
        "branch_rate": report.branch_rate,
        "uncovered_files_count": len(report.uncovered_files),
    }


@router.get("/reports")
async def list_reports(iteration_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Coverage agent not initialized")
    reports = await _agent.list_reports(iteration_id)
    return {
        "reports": [r.model_dump() for r in reports],
        "total": len(reports),
    }


@router.get("/{report_id}")
async def get_report(report_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Coverage agent not initialized")
    gaps = await _agent.get_uncovered_gaps(report_id)
    return {"report_id": report_id, "gaps": gaps, "gap_count": len(gaps)}
