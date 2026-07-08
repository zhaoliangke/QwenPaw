# -*- coding: utf-8 -*-
"""Data masking engine — detect and mask sensitive information.

Identifies common sensitive fields (phone, email, ID card, bank card, etc.)
and applies configurable masking rules to protect data in test logs,
reports, and exported artifacts.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Built-in sensitive field patterns
_SENSITIVE_PATTERNS = {
    "phone": {
        "pattern": re.compile(r"1[3-9]\d{9}"),
        "mask": lambda m: m.group()[:3] + "****" + m.group()[7:],
    },
    "email": {
        "pattern": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
        "mask": lambda m: m.group()[0] + "***@" + m.group().split("@")[1],
    },
    "id_card": {
        "pattern": re.compile(r"\d{17}[\dXx]"),
        "mask": lambda m: m.group()[:4] + "**********" + m.group()[14:],
    },
    "bank_card": {
        "pattern": re.compile(r"\d{16,19}"),
        "mask": lambda m: m.group()[:4] + " **** **** " + m.group()[-4:],
    },
    "password": {
        "pattern": re.compile(r'(password|passwd|pwd|secret|token|api[_-]?key)\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE),
        "mask": lambda m: m.group(1) + "=" + "*" * 8,
    },
}

# Field name keywords that indicate sensitive data
_SENSITIVE_FIELD_NAMES = {
    "phone", "mobile", "tel", "telephone",
    "email", "mail",
    "idcard", "id_card", "identity", "id_number",
    "bankcard", "bank_card", "card_no",
    "password", "passwd", "pwd", "secret",
    "token", "api_key", "apikey", "access_token",
    "name", "realname", "real_name",
    "address", "addr",
}


def mask_string(text: str, enabled_types: set[str] | None = None) -> str:
    """Apply masking rules to a string."""
    if not text:
        return text
    result = text
    for name, rule in _SENSITIVE_PATTERNS.items():
        if enabled_types and name not in enabled_types:
            continue
        try:
            result = rule["pattern"].sub(rule["mask"], result)
        except Exception:
            pass
    return result


def mask_dict(data: dict, enabled_types: set[str] | None = None, depth: int = 0) -> dict:
    """Recursively mask sensitive fields in a dict."""
    if depth > 10:
        return data
    result = {}
    for key, value in data.items():
        if _is_sensitive_field(key) and isinstance(value, str):
            result[key] = _mask_value(value, key)
        elif isinstance(value, dict):
            result[key] = mask_dict(value, enabled_types, depth + 1)
        elif isinstance(value, list):
            result[key] = mask_list(value, enabled_types, depth + 1)
        elif isinstance(value, str):
            result[key] = mask_string(value, enabled_types)
        else:
            result[key] = value
    return result


def mask_list(data: list, enabled_types: set[str] | None = None, depth: int = 0) -> list:
    """Recursively mask sensitive fields in a list."""
    if depth > 10:
        return data
    result = []
    for item in data:
        if isinstance(item, dict):
            result.append(mask_dict(item, enabled_types, depth + 1))
        elif isinstance(item, list):
            result.append(mask_list(item, enabled_types, depth + 1))
        elif isinstance(item, str):
            result.append(mask_string(item, enabled_types))
        else:
            result.append(item)
    return result


def mask_any(data: Any, enabled_types: set[str] | None = None) -> Any:
    """Mask any data type."""
    if isinstance(data, str):
        return mask_string(data, enabled_types)
    if isinstance(data, dict):
        return mask_dict(data, enabled_types)
    if isinstance(data, list):
        return mask_list(data, enabled_types)
    return data


def _is_sensitive_field(field_name: str) -> bool:
    normalized = field_name.lower().replace("-", "_").replace(".", "_")
    return normalized in _SENSITIVE_FIELD_NAMES


def _mask_value(value: str, field_type: str) -> str:
    if not value or len(value) <= 2:
        return "*" * len(value)
    if "phone" in field_type or "mobile" in field_type:
        return value[:3] + "****" + value[7:] if len(value) >= 11 else "*" * len(value)
    if "email" in field_type:
        parts = value.split("@")
        return parts[0][0] + "***@" + parts[1] if len(parts) == 2 else "*" * len(value)
    if "id" in field_type and "card" in field_type:
        return value[:4] + "**********" + value[14:] if len(value) >= 18 else "*" * len(value)
    if "bank" in field_type:
        return value[:4] + " **** **** " + value[-4:] if len(value) >= 16 else "*" * len(value)
    if "name" in field_type:
        return value[0] + "*" * (len(value) - 1)
    return value[0] + "*" * (len(value) - 2) + value[-1] if len(value) > 2 else "*" * len(value)


def detect_sensitive_fields(data: dict, prefix: str = "") -> list[dict]:
    """Detect and report sensitive fields in data."""
    findings = []
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if _is_sensitive_field(key) and isinstance(value, str):
            findings.append({
                "field": full_key,
                "type": _classify_field(key),
                "sample": value[:3] + "..." if len(value) > 3 else "***",
            })
        elif isinstance(value, dict):
            findings.extend(detect_sensitive_fields(value, full_key))
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            findings.extend(detect_sensitive_fields(value[0], full_key))
    return findings


def _classify_field(field_name: str) -> str:
    normalized = field_name.lower()
    if any(k in normalized for k in ["phone", "mobile", "tel"]):
        return "phone"
    if "email" in normalized:
        return "email"
    if "id" in normalized and "card" in normalized:
        return "id_card"
    if "bank" in normalized:
        return "bank_card"
    if any(k in normalized for k in ["password", "passwd", "pwd", "secret"]):
        return "password"
    if any(k in normalized for k in ["token", "api_key", "apikey"]):
        return "token"
    if "name" in normalized:
        return "name"
    if "address" in normalized:
        return "address"
    return "sensitive"
