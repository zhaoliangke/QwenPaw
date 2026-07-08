# -*- coding: utf-8 -*-
"""Collaboration router — comments, assignments, audit logs."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.collaboration_agent import CollaborationAgent
from models.collaboration import AuditAction, ResourceType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/collab", tags=["collaboration"])

_agent: CollaborationAgent | None = None


def init_collaboration_agent(workspace_dir: str):
    global _agent
    _agent = CollaborationAgent(workspace_dir)


@router.post("/comments")
async def add_comment(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Collaboration agent not initialized")
    comment = await _agent.add_comment(
        resource_type=body.get("resource_type", "case"),
        resource_id=body.get("resource_id", ""),
        author=body.get("author", ""),
        content=body.get("content", ""),
        parent_id=body.get("parent_id", ""),
    )
    return comment.model_dump()


@router.get("/comments")
async def list_comments(resource_type: str = "", resource_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Collaboration agent not initialized")
    comments = await _agent.list_comments(resource_type, resource_id)
    return {"comments": [c.model_dump() for c in comments], "total": len(comments)}


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str, user: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Collaboration agent not initialized")
    ok = await _agent.delete_comment(comment_id, user)
    return {"deleted": ok, "id": comment_id}


@router.post("/assignments")
async def create_assignment(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Collaboration agent not initialized")
    assignment = await _agent.create_assignment(
        resource_type=body.get("resource_type", "case"),
        resource_id=body.get("resource_id", ""),
        assignee=body.get("assignee", ""),
        assigner=body.get("assigner", ""),
        due_date=body.get("due_date", ""),
    )
    return assignment.model_dump()


@router.get("/assignments")
async def list_assignments(assignee: str = "", resource_id: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Collaboration agent not initialized")
    assignments = await _agent.list_assignments(assignee, resource_id)
    return {"assignments": [a.model_dump() for a in assignments], "total": len(assignments)}


@router.patch("/assignments/{assignment_id}")
async def update_assignment(assignment_id: str, body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Collaboration agent not initialized")
    ok = await _agent.update_assignment_status(assignment_id, body.get("status", ""), body.get("user", ""))
    return {"updated": ok, "id": assignment_id}


@router.post("/audit")
async def log_audit(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Collaboration agent not initialized")
    log = await _agent.log_audit(
        action=body.get("action", "create"),
        resource_type=body.get("resource_type", "case"),
        resource_id=body.get("resource_id", ""),
        user=body.get("user", ""),
        details=body.get("details", ""),
        ip_address=body.get("ip_address", ""),
    )
    return log.model_dump()


@router.get("/audit")
async def list_audit_logs(resource_id: str = "", user: str = "", limit: int = 100) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Collaboration agent not initialized")
    logs = await _agent.list_audit_logs(resource_id, user, limit)
    return {"logs": [l.model_dump() for l in logs], "total": len(logs)}
