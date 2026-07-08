# -*- coding: utf-8 -*-
"""Test Schedule Agent - manages test execution scheduling.

Uses asyncio for concurrency control, broadcasts progress via callback
(WebSocket integration point), supports auto-retry and failure isolation.
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from storage.paths import get_exec_log_dir
from models.execution import TestRun, TestCaseResult, ExecutionStatus
from common.trace_id import generate_run_id

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[dict], None]


class TestScheduleAgent:
    """Agent responsible for batch and single test execution."""

    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir
        self._active_runs: dict[str, TestRun] = {}
        self._progress_callbacks: dict[str, list[ProgressCallback]] = {}
        # Semaphore for concurrency control
        self._sem: Optional[asyncio.Semaphore] = None

    def on_progress(self, run_id: str, callback: ProgressCallback):
        """Register a progress callback (e.g. WebSocket push)."""
        self._progress_callbacks.setdefault(run_id, []).append(callback)

    def _broadcast_progress(self, run_id: str):
        run = self._active_runs.get(run_id)
        if not run:
            return
        total = len(run.case_ids)
        completed = len(run.results)
        payload = {
            "run_id": run_id,
            "status": run.status,
            "total": total,
            "completed": completed,
            "passed": sum(1 for r in run.results if r.status == ExecutionStatus.PASSED),
            "failed": sum(1 for r in run.results if r.status == ExecutionStatus.FAILED),
            "error": sum(1 for r in run.results if r.status == ExecutionStatus.ERROR),
            "skipped": sum(1 for r in run.results if r.status == ExecutionStatus.SKIPPED),
            "progress_pct": round(completed / total * 100, 1) if total > 0 else 0,
        }
        for cb in self._progress_callbacks.get(run_id, []):
            try:
                cb(payload)
            except Exception as e:
                logger.warning("Progress callback error for %s: %s", run_id, e)

    async def _execute_single_case(self, case_id: str, environment: str) -> TestCaseResult:
        """Execute a single test case.

        In production, this delegates to Playwright/subprocess via UIAutoAgent.
        Currently simulates execution with configurable pass/fail rate.
        """
        start = time.monotonic()
        try:
            # Simulate execution (placeholder for actual test runner)
            await asyncio.sleep(0.05)
            duration_ms = int((time.monotonic() - start) * 1000)

            # Production: invoke UIAutoAgent.execute_script() or API test runner
            import random
            outcome = random.choices(
                [ExecutionStatus.PASSED, ExecutionStatus.FAILED, ExecutionStatus.ERROR],
                weights=[0.75, 0.20, 0.05],
            )[0]

            return TestCaseResult(
                case_id=case_id,
                status=outcome,
                duration_ms=duration_ms,
            )
        except asyncio.CancelledError:
            return TestCaseResult(
                case_id=case_id,
                status=ExecutionStatus.ERROR,
                duration_ms=int((time.monotonic() - start) * 1000),
                error_stack="Execution cancelled",
            )
        except Exception as e:
            return TestCaseResult(
                case_id=case_id,
                status=ExecutionStatus.ERROR,
                duration_ms=int((time.monotonic() - start) * 1000),
                error_stack=str(e),
            )

    async def _execute_with_semaphore(
        self, case_id: str, environment: str, run_id: str
    ) -> TestCaseResult:
        async with self._sem:
            result = await self._execute_single_case(case_id, environment)
            run = self._active_runs.get(run_id)
            if run:
                run.results.append(result)
                self._broadcast_progress(run_id)
            return result

    async def run_batch(
        self,
        case_ids: list[str],
        iteration_id: str,
        concurrency: int = 4,
        environment: str = "test",
    ) -> dict:
        run_id = generate_run_id()
        run = TestRun(
            id=run_id,
            iteration_id=iteration_id,
            case_ids=case_ids,
            environment=environment,
            concurrency=concurrency,
            status="running",
        )

        exec_log_dir = get_exec_log_dir(self._workspace_dir, iteration_id)
        exec_log_dir.mkdir(parents=True, exist_ok=True)
        log_file = exec_log_dir / f"run_{run_id}.log"
        log_file.write_text(f"Test run {run_id} started at {datetime.utcnow().isoformat()}\n"
                            f"Cases: {len(case_ids)}, Concurrency: {concurrency}\n")

        self._active_runs[run_id] = run
        self._sem = asyncio.Semaphore(concurrency)
        self._broadcast_progress(run_id)

        tasks = [
            self._execute_with_semaphore(cid, environment, run_id)
            for cid in case_ids
        ]
        try:
            await asyncio.gather(*tasks)
            run.status = "completed"
        except Exception as e:
            logger.exception("Batch run %s failed: %s", run_id, e)
            run.status = "failed"
        finally:
            run.completed_at = datetime.utcnow()

        self._broadcast_progress(run_id)

        # Persist results
        result_file = exec_log_dir / f"{run_id}.json"
        import json
        result_file.write_text(
            json.dumps(run.model_dump(), ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        log_file.write_text(log_file.read_text() + f"\nRun completed at {run.completed_at.isoformat()}\n"
                            f"Status: {run.status}, Passed: {sum(1 for r in run.results if r.status == ExecutionStatus.PASSED)}\n")

        return run.model_dump()

    async def run_single(self, case_id: str, environment: str = "test", iteration_id: str = "") -> dict:
        result = await self._execute_single_case(case_id, environment)
        return result.model_dump()

    async def retry_failed(self, test_run_id: str) -> dict:
        run = self._active_runs.get(test_run_id)
        if not run:
            return {"error": "Test run not found"}

        failed = [r for r in run.results if r.status in (ExecutionStatus.FAILED, ExecutionStatus.ERROR)]
        if not failed:
            return {"retried_cases": 0, "message": "No failed cases to retry"}

        failed_ids = [r.case_id for r in failed]
        # Remove old failed results
        run.results = [r for r in run.results if r not in failed]

        self._sem = asyncio.Semaphore(run.concurrency)
        retry_tasks = [
            self._execute_with_semaphore(cid, run.environment, test_run_id)
            for cid in failed_ids
        ]
        try:
            results = await asyncio.gather(*retry_tasks)
        except Exception:
            results = []

        recovered = sum(1 for r in results if r.status == ExecutionStatus.PASSED)
        return {
            "retried_cases": len(failed_ids),
            "recovered": recovered,
            "still_failed": len(failed_ids) - recovered,
        }

    async def get_execution_progress(self, run_id: str) -> dict:
        run = self._active_runs.get(run_id)
        if not run:
            return {"error": "Test run not found"}

        total = len(run.case_ids)
        completed = len(run.results)
        passed = sum(1 for r in run.results if r.status == ExecutionStatus.PASSED)
        failed = sum(1 for r in run.results if r.status == ExecutionStatus.FAILED)

        return {
            "run_id": run_id,
            "status": run.status,
            "total": total,
            "completed": completed,
            "passed": passed,
            "failed": failed,
            "progress_pct": round(completed / total * 100, 1) if total > 0 else 0,
        }
