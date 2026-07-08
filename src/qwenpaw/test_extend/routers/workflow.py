# -*- coding: utf-8 -*-
"""Workflow Panel API routes.

Provides endpoints for the chat workflow panel to update step status,
query workflow state, and reset progress.
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


class UpdateStepRequest(BaseModel):
    """Request model for step status update."""

    iteration_id: str = Field(..., min_length=1)
    step_id: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)
    result_summary: dict | None = None
    error: str | None = None
    chat_session_id: str | None = None


class ResetWorkflowRequest(BaseModel):
    """Request model for workflow reset."""

    chat_session_id: str | None = None


VALID_STATUSES = {"pending", "running", "completed", "error", "skipped"}


def _get_store():
    """Get workflow store via StorageFactory."""
    from infra.storage_factory import StorageFactory
    from qwenpaw.constant import WORKING_DIR
    factory = StorageFactory(str(WORKING_DIR))
    return factory.create_workflow_store()


@router.post("/update")
async def update_workflow_step(body: UpdateStepRequest):
    """Update a workflow step's status and result.

    Called by the frontend when a tool_call completes, or by agents
    to report progress. Automatically recalculates overall progress.
    When status=completed, triggers knowledge archival.
    """
    from agents.workflow_archive_agent import WorkflowArchiveAgent
    from models.workflow_state import WORKFLOW_STEP_IDS
    from qwenpaw.constant import WORKING_DIR

    if body.step_id not in WORKFLOW_STEP_IDS:
        raise HTTPException(status_code=400, detail=f"Invalid step_id: {body.step_id}")
    if body.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status: {body.status}")

    store = _get_store()
    state = await store.update_step(
        iteration_id=body.iteration_id,
        step_id=body.step_id,
        status=body.status,
        result_summary=body.result_summary,
        error=body.error,
        chat_session_id=body.chat_session_id,
    )

    result = {
        "iteration_id": state.iteration_id,
        "overall_progress": state.overall_progress,
        "steps": [s.model_dump() for s in state.steps],
        "updated_at": state.updated_at.isoformat(),
    }

    if body.status == "completed":
        try:
            agent = WorkflowArchiveAgent(str(WORKING_DIR))
            archive_result = await agent.archive_step_result(
                iteration_id=body.iteration_id,
                step_id=body.step_id,
                result=body.result_summary or {},
            )
            result["archive"] = archive_result
        except Exception as e:
            logger.warning("Knowledge archival failed for step %s: %s", body.step_id, e)
            result["archive"] = {"status": "error", "message": str(e)}

    return result


@router.get("/{iteration_id}")
async def get_workflow_state(iteration_id: str):
    """Get the complete workflow state for an iteration."""
    store = _get_store()
    state = await store.get(iteration_id)

    if state is None:
        return {
            "iteration_id": iteration_id,
            "chat_session_id": None,
            "steps": [],
            "overall_progress": 0,
        }

    return {
        "iteration_id": state.iteration_id,
        "chat_session_id": state.chat_session_id,
        "overall_progress": state.overall_progress,
        "steps": [s.model_dump() for s in state.steps],
        "updated_at": state.updated_at.isoformat(),
    }


@router.post("/{iteration_id}/reset")
async def reset_workflow(iteration_id: str, body: ResetWorkflowRequest | None = None):
    """Reset workflow to initial state (all steps pending)."""
    store = _get_store()
    chat_session_id = body.chat_session_id if body else None

    state = await store.reset_workflow(iteration_id, chat_session_id=chat_session_id)

    return {
        "iteration_id": state.iteration_id,
        "overall_progress": state.overall_progress,
        "steps": [s.model_dump() for s in state.steps],
    }
