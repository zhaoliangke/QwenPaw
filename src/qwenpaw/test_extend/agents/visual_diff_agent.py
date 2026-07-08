# -*- coding: utf-8 -*-
"""Visual regression agent — screenshot capture + pixel-level diff.

Uses Playwright for screenshot capture and Pillow (if available)
for pixel comparison. Falls back to file-hash comparison when
Pillow is not installed.
"""

import asyncio
import hashlib
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from common.utils import read_json_file, write_json_file
from common.trace_id import generate_trace_id
from models.visual_diff import (
    DiffRegion,
    DiffStatus,
    VisualDiffResult,
    VisualDiffTest,
)
from storage.paths import get_visual_diff_dir

logger = logging.getLogger(__name__)


class VisualDiffAgent:
    def __init__(self, workspace_dir: str | Path):
        self._workspace = Path(workspace_dir)
        self._diff_dir = get_visual_diff_dir(self._workspace)
        self._diff_dir.mkdir(parents=True, exist_ok=True)
        self._has_pillow = self._check_pillow()

    def _check_pillow(self) -> bool:
        try:
            from PIL import Image, ImageChops
            return True
        except ImportError:
            logger.debug("Pillow not installed, using hash-based comparison")
            return False

    async def run_test(self, test: VisualDiffTest, run_id: str = "") -> VisualDiffResult:
        result = VisualDiffResult(test_id=test.id, run_id=run_id)
        test_dir = self._diff_dir / test.id
        test_dir.mkdir(parents=True, exist_ok=True)

        baseline_path = test_dir / "baseline.png"
        current_path = test_dir / f"current_{result.id}.png"
        diff_path = test_dir / f"diff_{result.id}.png"

        result.baseline_path = str(baseline_path)
        result.current_path = str(current_path)
        result.diff_path = str(diff_path)

        if not test.url:
            result.status = DiffStatus.ERROR
            result.error = "No URL specified"
            return result

        try:
            screenshot_ok = await self._capture_screenshot(test.url, current_path, test.viewport_width, test.viewport_height, test.wait_time_ms)
            if not screenshot_ok:
                result.status = DiffStatus.ERROR
                result.error = "Failed to capture screenshot"
                return result

            if not baseline_path.exists():
                import shutil
                shutil.copy2(current_path, baseline_path)
                result.status = DiffStatus.BASELINE_MISSING
                result.current_path = str(current_path)
                result.baseline_path = str(baseline_path)
                return result

            if self._has_pillow:
                diff_pct, diff_pixels, regions = self._pixel_diff(baseline_path, current_path, diff_path, test.threshold)
            else:
                diff_pct, diff_pixels, regions = self._hash_diff(baseline_path, current_path)

            result.diff_percentage = diff_pct
            result.diff_pixel_count = diff_pixels
            result.diff_regions = regions
            result.status = DiffStatus.MATCH if diff_pct <= test.threshold else DiffStatus.DIFFERENT

        except Exception as e:
            result.status = DiffStatus.ERROR
            result.error = str(e)[:300]

        result.executed_at = datetime.utcnow()
        self._save_result(result)
        return result

    async def _capture_screenshot(self, url: str, output_path: Path, width: int, height: int, wait_ms: int) -> bool:
        try:
            script = (
                "from playwright.sync_api import sync_playwright\n"
                "with sync_playwright() as p:\n"
                f"    browser = p.chromium.launch()\n"
                f"    page = browser.new_page(viewport={{'width': {width}, 'height': {height}}})\n"
                f"    page.goto('{url}', wait_until='networkidle')\n"
                f"    page.wait_for_timeout({wait_ms})\n"
                f"    page.screenshot(path='{output_path}', full_page=True)\n"
                f"    browser.close()\n"
            )
            proc = subprocess.run(
                ["python", "-c", script],
                capture_output=True, text=True, timeout=60,
                cwd=str(self._workspace),
            )
            return proc.returncode == 0 and output_path.exists()
        except Exception as e:
            logger.error("Screenshot capture failed: %s", e)
            return False

    def _pixel_diff(self, baseline_path: Path, current_path: Path, diff_path: Path, threshold: float) -> tuple[float, int, list[DiffRegion]]:
        from PIL import Image, ImageChops, ImageDraw

        baseline = Image.open(baseline_path).convert("RGB")
        current = Image.open(current_path).convert("RGB")

        if baseline.size != current.size:
            current = current.resize(baseline.size)

        diff = ImageChops.difference(baseline, current)
        diff_gray = diff.convert("L")

        pixels = list(diff_gray.getdata())
        total_pixels = len(pixels)
        diff_pixels = sum(1 for p in pixels if p > 30)
        diff_percentage = diff_pixels / total_pixels if total_pixels > 0 else 0

        regions = []
        if diff_percentage > threshold:
            diff_colored = diff_gray.point(lambda x: 255 if x > 30 else 0)
            diff_colored.save(diff_path)

            bbox = diff_colored.getbbox()
            if bbox:
                regions.append(DiffRegion(
                    x=bbox[0], y=bbox[1],
                    width=bbox[2] - bbox[0], height=bbox[3] - bbox[1],
                    diff_percentage=diff_percentage,
                ))

        return diff_percentage, diff_pixels, regions

    def _hash_diff(self, baseline_path: Path, current_path: Path) -> tuple[float, int, list[DiffRegion]]:
        baseline_hash = self._file_hash(baseline_path)
        current_hash = self._file_hash(current_path)
        if baseline_hash == current_hash:
            return 0.0, 0, []
        return 1.0, 0, [DiffRegion(x=0, y=0, width=0, height=0, diff_percentage=1.0)]

    def _file_hash(self, path: Path) -> str:
        return hashlib.md5(path.read_bytes()).hexdigest()

    def update_baseline(self, test_id: str) -> bool:
        test_dir = self._diff_dir / test_id
        if not test_dir.exists():
            return False
        currents = sorted(test_dir.glob("current_*.png"))
        if not currents:
            return False
        import shutil
        shutil.copy2(currents[-1], test_dir / "baseline.png")
        return True

    def list_results(self, test_id: str = "") -> list[VisualDiffResult]:
        results = []
        for f in sorted(self._diff_dir.glob("*/result_*.json")):
            data = read_json_file(f)
            if data:
                r = VisualDiffResult(**data)
                if not test_id or r.test_id == test_id:
                    results.append(r)
        return results

    def _save_result(self, result: VisualDiffResult):
        f = self._diff_dir / result.test_id / f"result_{result.id}.json"
        write_json_file(f, result.model_dump())
