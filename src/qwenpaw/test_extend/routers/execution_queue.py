# -*- coding: utf-8 -*-
"""Execution queue router."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.execution_queue_agent import ExecutionQueueAgent
from common.trace_id import generate_trace_id
from models.execution_queue import ExecutionJob, JobPriority, JobStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/queue", tags=["execution_queue"])

_agent: ExecutionQueueAgent | None = None


def init_queue_agent(workspace_dir: str, max_concurrency: int = 5):
    global _agent
    _agent = ExecutionQueueAgent(workspace_dir, max_concurrency)


@router.post("/enqueue")
async def enqueue_job(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Queue agent not initialized")
    job = ExecutionJob(
        case_id=body.get("case_id", ""),
        run_id=body.get("run_id", ""),
        iteration_id=body.get("iteration_id", ""),
        priority=JobPriority(body.get("priority", 2)),
        max_retries=body.get("max_retries", 2),
    )
    await _agent.enqueue(job)
    return {"job_id": job.id, "status": job.status.value, "priority": job.priority.name}


@router.post("/enqueue_batch")
async def enqueue_batch(body: dict[str, Any]) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Queue agent not initialized")
    case_ids = body.get("case_ids", [])
    if not case_ids:
        raise HTTPException(status_code=400, detail="case_ids required")
    jobs = await _agent.enqueue_batch(
        case_ids=case_ids,
        run_id=body.get("run_id", ""),
        iteration_id=body.get("iteration_id", ""),
        priority=JobPriority(body.get("priority", 2)),
        shard_size=body.get("shard_size", 0),
    )
    return {
        "run_id": body.get("run_id", ""),
        "total": len(jobs),
        "shard_count": max((j.shard_total for j in jobs), default=1),
        "job_ids": [j.id for j in jobs],
    }


@router.get("/jobs")
async def list_jobs(run_id: str = "", status: str = "") -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Queue agent not initialized")
    jobs = _agent.list_jobs(run_id, status)
    return {"jobs": [j.model_dump() for j in jobs], "total": len(jobs)}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Queue agent not initialized")
    job = _agent.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job.model_dump()


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str) -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Queue agent not initialized")
    ok = _agent.cancel_job(job_id)
    return {"cancelled": ok, "job_id": job_id}


@router.get("/stats")
async def get_stats() -> dict[str, Any]:
    if not _agent:
        raise HTTPException(status_code=503, detail="Queue agent not initialized")
    return _agent.get_stats().model_dump()
