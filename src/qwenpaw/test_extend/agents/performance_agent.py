# -*- coding: utf-8 -*-
"""Performance test agent — executes k6 scripts and collects metrics.

Supports load, stress, spike, and soak test types.
Parses k6 JSON output for metrics and threshold validation.
"""

import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from common.utils import read_json_file, write_json_file
from common.trace_id import generate_trace_id
from models.performance import (
    PerfMetric,
    PerfTestCase,
    PerfTestResult,
    PerfTestType,
    PerfThreshold,
)
from storage.paths import get_perf_dir

logger = logging.getLogger(__name__)


class PerformanceAgent:
    def __init__(self, workspace_dir: str | Path):
        self._workspace = Path(workspace_dir)
        self._perf_dir = get_perf_dir(self._workspace)
        self._perf_dir.mkdir(parents=True, exist_ok=True)

    async def run_test(self, test: PerfTestCase, run_id: str = "") -> PerfTestResult:
        result = PerfTestResult(test_id=test.id, run_id=run_id)

        if not test.script_path:
            result.status = "failed"
            result.error = "No script path specified"
            return result

        script_path = Path(test.script_path)
        if not script_path.is_absolute():
            script_path = self._workspace / script_path

        if not script_path.exists():
            result.status = "failed"
            result.error = f"Script not found: {test.script_path}"
            return result

        output_path = self._perf_dir / f"{result.id}_summary.json"
        cmd = [
            "k6", "run",
            "--out", f"json={output_path}",
            "--summary-export", str(output_path),
            str(script_path),
        ]

        env = {**test.env_vars}
        if test.target_url:
            env["TARGET_URL"] = test.target_url
        if test.vusers:
            env["VUS"] = str(test.vusers)

        start = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(self._workspace),
                env={**__import__("os").environ, **env},
            )
            elapsed = (time.monotonic() - start) * 1000

            if output_path.exists():
                result = self._parse_summary(output_path, test, result)

            if proc.returncode == 0:
                result.status = "passed"
            else:
                result.status = "failed"
                result.error = proc.stderr[:500] if proc.stderr else f"k6 exit code {proc.returncode}"

        except FileNotFoundError:
            result.status = "failed"
            result.error = "k6 not installed. Install with: npm install -g k6"
        except subprocess.TimeoutExpired:
            result.status = "failed"
            result.error = "Test timed out after 600s"
        except Exception as e:
            result.status = "failed"
            result.error = str(e)[:300]

        result.executed_at = datetime.utcnow()
        self._save_result(result)
        return result

    def _parse_summary(self, output_path: Path, test: PerfTestCase, result: PerfTestResult) -> PerfTestResult:
        try:
            with open(output_path, "r") as f:
                summary = json.load(f)
            result.raw_summary = summary

            metrics_data = summary.get("metrics", {})

            http_reqs = metrics_data.get("http_reqs", {})
            result.http_reqs = http_reqs.get("count", 0)

            http_failed = metrics_data.get("http_req_failed", {})
            result.http_req_failed = http_failed.get("passes", 0)

            http_duration = metrics_data.get("http_req_duration", {})
            result.http_req_duration_avg = http_duration.get("avg", 0)
            result.http_req_duration_p95 = http_duration.get("med", 0)

            iterations = metrics_data.get("iterations", {})
            result.iterations_completed = iterations.get("count", 0)

            data_received = metrics_data.get("data_received", {})
            result.data_received_mb = data_received.get("count", 0) / (1024 * 1024)

            result.metrics = self._extract_metrics(metrics_data)
            result.metrics = self._validate_thresholds(result.metrics, test.thresholds)

        except Exception as e:
            logger.error("Failed to parse k6 summary: %s", e)

        return result

    def _extract_metrics(self, metrics_data: dict) -> list[PerfMetric]:
        metrics = []
        metric_map = {
            "http_req_duration": ("response_time_avg", "ms"),
            "http_reqs": ("requests_total", "count"),
            "http_req_failed": ("failure_rate", "%"),
            "iterations": ("iterations", "count"),
            "vus": ("virtual_users", "count"),
        }
        for key, (name, unit) in metric_map.items():
            data = metrics_data.get(key, {})
            if "avg" in data:
                metrics.append(PerfMetric(name=name, value=data.get("avg", 0), unit=unit))
            elif "count" in data:
                metrics.append(PerfMetric(name=name, value=data.get("count", 0), unit=unit))
            elif "passes" in data:
                metrics.append(PerfMetric(name=name, value=data.get("passes", 0), unit=unit))
        return metrics

    def _validate_thresholds(self, metrics: list[PerfMetric], thresholds: list[PerfThreshold]) -> list[PerfMetric]:
        for metric in metrics:
            for t in thresholds:
                if t.metric in metric.name:
                    metric.threshold = t.value
                    if t.operator == ">" and metric.value > t.value:
                        metric.passed = False
                    elif t.operator == "<" and metric.value < t.value:
                        metric.passed = False
                    elif t.operator == ">=" and metric.value >= t.value:
                        metric.passed = False
                    elif t.operator == "<=" and metric.value <= t.value:
                        metric.passed = False
        return metrics

    def list_results(self, test_id: str = "") -> list[PerfTestResult]:
        results = []
        for f in sorted(self._perf_dir.glob("*_result.json")):
            data = read_json_file(f)
            if data:
                r = PerfTestResult(**data)
                if not test_id or r.test_id == test_id:
                    results.append(r)
        return results

    def get_result(self, result_id: str) -> PerfTestResult | None:
        f = self._perf_dir / f"{result_id}_result.json"
        if f.exists():
            data = read_json_file(f)
            return PerfTestResult(**data) if data else None
        return None

    def _save_result(self, result: PerfTestResult):
        f = self._perf_dir / f"{result.id}_result.json"
        write_json_file(f, result.model_dump())
