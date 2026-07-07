# -*- coding: utf-8 -*-
"""Test Platform traceability ID generator.

Generates unique, traceable identifiers that link requirements,
stories, test cases, and defects across the full development pipeline.
"""

import uuid
from datetime import datetime, timezone


def generate_trace_id(prefix: str = "TP") -> str:
    """Generate a unique traceability ID for a test asset.

    Format: {prefix}-{timestamp}-{short_uuid}

    Args:
        prefix: Two-letter prefix indicating the asset type.
            Common values: "TP" (Test Platform), "IT" (Iteration),
            "ST" (Story), "TC" (TestCase), "DF" (Defect).

    Returns:
        A unique traceability ID string, e.g. "TP-20260707-a1b2c3d4".

    Raises:
        ValueError: If prefix is not a non-empty string.
    """
    if not prefix or not isinstance(prefix, str):
        raise ValueError("prefix must be a non-empty string")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:8]
    return f"{prefix}-{ts}-{suffix}"


def generate_iteration_id() -> str:
    """Generate a unique iteration identifier."""
    return generate_trace_id("IT")


def generate_story_id() -> str:
    """Generate a unique story identifier."""
    return generate_trace_id("ST")


def generate_case_id() -> str:
    """Generate a unique test case identifier."""
    return generate_trace_id("TC")


def generate_report_id() -> str:
    """Generate a unique report identifier."""
    return generate_trace_id("RP")


def generate_run_id() -> str:
    """Generate a unique test run identifier."""
    return generate_trace_id("TR")


def generate_snapshot_id() -> str:
    """Generate a unique snapshot identifier."""
    return generate_trace_id("SN")
