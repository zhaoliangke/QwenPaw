# -*- coding: utf-8 -*-
"""Iteration data model."""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class IterationStatus(str, Enum):
    """Iteration lifecycle status."""

    DRAFT = "draft"
    REVIEWING = "reviewing"
    TESTING = "testing"
    RELEASED = "released"
    ARCHIVED = "archived"


class Iteration(BaseModel):
    """A testing iteration that groups requirements, stories, cases, and runs."""

    id: str = Field(default_factory=lambda: "", description="Unique iteration identifier")
    name: str = Field(description="Human-readable iteration name")
    version: str = Field(description="Software version number")
    module: str = Field(description="Module or component name")
    description: Optional[str] = Field(default=None, description="Optional description")
    start_date: date = Field(description="Iteration start date")
    end_date: date = Field(description="Iteration end date")
    git_branch: Optional[str] = Field(default=None, description="Related Git branch")
    test_environment: Optional[str] = Field(default=None, description="Test environment name")
    status: IterationStatus = Field(default=IterationStatus.DRAFT)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    traceability_id: str = Field(default="", description="Full-chain traceability ID")
