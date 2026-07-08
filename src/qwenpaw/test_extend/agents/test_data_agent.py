# -*- coding: utf-8 -*-
"""Test data management agent.

Orchestrates test data creation, generation, import, and variable substitution.
"""

import logging
from pathlib import Path
from typing import Any

from common.test_data_gen import generate_from_schema
from common.trace_id import generate_trace_id
from models.test_data import TestData, TestDataItem, DataSourceType
from storage.test_data_store import TestDataStore

logger = logging.getLogger(__name__)


class TestDataAgent:
    """Manages test data lifecycle."""

    def __init__(self, workspace_dir: str | Path):
        self._store = TestDataStore(workspace_dir)

    async def create_test_data(
        self,
        name: str,
        description: str = "",
        product_line: str = "",
        iteration_id: str = "",
        schema: dict | None = None,
        count: int = 10,
    ) -> dict[str, Any]:
        items = []
        if schema:
            values = generate_from_schema(schema, count)
            items.append(TestDataItem(
                name=f"{name}_item",
                values=values,
                source_type=DataSourceType.INLINE,
                schema=schema,
            ))

        data = TestData(
            id=generate_trace_id("TD"),
            name=name,
            description=description,
            product_line=product_line,
            iteration_id=iteration_id,
            items=items,
        )
        data = await self._store.create(data)
        return {"id": data.id, "name": data.name, "item_count": len(data.items)}

    async def list_test_data(self, iteration_id: str = "") -> dict[str, Any]:
        items = await self._store.list_all(iteration_id=iteration_id)
        return {"items": [i.model_dump() for i in items], "total": len(items)}

    async def get_test_data(self, data_id: str) -> dict[str, Any]:
        item = await self._store.get(data_id)
        if item:
            return item.model_dump()
        return {"error": "Test data not found", "id": data_id}

    async def delete_test_data(self, data_id: str) -> dict[str, Any]:
        ok = await self._store.delete(data_id)
        return {"deleted": ok, "id": data_id}
