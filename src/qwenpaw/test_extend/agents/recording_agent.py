# -*- coding: utf-8 -*-
"""Video recording agent — manages Playwright trace recording.

Uses Playwright's built-in tracing to capture execution traces
(.zip) that can be viewed in Playwright Trace Viewer or converted
to video format. This agent coordinates recording lifecycle and
embeds results into test reports.
"""

import json
import logging
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from common.utils import read_json_file, write_json_file
from common.trace_id import generate_trace_id
from models.recording import RecordingStatus, VideoRecording
from storage.paths import get_recording_dir

logger = logging.getLogger(__name__)


class RecordingAgent:
    def __init__(self, workspace_dir: str | Path):
        self._workspace = Path(workspace_dir)
        self._recording_dir = get_recording_dir(self._workspace)
        self._recording_dir.mkdir(parents=True, exist_ok=True)

    def start_recording(
        self,
        case_id: str = "",
        run_id: str = "",
        iteration_id: str = "",
        script_id: str = "",
    ) -> VideoRecording:
        rec = VideoRecording(
            id=generate_trace_id("VR"),
            case_id=case_id,
            run_id=run_id,
            iteration_id=iteration_id,
            script_id=script_id,
            status=RecordingStatus.RECORDING,
        )
        rec_dir = self._recording_dir / rec.id
        rec_dir.mkdir(parents=True, exist_ok=True)
        rec.trace_path = str(rec_dir / "trace.zip")
        rec.video_path = str(rec_dir / "video.webm")
        self._save_recording(rec)
        return rec

    def stop_recording(self, rec_id: str, success: bool = True, error: str = "") -> VideoRecording | None:
        rec = self.get_recording(rec_id)
        if not rec:
            return None
        rec.status = RecordingStatus.COMPLETED if success else RecordingStatus.FAILED
        rec.error = error
        rec.duration_ms = int((datetime.utcnow() - rec.created_at).total_seconds() * 1000)

        # Check actual file sizes
        trace_path = Path(rec.trace_path)
        if trace_path.exists():
            rec.file_size_bytes = trace_path.stat().st_size

        self._save_recording(rec)
        return rec

    def get_recording(self, rec_id: str) -> VideoRecording | None:
        f = self._recording_dir / f"{rec_id}.json"
        if f.exists():
            data = read_json_file(f)
            return VideoRecording(**data) if data else None
        return None

    def list_recordings(self, run_id: str = "", case_id: str = "") -> list[VideoRecording]:
        results = []
        for f in sorted(self._recording_dir.glob("*.json")):
            data = read_json_file(f)
            if data:
                rec = VideoRecording(**data)
                if (not run_id or rec.run_id == run_id) and (not case_id or rec.case_id == case_id):
                    results.append(rec)
        return results

    def get_trace_viewer_url(self, rec_id: str) -> str:
        """Return the Playwright Trace Viewer URL for a recording."""
        rec = self.get_recording(rec_id)
        if not rec:
            return ""
        return f"https://trace.playwright.dev/?trace={rec.trace_path}"

    def generate_report_snippet(self, rec_id: str) -> dict[str, Any]:
        """Generate embeddable report data for a recording."""
        rec = self.get_recording(rec_id)
        if not rec:
            return {"error": "Recording not found"}
        return {
            "recording_id": rec.id,
            "trace_url": self.get_trace_viewer_url(rec_id),
            "video_url": f"/api/test/recording/{rec.id}/video" if rec.video_path else "",
            "duration_ms": rec.duration_ms,
            "status": rec.status.value,
            "file_size_kb": rec.file_size_bytes // 1024,
        }

    def get_playwright_trace_config(self, rec_id: str) -> dict[str, Any]:
        """Return Playwright browser context config for tracing."""
        rec = self.get_recording(rec_id)
        if not rec:
            return {}
        return {
            "trace": rec.trace_path,
            "screenshots": True,
            "snapshots": True,
        }

    def _save_recording(self, rec: VideoRecording):
        f = self._recording_dir / f"{rec.id}.json"
        write_json_file(f, rec.model_dump())
