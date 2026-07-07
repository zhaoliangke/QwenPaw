# -*- coding: utf-8 -*-
"""Traceability data model for full-chain linking."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TraceRecord(BaseModel):
    """Links requirements, stories, cases, and defects across the pipeline."""

    id: str = Field(description="Unique trace record identifier")
    iteration_id: str = Field(description="Parent iteration ID")
    story_ids: list[str] = Field(default_factory=list, description="Related story IDs")
    case_ids: list[str] = Field(default_factory=list, description="Related test case IDs")
    defect_ids: list[str] = Field(default_factory=list, description="Related defect ticket IDs")
    report_id: Optional[str] = Field(default=None, description="Related report ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
