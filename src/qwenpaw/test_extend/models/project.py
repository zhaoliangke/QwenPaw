# -*- coding: utf-8 -*-
"""Project data model for managing test target applications."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Project(BaseModel):
    """A test target application with its access URL and metadata."""

    id: str = Field(default_factory=lambda: "", description="Unique project identifier")
    name: str = Field(description="Project name")
    target_url: str = Field(description="Base URL for UI automation testing")
    description: Optional[str] = Field(default=None, description="Project description")
    env: str = Field(default="test", description="Environment: test/staging/prod")
    tags: list[str] = Field(default_factory=list, description="Classification tags")
    owner: str = Field(default="", description="Project owner")
    is_active: bool = Field(default=True, description="Whether this project is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
