# -*- coding: utf-8 -*-
"""Test case version control models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class ChangeType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    ROLLED_BACK = "rolled_back"


class FieldChange(BaseModel):
    field: str
    old_value: Any = None
    new_value: Any = None


class CaseVersion(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("CV"))
    case_id: str = ""
    version: int = 0
    case_data: dict[str, Any] = Field(default_factory=dict)
    change_type: ChangeType = ChangeType.CREATED
    changes: list[FieldChange] = Field(default_factory=list)
    comment: str = ""
    created_by: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CaseDiff(BaseModel):
    case_id: str
    from_version: int
    to_version: int
    changes: list[FieldChange] = Field(default_factory=list)
    has_differences: bool = False
