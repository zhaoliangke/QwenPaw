# -*- coding: utf-8 -*-
"""Collaboration models — comments, assignments, and audit logs."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class ResourceType(str, Enum):
    CASE = "case"
    RUN = "run"
    REPORT = "report"
    DEFECT = "defect"


class Comment(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("CM"))
    resource_type: ResourceType = ResourceType.CASE
    resource_id: str = ""
    author: str = ""
    content: str = ""
    parent_id: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Assignment(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("AS"))
    resource_type: ResourceType = ResourceType.CASE
    resource_id: str = ""
    assignee: str = ""
    assigner: str = ""
    status: str = "pending"
    due_date: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    ASSIGN = "assign"
    COMMENT = "comment"
    EXPORT = "export"


class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("AL"))
    action: AuditAction = AuditAction.CREATE
    resource_type: ResourceType = ResourceType.CASE
    resource_id: str = ""
    user: str = ""
    details: str = ""
    ip_address: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
