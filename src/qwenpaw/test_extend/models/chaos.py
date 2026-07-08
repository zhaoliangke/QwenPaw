# -*- coding: utf-8 -*-
"""Chaos engineering models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class ChaosType(str, Enum):
    NETWORK_DELAY = "network_delay"
    NETWORK_LOSS = "network_loss"
    ERROR_INJECTION = "error_injection"
    RESOURCE_STRESS = "resource_stress"
    DNS_FAILURE = "dns_failure"
    CLOCK_SKEW = "clock_skew"


class ChaosStatus(str, Enum):
    PENDING = "pending"
    INJECTING = "injecting"
    ROLLING_BACK = "rolling_back"
    COMPLETED = "completed"
    FAILED = "failed"


class ChaosTarget(BaseModel):
    host: str = ""
    port: int = 0
    protocol: str = "tcp"
    endpoint: str = ""


class ChaosExperiment(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("CE"))
    name: str
    description: str = ""
    chaos_type: ChaosType = ChaosType.NETWORK_DELAY
    target: ChaosTarget = Field(default_factory=ChaosTarget)
    duration_seconds: int = 30
    intensity: float = 1.0
    parameters: dict[str, Any] = Field(default_factory=dict)
    status: ChaosStatus = ChaosStatus.PENDING
    rollback_enabled: bool = True
    iteration_id: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChaosResult(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("CR"))
    experiment_id: str = ""
    status: ChaosStatus = ChaosStatus.PENDING
    error_rate_before: float = 0.0
    error_rate_during: float = 0.0
    response_time_before_ms: float = 0.0
    response_time_during_ms: float = 0.0
    recovery_time_ms: float = 0.0
    impact_score: float = 0.0
    findings: list[str] = Field(default_factory=list)
    error: str = ""
    executed_at: datetime = Field(default_factory=datetime.utcnow)
