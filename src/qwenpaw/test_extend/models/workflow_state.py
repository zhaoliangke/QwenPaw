# -*- coding: utf-8 -*-
"""Workflow state models for the test platform chat workflow panel."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


WORKFLOW_STEP_IDS = ["requirement", "functional", "ui-auto", "review", "execution", "report"]

WORKFLOW_STEP_NAMES = {
    "requirement": "需求分析",
    "functional": "生成功能用例",
    "ui-auto": "生成UI用例",
    "review": "用例评审",
    "execution": "自动测试执行",
    "report": "端到端测试报告",
}

WORKFLOW_STEP_STATUS = ["pending", "running", "completed", "error", "skipped"]


class WorkflowStepRecord(BaseModel):
    """Record of a single workflow step's execution state."""

    step_id: str = Field(description="Step identifier")
    name: str = Field(description="Display name")
    status: str = Field(default="pending", description="Step status: pending|running|completed|error|skipped")
    result_summary: dict[str, Any] = Field(default_factory=dict, description="Summary of step output artifacts")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    started_at: Optional[datetime] = Field(default=None, description="When step started")
    completed_at: Optional[datetime] = Field(default=None, description="When step completed")


class WorkflowState(BaseModel):
    """Complete workflow state for a test iteration."""

    iteration_id: str = Field(description="Parent iteration ID")
    chat_session_id: Optional[str] = Field(default=None, description="Associated chat session")
    steps: list[WorkflowStepRecord] = Field(default_factory=list, description="All step records")
    overall_progress: int = Field(default=0, ge=0, le=100, description="Overall completion percentage")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


def create_default_workflow_state(iteration_id: str, chat_session_id: Optional[str] = None) -> WorkflowState:
    """Create a workflow state with all 6 steps initialized to pending."""
    return WorkflowState(
        iteration_id=iteration_id,
        chat_session_id=chat_session_id,
        steps=[
            WorkflowStepRecord(step_id=step_id, name=WORKFLOW_STEP_NAMES[step_id], status="pending")
            for step_id in WORKFLOW_STEP_IDS
        ],
        overall_progress=0,
    )
