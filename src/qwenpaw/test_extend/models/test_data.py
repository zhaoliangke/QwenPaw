# -*- coding: utf-8 -*-
"""Test data management models.

Supports data-driven testing with parameterized fixtures,
CSV/JSON data sources, and variable substitution.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class DataSourceType(str, Enum):
    INLINE = "inline"
    CSV = "csv"
    JSON = "json"
    FAKER = "faker"


from common.trace_id import generate_trace_id


def _td_id():
    return generate_trace_id("TD")


def _fixture_id():
    return generate_trace_id("FX")


class TestDataItem(BaseModel):
    name: str
    values: list[dict] = Field(default_factory=list)
    source_type: DataSourceType = DataSourceType.INLINE
    source_path: Optional[str] = None
    locale: str = "zh_CN"
    count: int = 10
    schema: dict = Field(default_factory=dict)


class TestData(BaseModel):
    id: str = Field(default_factory=_td_id)
    name: str
    description: str = ""
    product_line: str = ""
    iteration_id: str = ""
    items: list[TestDataItem] = Field(default_factory=list)
    variables: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Fixture(BaseModel):
    id: str = Field(default_factory=_fixture_id)
    name: str
    setup_steps: list[str] = Field(default_factory=list)
    teardown_steps: list[str] = Field(default_factory=list)
    variables: dict = Field(default_factory=dict)
