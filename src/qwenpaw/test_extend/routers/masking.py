# -*- coding: utf-8 -*-
"""Data masking API router."""

import logging
from typing import Any

from fastapi import APIRouter

from common.data_masking import (
    detect_sensitive_fields,
    mask_any,
    mask_dict,
    mask_string,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/masking", tags=["masking"])


@router.post("/mask")
async def mask_data(body: dict[str, Any]) -> dict[str, Any]:
    """Apply masking to arbitrary data."""
    data = body.get("data")
    enabled_types = set(body.get("enabled_types", [])) if body.get("enabled_types") else None
    masked = mask_any(data, enabled_types)
    return {"masked": masked}


@router.post("/mask_string")
async def mask_string_endpoint(body: dict[str, Any]) -> dict[str, Any]:
    """Apply masking to a plain string."""
    text = body.get("text", "")
    enabled_types = set(body.get("enabled_types", [])) if body.get("enabled_types") else None
    return {"masked": mask_string(text, enabled_types)}


@router.post("/detect")
async def detect_sensitive(body: dict[str, Any]) -> dict[str, Any]:
    """Detect sensitive fields in data without masking."""
    data = body.get("data", {})
    if isinstance(data, dict):
        findings = detect_sensitive_fields(data)
    else:
        findings = []
    return {"findings": findings, "count": len(findings)}
