# -*- coding: utf-8 -*-
"""Performance test models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class PerfTestType(str, Enum):
    LOAD = "load"
    STRESS = "stress"
    SPIKE = "spike"
    SOAK = "soak"


class PerfThreshold(BaseModel):
    metric: str
    operator: str
    value: float
    passed: bool = True


class PerfMetric(BaseModel):
    name: str
    value: float
    unit: str
    threshold: float | None = None
    passed: bool = True


class PerfTestCase(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("PT"))
    name: str
    description: str = ""
    test_type: PerfTestType = PerfTestType.LOAD
    script_path: str = ""
    target_url: str = ""
    vusers: int = 10
    duration: str = "30s"
    iteration_id: str = ""
    thresholds: list[PerfThreshold] = Field(default_factory=list)
    env_vars: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PerfTestResult(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("PR"))
    test_id: str = ""
    run_id: str = ""
    status: str = "pending"
    metrics: list[PerfMetric] = Field(default_factory=list)
    http_reqs: int = 0
    http_req_failed: float = 0.0
    http_req_duration_p95: float = 0.0
    http_req_duration_avg: float = 0.0
    iterations_completed: int = 0
    data_received_mb: float = 0.0
    raw_summary: dict[str, Any] = Field(default_factory=dict)
    error: str = ""
    executed_at: datetime = Field(default_factory=datetime.utcnow)
