# -*- coding: utf-8 -*-
"""Test data store — persistence for TestData and Fixture models."""

import logging
from pathlib import Path

from common.utils import read_json_file, write_json_file
from models.test_data import TestData
from .base_store import BaseStore
from .paths import get_test_data_dir

logger = logging.getLogger(__name__)


class TestDataStore(BaseStore[TestData]):
    def __init__(self, workspace_dir: str | Path):
        self._workspace_dir = Path(workspace_dir)

    def _path(self, item_id: str, iteration_id: str) -> Path:
        return get_test_data_dir(self._workspace_dir, iteration_id) / f"{item_id}.json"

    def _ensure(self, iteration_id: str):
        get_test_data_dir(self._workspace_dir, iteration_id).mkdir(parents=True, exist_ok=True)

    async def create(self, item: TestData) -> TestData:
        if item.iteration_id:
            self._ensure(item.iteration_id)
            write_json_file(self._path(item.id, item.iteration_id), item.model_dump())
        return item

    async def get(self, item_id: str) -> TestData | None:
        pattern = f"*/test_data/{item_id}.json"
        for f in self._workspace_dir.glob(pattern):
            data = read_json_file(f)
            return TestData(**data) if data else None
        return None

    async def list_all(self, **filters) -> list[TestData]:
        result = []
        iteration_id = filters.get("iteration_id")
        if iteration_id:
            td_dir = get_test_data_dir(self._workspace_dir, iteration_id)
            files = sorted(td_dir.glob("*.json")) if td_dir.exists() else []
        else:
            files = sorted(self._workspace_dir.glob("*/test_data/*.json"))
        for f in files:
            data = read_json_file(f)
            if data:
                result.append(TestData(**data))
        return result

    async def update(self, item: TestData) -> TestData:
        if item.iteration_id:
            self._ensure(item.iteration_id)
            write_json_file(self._path(item.id, item.iteration_id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        for f in self._workspace_dir.glob(f"*/test_data/{item_id}.json"):
            f.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return bool(list(self._workspace_dir.glob(f"*/test_data/{item_id}.json")))
