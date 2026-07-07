# -*- coding: utf-8 -*-
"""Story data model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AcceptanceCriteria(BaseModel):
    """A single acceptance criterion for a user story in Gherkin format."""

    scenario: str = Field(description="Human-readable scenario description")
    gherkin: str = Field(description="Full Gherkin Given-When-Then specification")


class Story(BaseModel):
    """A user story decomposed from a PRD requirement."""

    id: str = Field(description="Unique story identifier")
    iteration_id: str = Field(description="Parent iteration ID")
    parent_story_id: Optional[str] = Field(default=None, description="Parent story for hierarchical structure")
    title: str = Field(description="Story title")
    as_a: str = Field(description="As a [role]")
    i_want: str = Field(description="I want [feature]")
    so_that: str = Field(description="So that [benefit]")
    acceptance_criteria: list[AcceptanceCriteria] = Field(default_factory=list)
    priority: str = Field(default="medium", description="Story priority: high/medium/low")
    traceability_id: str = Field(default="", description="Full-chain traceability ID")
    is_validated: bool = Field(default=False, description="Whether AI has validated completeness")
    validation_issues: list[str] = Field(default_factory=list, description="Issues found during validation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
