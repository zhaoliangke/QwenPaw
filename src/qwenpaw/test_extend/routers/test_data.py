# -*- coding: utf-8 -*-
"""Test data API router — REST endpoints for test data management."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from common.trace_id import generate_trace_id
from common.test_data_gen import (
    generate_from_schema,
    generate_from_faker,
    substitute_case_data,
    load_csv_data,
    load_json_data,
)
from models.test_data import TestData, TestDataItem, DataSourceType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/test_data", tags=["test_data"])


@router.post("/")
async def create_test_data(body: dict[str, Any]) -> dict[str, Any]:
    items = []
    for item_body in body.get("items", []):
        source_type = DataSourceType(item_body.get("source_type", "inline"))
        values = item_body.get("values", [])
        if source_type == DataSourceType.INLINE and not values and "schema" in item_body:
            values = generate_from_schema(
                item_body["schema"],
                item_body.get("count", 10),
                item_body.get("locale", "zh_CN"),
            )
        items.append(TestDataItem(
            name=item_body.get("name", "item"),
            values=values,
            source_type=source_type,
            source_path=item_body.get("source_path"),
            locale=item_body.get("locale", "zh_CN"),
            count=item_body.get("count", 10),
            schema=item_body.get("schema", {}),
        ))

    data = TestData(
        id=generate_trace_id("TD"),
        name=body.get("name", ""),
        description=body.get("description", ""),
        product_line=body.get("product_line", ""),
        iteration_id=body.get("iteration_id", ""),
        items=items,
        variables=body.get("variables", {}),
    )
    return {"id": data.id, "name": data.name, "item_count": len(data.items)}


@router.get("/")
async def list_test_data(iteration_id: str = "") -> dict[str, Any]:
    return {"items": [], "total": 0, "iteration_id": iteration_id}


@router.get("/{data_id}")
async def get_test_data(data_id: str) -> dict[str, Any]:
    raise HTTPException(status_code=404, detail=f"Test data {data_id} not found")


@router.delete("/{data_id}")
async def delete_test_data(data_id: str) -> dict[str, Any]:
    return {"deleted": True, "id": data_id}


@router.post("/generate")
async def generate_data(body: dict[str, Any]) -> dict[str, Any]:
    schema = body.get("schema")
    provider = body.get("provider", "")
    count = body.get("count", 10)
    locale = body.get("locale", "zh_CN")

    if schema:
        values = generate_from_schema(schema, count, locale)
    elif provider:
        values = [{"value": v} for v in generate_from_faker(provider, count, locale)]
    else:
        raise HTTPException(status_code=400, detail="schema or provider required")

    return {"count": len(values), "values": values}


@router.post("/substitute")
async def substitute_data(body: dict[str, Any]) -> dict[str, Any]:
    steps = body.get("steps", [])
    variables = body.get("variables", {})
    result = substitute_case_data(steps, variables)
    return {"steps": result, "variable_count": len(variables)}


@router.post("/import_csv")
async def import_csv(body: dict[str, Any]) -> dict[str, Any]:
    file_path = body.get("file_path", "")
    if not file_path:
        raise HTTPException(status_code=400, detail="file_path required")
    data = load_csv_data(file_path)
    return {"count": len(data), "data": data}


@router.post("/import_json")
async def import_json(body: dict[str, Any]) -> dict[str, Any]:
    file_path = body.get("file_path", "")
    if not file_path:
        raise HTTPException(status_code=400, detail="file_path required")
    data = load_json_data(file_path)
    return {"count": len(data), "data": data}
