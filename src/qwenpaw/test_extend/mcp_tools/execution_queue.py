# -*- coding: utf-8 -*-
"""Execution queue MCP tools."""

import logging

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        from agents.execution_queue_agent import ExecutionQueueAgent
        from qwenpaw.constant import WORKING_DIR
        _agent = ExecutionQueueAgent(WORKING_DIR)
    return _agent


async def enqueue_job_tool(
    case_id: str,
    run_id: str = "",
    priority: int = 2,
    iteration_id: str = "",
) -> dict:
    from models.execution_queue import ExecutionJob, JobPriority
    job = ExecutionJob(
        case_id=case_id, run_id=run_id, iteration_id=iteration_id,
        priority=JobPriority(priority),
    )
    await _get_agent().enqueue(job)
    return {"job_id": job.id, "status": job.status.value}


async def enqueue_batch_tool(
    case_ids: list[str],
    run_id: str = "",
    priority: int = 2,
    shard_size: int = 0,
) -> dict:
    from models.execution_queue import JobPriority
    jobs = await _get_agent().enqueue_batch(
        case_ids=case_ids, run_id=run_id,
        priority=JobPriority(priority), shard_size=shard_size,
    )
    return {"total": len(jobs), "job_ids": [j.id for j in jobs]}


async def get_queue_stats_tool() -> dict:
    return _get_agent().get_stats().model_dump()


async def cancel_job_tool(job_id: str) -> dict:
    ok = _get_agent().cancel_job(job_id)
    return {"cancelled": ok, "job_id": job_id}


async def list_queue_jobs_tool(run_id: str = "", status: str = "") -> dict:
    jobs = _get_agent().list_jobs(run_id, status)
    return {"jobs": [j.model_dump() for j in jobs], "total": len(jobs)}
