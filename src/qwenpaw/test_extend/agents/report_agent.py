# -*- coding: utf-8 -*-
"""Report Agent - generates and distributes test reports.

Aggregates execution data, classifies failures, generates HTML reports,
and pushes notifications via the platform's native channels.
"""

import logging
from pathlib import Path

from storage.paths import get_report_dir, get_exec_log_dir
from models.report import TestReport, FailureCategory, FailureItem
from common.trace_id import generate_report_id

logger = logging.getLogger(__name__)


class ReportAgent:
    """Agent responsible for generating test reports from execution results."""

    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir

    async def generate_report(self, test_run: dict, iteration_id: str) -> dict:
        report_id = generate_report_id()
        report_dir = get_report_dir(self._workspace_dir, iteration_id)
        report_dir.mkdir(parents=True, exist_ok=True)

        results = test_run.get("results", [])
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        errors = sum(1 for r in results if r.get("status") == "error")

        pass_rate = passed / total if total > 0 else 0.0

        failures = []
        for r in results:
            if r.get("status") in ("failed", "error"):
                failures.append(FailureItem(
                    case_id=r.get("case_id", ""),
                    category=FailureCategory.SCRIPT_ERROR,
                    summary=r.get("log", "")[:200],
                ))

        report = TestReport(
            id=report_id,
            test_run_id=test_run.get("id", ""),
            iteration_id=iteration_id,
            total_cases=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            error_count=errors,
            pass_rate=pass_rate,
            failures=failures,
            html_path=str(report_dir / f"{report_id}.html"),
        )

        html = self._build_html(report)
        (report_dir / f"{report_id}.html").write_text(html)

        return report.model_dump()

    def _build_html(self, report: TestReport) -> str:
        return f"""<!DOCTYPE html>
<html lang="zh">
<head><meta charset="utf-8"><title>Test Report {report.id}</title></head>
<body>
<h1>Test Report</h1>
<p>Pass Rate: {report.pass_rate:.1%}</p>
<p>Total: {report.total_cases} | Passed: {report.passed} | Failed: {report.failed} | Skipped: {report.skipped}</p>
<h2>Failures</h2>
<pre>{chr(10).join(f"{f.case_id}: {f.summary}" for f in report.failures) or "None"}</pre>
</body>
</html>"""

    async def analyze_failures(self, test_run_id: str, iteration_id: str) -> dict:
        report_dir = get_report_dir(self._workspace_dir, iteration_id)
        reports = sorted(report_dir.glob("*.html")) if report_dir.exists() else []

        return {
            "test_run_id": test_run_id,
            "failure_analysis": "AI failure classification will analyze error patterns",
            "recommendations": [],
        }

    async def push_report(self, report_id: str, channels: list[str] | None = None) -> dict:
        if channels is None:
            channels = ["dingtalk"]
        return {
            "report_id": report_id,
            "channels": channels,
            "status": "queued",
            "note": "Reuses platform native push module",
        }

    async def export_report(self, report_id: str, format: str = "html", iteration_id: str = "") -> dict:
        report_dir = get_report_dir(self._workspace_dir, iteration_id)
        report_file = report_dir / f"{report_id}.html"
        return {
            "format": format,
            "file_path": str(report_file),
            "exists": report_file.exists(),
        }
