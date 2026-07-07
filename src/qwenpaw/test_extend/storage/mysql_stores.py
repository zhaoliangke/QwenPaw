# -*- coding: utf-8 -*-
"""MySQL-based domain stores using SQLAlchemy async models.

These stores are used when TEST_PLATFORM_DB_BACKEND is 'mysql'.
They mirror the FileStore interface so callers don't need to change.
"""

import logging
from datetime import datetime
from typing import Optional

from ..infra.db_session import get_db_session
from ..infra.db_models import (
    IterationModel, StoryModel, TestCaseModel, TestRunModel,
    ReportModel, TraceRecordModel, KnowledgeDocumentModel,
)
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


def _to_dict(model_instance, exclude: set | None = None) -> dict:
    """Convert SQLAlchemy model to dict, excluding specified keys."""
    if model_instance is None:
        return {}
    exclude = exclude or set()
    return {
        c.name: getattr(model_instance, c.name)
        for c in model_instance.__table__.columns
        if c.name not in exclude
    }


class MySQLIterationStore(BaseStore[Iteration]):
    async def create(self, item: Iteration) -> Iteration:
        if not item.id:
            item.id = generate_iteration_id()
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            model = IterationModel(
                id=item.id,
                name=item.name,
                version=item.version,
                module=item.module,
                description=item.description,
                start_date=item.start_date,
                end_date=item.end_date,
                git_branch=item.git_branch,
                test_environment=item.test_environment,
                status=item.status.value if hasattr(item.status, 'value') else str(item.status),
                traceability_id=item.traceability_id,
            )
            session.add(model)
            await session.commit()
            return item

    async def get(self, item_id: str) -> Optional[Iteration]:
        async for session in get_db_session():
            if session is None:
                return None
            from sqlalchemy import select
            result = await session.execute(
                select(IterationModel).where(IterationModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            if model:
                return Iteration(**_to_dict(model))
            return None

    async def list_all(self, **filters) -> list[Iteration]:
        async for session in get_db_session():
            if session is None:
                return []
            from sqlalchemy import select
            stmt = select(IterationModel)
            if "status" in filters:
                stmt = stmt.where(IterationModel.status == filters["status"])
            if "module" in filters:
                stmt = stmt.where(IterationModel.module == filters["module"])
            stmt = stmt.order_by(IterationModel.created_at.desc())
            result = await session.execute(stmt)
            return [Iteration(**_to_dict(m)) for m in result.scalars().all()]

    async def update(self, item: Iteration) -> Iteration:
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            from sqlalchemy import select
            result = await session.execute(
                select(IterationModel).where(IterationModel.id == item.id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"Iteration {item.id} not found")
            model.name = item.name
            model.version = item.version
            model.module = item.module
            model.description = item.description
            model.start_date = item.start_date
            model.end_date = item.end_date
            model.git_branch = item.git_branch
            model.test_environment = item.test_environment
            model.status = item.status.value if hasattr(item.status, 'value') else str(item.status)
            model.traceability_id = item.traceability_id
            model.updated_at = datetime.utcnow()
            await session.commit()
            return item

    async def delete(self, item_id: str) -> bool:
        async for session in get_db_session():
            if session is None:
                return False
            from sqlalchemy import select
            result = await session.execute(
                select(IterationModel).where(IterationModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

    async def exists(self, item_id: str) -> bool:
        item = await self.get(item_id)
        return item is not None


class MySQLStoryStore(BaseStore[Story]):
    async def create(self, item: Story) -> Story:
        if not item.id:
            item.id = generate_story_id()
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            model = StoryModel(
                id=item.id,
                iteration_id=item.iteration_id,
                parent_story_id=item.parent_story_id,
                title=item.title,
                as_a=item.as_a,
                i_want=item.i_want,
                so_that=item.so_that,
                acceptance_criteria=item.acceptance_criteria,
                priority=item.priority,
                traceability_id=item.traceability_id,
                is_validated=item.is_validated,
                validation_issues=item.validation_issues,
            )
            session.add(model)
            await session.commit()
            return item

    async def get(self, item_id: str) -> Optional[Story]:
        async for session in get_db_session():
            if session is None:
                return None
            from sqlalchemy import select
            result = await session.execute(
                select(StoryModel).where(StoryModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            return Story(**_to_dict(model)) if model else None

    async def list_all(self, **filters) -> list[Story]:
        async for session in get_db_session():
            if session is None:
                return []
            from sqlalchemy import select
            stmt = select(StoryModel)
            if "iteration_id" in filters:
                stmt = stmt.where(StoryModel.iteration_id == filters["iteration_id"])
            if "priority" in filters:
                stmt = stmt.where(StoryModel.priority == filters["priority"])
            stmt = stmt.order_by(StoryModel.created_at.desc())
            result = await session.execute(stmt)
            return [Story(**_to_dict(m)) for m in result.scalars().all()]

    async def update(self, item: Story) -> Story:
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            from sqlalchemy import select
            result = await session.execute(
                select(StoryModel).where(StoryModel.id == item.id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"Story {item.id} not found")
            for field in ("title", "as_a", "i_want", "so_that", "acceptance_criteria",
                          "priority", "traceability_id", "is_validated", "validation_issues"):
                setattr(model, field, getattr(item, field))
            await session.commit()
            return item

    async def delete(self, item_id: str) -> bool:
        async for session in get_db_session():
            if session is None:
                return False
            from sqlalchemy import select
            result = await session.execute(
                select(StoryModel).where(StoryModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

    async def exists(self, item_id: str) -> bool:
        return await self.get(item_id) is not None


class MySQLCaseStore(BaseStore[TestCase]):
    async def create(self, item: TestCase) -> TestCase:
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            model = TestCaseModel(
                id=item.id,
                story_id=item.story_id,
                iteration_id=item.iteration_id,
                title=item.title,
                type=item.type,
                priority=item.priority,
                module=item.module,
                preconditions=item.preconditions,
                steps=item.steps,
                expected_results=item.expected_results,
                tags=item.tags,
                is_active=item.is_active,
                traceability_id=item.traceability_id,
            )
            session.add(model)
            await session.commit()
            return item

    async def get(self, item_id: str) -> Optional[TestCase]:
        async for session in get_db_session():
            if session is None:
                return None
            from sqlalchemy import select
            result = await session.execute(
                select(TestCaseModel).where(TestCaseModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            return TestCase(**_to_dict(model)) if model else None

    async def list_all(self, **filters) -> list[TestCase]:
        async for session in get_db_session():
            if session is None:
                return []
            from sqlalchemy import select
            stmt = select(TestCaseModel)
            if "iteration_id" in filters:
                stmt = stmt.where(TestCaseModel.iteration_id == filters["iteration_id"])
            if "story_id" in filters:
                stmt = stmt.where(TestCaseModel.story_id == filters["story_id"])
            if "type" in filters:
                stmt = stmt.where(TestCaseModel.type == filters["type"])
            stmt = stmt.order_by(TestCaseModel.created_at.desc())
            result = await session.execute(stmt)
            return [TestCase(**_to_dict(m)) for m in result.scalars().all()]

    async def update(self, item: TestCase) -> TestCase:
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            from sqlalchemy import select
            result = await session.execute(
                select(TestCaseModel).where(TestCaseModel.id == item.id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"TestCase {item.id} not found")
            for field in ("title", "type", "priority", "module", "preconditions",
                          "steps", "expected_results", "tags", "is_active",
                          "traceability_id"):
                setattr(model, field, getattr(item, field))
            await session.commit()
            return item

    async def delete(self, item_id: str) -> bool:
        async for session in get_db_session():
            if session is None:
                return False
            from sqlalchemy import select
            result = await session.execute(
                select(TestCaseModel).where(TestCaseModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

    async def exists(self, item_id: str) -> bool:
        return await self.get(item_id) is not None


class MySQLTestRunStore(BaseStore[TestRun]):
    async def create(self, item: TestRun) -> TestRun:
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            model = TestRunModel(
                id=item.id,
                iteration_id=item.iteration_id,
                case_ids=item.case_ids,
                environment=item.environment,
                concurrency=item.concurrency,
                status=item.status,
                results=[r.model_dump() for r in item.results] if item.results else [],
                started_at=item.started_at,
                completed_at=item.completed_at,
            )
            session.add(model)
            await session.commit()
            return item

    async def get(self, item_id: str) -> Optional[TestRun]:
        async for session in get_db_session():
            if session is None:
                return None
            from sqlalchemy import select
            result = await session.execute(
                select(TestRunModel).where(TestRunModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            return TestRun(**_to_dict(model)) if model else None

    async def list_all(self, **filters) -> list[TestRun]:
        async for session in get_db_session():
            if session is None:
                return []
            from sqlalchemy import select
            stmt = select(TestRunModel)
            if "iteration_id" in filters:
                stmt = stmt.where(TestRunModel.iteration_id == filters["iteration_id"])
            if "status" in filters:
                stmt = stmt.where(TestRunModel.status == filters["status"])
            stmt = stmt.order_by(TestRunModel.started_at.desc())
            result = await session.execute(stmt)
            return [TestRun(**_to_dict(m)) for m in result.scalars().all()]

    async def update(self, item: TestRun) -> TestRun:
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            from sqlalchemy import select
            result = await session.execute(
                select(TestRunModel).where(TestRunModel.id == item.id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"TestRun {item.id} not found")
            model.status = item.status
            model.results = [r.model_dump() for r in item.results] if item.results else []
            model.completed_at = item.completed_at
            await session.commit()
            return item

    async def delete(self, item_id: str) -> bool:
        async for session in get_db_session():
            if session is None:
                return False
            from sqlalchemy import select
            result = await session.execute(
                select(TestRunModel).where(TestRunModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

    async def exists(self, item_id: str) -> bool:
        return await self.get(item_id) is not None


class MySQLReportStore(BaseStore[TestReport]):
    async def create(self, item: TestReport) -> TestReport:
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            model = ReportModel(
                id=item.id,
                test_run_id=item.test_run_id,
                iteration_id=item.iteration_id,
                total_cases=item.total_cases,
                passed=item.passed,
                failed=item.failed,
                skipped=item.skipped,
                error_count=item.error_count,
                pass_rate=item.pass_rate,
                coverage_rate=item.coverage_rate,
                failures=item.failures,
                defect_chart_url=item.defect_chart_url,
                html_path=item.html_path,
            )
            session.add(model)
            await session.commit()
            return item

    async def get(self, item_id: str) -> Optional[TestReport]:
        async for session in get_db_session():
            if session is None:
                return None
            from sqlalchemy import select
            result = await session.execute(
                select(ReportModel).where(ReportModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            return TestReport(**_to_dict(model)) if model else None

    async def list_all(self, **filters) -> list[TestReport]:
        async for session in get_db_session():
            if session is None:
                return []
            from sqlalchemy import select
            stmt = select(ReportModel)
            if "iteration_id" in filters:
                stmt = stmt.where(ReportModel.iteration_id == filters["iteration_id"])
            if "test_run_id" in filters:
                stmt = stmt.where(ReportModel.test_run_id == filters["test_run_id"])
            stmt = stmt.order_by(ReportModel.generated_at.desc())
            result = await session.execute(stmt)
            return [TestReport(**_to_dict(m)) for m in result.scalars().all()]

    async def update(self, item: TestReport) -> TestReport:
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            from sqlalchemy import select
            result = await session.execute(
                select(ReportModel).where(ReportModel.id == item.id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"Report {item.id} not found")
            for field in ("total_cases", "passed", "failed", "skipped", "error_count",
                          "pass_rate", "coverage_rate", "failures", "defect_chart_url",
                          "html_path"):
                setattr(model, field, getattr(item, field))
            await session.commit()
            return item

    async def delete(self, item_id: str) -> bool:
        async for session in get_db_session():
            if session is None:
                return False
            from sqlalchemy import select
            result = await session.execute(
                select(ReportModel).where(ReportModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

    async def exists(self, item_id: str) -> bool:
        return await self.get(item_id) is not None


class MySQLTraceStore(BaseStore[TraceRecord]):
    async def create(self, item: TraceRecord) -> TraceRecord:
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            model = TraceRecordModel(
                id=item.id,
                iteration_id=item.iteration_id,
                story_ids=item.story_ids,
                case_ids=item.case_ids,
                defect_ids=item.defect_ids,
                report_id=item.report_id,
            )
            session.add(model)
            await session.commit()
            return item

    async def get(self, item_id: str) -> Optional[TraceRecord]:
        async for session in get_db_session():
            if session is None:
                return None
            from sqlalchemy import select
            result = await session.execute(
                select(TraceRecordModel).where(TraceRecordModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            return TraceRecord(**_to_dict(model)) if model else None

    async def list_all(self, **filters) -> list[TraceRecord]:
        async for session in get_db_session():
            if session is None:
                return []
            from sqlalchemy import select
            stmt = select(TraceRecordModel)
            if "iteration_id" in filters:
                stmt = stmt.where(TraceRecordModel.iteration_id == filters["iteration_id"])
            stmt = stmt.order_by(TraceRecordModel.created_at.desc())
            result = await session.execute(stmt)
            return [TraceRecord(**_to_dict(m)) for m in result.scalars().all()]

    async def update(self, item: TraceRecord) -> TraceRecord:
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            from sqlalchemy import select
            result = await session.execute(
                select(TraceRecordModel).where(TraceRecordModel.id == item.id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"TraceRecord {item.id} not found")
            for field in ("story_ids", "case_ids", "defect_ids", "report_id"):
                setattr(model, field, getattr(item, field))
            await session.commit()
            return item

    async def delete(self, item_id: str) -> bool:
        async for session in get_db_session():
            if session is None:
                return False
            from sqlalchemy import select
            result = await session.execute(
                select(TraceRecordModel).where(TraceRecordModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

    async def exists(self, item_id: str) -> bool:
        return await self.get(item_id) is not None


class MySQLKnowledgeStore(BaseStore[KnowledgeDocument]):
    async def create(self, item: KnowledgeDocument) -> KnowledgeDocument:
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            model = KnowledgeDocumentModel(
                id=item.id,
                title=item.title,
                content=item.content,
                product_line=item.product_line,
                doc_type=item.doc_type,
                tags=item.tags,
                iteration_id=item.iteration_id,
                file_path=item.file_path,
            )
            session.add(model)
            await session.commit()
            return item

    async def get(self, item_id: str) -> Optional[KnowledgeDocument]:
        async for session in get_db_session():
            if session is None:
                return None
            from sqlalchemy import select
            result = await session.execute(
                select(KnowledgeDocumentModel).where(KnowledgeDocumentModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            return KnowledgeDocument(**_to_dict(model)) if model else None

    async def list_all(self, **filters) -> list[KnowledgeDocument]:
        async for session in get_db_session():
            if session is None:
                return []
            from sqlalchemy import select
            stmt = select(KnowledgeDocumentModel)
            if "product_line" in filters:
                stmt = stmt.where(KnowledgeDocumentModel.product_line == filters["product_line"])
            if "doc_type" in filters:
                stmt = stmt.where(KnowledgeDocumentModel.doc_type == filters["doc_type"])
            stmt = stmt.order_by(KnowledgeDocumentModel.created_at.desc())
            result = await session.execute(stmt)
            return [KnowledgeDocument(**_to_dict(m)) for m in result.scalars().all()]

    async def update(self, item: KnowledgeDocument) -> KnowledgeDocument:
        async for session in get_db_session():
            if session is None:
                raise RuntimeError("MySQL not initialized")
            from sqlalchemy import select
            result = await session.execute(
                select(KnowledgeDocumentModel).where(KnowledgeDocumentModel.id == item.id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"KnowledgeDocument {item.id} not found")
            for field in ("title", "content", "product_line", "doc_type", "tags",
                          "iteration_id", "file_path"):
                setattr(model, field, getattr(item, field))
            await session.commit()
            return item

    async def delete(self, item_id: str) -> bool:
        async for session in get_db_session():
            if session is None:
                return False
            from sqlalchemy import select
            result = await session.execute(
                select(KnowledgeDocumentModel).where(KnowledgeDocumentModel.id == item_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

    async def exists(self, item_id: str) -> bool:
        return await self.get(item_id) is not None
