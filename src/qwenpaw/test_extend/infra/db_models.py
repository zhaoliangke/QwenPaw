# -*- coding: utf-8 -*-
"""SQLAlchemy ORM models for the AI Test Platform.

These models are used when the MySQL backend is enabled.
They mirror the Pydantic models but add database-level features
(relationships, indexes, cascading deletes).

All tables are prefixed with 'test_' to avoid conflicts.

When SQLAlchemy is not installed, lazy placeholders are provided
so the module can be imported without errors.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

try:
    from sqlalchemy import (
        Column, String, Integer, Float, Boolean, Date, DateTime,
        Text, JSON, ForeignKey, Index,
    )
    from sqlalchemy.orm import declarative_base, relationship
    _HAS_SQLALCHEMY = True
except ImportError:
    _HAS_SQLALCHEMY = False

if _HAS_SQLALCHEMY:
    Base = declarative_base()

    class IterationModel(Base):
        __tablename__ = "test_iterations"

        id = Column(String(64), primary_key=True)
        name = Column(String(256), nullable=False, index=True)
        version = Column(String(64), nullable=False)
        module = Column(String(256), nullable=False)
        description = Column(Text, nullable=True)
        start_date = Column(Date, nullable=False)
        end_date = Column(Date, nullable=False)
        git_branch = Column(String(256), nullable=True)
        test_environment = Column(String(512), nullable=True)
        status = Column(String(32), nullable=False, default="draft", index=True)
        traceability_id = Column(String(64), default="")
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        stories = relationship("StoryModel", back_populates="iteration", cascade="all, delete-orphan")
        cases = relationship("TestCaseModel", back_populates="iteration", cascade="all, delete-orphan")

        __table_args__ = (
            Index("idx_iteration_status", "status"),
            Index("idx_iteration_module", "module"),
        )

    class StoryModel(Base):
        __tablename__ = "test_stories"

        id = Column(String(64), primary_key=True)
        iteration_id = Column(String(64), ForeignKey("test_iterations.id", ondelete="CASCADE"), nullable=False, index=True)
        parent_story_id = Column(String(64), ForeignKey("test_stories.id", ondelete="SET NULL"), nullable=True)
        title = Column(String(512), nullable=False)
        as_a = Column(String(256), default="")
        i_want = Column(Text, default="")
        so_that = Column(Text, default="")
        acceptance_criteria = Column(JSON, default=list)
        priority = Column(String(16), default="medium")
        traceability_id = Column(String(64), default="")
        is_validated = Column(Boolean, default=False)
        validation_issues = Column(JSON, default=list)
        created_at = Column(DateTime, default=datetime.utcnow)

        iteration = relationship("IterationModel", back_populates="stories")
        cases = relationship("TestCaseModel", back_populates="story", cascade="all, delete-orphan")

        __table_args__ = (
            Index("idx_story_iteration", "iteration_id"),
            Index("idx_story_priority", "priority"),
        )

    class TestCaseModel(Base):
        __tablename__ = "test_cases"

        id = Column(String(64), primary_key=True)
        story_id = Column(String(64), ForeignKey("test_stories.id", ondelete="CASCADE"), nullable=False, index=True)
        iteration_id = Column(String(64), ForeignKey("test_iterations.id", ondelete="CASCADE"), nullable=False, index=True)
        title = Column(String(512), nullable=False)
        type = Column(String(32), nullable=False, default="functional", index=True)
        priority = Column(String(16), default="medium")
        module = Column(String(256), default="")
        preconditions = Column(JSON, default=list)
        steps = Column(JSON, default=list)
        expected_results = Column(JSON, default=list)
        tags = Column(JSON, default=list)
        is_active = Column(Boolean, default=True)
        traceability_id = Column(String(64), default="")
        created_at = Column(DateTime, default=datetime.utcnow)

        iteration = relationship("IterationModel", back_populates="cases")
        story = relationship("StoryModel", back_populates="cases")

        __table_args__ = (
            Index("idx_case_story", "story_id"),
            Index("idx_case_type", "type"),
            Index("idx_case_priority", "priority"),
        )

    class TestRunModel(Base):
        __tablename__ = "test_runs"

        id = Column(String(64), primary_key=True)
        iteration_id = Column(String(64), ForeignKey("test_iterations.id", ondelete="CASCADE"), nullable=False, index=True)
        case_ids = Column(JSON, default=list)
        environment = Column(String(32), default="test")
        concurrency = Column(Integer, default=4)
        status = Column(String(32), default="pending", index=True)
        results = Column(JSON, default=list)
        started_at = Column(DateTime, default=datetime.utcnow)
        completed_at = Column(DateTime, nullable=True)

        __table_args__ = (
            Index("idx_run_iteration", "iteration_id"),
            Index("idx_run_status", "status"),
        )

    class ReportModel(Base):
        __tablename__ = "test_reports"

        id = Column(String(64), primary_key=True)
        test_run_id = Column(String(64), ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False, index=True)
        iteration_id = Column(String(64), ForeignKey("test_iterations.id", ondelete="CASCADE"), nullable=False, index=True)
        total_cases = Column(Integer, default=0)
        passed = Column(Integer, default=0)
        failed = Column(Integer, default=0)
        skipped = Column(Integer, default=0)
        error_count = Column(Integer, default=0)
        pass_rate = Column(Float, default=0.0)
        coverage_rate = Column(Float, default=0.0)
        failures = Column(JSON, default=list)
        defect_chart_url = Column(String(1024), nullable=True)
        html_path = Column(String(1024), nullable=True)
        generated_at = Column(DateTime, default=datetime.utcnow)

        __table_args__ = (
            Index("idx_report_iteration", "iteration_id"),
            Index("idx_report_run", "test_run_id"),
        )

    class TraceRecordModel(Base):
        __tablename__ = "test_trace_records"

        id = Column(String(64), primary_key=True)
        iteration_id = Column(String(64), ForeignKey("test_iterations.id", ondelete="CASCADE"), nullable=False, index=True)
        story_ids = Column(JSON, default=list)
        case_ids = Column(JSON, default=list)
        defect_ids = Column(JSON, default=list)
        report_id = Column(String(64), nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)

        __table_args__ = (
            Index("idx_trace_iteration", "iteration_id"),
        )

    class KnowledgeDocumentModel(Base):
        __tablename__ = "test_knowledge_docs"

        id = Column(String(64), primary_key=True)
        title = Column(String(512), nullable=False)
        content = Column(Text, default="")
        product_line = Column(String(256), nullable=True, index=True)
        doc_type = Column(String(64), default="general")
        tags = Column(JSON, default=list)
        iteration_id = Column(String(64), nullable=True, index=True)
        file_path = Column(String(1024), nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)

        __table_args__ = (
            Index("idx_knowledge_product", "product_line"),
            Index("idx_knowledge_type", "doc_type"),
        )

else:
    Base = type("Base", (), {"metadata": type("Meta", (), {"tables": {}, "create_all": lambda self, bind: None})()})()

    class IterationModel: pass
    class StoryModel: pass
    class TestCaseModel: pass
    class TestRunModel: pass
    class ReportModel: pass
    class TraceRecordModel: pass
    class KnowledgeDocumentModel: pass
