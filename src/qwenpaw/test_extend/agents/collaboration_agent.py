# -*- coding: utf-8 -*-
"""Collaboration agent — comments, assignments, and audit logging."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from common.utils import read_json_file, write_json_file
from common.trace_id import generate_trace_id
from models.collaboration import (
    AuditAction,
    AuditLog,
    Assignment,
    Comment,
    ResourceType,
)
from storage.paths import get_collaboration_dir

logger = logging.getLogger(__name__)


class CollaborationAgent:
    def __init__(self, workspace_dir: str | Path):
        self._workspace = Path(workspace_dir)
        self._collab_dir = get_collaboration_dir(self._workspace)
        self._collab_dir.mkdir(parents=True, exist_ok=True)
        self._comments_file = self._collab_dir / "comments.json"
        self._assignments_file = self._collab_dir / "assignments.json"
        self._audit_file = self._collab_dir / "audit_logs.json"
        self._comments: list[dict] = self._load_list(self._comments_file)
        self._assignments: list[dict] = self._load_list(self._assignments_file)
        self._audit_logs: list[dict] = self._load_list(self._audit_file)

    async def add_comment(
        self,
        resource_type: str,
        resource_id: str,
        author: str,
        content: str,
        parent_id: str = "",
    ) -> Comment:
        comment = Comment(
            resource_type=ResourceType(resource_type),
            resource_id=resource_id,
            author=author,
            content=content,
            parent_id=parent_id,
        )
        self._comments.append(comment.model_dump())
        self._save_list(self._comments_file, self._comments)
        await self._log_audit(AuditAction.COMMENT, ResourceType(resource_type), resource_id, author, f"Comment added")
        return comment

    async def list_comments(self, resource_type: str = "", resource_id: str = "") -> list[Comment]:
        results = []
        for data in self._comments:
            if resource_type and data.get("resource_type") != resource_type:
                continue
            if resource_id and data.get("resource_id") != resource_id:
                continue
            results.append(Comment(**data))
        return sorted(results, key=lambda c: c.created_at, reverse=True)

    async def delete_comment(self, comment_id: str, user: str = "") -> bool:
        for i, data in enumerate(self._comments):
            if data.get("id") == comment_id:
                self._comments.pop(i)
                self._save_list(self._comments_file, self._comments)
                await self._log_audit(AuditAction.DELETE, ResourceType.CASE, comment_id, user, f"Comment deleted")
                return True
        return False

    async def create_assignment(
        self,
        resource_type: str,
        resource_id: str,
        assignee: str,
        assigner: str = "",
        due_date: str = "",
    ) -> Assignment:
        assignment = Assignment(
            resource_type=ResourceType(resource_type),
            resource_id=resource_id,
            assignee=assignee,
            assigner=assigner,
            due_date=due_date,
        )
        self._assignments.append(assignment.model_dump())
        self._save_list(self._assignments_file, self._assignments)
        await self._log_audit(AuditAction.ASSIGN, ResourceType(resource_type), resource_id, assigner, f"Assigned to {assignee}")
        return assignment

    async def list_assignments(self, assignee: str = "", resource_id: str = "") -> list[Assignment]:
        results = []
        for data in self._assignments:
            if assignee and data.get("assignee") != assignee:
                continue
            if resource_id and data.get("resource_id") != resource_id:
                continue
            results.append(Assignment(**data))
        return sorted(results, key=lambda a: a.created_at, reverse=True)

    async def update_assignment_status(self, assignment_id: str, status: str, user: str = "") -> bool:
        for data in self._assignments:
            if data.get("id") == assignment_id:
                data["status"] = status
                self._save_list(self._assignments_file, self._assignments)
                await self._log_audit(AuditAction.UPDATE, ResourceType(data.get("resource_type", "case")), data.get("resource_id", ""), user, f"Assignment status -> {status}")
                return True
        return False

    async def log_audit(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user: str = "",
        details: str = "",
        ip_address: str = "",
    ) -> AuditLog:
        return await self._log_audit(
            AuditAction(action), ResourceType(resource_type),
            resource_id, user, details, ip_address,
        )

    async def list_audit_logs(self, resource_id: str = "", user: str = "", limit: int = 100) -> list[AuditLog]:
        results = []
        for data in self._audit_logs:
            if resource_id and data.get("resource_id") != resource_id:
                continue
            if user and data.get("user") != user:
                continue
            results.append(AuditLog(**data))
        return sorted(results, key=lambda l: l.created_at, reverse=True)[:limit]

    async def _log_audit(self, action: AuditAction, resource_type: ResourceType, resource_id: str, user: str = "", details: str = "", ip_address: str = "") -> AuditLog:
        log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user=user,
            details=details,
            ip_address=ip_address,
        )
        self._audit_logs.append(log.model_dump())
        self._save_list(self._audit_file, self._audit_logs)
        return log

    def _load_list(self, path: Path) -> list[dict]:
        if path.exists():
            data = read_json_file(path)
            return data if isinstance(data, list) else []
        return []

    def _save_list(self, path: Path, data: list[dict]):
        write_json_file(path, data)
