# -*- coding: utf-8 -*-
"""Execution queue models — priority-based job scheduling."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class JobPriority(int, Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class ExecutionJob(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("EJ"))
    case_id: str = ""
    run_id: str = ""
    iteration_id: str = ""
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    retry_count: int = 0
    max_retries: int = 2
    shard_id: str = ""
    shard_index: int = 0
    shard_total: int = 1
    result: dict[str, Any] = Field(default_factory=dict)
    error: str = ""
    queued_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class QueueStats(BaseModel):
    total_jobs: int = 0
    pending: int = 0
    running: int = 0
    passed: int = 0
    failed: int = 0
    cancelled: int = 0
    avg_wait_ms: float = 0.0
    avg_runtime_ms: float = 0.0
    throughput_per_min: float = 0.0
