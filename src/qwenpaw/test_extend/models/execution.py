# -*- coding: utf-8 -*-
"""Execution result and test run data models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    """Status of a single test case execution."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestCaseResult(BaseModel):
    """Result of executing a single test case."""

    case_id: str = Field(description="Test case identifier")
    status: ExecutionStatus = Field(description="Execution outcome")
    duration_ms: int = Field(default=0, description="Execution duration in milliseconds")
    screenshots: list[str] = Field(default_factory=list, description="Screenshot file paths")
    log: str = Field(default="", description="Execution log output")
    error_stack: Optional[str] = Field(default=None, description="Error stack trace if failed")
    retry_count: int = Field(default=0, description="Number of retry attempts")


class TestRun(BaseModel):
    """A test execution run containing multiple case results."""

    id: str = Field(description="Unique test run identifier")
    iteration_id: str = Field(description="Parent iteration ID")
    case_ids: list[str] = Field(description="Test case IDs included in this run")
    environment: str = Field(default="test", description="Target environment")
    concurrency: int = Field(default=4, description="Parallel execution count")
    status: str = Field(default="pending", description="Run status: pending/running/completed/failed")
    results: list[TestCaseResult] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
