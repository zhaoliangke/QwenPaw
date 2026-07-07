# -*- coding: utf-8 -*-
"""File-based domain stores.

Each store persists data as JSON files under workspace/test/{domain}/.
These are used when TEST_PLATFORM_DB_BACKEND is 'file' (default).
"""

import logging
from pathlib import Path

from ..common.utils import read_json_file, write_json_file
from ..models.iteration import Iteration
from ..models.story import Story
from ..models.test_case import TestCase
from ..models.execution import TestRun
from ..models.report import TestReport
from ..models.traceability import TraceRecord
from ..models.knowledge import KnowledgeDocument
from ..common.trace_id import generate_iteration_id, generate_story_id
from .base_store import BaseStore

logger = logging.getLogger(__name__)


class FileIterationStore(BaseStore[Iteration]):
    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "iteration"

    def _path(self, iteration_id: str) -> Path:
        return self._root / iteration_id / "iteration.json"

    def _ensure(self, iteration_id: str):
        (self._root / iteration_id).mkdir(parents=True, exist_ok=True)

    async def create(self, item: Iteration) -> Iteration:
        if not item.id:
            item.id = generate_iteration_id()
        self._ensure(item.id)
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def get(self, item_id: str) -> Iteration | None:
        data = read_json_file(self._path(item_id))
        return Iteration(**data) if data else None

    async def list_all(self, **filters) -> list[Iteration]:
        if not self._root.exists():
            return []
        result = []
        for d in sorted(self._root.iterdir()):
            if d.is_dir():
                f = d / "iteration.json"
                if f.exists():
                    data = read_json_file(f)
                    if data:
                        item = Iteration(**data)
                        if "status" in filters and item.status != filters["status"]:
                            continue
                        if "module" in filters and item.module != filters["module"]:
                            continue
                        result.append(item)
        return result

    async def update(self, item: Iteration) -> Iteration:
        self._ensure(item.id)
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        p = self._path(item_id)
        if p.exists():
            p.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return self._path(item_id).exists()


class FileStoryStore(BaseStore[Story]):
    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "story"

    def _path(self, story_id: str) -> Path:
        return self._root / f"{story_id}.json"

    def _ensure(self):
        self._root.mkdir(parents=True, exist_ok=True)

    async def create(self, item: Story) -> Story:
        if not item.id:
            item.id = generate_story_id()
        self._ensure()
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def get(self, item_id: str) -> Story | None:
        data = read_json_file(self._path(item_id))
        return Story(**data) if data else None

    async def list_all(self, **filters) -> list[Story]:
        self._ensure()
        result = []
        for f in sorted(self._root.glob("*.json")):
            data = read_json_file(f)
            if data:
                item = Story(**data)
                if "iteration_id" in filters and item.iteration_id != filters["iteration_id"]:
                    continue
                if "priority" in filters and item.priority != filters["priority"]:
                    continue
                result.append(item)
        return result

    async def update(self, item: Story) -> Story:
        self._ensure()
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        p = self._path(item_id)
        if p.exists():
            p.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return self._path(item_id).exists()


class FileCaseStore(BaseStore[TestCase]):
    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "case"

    def _path(self, case_id: str) -> Path:
        return self._root / f"{case_id}.json"

    def _ensure(self):
        self._root.mkdir(parents=True, exist_ok=True)

    async def create(self, item: TestCase) -> TestCase:
        self._ensure()
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def get(self, item_id: str) -> TestCase | None:
        data = read_json_file(self._path(item_id))
        return TestCase(**data) if data else None

    async def list_all(self, **filters) -> list[TestCase]:
        self._ensure()
        result = []
        for f in sorted(self._root.glob("*.json")):
            data = read_json_file(f)
            if data:
                item = TestCase(**data)
                if "iteration_id" in filters and item.iteration_id != filters["iteration_id"]:
                    continue
                if "story_id" in filters and item.story_id != filters["story_id"]:
                    continue
                if "type" in filters and item.type != filters["type"]:
                    continue
                result.append(item)
        return result

    async def update(self, item: TestCase) -> TestCase:
        self._ensure()
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        p = self._path(item_id)
        if p.exists():
            p.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return self._path(item_id).exists()


class FileTestRunStore(BaseStore[TestRun]):
    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "exec"

    def _path(self, run_id: str) -> Path:
        return self._root / f"{run_id}.json"

    def _ensure(self):
        self._root.mkdir(parents=True, exist_ok=True)

    async def create(self, item: TestRun) -> TestRun:
        self._ensure()
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def get(self, item_id: str) -> TestRun | None:
        data = read_json_file(self._path(item_id))
        return TestRun(**data) if data else None

    async def list_all(self, **filters) -> list[TestRun]:
        self._ensure()
        result = []
        for f in sorted(self._root.glob("*.json")):
            data = read_json_file(f)
            if data:
                item = TestRun(**data)
                if "iteration_id" in filters and item.iteration_id != filters["iteration_id"]:
                    continue
                if "status" in filters and item.status != filters["status"]:
                    continue
                result.append(item)
        return result

    async def update(self, item: TestRun) -> TestRun:
        self._ensure()
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        p = self._path(item_id)
        if p.exists():
            p.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return self._path(item_id).exists()


class FileReportStore(BaseStore[TestReport]):
    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "report"

    def _path(self, report_id: str) -> Path:
        return self._root / f"{report_id}.json"

    def _ensure(self):
        self._root.mkdir(parents=True, exist_ok=True)

    async def create(self, item: TestReport) -> TestReport:
        self._ensure()
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def get(self, item_id: str) -> TestReport | None:
        data = read_json_file(self._path(item_id))
        return TestReport(**data) if data else None

    async def list_all(self, **filters) -> list[TestReport]:
        self._ensure()
        result = []
        for f in sorted(self._root.glob("*.json")):
            data = read_json_file(f)
            if data:
                item = TestReport(**data)
                if "iteration_id" in filters and item.iteration_id != filters["iteration_id"]:
                    continue
                if "test_run_id" in filters and item.test_run_id != filters["test_run_id"]:
                    continue
                result.append(item)
        return result

    async def update(self, item: TestReport) -> TestReport:
        self._ensure()
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        p = self._path(item_id)
        if p.exists():
            p.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return self._path(item_id).exists()


class FileTraceStore(BaseStore[TraceRecord]):
    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "trace"

    def _path(self, record_id: str) -> Path:
        return self._root / f"{record_id}.json"

    def _ensure(self):
        self._root.mkdir(parents=True, exist_ok=True)

    async def create(self, item: TraceRecord) -> TraceRecord:
        self._ensure()
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def get(self, item_id: str) -> TraceRecord | None:
        data = read_json_file(self._path(item_id))
        return TraceRecord(**data) if data else None

    async def list_all(self, **filters) -> list[TraceRecord]:
        self._ensure()
        result = []
        for f in sorted(self._root.glob("*.json")):
            data = read_json_file(f)
            if data:
                item = TraceRecord(**data)
                if "iteration_id" in filters and item.iteration_id != filters["iteration_id"]:
                    continue
                result.append(item)
        return result

    async def update(self, item: TraceRecord) -> TraceRecord:
        self._ensure()
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        p = self._path(item_id)
        if p.exists():
            p.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return self._path(item_id).exists()


class FileKnowledgeStore(BaseStore[KnowledgeDocument]):
    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "knowledge" / "docs"

    def _path(self, doc_id: str) -> Path:
        return self._root / f"{doc_id}.json"

    def _ensure(self):
        self._root.mkdir(parents=True, exist_ok=True)

    async def create(self, item: KnowledgeDocument) -> KnowledgeDocument:
        self._ensure()
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def get(self, item_id: str) -> KnowledgeDocument | None:
        data = read_json_file(self._path(item_id))
        return KnowledgeDocument(**data) if data else None

    async def list_all(self, **filters) -> list[KnowledgeDocument]:
        self._ensure()
        result = []
        for f in sorted(self._root.glob("*.json")):
            data = read_json_file(f)
            if data:
                item = KnowledgeDocument(**data)
                if "product_line" in filters and item.product_line != filters["product_line"]:
                    continue
                if "doc_type" in filters and item.doc_type != filters["doc_type"]:
                    continue
                result.append(item)
        return result

    async def update(self, item: KnowledgeDocument) -> KnowledgeDocument:
        self._ensure()
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        p = self._path(item_id)
        if p.exists():
            p.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return self._path(item_id).exists()
