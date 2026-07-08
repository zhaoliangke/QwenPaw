# -*- coding: utf-8 -*-
"""Collaboration MCP tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.collaboration_agent import CollaborationAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = CollaborationAgent(WORKING_DIR)
    return _agent


async def add_comment_tool(
    resource_type: str,
    resource_id: str,
    author: str,
    content: str,
    parent_id: str = "",
) -> dict:
    comment = await _get_agent().add_comment(resource_type, resource_id, author, content, parent_id)
    return comment.model_dump()


async def list_comments_tool(resource_type: str = "", resource_id: str = "") -> dict:
    comments = await _get_agent().list_comments(resource_type, resource_id)
    return {"comments": [c.model_dump() for c in comments], "total": len(comments)}


async def create_assignment_tool(
    resource_type: str,
    resource_id: str,
    assignee: str,
    assigner: str = "",
    due_date: str = "",
) -> dict:
    assignment = await _get_agent().create_assignment(resource_type, resource_id, assignee, assigner, due_date)
    return assignment.model_dump()


async def list_assignments_tool(assignee: str = "") -> dict:
    assignments = await _get_agent().list_assignments(assignee)
    return {"assignments": [a.model_dump() for a in assignments], "total": len(assignments)}


async def log_audit_tool(action: str, resource_type: str, resource_id: str, user: str = "", details: str = "") -> dict:
    log = await _get_agent().log_audit(action, resource_type, resource_id, user, details)
    return log.model_dump()


async def list_audit_logs_tool(resource_id: str = "", user: str = "", limit: int = 100) -> dict:
    logs = await _get_agent().list_audit_logs(resource_id, user, limit)
    return {"logs": [l.model_dump() for l in logs], "total": len(logs)}
