# -*- coding: utf-8 -*-
"""Video recording models for Playwright trace capture."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from common.trace_id import generate_trace_id


class RecordingStatus(str, Enum):
    RECORDING = "recording"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoRecording(BaseModel):
    id: str = Field(default_factory=lambda: generate_trace_id("VR"))
    case_id: str = ""
    run_id: str = ""
    iteration_id: str = ""
    script_id: str = ""
    status: RecordingStatus = RecordingStatus.RECORDING
    trace_path: str = ""
    video_path: str = ""
    duration_ms: int = 0
    width: int = 1280
    height: int = 720
    file_size_bytes: int = 0
    error: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
