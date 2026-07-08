# -*- coding: utf-8 -*-
"""Data masking MCP tools."""

import logging

from common.data_masking import detect_sensitive_fields, mask_any, mask_string

logger = logging.getLogger(__name__)


async def mask_data_tool(data: dict | list | str, enabled_types: list[str] | None = None) -> dict:
    types = set(enabled_types) if enabled_types else None
    return {"masked": mask_any(data, types)}


async def mask_string_tool(text: str, enabled_types: list[str] | None = None) -> dict:
    types = set(enabled_types) if enabled_types else None
    return {"masked": mask_string(text, types)}


async def detect_sensitive_tool(data: dict) -> dict:
    findings = detect_sensitive_fields(data) if isinstance(data, dict) else []
    return {"findings": findings, "count": len(findings)}
