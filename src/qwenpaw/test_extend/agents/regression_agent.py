# -*- coding: utf-8 -*-
"""Smart regression test selection agent.

Analyzes git diffs between commits to determine which test cases
are affected by code changes, enabling targeted regression testing
instead of running the full suite.
"""

import logging
import re
from typing import Any
import subprocess
from pathlib import Path

from models.regression import CodeChange, ChangeType, RegressionPlan

logger = logging.getLogger(__name__)


class RegressionAgent:
    """Selects test cases for regression based on code changes."""

    def __init__(self, workspace_dir: str):
        self._workspace = Path(workspace_dir)

    async def analyze_diff(
        self,
        base_ref: str,
        head_ref: str,
        iteration_id: str = "",
    ) -> RegressionPlan:
        """Analyze git diff and produce a regression plan."""
        changes = await self._get_diff_changes(base_ref, head_ref)
        return RegressionPlan(
            iteration_id=iteration_id,
            base_ref=base_ref,
            head_ref=head_ref,
            changes=changes,
        )

    async def select_cases(
        self,
        plan: RegressionPlan,
        all_cases: list[dict[str, Any]],
    ) -> RegressionPlan:
        """Select which test cases to run based on code changes."""
        if not plan.changes or not all_cases:
            plan.selected_cases = [c.get("id", "") for c in all_cases]
            plan.total_cases = len(all_cases)
            plan.selected_count = len(plan.selected_cases)
            return plan

        changed_files = {c.file_path for c in plan.changes}
        changed_funcs = set()
        for c in plan.changes:
            changed_funcs.update(c.functions_changed)

        selected = []
        skipped = []
        reasons: dict[str, str] = {}

        for case in all_cases:
            case_id = case.get("id", "")
            case_targets = case.get("target_files", [])
            case_tags = case.get("tags", [])
            case_module = case.get("module", "")

            is_selected = False
            reason = ""

            # Direct file match
            for target in case_targets:
                if any(self._path_matches(target, cf) for cf in changed_files):
                    is_selected = True
                    reason = f"target file matches changed file"
                    break

            # Module-level match
            if not is_selected and case_module:
                for change_file in changed_files:
                    if case_module in change_file:
                        is_selected = True
                        reason = f"module '{case_module}' affected"
                        break

            # Tag-based selection
            if not is_selected:
                for tag in case_tags:
                    if tag in changed_funcs or any(tag in f for f in changed_files):
                        is_selected = True
                        reason = f"tag '{tag}' matches change"
                        break

            # Always select smoke tests
            if not is_selected and "smoke" in case_tags:
                is_selected = True
                reason = "smoke test (always included)"

            if is_selected:
                selected.append(case_id)
                reasons[case_id] = reason
            else:
                skipped.append(case_id)

        plan.selected_cases = selected
        plan.skipped_cases = skipped
        plan.selection_reason = reasons
        plan.total_cases = len(all_cases)
        plan.selected_count = len(selected)
        if all_cases:
            plan.estimated_time_saved = (1 - len(selected) / len(all_cases)) * 100

        return plan

    async def _get_diff_changes(self, base_ref: str, head_ref: str) -> list[CodeChange]:
        """Get changed files and line numbers from git diff."""
        changes = []
        try:
            result = subprocess.run(
                ["git", "diff", "--unified=0", "--diff-filter=AMR", f"{base_ref}...{head_ref}"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self._workspace),
            )
            if result.returncode != 0:
                logger.warning("git diff failed: %s", result.stderr[:200])
                return changes

            changes = self._parse_diff_output(result.stdout)
        except FileNotFoundError:
            logger.warning("git not available in workspace")
        except subprocess.TimeoutExpired:
            logger.warning("git diff timed out")

        return changes

    def _parse_diff_output(self, diff_text: str) -> list[CodeChange]:
        """Parse unified diff output into CodeChange objects."""
        changes: list[CodeChange] = []
        current_file: str | None = None
        added_lines: list[int] = []
        removed_lines: list[int] = []

        for line in diff_text.split("\n"):
            if line.startswith("diff --git"):
                if current_file:
                    changes.append(CodeChange(
                        file_path=current_file,
                        change_type=ChangeType.MODIFIED,
                        added_lines=added_lines,
                        removed_lines=removed_lines,
                    ))
                # Extract file path from: diff --git a/path b/path
                parts = line.split(" b/")
                current_file = parts[-1] if len(parts) > 1 else None
                added_lines = []
                removed_lines = []
            elif line.startswith("@@"):
                # Parse hunk header: @@ -old,count +new,count @@
                match = re.search(r"\+(\d+)(?:,(\d+))?", line)
                if match:
                    start = int(match.group(1))
                    count = int(match.group(2)) if match.group(2) else 1
                    added_lines.extend(range(start, start + count))
            elif line.startswith("+") and not line.startswith("+++"):
                pass
            elif line.startswith("-") and not line.startswith("---"):
                match = re.search(r"\-(\d+)", line)
                if match:
                    removed_lines.append(int(match.group(1)))

        if current_file:
            changes.append(CodeChange(
                file_path=current_file,
                change_type=ChangeType.MODIFIED,
                added_lines=added_lines,
                removed_lines=removed_lines,
            ))

        return changes

    def _path_matches(self, target: str, changed: str) -> bool:
        """Check if a target path matches a changed file path."""
        return target in changed or changed in target

    async def get_impact_summary(self, plan: RegressionPlan) -> dict[str, Any]:
        """Generate a human-readable impact summary."""
        modules_affected = set()
        for change in plan.changes:
            parts = change.file_path.split("/")
            if len(parts) > 1:
                modules_affected.add(parts[0])

        return {
            "total_changes": len(plan.changes),
            "modules_affected": list(modules_affected),
            "total_cases": plan.total_cases,
            "selected_cases": plan.selected_count,
            "skipped_cases": len(plan.skipped_cases),
            "estimated_time_saved": f"{plan.estimated_time_saved:.0f}%",
        }
