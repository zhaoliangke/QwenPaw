# -*- coding: utf-8 -*-
"""File-based domain stores.

Each store persists data as JSON files under workspace/test/{domain}/.
These are used when TEST_PLATFORM_DB_BACKEND is 'file' (default).
"""

import logging
from datetime import datetime
from pathlib import Path

from common.utils import read_json_file, write_json_file
from models.iteration import Iteration
from models.story import Story
from models.test_case import TestCase
from models.execution import TestRun
from models.report import TestReport
from models.traceability import TraceRecord
from models.knowledge import KnowledgeDocument
from models.workflow_state import WorkflowState, WorkflowStepRecord, WORKFLOW_STEP_IDS, WORKFLOW_STEP_NAMES, create_default_workflow_state
from models.project import Project
from models.element_map import ElementMap
from common.trace_id import generate_iteration_id, generate_story_id
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
        self._root = Path(workspace_dir) / "test" / "iteration"

    def _path(self, story_id: str, iteration_id: str | None = None) -> Path:
        if iteration_id:
            return self._root / iteration_id / "story" / f"{story_id}.json"
        return self._root / "*/story" / f"{story_id}.json"

    def _ensure(self, iteration_id: str):
        (self._root / iteration_id / "story").mkdir(parents=True, exist_ok=True)

    async def create(self, item: Story) -> Story:
        if not item.id:
            item.id = generate_story_id()
        self._ensure(item.iteration_id)
        write_json_file(self._path(item.id, item.iteration_id), item.model_dump())
        return item

    async def get(self, item_id: str) -> Story | None:
        for f in self._root.glob(f"*/story/{item_id}.json"):
            data = read_json_file(f)
            if data:
                return Story(**data)
        return None

    async def list_all(self, **filters) -> list[Story]:
        if not self._root.exists():
            return []
        result = []
        iteration_id = filters.get("iteration_id")
        if iteration_id:
            story_dir = self._root / iteration_id / "story"
            for f in sorted(story_dir.glob("*.json")) if story_dir.exists() else []:
                data = read_json_file(f)
                if data:
                    item = Story(**data)
                    if "priority" in filters and item.priority != filters["priority"]:
                        continue
                    result.append(item)
        else:
            for f in sorted(self._root.glob("*/story/*.json")):
                data = read_json_file(f)
                if data:
                    item = Story(**data)
                    if "priority" in filters and item.priority != filters["priority"]:
                        continue
                    result.append(item)
        return result

    async def update(self, item: Story) -> Story:
        self._ensure(item.iteration_id)
        write_json_file(self._path(item.id, item.iteration_id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        for f in self._root.glob(f"*/story/{item_id}.json"):
            f.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return bool(list(self._root.glob(f"*/story/{item_id}.json")))


class FileCaseStore(BaseStore[TestCase]):
    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "iteration"

    def _path(self, case_id: str, iteration_id: str | None = None) -> Path:
        if iteration_id:
            return self._root / iteration_id / "case" / f"{case_id}.json"
        return self._root / "*/case" / f"{case_id}.json"

    def _ensure(self, iteration_id: str):
        (self._root / iteration_id / "case").mkdir(parents=True, exist_ok=True)

    async def create(self, item: TestCase) -> TestCase:
        self._ensure(item.iteration_id)
        write_json_file(self._path(item.id, item.iteration_id), item.model_dump())
        return item

    async def get(self, item_id: str) -> TestCase | None:
        for f in self._root.glob(f"*/case/{item_id}.json"):
            data = read_json_file(f)
            if data:
                return TestCase(**data)
        return None

    async def list_all(self, **filters) -> list[TestCase]:
        if not self._root.exists():
            return []
        result = []
        iteration_id = filters.get("iteration_id")
        if iteration_id:
            case_dir = self._root / iteration_id / "case"
            for f in sorted(case_dir.glob("*.json")) if case_dir.exists() else []:
                data = read_json_file(f)
                if data:
                    item = TestCase(**data)
                    if "story_id" in filters and item.story_id != filters["story_id"]:
                        continue
                    if "type" in filters and item.type != filters["type"]:
                        continue
                    result.append(item)
        else:
            for f in sorted(self._root.glob("*/case/*.json")):
                data = read_json_file(f)
                if data:
                    item = TestCase(**data)
                    if "story_id" in filters and item.story_id != filters["story_id"]:
                        continue
                    if "type" in filters and item.type != filters["type"]:
                        continue
                    result.append(item)
        return result

    async def update(self, item: TestCase) -> TestCase:
        self._ensure(item.iteration_id)
        write_json_file(self._path(item.id, item.iteration_id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        for f in self._root.glob(f"*/case/{item_id}.json"):
            f.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return bool(list(self._root.glob(f"*/case/{item_id}.json")))


class FileTestRunStore(BaseStore[TestRun]):
    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "iteration"

    def _path(self, run_id: str, iteration_id: str | None = None) -> Path:
        if iteration_id:
            return self._root / iteration_id / "exec_log" / f"{run_id}.json"
        return self._root / "*/exec_log" / f"{run_id}.json"

    def _ensure(self, iteration_id: str):
        (self._root / iteration_id / "exec_log").mkdir(parents=True, exist_ok=True)

    async def create(self, item: TestRun) -> TestRun:
        self._ensure(item.iteration_id)
        write_json_file(self._path(item.id, item.iteration_id), item.model_dump())
        return item

    async def get(self, item_id: str) -> TestRun | None:
        for f in self._root.glob(f"*/exec_log/{item_id}.json"):
            data = read_json_file(f)
            if data:
                return TestRun(**data)
        return None

    async def list_all(self, **filters) -> list[TestRun]:
        if not self._root.exists():
            return []
        result = []
        iteration_id = filters.get("iteration_id")
        if iteration_id:
            log_dir = self._root / iteration_id / "exec_log"
            for f in sorted(log_dir.glob("*.json")) if log_dir.exists() else []:
                data = read_json_file(f)
                if data:
                    item = TestRun(**data)
                    if "status" in filters and item.status != filters["status"]:
                        continue
                    result.append(item)
        else:
            for f in sorted(self._root.glob("*/exec_log/*.json")):
                data = read_json_file(f)
                if data:
                    item = TestRun(**data)
                    if "status" in filters and item.status != filters["status"]:
                        continue
                    result.append(item)
        return result

    async def update(self, item: TestRun) -> TestRun:
        self._ensure(item.iteration_id)
        write_json_file(self._path(item.id, item.iteration_id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        for f in self._root.glob(f"*/exec_log/{item_id}.json"):
            f.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return bool(list(self._root.glob(f"*/exec_log/{item_id}.json")))


class FileReportStore(BaseStore[TestReport]):
    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "iteration"

    def _path(self, report_id: str, iteration_id: str | None = None) -> Path:
        if iteration_id:
            return self._root / iteration_id / "report" / f"{report_id}.json"
        return self._root / "*/report" / f"{report_id}.json"

    def _ensure(self, iteration_id: str):
        (self._root / iteration_id / "report").mkdir(parents=True, exist_ok=True)

    async def create(self, item: TestReport) -> TestReport:
        self._ensure(item.iteration_id)
        write_json_file(self._path(item.id, item.iteration_id), item.model_dump())
        return item

    async def get(self, item_id: str) -> TestReport | None:
        for f in self._root.glob(f"*/report/{item_id}.json"):
            data = read_json_file(f)
            if data:
                return TestReport(**data)
        return None

    async def list_all(self, **filters) -> list[TestReport]:
        if not self._root.exists():
            return []
        result = []
        iteration_id = filters.get("iteration_id")
        if iteration_id:
            report_dir = self._root / iteration_id / "report"
            for f in sorted(report_dir.glob("*.json")) if report_dir.exists() else []:
                data = read_json_file(f)
                if data:
                    item = TestReport(**data)
                    if "test_run_id" in filters and item.test_run_id != filters["test_run_id"]:
                        continue
                    result.append(item)
        else:
            for f in sorted(self._root.glob("*/report/*.json")):
                data = read_json_file(f)
                if data:
                    item = TestReport(**data)
                    if "test_run_id" in filters and item.test_run_id != filters["test_run_id"]:
                        continue
                    result.append(item)
        return result

    async def update(self, item: TestReport) -> TestReport:
        self._ensure(item.iteration_id)
        write_json_file(self._path(item.id, item.iteration_id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        for f in self._root.glob(f"*/report/{item_id}.json"):
            f.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return bool(list(self._root.glob(f"*/report/{item_id}.json")))


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
                if "iteration_id" in filters and item.iteration_id != filters["iteration_id"]:
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


class FileWorkflowStore(BaseStore[WorkflowState]):
    """File-based workflow state persistence for the chat workflow panel.

    Stores a single workflow.json per iteration under workspace/test/iteration/{id}/.
    Provides atomic step-level updates with automatic progress calculation.
    """

    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "iteration"

    def _path(self, iteration_id: str) -> Path:
        return self._root / iteration_id / "workflow.json"

    def _ensure(self, iteration_id: str):
        (self._root / iteration_id).mkdir(parents=True, exist_ok=True)

    async def create(self, item: WorkflowState) -> WorkflowState:
        self._ensure(item.iteration_id)
        write_json_file(self._path(item.iteration_id), item.model_dump())
        return item

    async def get(self, item_id: str) -> WorkflowState | None:
        data = read_json_file(self._path(item_id))
        if data:
            return WorkflowState(**data)
        return None

    async def list_all(self, **filters) -> list[WorkflowState]:
        if not self._root.exists():
            return []
        result = []
        for d in sorted(self._root.iterdir()):
            if d.is_dir():
                f = d / "workflow.json"
                if f.exists():
                    data = read_json_file(f)
                    if data:
                        item = WorkflowState(**data)
                        if "chat_session_id" in filters and item.chat_session_id != filters["chat_session_id"]:
                            continue
                        if "iteration_id" in filters and item.iteration_id != filters["iteration_id"]:
                            continue
                        result.append(item)
        return result

    async def update(self, item: WorkflowState) -> WorkflowState:
        self._ensure(item.iteration_id)
        item.updated_at = datetime.utcnow()
        write_json_file(self._path(item.iteration_id), item.model_dump())
        return item

    async def delete(self, item_id: str) -> bool:
        p = self._path(item_id)
        if p.exists():
            p.unlink()
            return True
        return False

    async def exists(self, item_id: str) -> bool:
        return self._path(item_id).exists()

    # --- Workflow-specific operations ---

    async def update_step(
        self,
        iteration_id: str,
        step_id: str,
        status: str,
        result_summary: dict | None = None,
        error: str | None = None,
        chat_session_id: str | None = None,
    ) -> WorkflowState:
        """Update a single step's status and result, recalculating overall progress."""
        state = await self.get(iteration_id)
        if state is None:
            state = create_default_workflow_state(iteration_id)

        if chat_session_id and state.chat_session_id is None:
            state.chat_session_id = chat_session_id

        step_found = False
        for step in state.steps:
            if step.step_id == step_id:
                step.status = status
                if result_summary is not None:
                    step.result_summary = result_summary
                if error is not None:
                    step.error = error
                if status == "running" and step.started_at is None:
                    step.started_at = datetime.utcnow()
                if status in ("completed", "error", "skipped"):
                    step.completed_at = datetime.utcnow()
                step_found = True
                break

        if not step_found:
            new_step = WorkflowStepRecord(
                step_id=step_id,
                name=WORKFLOW_STEP_NAMES.get(step_id, step_id),
                status=status,
                result_summary=result_summary or {},
                error=error,
                started_at=datetime.utcnow() if status == "running" else None,
                completed_at=datetime.utcnow() if status in ("completed", "error", "skipped") else None,
            )
            state.steps.append(new_step)

        completed_count = sum(1 for s in state.steps if s.status == "completed")
        total_count = len(state.steps) if state.steps else len(WORKFLOW_STEP_IDS)
        state.overall_progress = round((completed_count / total_count) * 100) if total_count > 0 else 0
        state.updated_at = datetime.utcnow()

        await self.update(state)
        return state

    async def reset_workflow(
        self, iteration_id: str, chat_session_id: str | None = None
    ) -> WorkflowState:
        """Reset all steps to pending."""
        state = create_default_workflow_state(iteration_id)
        if chat_session_id:
            state.chat_session_id = chat_session_id
        await self.create(state)
        return state

    async def get_step(self, iteration_id: str, step_id: str) -> WorkflowStepRecord | None:
        """Get a specific step record."""
        state = await self.get(iteration_id)
        if state is None:
            return None
        for step in state.steps:
            if step.step_id == step_id:
                return step
        return None


class FileProjectStore:
    """Stores project data as JSON files under workspace/test/project/."""

    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "project"

    def _path(self, project_id: str) -> Path:
        return self._root / f"{project_id}.json"

    async def create(self, item: Project) -> Project:
        self._root.mkdir(parents=True, exist_ok=True)
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def get(self, item_id: str) -> Project | None:
        path = self._path(item_id)
        if not path.exists():
            return None
        data = read_json_file(path)
        if data:
            return Project(**data)
        return None

    async def update(self, item: Project) -> Project:
        item.updated_at = datetime.utcnow()
        return await self.create(item)

    async def delete(self, item_id: str) -> bool:
        path = self._path(item_id)
        if path.exists():
            path.unlink()
            return True
        return False

    async def list_all(self, **filters) -> list[Project]:
        if not self._root.exists():
            return []
        result = []
        for f in sorted(self._root.glob("*.json")):
            data = read_json_file(f)
            if data:
                item = Project(**data)
                if "is_active" in filters and item.is_active != filters["is_active"]:
                    continue
                if "env" in filters and item.env != filters["env"]:
                    continue
                if "tags" in filters and not any(t in item.tags for t in filters["tags"]):
                    continue
                result.append(item)
        return result


class FileElementMapStore:
    """Stores element maps as JSON files under workspace/test/element_map/."""

    def __init__(self, workspace_dir: str):
        self._root = Path(workspace_dir) / "test" / "element_map"

    def _path(self, map_id: str) -> Path:
        return self._root / f"{map_id}.json"

    async def create(self, item: ElementMap) -> ElementMap:
        self._root.mkdir(parents=True, exist_ok=True)
        write_json_file(self._path(item.id), item.model_dump())
        return item

    async def get(self, item_id: str) -> ElementMap | None:
        path = self._path(item_id)
        if not path.exists():
            return None
        data = read_json_file(path)
        if data:
            return ElementMap(**data)
        return None

    async def update(self, item: ElementMap) -> ElementMap:
        item.updated_at = datetime.utcnow()
        return await self.create(item)

    async def delete(self, item_id: str) -> bool:
        path = self._path(item_id)
        if path.exists():
            path.unlink()
            return True
        return False

    async def list_all(self, **filters) -> list[ElementMap]:
        if not self._root.exists():
            return []
        result = []
        for f in sorted(self._root.glob("*.json")):
            data = read_json_file(f)
            if data:
                item = ElementMap(**data)
                if "project_id" in filters and item.project_id != filters["project_id"]:
                    continue
                if "page_name" in filters and item.page_name != filters["page_name"]:
                    continue
                result.append(item)
        return result
