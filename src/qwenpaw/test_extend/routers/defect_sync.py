# -*- coding: utf-8 -*-
"""Defect synchronization API router.

Provides endpoints for submitting defects to Jira/ZenTao and
managing defect traceability links.

Prefix: /api/test/defect/
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["Defect Sync"])


class DefectSubmitRequest(BaseModel):
    failure_summary: str = Field(description="Brief description of the failure")
    steps: list[str] = Field(default_factory=list)
    expected: str = ""
    actual: str = ""
    severity: str = Field(default="medium", description="critical/high/medium/low")
    iteration_id: str = ""
    story_id: str | None = None
    case_id: str | None = None
    screenshots: list[str] = Field(default_factory=list)
    target_system: str = Field(default="jira", description="jira or zentao")


class DefectSubmitResponse(BaseModel):
    defect_id: str
    external_ticket_id: str
    external_url: str
    status: str
    submitted_at: str


class DefectStatusRequest(BaseModel):
    defect_id: str = Field(description="Local defect record ID")
    target_system: str = Field(default="jira")


class DefectStatusResponse(BaseModel):
    defect_id: str
    external_ticket_id: str
    external_status: str
    synced_at: str


@router.post("/submit", response_model=DefectSubmitResponse)
async def submit_defect(req: DefectSubmitRequest):
    try:
        from mcp_tools.defect_sync import submit_defect as submit_tool
        result = submit_tool(
            failure_summary=req.failure_summary,
            steps=req.steps,
            expected=req.expected,
            actual=req.actual,
            severity=req.severity,
            iteration_id=req.iteration_id,
            story_id=req.story_id,
            case_id=req.case_id,
            screenshots=req.screenshots,
            target_system=req.target_system,
        )
        return DefectSubmitResponse(
            defect_id=result.get("defect_id", ""),
            external_ticket_id=result.get("external_ticket_id", ""),
            external_url=result.get("external_url", ""),
            status=result.get("status", "submitted"),
            submitted_at=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/status", response_model=DefectStatusResponse)
async def sync_defect_status(req: DefectStatusRequest):
    try:
        from mcp_tools.defect_sync import sync_defect_status as sync_tool
        result = sync_tool(
            defect_id=req.defect_id,
            target_system=req.target_system,
        )
        return DefectStatusResponse(
            defect_id=result.get("defect_id", req.defect_id),
            external_ticket_id=result.get("external_ticket_id", ""),
            external_status=result.get("external_status", "unknown"),
            synced_at=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_defects(iteration_id: str = ""):
    return {"iteration_id": iteration_id, "defects": []}
