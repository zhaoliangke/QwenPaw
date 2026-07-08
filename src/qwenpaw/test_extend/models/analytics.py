# -*- coding: utf-8 -*-
"""Test asset analytics dashboard models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class TrendGranularity(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TrendPoint(BaseModel):
    date: str
    value: float


class TestExecutionTrend(BaseModel):
    granularity: TrendGranularity = TrendGranularity.DAILY
    total_runs: list[TrendPoint] = Field(default_factory=list)
    pass_rates: list[TrendPoint] = Field(default_factory=list)
    avg_duration_ms: list[TrendPoint] = Field(default_factory=list)
    defect_counts: list[TrendPoint] = Field(default_factory=list)


class ModuleCoverage(BaseModel):
    module: str
    case_count: int = 0
    coverage_rate: float = 0.0
    last_run: str = ""


class AssetMetrics(BaseModel):
    total_cases: int = 0
    total_runs: int = 0
    total_defects: int = 0
    avg_pass_rate: float = 0.0
    avg_duration_ms: float = 0.0
    total_execution_hours: float = 0.0
    automation_rate: float = 0.0
    flaky_rate: float = 0.0


class TopDefectModule(BaseModel):
    module: str
    defect_count: int = 0
    severity: str = ""


class DashboardSummary(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("DB"))
    iteration_id: str = ""
    asset_metrics: AssetMetrics = Field(default_factory=AssetMetrics)
    execution_trend: TestExecutionTrend = Field(default_factory=TestExecutionTrend)
    module_coverages: list[ModuleCoverage] = Field(default_factory=list)
    top_defect_modules: list[TopDefectModule] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
