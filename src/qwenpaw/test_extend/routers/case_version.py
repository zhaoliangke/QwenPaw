# -*- coding: utf-8 -*-
"""Case version control router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.case_version_agent import CaseVersionTracker
from models.case_version import ChangeType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/case_version", tags=["case_version"])

_tracker: CaseVersionTracker | None = None


def init_case_version_tracker(workspace_dir: str):
    global _tracker
    _tracker = CaseVersionTracker(workspace_dir)


@router.post("/{case_id}/snapshot")
async def create_snapshot(case_id: str, body: dict[str, Any]) -> dict[str, Any]:
    if not _tracker:
        raise HTTPException(status_code=503, detail="Version tracker not initialized")
    case_data = body.get("case_data", {})
    change_type = ChangeType(body.get("change_type", "updated"))
    version = _tracker.create_version(
        case_id=case_id,
        case_data=case_data,
        change_type=change_type,
        comment=body.get("comment", ""),
        created_by=body.get("created_by", ""),
        previous_data=body.get("previous_data"),
    )
    return {
        "version_id": version.id,
        "case_id": version.case_id,
        "version": version.version,
        "change_type": version.change_type.value,
        "changes_count": len(version.changes),
    }


@router.get("/{case_id}/versions")
async def list_versions(case_id: str) -> dict[str, Any]:
    if not _tracker:
        raise HTTPException(status_code=503, detail="Version tracker not initialized")
    versions = _tracker.list_versions(case_id)
    return {
        "versions": [v.model_dump() for v in versions],
        "total": len(versions),
    }


@router.get("/{case_id}/versions/{version}")
async def get_version(case_id: str, version: int) -> dict[str, Any]:
    if not _tracker:
        raise HTTPException(status_code=503, detail="Version tracker not initialized")
    v = _tracker.get_version(case_id, version)
    if not v:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")
    return v.model_dump()


@router.get("/{case_id}/diff")
async def diff_versions(case_id: str, from_ver: int, to_ver: int) -> dict[str, Any]:
    if not _tracker:
        raise HTTPException(status_code=503, detail="Version tracker not initialized")
    diff = _tracker.diff_versions(case_id, from_ver, to_ver)
    return diff.model_dump()


@router.post("/{case_id}/rollback")
async def rollback(case_id: str, body: dict[str, Any]) -> dict[str, Any]:
    if not _tracker:
        raise HTTPException(status_code=503, detail="Version tracker not initialized")
    version = body.get("version", 0)
    comment = body.get("comment", "")
    result = _tracker.rollback(case_id, version, comment)
    if not result:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")
    return {
        "version_id": result.id,
        "case_id": result.case_id,
        "version": result.version,
        "change_type": result.change_type.value,
    }
