# -*- coding: utf-8 -*-
"""Test report data model."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class FailureCategory(str, Enum):
    """Root cause classification for failed test cases."""

    PRODUCT_DEFECT = "product_defect"
    SCRIPT_ERROR = "script_error"
    ENVIRONMENT_FAULT = "environment_fault"


class FailureItem(BaseModel):
    """Summary of a single test failure."""

    case_id: str = Field(description="Failed test case ID")
    category: FailureCategory = Field(description="Root cause category")
    summary: str = Field(description="Brief failure description")
    detail: str = Field(default="", description="Detailed failure analysis")


class TestReport(BaseModel):
    """A test report aggregating results from a test run."""

    id: str = Field(default_factory=lambda: "", description="Unique report identifier")
    test_run_id: str = Field(description="Source test run ID")
    iteration_id: str = Field(description="Parent iteration ID")
    total_cases: int = Field(default=0)
    passed: int = Field(default=0)
    failed: int = Field(default=0)
    skipped: int = Field(default=0)
    error_count: int = Field(default=0)
    pass_rate: float = Field(default=0.0, description="Pass rate as fraction (0.0 - 1.0)")
    coverage_rate: float = Field(default=0.0, description="Coverage rate as fraction (0.0 - 1.0)")
    failures: list[FailureItem] = Field(default_factory=list)
    defect_chart_url: Optional[str] = Field(default=None, description="Defect classification chart URL")
    html_path: Optional[str] = Field(default=None, description="HTML report file path")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
