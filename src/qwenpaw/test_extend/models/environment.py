# -*- coding: utf-8 -*-
"""Environment management models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class EnvStatus(str, Enum):
    READY = "ready"
    BUSY = "busy"
    DOWN = "down"
    UNKNOWN = "unknown"


class Environment(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("ENV"))
    name: str
    base_url: str
    description: str = ""
    iteration_id: str = ""
    status: EnvStatus = EnvStatus.UNKNOWN
    health_check_url: str = ""
    env_vars: dict[str, str] = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)
    last_check: datetime | None = None
    response_time_ms: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EnvHealthResult(BaseModel):
    env_id: str
    status: EnvStatus
    response_time_ms: float = 0.0
    status_code: int = 0
    error: str = ""
    checked_at: datetime = Field(default_factory=datetime.utcnow)
