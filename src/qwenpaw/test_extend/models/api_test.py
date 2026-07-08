# -*- coding: utf-8 -*-
"""API test models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class AssertionType(str, Enum):
    STATUS_CODE = "status_code"
    BODY_CONTAINS = "body_contains"
    BODY_EQUALS = "body_equals"
    JSON_PATH = "json_path"
    RESPONSE_TIME = "response_time"
    HEADER = "header"


class ApiTestCase(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("AT"))
    name: str
    method: HttpMethod = HttpMethod.GET
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    query_params: dict[str, str] = Field(default_factory=dict)
    body: Any = None
    assertions: list[dict[str, Any]] = Field(default_factory=list)
    timeout: int = 30
    iteration_id: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApiTestResult(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("AR"))
    case_id: str = ""
    run_id: str = ""
    status: str = "pending"
    status_code: int = 0
    response_body: str = ""
    response_headers: dict = Field(default_factory=dict)
    response_time_ms: float = 0.0
    assertion_results: list[dict[str, Any]] = Field(default_factory=list)
    passed_assertions: int = 0
    total_assertions: int = 0
    error: str = ""
    executed_at: datetime = Field(default_factory=datetime.utcnow)


class ApiTestSuite(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("AS"))
    name: str
    description: str = ""
    iteration_id: str = ""
    base_url: str = ""
    case_ids: list[str] = Field(default_factory=list)
    env_vars: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
