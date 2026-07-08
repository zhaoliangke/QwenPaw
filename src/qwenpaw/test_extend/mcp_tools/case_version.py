# -*- coding: utf-8 -*-
"""Case version control MCP tools."""

import logging

logger = logging.getLogger(__name__)

_tracker = None


def _get_tracker():
    global _tracker
    if _tracker is None:
        from agents.case_version_agent import CaseVersionTracker
        from qwenpaw.constant import WORKING_DIR
        _tracker = CaseVersionTracker(WORKING_DIR)
    return _tracker


async def create_case_snapshot_tool(
    case_id: str,
    case_data: dict,
    change_type: str = "updated",
    comment: str = "",
    created_by: str = "",
    previous_data: dict | None = None,
) -> dict:
    version = _get_tracker().create_version(
        case_id=case_id, case_data=case_data,
        change_type=change_type, comment=comment,
        created_by=created_by, previous_data=previous_data,
    )
    return {"version_id": version.id, "case_id": version.case_id, "version": version.version}


async def list_case_versions_tool(case_id: str) -> dict:
    versions = _get_tracker().list_versions(case_id)
    return {"versions": [v.model_dump() for v in versions], "total": len(versions)}


async def diff_case_versions_tool(case_id: str, from_ver: int, to_ver: int) -> dict:
    return _get_tracker().diff_versions(case_id, from_ver, to_ver)


async def rollback_case_tool(case_id: str, version: int, comment: str = "") -> dict:
    result = _get_tracker().rollback(case_id, version, comment)
    if not result:
        return {"error": f"Version {version} not found"}
    return {"version_id": result.id, "version": result.version}
