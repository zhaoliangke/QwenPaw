# -*- coding: utf-8 -*-
"""Test case data model."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CaseType(str, Enum):
    """Classification of test case by coverage dimension."""

    FUNCTIONAL = "functional"
    BOUNDARY = "boundary"
    EXCEPTION = "exception"
    SECURITY = "security"
    UI = "ui"


class TestCase(BaseModel):
    """A test case generated from a user story."""

    id: str = Field(description="Unique test case identifier")
    story_id: str = Field(description="Parent story ID")
    iteration_id: str = Field(description="Parent iteration ID")
    title: str = Field(description="Test case title")
    type: CaseType = Field(description="Coverage dimension type")
    priority: str = Field(default="medium", description="Priority: high/medium/low")
    module: str = Field(default="", description="Module or component name")
    preconditions: list[str] = Field(default_factory=list, description="Preconditions before execution")
    steps: list[str] = Field(default_factory=list, description="Ordered execution steps")
    expected_results: list[str] = Field(default_factory=list, description="Expected outcomes for each step")
    tags: list[str] = Field(default_factory=list, description="Classification tags")
    is_active: bool = Field(default=True, description="Whether this case is enabled")
    traceability_id: str = Field(default="", description="Full-chain traceability ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
