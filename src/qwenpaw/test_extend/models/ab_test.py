# -*- coding: utf-8 -*-
"""A/B test models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class ABStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    INCONCLUSIVE = "inconclusive"


class Variant(BaseModel):
    name: str
    weight: float = 1.0
    url: str = ""
    description: str = ""


class MetricResult(BaseModel):
    metric_name: str
    control_value: float
    treatment_value: float
    lift_percentage: float
    p_value: float
    significant: bool


class ABTest(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("AB"))
    name: str
    description: str = ""
    hypothesis: str = ""
    control: Variant = Field(default_factory=lambda: Variant(name="control"))
    treatment: Variant = Field(default_factory=lambda: Variant(name="treatment"))
    metrics: list[str] = Field(default_factory=list)
    significance_level: float = 0.05
    target_sample_size: int = 1000
    status: ABStatus = ABStatus.RUNNING
    iteration_id: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ABTestResult(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("AR"))
    test_id: str = ""
    status: ABStatus = ABStatus.RUNNING
    sample_size_control: int = 0
    sample_size_treatment: int = 0
    metric_results: list[MetricResult] = Field(default_factory=list)
    winner: str = ""
    conclusion: str = ""
    executed_at: datetime = Field(default_factory=datetime.utcnow)
