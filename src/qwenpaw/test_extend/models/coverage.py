# -*- coding: utf-8 -*-
"""Coverage analysis models."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


def _cov_id():
    return generate_trace_id("CV")


class CoverageType(str, Enum):
    LINE = "line"
    BRANCH = "branch"
    FUNCTION = "function"


class CoverageReport(BaseModel):
    id: str = Field(default_factory=_cov_id)
    iteration_id: str = ""
    run_id: str = ""
    coverage_type: CoverageType = CoverageType.LINE
    total_lines: int = 0
    covered_lines: int = 0
    total_branches: int = 0
    covered_branches: int = 0
    line_rate: float = 0.0
    branch_rate: float = 0.0
    uncovered_files: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def summary(self) -> str:
        return (
            f"Line: {self.line_rate:.1%} ({self.covered_lines}/{self.total_lines}), "
            f"Branch: {self.branch_rate:.1%} ({self.covered_branches}/{self.total_branches})"
        )
