# -*- coding: utf-8 -*-
"""Execution queue agent — priority-based scheduling with smart retry.

Features:
- Priority queue (CRITICAL > HIGH > NORMAL > LOW)
- Task sharding (split large batches into shards)
- Smart retry with exponential backoff
- Real-time stats and progress tracking
"""

import asyncio
import heapq
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from common.utils import read_json_file, write_json_file
from common.trace_id import generate_trace_id
from models.execution_queue import (
    ExecutionJob,
    JobPriority,
    JobStatus,
    QueueStats,
)
from storage.paths import get_queue_dir

logger = logging.getLogger(__name__)


class ExecutionQueueAgent:
    def __init__(self, workspace_dir: str | Path, max_concurrency: int = 5):
        self._workspace = Path(workspace_dir)
        self._queue_dir = get_queue_dir(self._workspace)
        self._queue_dir.mkdir(parents=True, exist_ok=True)
        self._max_concurrency = max_concurrency
        self._queue: list[tuple[int, datetime, str, ExecutionJob]] = []
        self._jobs: dict[str, ExecutionJob] = {}
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._running = False
        self._progress_callbacks: list[Callable] = []

    async def enqueue(self, job: ExecutionJob) -> ExecutionJob:
        job.status = JobStatus.QUEUED
        job.queued_at = datetime.utcnow()
        self._jobs[job.id] = job
        heapq.heappush(self._queue, (job.priority.value, job.queued_at, job.id, job))
        self._save_job(job)
        logger.info("Enqueued job %s (priority=%s, case=%s)", job.id, job.priority.name, job.case_id)
        return job

    async def enqueue_batch(
        self,
        case_ids: list[str],
        run_id: str = "",
        iteration_id: str = "",
        priority: JobPriority = JobPriority.NORMAL,
        shard_size: int = 0,
    ) -> list[ExecutionJob]:
        jobs = []
        for i, case_id in enumerate(case_ids):
            shard_index = 0
            shard_total = 1
            shard_id = ""
            if shard_size > 0 and len(case_ids) > shard_size:
                shard_index = i // shard_size
                shard_total = (len(case_ids) + shard_size - 1) // shard_size
                shard_id = f"shard_{shard_index}"

            job = ExecutionJob(
                case_id=case_id,
                run_id=run_id,
                iteration_id=iteration_id,
                priority=priority,
                shard_id=shard_id,
                shard_index=shard_index,
                shard_total=shard_total,
            )
            await self.enqueue(job)
            jobs.append(job)
        return jobs

    async def start_worker(self, executor: Callable[[ExecutionJob], Any]):
        self._running = True
        logger.info("Queue worker started (concurrency=%d)", self._max_concurrency)
        while self._running:
            if not self._queue:
                await asyncio.sleep(0.5)
                continue

            async with self._semaphore:
                if not self._queue:
                    continue
                _, _, job_id, job = heapq.heappop(self._queue)
                if job.status == JobStatus.CANCELLED:
                    continue

                job.status = JobStatus.RUNNING
                job.started_at = datetime.utcnow()
                self._notify_progress(job)

                try:
                    result = await executor(job)
                    job.result = result if isinstance(result, dict) else {"result": str(result)}
                    job.status = JobStatus.PASSED
                except Exception as e:
                    job.error = str(e)[:300]
                    if job.retry_count < job.max_retries:
                        job.retry_count += 1
                        job.status = JobStatus.RETRYING
                        await asyncio.sleep(2 ** job.retry_count)
                        await self.enqueue(job)
                    else:
                        job.status = JobStatus.FAILED

                job.completed_at = datetime.utcnow()
                self._save_job(job)
                self._notify_progress(job)

    def stop_worker(self):
        self._running = False

    def cancel_job(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job and job.status in (JobStatus.PENDING, JobStatus.QUEUED):
            job.status = JobStatus.CANCELLED
            self._save_job(job)
            return True
        return False

    def get_job(self, job_id: str) -> ExecutionJob | None:
        return self._jobs.get(job_id)

    def list_jobs(self, run_id: str = "", status: str = "") -> list[ExecutionJob]:
        jobs = list(self._jobs.values())
        if run_id:
            jobs = [j for j in jobs if j.run_id == run_id]
        if status:
            jobs = [j for j in jobs if j.status.value == status]
        return sorted(jobs, key=lambda j: j.queued_at, reverse=True)

    def get_stats(self) -> QueueStats:
        jobs = list(self._jobs.values())
        if not jobs:
            return QueueStats()

        pending = sum(1 for j in jobs if j.status == JobStatus.QUEUED)
        running = sum(1 for j in jobs if j.status == JobStatus.RUNNING)
        passed = sum(1 for j in jobs if j.status == JobStatus.PASSED)
        failed = sum(1 for j in jobs if j.status == JobStatus.FAILED)
        cancelled = sum(1 for j in jobs if j.status == JobStatus.CANCELLED)

        completed = [j for j in jobs if j.completed_at and j.started_at]
        wait_times = [(j.started_at - j.queued_at).total_seconds() * 1000 for j in completed if j.started_at]
        run_times = [(j.completed_at - j.started_at).total_seconds() * 1000 for j in completed if j.started_at and j.completed_at]

        avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0
        avg_runtime = sum(run_times) / len(run_times) if run_times else 0

        return QueueStats(
            total_jobs=len(jobs),
            pending=pending,
            running=running,
            passed=passed,
            failed=failed,
            cancelled=cancelled,
            avg_wait_ms=avg_wait,
            avg_runtime_ms=avg_runtime,
            throughput_per_min=(passed + failed) / (sum(run_times) / 60000) if run_times and sum(run_times) > 0 else 0,
        )

    def on_progress(self, callback: Callable):
        self._progress_callbacks.append(callback)

    def _notify_progress(self, job: ExecutionJob):
        for cb in self._progress_callbacks:
            try:
                cb(job)
            except Exception:
                pass

    def _save_job(self, job: ExecutionJob):
        f = self._queue_dir / f"{job.id}.json"
        write_json_file(f, job.model_dump())
