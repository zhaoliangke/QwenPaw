# -*- coding: utf-8 -*-
"""Common utilities for the test platform extension."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def read_json_file(path: Path) -> dict[str, Any]:
    """Read a JSON file and return its contents.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON content as a dictionary. Returns empty dict if
        the file does not exist.

    Raises:
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _json_default_serializer(obj: Any) -> str:
    """Custom JSON serializer that converts datetime to ISO format."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def write_json_file(path: Path, data: dict[str, Any]) -> None:
    """Write data to a JSON file atomically.

    Args:
        path: Destination file path.
        data: Dictionary to serialize as JSON.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=_json_default_serializer),
        encoding="utf-8",
    )
    tmp_path.replace(path)


def list_json_files(directory: Path) -> list[Path]:
    """List all JSON files in a directory.

    Args:
        directory: Directory to scan.

    Returns:
        Sorted list of JSON file paths.
    """
    if not directory.exists():
        return []
    return sorted(directory.glob("*.json"))
