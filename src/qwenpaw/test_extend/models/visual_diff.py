# -*- coding: utf-8 -*-
"""Visual regression test models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class DiffStatus(str, Enum):
    MATCH = "match"
    DIFFERENT = "different"
    BASELINE_MISSING = "baseline_missing"
    ERROR = "error"


class DiffRegion(BaseModel):
    x: int
    y: int
    width: int
    height: int
    diff_percentage: float


class VisualDiffTest(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("VD"))
    name: str
    description: str = ""
    url: str = ""
    selector: str = ""
    viewport_width: int = 1280
    viewport_height: int = 720
    threshold: float = 0.1
    wait_time_ms: int = 1000
    iteration_id: str = ""
    baseline_path: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VisualDiffResult(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("VR"))
    test_id: str = ""
    run_id: str = ""
    status: DiffStatus = DiffStatus.MATCH
    diff_percentage: float = 0.0
    diff_pixel_count: int = 0
    baseline_path: str = ""
    current_path: str = ""
    diff_path: str = ""
    diff_regions: list[DiffRegion] = Field(default_factory=list)
    error: str = ""
    executed_at: datetime = Field(default_factory=datetime.utcnow)
