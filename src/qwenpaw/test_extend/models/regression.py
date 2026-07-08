# -*- coding: utf-8 -*-
"""Regression test selection models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class ChangeType(str, Enum):
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class CodeChange(BaseModel):
    file_path: str
    change_type: ChangeType
    added_lines: list[int] = Field(default_factory=list)
    removed_lines: list[int] = Field(default_factory=list)
    functions_changed: list[str] = Field(default_factory=list)


from common.trace_id import generate_trace_id


def _reg_id():
    return generate_trace_id("RP")


class RegressionPlan(BaseModel):
    id: str = Field(default_factory=_reg_id)
    iteration_id: str = ""
    base_ref: str = ""
    head_ref: str = ""
    changes: list[CodeChange] = Field(default_factory=list)
    selected_cases: list[str] = Field(default_factory=list)
    skipped_cases: list[str] = Field(default_factory=list)
    selection_reason: dict[str, str] = Field(default_factory=dict)
    total_cases: int = 0
    selected_count: int = 0
    estimated_time_saved: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
