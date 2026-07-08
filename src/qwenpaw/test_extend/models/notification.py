# -*- coding: utf-8 -*-
"""Notification models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class ChannelType(str, Enum):
    DINGTALK = "dingtalk"
    FEISHU = "feishu"
    WECOM = "wecom"
    WEBHOOK = "webhook"
    EMAIL = "email"


class NotifyTrigger(str, Enum):
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"
    COVERAGE_DROP = "coverage_drop"
    DEFECT_CREATED = "defect_created"
    REGRESSION_BLOCKED = "regression_blocked"
    MANUAL = "manual"


class NotifyRule(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("NR"))
    name: str
    iteration_id: str = ""
    triggers: list[NotifyTrigger] = Field(default_factory=list)
    channels: list[ChannelType] = Field(default_factory=list)
    webhook_urls: dict[str, str] = Field(default_factory=dict)
    min_severity: str = "info"
    enabled: bool = True


class NotifyMessage(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("NM"))
    rule_id: str = ""
    trigger: NotifyTrigger = NotifyTrigger.MANUAL
    channel: ChannelType = ChannelType.WEBHOOK
    title: str
    content: str
    iteration_id: str = ""
    run_id: str = ""
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"
    error: str = ""
    raw_response: str = ""


class NotifyLog(BaseModel):
    messages: list[NotifyMessage] = Field(default_factory=list)
    total: int = 0
