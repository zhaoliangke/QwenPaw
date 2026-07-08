# -*- coding: utf-8 -*-
"""Test Data Management MCP Tools.

Provides tools for creating, generating, and managing test data sets.
All tools register into the platform's native tool pipeline.
"""

import logging
from pathlib import Path

from common.test_data_gen import (
    generate_from_schema,
    generate_from_faker,
    substitute_case_data,
    load_csv_data,
    load_json_data,
)
from models.test_data import TestData, TestDataItem, DataSourceType

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.test_data_agent import TestDataAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = TestDataAgent(WORKING_DIR)
    return _agent


async def create_test_data_tool(
    name: str,
    description: str = "",
    product_line: str = "",
    iteration_id: str = "",
    schema: dict | None = None,
    count: int = 10,
) -> dict:
    return await _get_agent().create_test_data(
        name=name, description=description, product_line=product_line,
        iteration_id=iteration_id, schema=schema, count=count,
    )


async def generate_test_data_tool(
    data_id: str,
    schema: dict | None = None,
    provider: str = "",
    count: int = 10,
    locale: str = "zh_CN",
) -> dict:
    if schema:
        values = generate_from_schema(schema, count, locale)
    elif provider:
        values = [{"value": v} for v in generate_from_faker(provider, count, locale)]
    else:
        return {"error": "Either schema or provider must be specified"}
    return {"data_id": data_id, "count": len(values), "values": values}


async def list_test_data_tool(iteration_id: str = "") -> dict:
    return await _get_agent().list_test_data(iteration_id=iteration_id)


async def get_test_data_tool(data_id: str) -> dict:
    return await _get_agent().get_test_data(data_id)


async def delete_test_data_tool(data_id: str) -> dict:
    return await _get_agent().delete_test_data(data_id)


async def substitute_variables_tool(steps: list[str], variables: dict) -> dict:
    result = substitute_case_data(steps, variables)
    return {"steps": result, "variable_count": len(variables)}
