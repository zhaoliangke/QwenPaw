# -*- coding: utf-8 -*-
"""UI Automation Agent - Playwright script generation and execution.

Two-phase architecture:
  Phase 1: Template-based generation with element mapping table
  Phase 2: AI-driven generation using LLM to analyze test cases

Supports:
  - data-testid / aria-label / role / CSS selector positioning
  - Explicit waits (expect().to_be_visible)
  - Semantic assertions (expect().to_have_text, .to_have_value, etc.)
  - Page Object Layered organization
  - Project URL from project management module
  - Visual regression screenshots per step
"""
import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from storage.paths import get_script_dir, get_exec_log_dir
from models.execution import TestCaseResult, ExecutionStatus

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Playwright template (Phase 1: template-based)
# -------------------------------------------------------------------

PLAYWRIGHT_SCRIPT_TEMPLATE = '''"""Auto-generated Playwright E2E test: {title}
Test Case ID: {case_id}
Page Object: {page_object_display}
"""

import os
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "{base_url}"
SCREENSHOT_DIR = os.environ.get("PLAYWRIGHT_SCREENSHOT_DIR", "./screenshots")

{pytest_fixtures}

{page_object_section}

{test_functions}
'''


def _build_test_function(
    test_name: str,
    title: str,
    steps: list[dict],
    element_map: dict,
    case_id: str,
) -> str:
    """Build a single test function from structured steps."""
    lines = [f'def {test_name}(page: Page):']
    lines.append(f'    """{title}"""')
    steps_with_goto = [{"action": "navigate", "selector": "page.goto(BASE_URL)"}] + steps
    for step in steps_with_goto:
        action = step.get("action", "click")
        description = step.get("description", "")
        wait_ms = step.get("wait_ms", 0)
        if description:
            lines.append(f"    # {description}")
        code = _action_to_code(action, step, element_map)
        if code:
            lines.extend(f"    {ln}" for ln in code)
        if wait_ms > 0:
            lines.append(f"    page.wait_for_timeout({wait_ms})")
    lines.append("")
    return "\n".join(lines)


def _resolve_selector(step: dict, element_map: dict) -> str:
    """Resolve element selector from step + element map with priority order."""
    # Priority: explicit selector > element_ref from map > element_id > data-testid > role + name > text
    explicit = step.get("selector", "")
    if explicit:
        return explicit

    ref = step.get("element_ref", "")
    if ref and ref in element_map:
        return element_map[ref]

    eid = step.get("element_id", "")
    if eid:
        return f'[data-testid="{eid}"]'

    role_val = step.get("role", "")
    name_val = step.get("name", "")
    if role_val and name_val:
        return f'get_by_role("{role_val}", name="{name_val}")'
    if role_val:
        return f'get_by_role("{role_val}")'

    label = step.get("label", "")
    if label:
        return f'get_by_label("{label}")'

    text_val = step.get("text", "")
    if text_val:
        return f'get_by_text("{text_val}")'

    placeholder = step.get("placeholder", "")
    if placeholder:
        return f'get_by_placeholder("{placeholder}")'

    return 'locator("body")'


def _action_to_code(action: str, step: dict, element_map: dict) -> list[str]:
    """Convert a step action + metadata to Playwright code lines."""
    selector = _resolve_selector(step, element_map)
    value = step.get("value", "")

    if action == "navigate":
        lines = ["page.goto(BASE_URL)"]
        if step.get("title_contains"):
            lines.append(f"expect(page).to_have_title(re.compile(r\"{step['title_contains']}\"))")
            return lines
        return lines

    if action == "click":
        selector = _resolve_selector(step, element_map)
        code = [f"page.{selector}.click()"]
        expect_check = step.get("expect")
        if expect_check == "visible":
            code.append(f"expect(page.{selector}).to_be_visible()")
        return code

    if action == "fill":
        if not value:
            return []
        return [
            f"page.{selector}.fill(\"{value}\")",
            f"expect(page.{selector}).to_have_value(\"{value}\")",
        ]

    if action == "select":
        if not value:
            return []
        return [
            f"page.{selector}.select_option(\"{value}\")",
            f"expect(page.{selector}).to_have_value(\"{value}\")",
        ]

    if action == "check":
        return [
            f"page.{selector}.check()",
            f"expect(page.{selector}).to_be_checked()",
        ]

    if action == "uncheck":
        return [
            f"page.{selector}.uncheck()",
            f"expect(page.{selector}).not_to_be_checked()",
        ]

    if action == "hover":
        return [f"page.{selector}.hover()"]

    if action == "assert_visible":
        return [f"expect(page.{selector}).to_be_visible(timeout=10000)"]

    if action == "assert_text":
        return [f"expect(page.{selector}).to_contain_text(\"{value}\")"]

    if action == "assert_hidden":
        return [f"expect(page.{selector}).not_to_be_visible()"]

    if action == "assert_count":
        return [f"expect(page.{selector}).to_have_count({value or 1})"]

    if action == "screenshot":
        name = step.get("screenshot_name", "step")
        return [f'page.screenshot(path=os.path.join(SCREENSHOT_DIR, "{name}.png"))']

    if action == "wait_for_selector":
        return [f"page.{selector}.wait_for(state=\"visible\")"]

    if action == "wait_for_url":
        return [f"page.wait_for_url(\"**{value}**\")"] if value else []

    if action == "assert_url":
        return [f'expect(page).to_have_url(re.compile(r\"{value}\"))'] if value else []

    if action == "upload_file":
        return [f"page.{selector}.set_input_files(\"{value}\")"] if value else []

    if action == "confirm_dialog":
        return [
            "def handle_dialog(dialog):",
            "    dialog.accept()",
            "page.once(\"dialog\", handle_dialog)",
        ]
        return f.split("\n")
    return []


# -------------------------------------------------------------------
# AI-driven generation (Phase 2)
# -------------------------------------------------------------------

SYSTEM_PROMPT_FOR_UI_SCRIPT = """You are a Playwright test automation expert. Given a test case and element mapping table, generate a stable Playwright Python script.

STRICT RULES:
1. Use ONLY the selectors from the element map (data-testid preferred).
2. Always use `expect().to_be_visible(timeout=10000)` before interacting.
3. Every action must be followed by an assertion (expect).
4. No `page.wait_for_timeout()` unless explicitly specified.
5. No hardcoded credentials or sensitive data.
6. Use `page.goto(BASE_URL)` at the start.
7. Output ONLY valid Python code — no markdown fences, no explanations.

Output format:
```python
# test: {title}
import os
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "{base_url}"

def test_{safe_name}(page: Page):
    \"\"\"{title}\"\"\"
    page.goto(BASE_URL)
    # ... your code here
```
"""


class UIAutoAgent:
    """Agent responsible for UI automation script lifecyle.

    Two generation modes:
      - "template": Structured steps + element map → Playwright script
      - "ai": LLM analyzes test case → Playwright script (when LLM available)
    """

    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir

    # ---------------------------------------------------------------
    # Primary: generate_script (unified entry)
    # ---------------------------------------------------------------

    async def generate_script(
        self,
        test_case: dict,
        base_url: str = "",
        page_object: str = "",
        element_map: Optional[dict] = None,
        mode: str = "template",
        project_id: str = "",
        iteration_id: str = "",
    ) -> dict:
        """Generate a Playwright script from a test case.

        Args:
            test_case: dict with id, title, steps (list of action dicts or strings), preconditions
            base_url: target URL (from project or env)
            page_object: page object class name
            element_map: dict mapping semantic names to CSS selectors
            mode: "template" (default) or "ai" (LLM-driven)
            project_id: project ID for reading target_url from project store
            iteration_id: iteration ID for file storage

        Returns:
            dict with case_id, script, language, framework
        """
        # Resolve base_url from project store if project_id provided
        if project_id and not base_url:
            base_url = await self._resolve_project_url(project_id)

        element_map = element_map or {}

        if mode == "ai":
            return await self._generate_ai(test_case, base_url, element_map)

        return await self._generate_template(
            test_case, base_url, page_object, element_map
        )

    # ---------------------------------------------------------------
    # Phase 1: Template-based generation
    # ---------------------------------------------------------------

    async def _generate_template(
        self,
        test_case: dict,
        base_url: str,
        page_object: str,
        element_map: dict,
    ) -> dict:
        """Generate a Playwright script from a structured test case using templates."""
        case_id = test_case.get("id", "")
        title = test_case.get("title", "Untitled")
        steps = test_case.get("steps", [])
        preconditions = test_case.get("preconditions", [])

        # Normalize steps — accept both string and dict formats
        normalized_steps = self._normalize_steps(steps)

        test_name = self._make_test_name(case_id or title)
        test_func = _build_test_function(
            test_name, title, normalized_steps, element_map, case_id
        )

        page_object_display = page_object or "(none)"
        page_object_section = (
            f"class {page_object}Page:\n    \"\"\"Page Object for {page_object}\"\"\"\n    pass\n"
            if page_object
            else ""
        )

        fixtures = ""
        if preconditions:
            fixture_lines = [
                "@pytest.fixture(autouse=True)",
                "def setup_data(request):",
            ]
            for cond in preconditions:
                fixture_lines.append(f"    # Precondition: {cond}")
            fixture_lines.append("    yield")
            fixtures = "\n".join(fixture_lines)

        script = PLAYWRIGHT_SCRIPT_TEMPLATE.format(
            title=title,
            case_id=case_id,
            base_url=base_url or "http://localhost",
            page_object_display=page_object_display,
            page_object_section=page_object_section,
            pytest_fixtures=fixtures,
            test_functions=test_func,
        )

        return {
            "case_id": case_id,
            "script": script,
            "language": "python",
            "framework": "playwright",
            "generated_at": datetime.utcnow().isoformat(),
            "mode": "template",
        }

    # ---------------------------------------------------------------
    # Phase 2: AI-driven generation
    # ---------------------------------------------------------------

    async def _generate_ai(
        self,
        test_case: dict,
        base_url: str,
        element_map: dict,
    ) -> dict:
        """Generate a Playwright script using LLM analysis.

        The LLM receives the test case + element mapping table and
        produces a stable Playwright Python script.
        """
        case_id = test_case.get("id", "")
        title = test_case.get("title", "Untitled")
        preconditions = test_case.get("preconditions", [])

        # Build prompt
        element_map_str = "\n".join(
            f"  {k}: {v}" for k, v in element_map.items()
        ) if element_map else "  (no element map provided)"

        prompt = f"""Generate a Playwright test for:

**Test Case**: {case_id} — {title}
**Preconditions**: {json.dumps(preconditions, ensure_ascii=False)}
**Target URL**: {base_url or "http://localhost"}
**Element Map**:
{element_map_str}

**Test Steps**:
{json.dumps(test_case.get('steps', []), ensure_ascii=False, indent=2)}

Generate the test function now."""
        try:
            from qwenpaw.providers.provider_manager import ProviderManager
            from agentscope.message import Msg

            model = ProviderManager.get_active_chat_model()
            if model is None:
                logger.warning("No active chat model, falling back to template")
                return await self._generate_template(test_case, base_url, "", element_map)

            messages = [
                Msg(role="system", content=SYSTEM_PROMPT_FOR_UI_SCRIPT.format(
                    title=title,
                    base_url=base_url or "http://localhost",
                    safe_name=self._make_test_name(title),
                ), name="test_platform"),
                Msg(role="user", content=prompt, name="test_platform"),
            ]
            response = await asyncio.wait_for(model(messages), timeout=30.0)
            if hasattr(response, "__aiter__"):
                accumulated = ""
                async for chunk in response:
                    if hasattr(chunk, "text"):
                        accumulated += chunk.text
                    elif hasattr(chunk, "content"):
                        accumulated += str(chunk.content)
                response_text = accumulated
            elif hasattr(response, "text"):
                response_text = response.text
            elif hasattr(response, "content"):
                response_text = str(response.content)
            else:
                response_text = str(response)

            code = self._extract_code_block(response_text)
        except Exception as e:
            logger.warning("AI generation failed, falling back to template: %s", e)
            return await self._generate_template(test_case, base_url, "", element_map)

        if not code:
            return await self._generate_template(test_case, base_url, "", element_map)

        return {
            "case_id": case_id,
            "script": code,
            "language": "python", 
            "framework": "playwright",
            "generated_at": datetime.utcnow().isoformat(),
            "mode": "ai",
        }

    # ---------------------------------------------------------------
    # Debug & Execute
    # ---------------------------------------------------------------

    async def debug_script(
        self,
        script_content: str,
        iteration_id: str,
        base_url: str = "",
    ) -> dict:
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
                env={**os.environ, **env},
                cwd=str(exec_log_dir),
            )
            duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
            status = ExecutionStatus.PASSED if result.returncode == 0 else ExecutionStatus.FAILED
            screenshots = sorted(screenshots_dir.glob("*.png")) if screenshots_dir.exists() else []
            log_output = (result.stdout + "\n" + result.stderr).strip()
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
            return {"status": ExecutionStatus.ERROR.value, "duration_ms": 120000, "screenshots": [], "log": "Execution timed out after 120 seconds", "error_stack": "TimeoutExpired"}
        except Exception as e:
            return {"status": ExecutionStatus.ERROR.value, "duration_ms": int((datetime.utcnow() - start).total_seconds() * 1000), "screenshots": [], "log": str(e), "error_stack": str(e)}

    async def capture_screenshot(self, iteration_id: str, step_name: str = "") -> str:
        exec_log_dir = get_exec_log_dir(self._workspace_dir, iteration_id)
        ss_dir = exec_log_dir / "screenshots"
        ss_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{step_name or 'step'}_{datetime.utcnow().strftime('%H%M%S')}.png"
        return str(ss_dir / filename)

    # ---------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------

    def _normalize_steps(self, steps: list) -> list[dict]:
        """Normalize steps to unified dict format.

        Accepts both string ("打开登录页") and dict ({"action": "click", "text": "登录"}).
        """
        result = []
        for s in steps:
            if isinstance(s, str):
                result.append({
                    "action": "click",
                    "text": s,
                    "description": s,
                })
            elif isinstance(s, dict):
                result.append(s)
        return result

    def _make_test_name(self, raw: str) -> str:
        """Generate a valid Python function name from a test title."""
        import re
        name = re.sub(r"[^\w]+", "_", raw).strip("_").lower()
        if not name:
            name = "test_case"
        if not name.startswith("test_"):
            name = f"test_{name}"
        return name

    async def _resolve_project_url(self, project_id: str) -> str:
        """Read target_url from project management module."""
        try:
            from infra.storage_factory import StorageFactory
            from qwenpaw.constant import WORKING_DIR
            store = StorageFactory(str(WORKING_DIR)).create_project_store()
            project = await store.get(project_id)
            if project and project.target_url:
                return project.target_url
        except Exception as e:
            logger.warning("Failed to resolve project URL for %s: %s", project_id, e)
        return ""

    def _extract_code_block(self, text: str) -> str:
        """Extract Python code from LLM response (may contain markdown fences)."""
        if not text:
            return ""
        if "```python" in text:
            parts = text.split("```python", 1)
            if len(parts) > 1:
                code = parts[1].split("```", 1)[0]
                return code.strip()
        if "```" in text:
            parts = text.split("```", 1)
            if len(parts) > 1:
                code = parts[1].split("```", 1)[0]
                return code.strip()
        if "def test_" in text:
            return text.strip()
        return ""
