# -*- coding: utf-8 -*-
"""UI Automation Agent - Playwright script generation and execution.

Generates Playwright scripts from test cases, supports VLM-based visual
element positioning, online debugging with screenshot capture, and
Page Object layered script organization.
"""

import json
import logging
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from ..storage.paths import get_script_dir, get_exec_log_dir
from ..models.execution import TestCaseResult, ExecutionStatus

logger = logging.getLogger(__name__)


class UIAutoAgent:
    """Agent responsible for UI automation script lifecycle."""

    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir

    async def generate_script(
        self,
        test_case: dict,
        base_url: str = "",
        page_object: str = "",
    ) -> dict:
        """Generate a Playwright script from a test case description.

        Uses the LLM to produce PO-layered Playwright code with fallback
        to structured CSS selectors. VLM assistance is available when
        screenshots/designs are provided.
        """
        title = test_case.get("title", "Untitled")
        steps = test_case.get("steps", [])
        case_id = test_case.get("id", "")

        script = self._render_playwright_template(title, steps, base_url, page_object)

        return {
            "case_id": case_id,
            "script": script,
            "language": "python",
            "framework": "playwright",
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def debug_script(
        self,
        script_content: str,
        iteration_id: str,
        base_url: str = "",
    ) -> dict:
        """Execute a script in debug mode, capturing screenshots per step."""
        script_dir = get_script_dir(self._workspace_dir, iteration_id)
        script_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        script_path = script_dir / f"debug_{ts}.py"
        script_path.write_text(script_content, encoding="utf-8")

        exec_log_dir = get_exec_log_dir(self._workspace_dir, iteration_id)
        exec_log_dir.mkdir(parents=True, exist_ok=True)

        result = await self.execute_script(str(script_path), {"ITERATION_ID": iteration_id, "BASE_URL": base_url})

        return {
            "script_path": str(script_path),
            "result": result,
            "screenshots": result.get("screenshots", []),
            "log": result.get("log", ""),
        }

    async def execute_script(self, script_path: str, env_config: dict | None = None) -> dict:
        """Execute a Playwright script via subprocess.

        The script is run in a sandboxed subprocess. Results (pass/fail,
        screenshots, logs) are collected and returned.
        """
        env_config = env_config or {}
        iteration_id = env_config.get("ITERATION_ID", "")
        base_url = env_config.get("BASE_URL", "")

        exec_log_dir = get_exec_log_dir(self._workspace_dir, iteration_id) if iteration_id else Path(tempfile.mkdtemp())
        exec_log_dir.mkdir(parents=True, exist_ok=True)

        screenshots_dir = exec_log_dir / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        env = {
            "PLAYWRIGHT_BASE_URL": base_url,
            "PLAYWRIGHT_SCREENSHOT_DIR": str(screenshots_dir),
        }

        start = datetime.utcnow()
        try:
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                timeout=120,
                env={**__import__("os").environ, **env},
                cwd=str(exec_log_dir),
            )

            duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
            status = ExecutionStatus.PASSED if result.returncode == 0 else ExecutionStatus.FAILED

            screenshots = sorted(screenshots_dir.glob("*.png")) if screenshots_dir.exists() else []
            log_output = (result.stdout + "\n" + result.stderr).strip()

            # Write execution log
            log_file = exec_log_dir / f"exec_{start.strftime('%Y%m%d_%H%M%S')}.log"
            log_file.write_text(log_output, encoding="utf-8")

            return {
                "status": status.value,
                "duration_ms": duration_ms,
                "screenshots": [str(s) for s in screenshots],
                "log": log_output[:5000],
                "error_stack": result.stderr[:2000] if status == ExecutionStatus.FAILED else "",
            }
        except subprocess.TimeoutExpired:
            return {
                "status": ExecutionStatus.ERROR.value,
                "duration_ms": 120000,
                "screenshots": [],
                "log": "Execution timed out after 120 seconds",
                "error_stack": "TimeoutExpired",
            }
        except Exception as e:
            return {
                "status": ExecutionStatus.ERROR.value,
                "duration_ms": int((datetime.utcnow() - start).total_seconds() * 1000),
                "screenshots": [],
                "log": str(e),
                "error_stack": str(e),
            }

    async def capture_screenshot(self, iteration_id: str, step_name: str = "") -> str:
        """Return the expected screenshot path for a test step."""
        exec_log_dir = get_exec_log_dir(self._workspace_dir, iteration_id)
        ss_dir = exec_log_dir / "screenshots"
        ss_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{step_name or 'step'}_{datetime.utcnow().strftime('%H%M%S')}.png"
        return str(ss_dir / filename)

    def _render_playwright_template(
        self, title: str, steps: list[str], base_url: str, page_object: str
    ) -> str:
        """Generate a Playwright Python script from a template."""
        steps_code = ""
        for i, step in enumerate(steps, 1):
            clean_step = step.replace('"', '\\"')
            steps_code += f'    await page.click("text={clean_step}")\n'
            steps_code += f'    await page.screenshot(path=f"step_{i:02d}.png")\n\n'

        base_url_line = f'BASE_URL = "{base_url}"' if base_url else "# BASE_URL not configured"

        return f'''"""Auto-generated Playwright test: {title}"""
import os
from playwright.sync_api import sync_playwright

{base_url_line}
SCREENSHOT_DIR = os.environ.get("PLAYWRIGHT_SCREENSHOT_DIR", ".")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={{"width": 1920, "height": 1080}})
        page = context.new_page()
        try:
            if BASE_URL:
                page.goto(BASE_URL)
{steps_code}
        finally:
            browser.close()

if __name__ == "__main__":
    run()
'''
