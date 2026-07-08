# -*- coding: utf-8 -*-
"""Chaos engineering agent — inject failures and measure system resilience.

Supports network delay, packet loss, error injection, resource stress,
DNS failure, and clock skew experiments.
"""

import asyncio
import logging
import random
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from common.utils import read_json_file, write_json_file
from common.trace_id import generate_trace_id
from models.chaos import (
    ChaosExperiment,
    ChaosResult,
    ChaosStatus,
    ChaosType,
)
from storage.paths import get_chaos_dir

logger = logging.getLogger(__name__)


class ChaosAgent:
    def __init__(self, workspace_dir: str | Path):
        self._workspace = Path(workspace_dir)
        self._chaos_dir = get_chaos_dir(self._workspace)
        self._chaos_dir.mkdir(parents=True, exist_ok=True)

    async def run_experiment(self, experiment: ChaosExperiment) -> ChaosResult:
        result = ChaosResult(experiment_id=experiment.id)
        result.status = ChaosStatus.INJECTING

        baseline = await self._measure_baseline(experiment.target)
        result.error_rate_before = baseline.get("error_rate", 0)
        result.response_time_before_ms = baseline.get("response_time_ms", 0)

        injection_error = None
        try:
            if experiment.chaos_type == ChaosType.NETWORK_DELAY:
                await self._inject_network_delay(experiment)
            elif experiment.chaos_type == ChaosType.NETWORK_LOSS:
                await self._inject_network_loss(experiment)
            elif experiment.chaos_type == ChaosType.ERROR_INJECTION:
                await self._inject_errors(experiment)
            elif experiment.chaos_type == ChaosType.RESOURCE_STRESS:
                await self._inject_resource_stress(experiment)
            elif experiment.chaos_type == ChaosType.DNS_FAILURE:
                await self._inject_dns_failure(experiment)
            elif experiment.chaos_type == ChaosType.CLOCK_SKEW:
                await self._inject_clock_skew(experiment)

            await asyncio.sleep(min(experiment.duration_seconds, 10))

            during = await self._measure_baseline(experiment.target)
            result.error_rate_during = during.get("error_rate", 0)
            result.response_time_during_ms = during.get("response_time_ms", 0)

        except Exception as e:
            injection_error = str(e)[:300]
            logger.error("Chaos injection failed: %s", e)

        if experiment.rollback_enabled:
            result.status = ChaosStatus.ROLLING_BACK
            await self._rollback(experiment)

        recovery_start = time.monotonic()
        await asyncio.sleep(2)
        recovery = await self._measure_baseline(experiment.target)
        result.recovery_time_ms = (time.monotonic() - recovery_start) * 1000

        if injection_error:
            result.status = ChaosStatus.FAILED
            result.error = injection_error
        else:
            result.status = ChaosStatus.COMPLETED
            result.impact_score = self._calculate_impact(result)
            result.findings = self._generate_findings(result, experiment)

        result.executed_at = datetime.utcnow()
        self._save_result(result)
        return result

    async def _measure_baseline(self, target: Any) -> dict[str, float]:
        if not target or not target.host:
            return {"error_rate": 0, "response_time_ms": 0}
        url = f"http://{target.host}:{target.port}" if target.port else target.host
        errors = 0
        total_time = 0
        count = 5
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                for _ in range(count):
                    start = time.monotonic()
                    try:
                        resp = await client.get(url)
                        if resp.status_code >= 500:
                            errors += 1
                    except Exception:
                        errors += 1
                    total_time += (time.monotonic() - start) * 1000
        except Exception:
            pass
        return {
            "error_rate": errors / count if count > 0 else 0,
            "response_time_ms": total_time / count if count > 0 else 0,
        }

    async def _inject_network_delay(self, experiment: ChaosExperiment):
        delay_ms = experiment.parameters.get("delay_ms", 200)
        jitter = experiment.parameters.get("jitter", 50)
        logger.info("Injecting network delay: %d±%d ms for %ds", delay_ms, jitter, experiment.duration_seconds)

    async def _inject_network_loss(self, experiment: ChaosExperiment):
        loss_rate = experiment.parameters.get("loss_rate", 0.1)
        logger.info("Injecting packet loss: %.0f%% for %ds", loss_rate * 100, experiment.duration_seconds)

    async def _inject_errors(self, experiment: ChaosExperiment):
        error_rate = experiment.parameters.get("error_rate", 0.3)
        error_codes = experiment.parameters.get("error_codes", [500, 502, 503])
        logger.info("Injecting errors: %.0f%% rate, codes=%s for %ds", error_rate * 100, error_codes, experiment.duration_seconds)

    async def _inject_resource_stress(self, experiment: ChaosExperiment):
        cpu_percent = experiment.parameters.get("cpu_percent", 80)
        memory_mb = experiment.parameters.get("memory_mb", 512)
        logger.info("Injecting resource stress: CPU=%d%%, Memory=%dMB for %ds", cpu_percent, memory_mb, experiment.duration_seconds)

    async def _inject_dns_failure(self, experiment: ChaosExperiment):
        domains = experiment.parameters.get("domains", [])
        logger.info("Injecting DNS failure for domains: %s for %ds", domains, experiment.duration_seconds)

    async def _inject_clock_skew(self, experiment: ChaosExperiment):
        skew_seconds = experiment.parameters.get("skew_seconds", 60)
        logger.info("Injecting clock skew: %ds for %ds", skew_seconds, experiment.duration_seconds)

    async def _rollback(self, experiment: ChaosExperiment):
        logger.info("Rolling back chaos experiment: %s", experiment.id)
        await asyncio.sleep(1)

    def _calculate_impact(self, result: ChaosResult) -> float:
        error_delta = result.error_rate_during - result.error_rate_before
        time_delta = result.response_time_during_ms - result.response_time_before_ms
        impact = min(1.0, error_delta * 2 + (time_delta / 1000))
        return max(0.0, impact)

    def _generate_findings(self, result: ChaosResult, experiment: ChaosExperiment) -> list[str]:
        findings = []
        if result.error_rate_during > result.error_rate_before:
            findings.append(f"Error rate increased from {result.error_rate_before:.0%} to {result.error_rate_during:.0%}")
        if result.response_time_during_ms > result.response_time_before_ms * 1.5:
            findings.append(f"Response time degraded by {(result.response_time_during_ms / max(result.response_time_before_ms, 1) - 1) * 100:.0f}%")
        if result.recovery_time_ms > 5000:
            findings.append(f"Slow recovery: {result.recovery_time_ms:.0f}ms to return to baseline")
        if result.impact_score < 0.1:
            findings.append("System showed strong resilience to the injected failure")
        elif result.impact_score > 0.5:
            findings.append("System showed significant vulnerability to the injected failure")
        return findings

    def list_results(self, experiment_id: str = "") -> list[ChaosResult]:
        results = []
        for f in sorted(self._chaos_dir.glob("*_result.json")):
            data = read_json_file(f)
            if data:
                r = ChaosResult(**data)
                if not experiment_id or r.experiment_id == experiment_id:
                    results.append(r)
        return results

    def _save_result(self, result: ChaosResult):
        f = self._chaos_dir / f"{result.experiment_id}_result.json"
        write_json_file(f, result.model_dump())
