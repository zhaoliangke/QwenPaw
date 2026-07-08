# -*- coding: utf-8 -*-
"""Coverage analysis agent.

Integrates with coverage.py (or equivalent) to compute test coverage
per iteration and per test case batch. Stores coverage reports and
provides gap analysis for uncovered code paths.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from models.coverage import CoverageReport, CoverageType
from storage.paths import get_coverage_dir

logger = logging.getLogger(__name__)


class CoverageAgent:
    """Analyzes test coverage and identifies gaps."""

    def __init__(self, workspace_dir: str):
        self._workspace = Path(workspace_dir)
        self._report_dir = get_coverage_dir(self._workspace)
        self._report_dir.mkdir(parents=True, exist_ok=True)

    async def run_coverage(
        self,
        source_path: str,
        test_path: str,
        iteration_id: str = "",
        run_id: str = "",
    ) -> CoverageReport:
        """Run coverage.py and parse results into a CoverageReport."""
        try:
            result = subprocess.run(
                ["python", "-m", "coverage", "run", "--source", source_path, "-m", "pytest", test_path, "-q"],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(self._workspace),
            )
            logger.info("Coverage run completed with exit code %d", result.returncode)
        except FileNotFoundError:
            logger.warning("coverage.py or pytest not installed, generating placeholder report")
        except subprocess.TimeoutExpired:
            logger.warning("Coverage run timed out")

        # Parse coverage.json if available
        json_path = self._workspace / "coverage.json"
        if json_path.exists():
            return await self._parse_coverage_json(json_path, iteration_id, run_id)

        return CoverageReport(
            iteration_id=iteration_id,
            run_id=run_id,
            total_lines=0,
            covered_lines=0,
            line_rate=0.0,
        )

    async def _parse_coverage_json(
        self,
        json_path: Path,
        iteration_id: str,
        run_id: str,
    ) -> CoverageReport:
        """Parse coverage.py JSON output."""
        try:
            with open(json_path, "r") as f:
                cov_data = json.load(f)

            totals = cov_data.get("totals", {})
            covered_lines = totals.get("covered_lines", 0)
            missing_lines = totals.get("missing_lines", 0)
            total_lines = covered_lines + missing_lines

            uncovered_files = []
            for file_path, file_data in cov_data.get("files", {}).items():
                missing = file_data.get("missing_lines", [])
                if missing:
                    uncovered_files.append({
                        "file": file_path,
                        "missing_lines": missing[:50],
                        "missing_count": len(missing),
                    })

            report = CoverageReport(
                iteration_id=iteration_id,
                run_id=run_id,
                total_lines=total_lines,
                covered_lines=covered_lines,
                line_rate=(covered_lines / total_lines) if total_lines > 0 else 0.0,
                uncovered_files=sorted(uncovered_files, key=lambda x: x["missing_count"], reverse=True)[:20],
            )

            # Persist report
            report_path = self._report_dir / f"{report.id}.json"
            with open(report_path, "w") as f:
                f.write(report.model_dump_json())

            return report
        except Exception as e:
            logger.error("Failed to parse coverage.json: %s", e)
            return CoverageReport(iteration_id=iteration_id, run_id=run_id)

    async def get_uncovered_gaps(self, report_id: str) -> list[dict[str, Any]]:
        """Identify uncovered code paths that need test cases."""
        report_path = self._report_dir / f"{report_id}.json"
        if not report_path.exists():
            return []
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            return data.get("uncovered_files", [])
        except Exception:
            return []

    async def list_reports(self, iteration_id: str = "") -> list[CoverageReport]:
        """List coverage reports, optionally filtered by iteration."""
        reports = []
        for f in sorted(self._report_dir.glob("*.json")):
            try:
                with open(f, "r") as fh:
                    data = json.load(fh)
                report = CoverageReport(**data)
                if not iteration_id or report.iteration_id == iteration_id:
                    reports.append(report)
            except Exception:
                continue
        return reports
