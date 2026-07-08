# -*- coding: utf-8 -*-
"""Iteration snapshot management."""

import json
import logging
import shutil
from pathlib import Path
from datetime import datetime

from .paths import get_iteration_dir, get_snapshot_dir
from common.trace_id import generate_snapshot_id

logger = logging.getLogger(__name__)


def create_snapshot(workspace_dir: Path, iteration_id: str) -> dict:
    """Create a full snapshot of an iteration's current state."""
    snap_id = generate_snapshot_id()
    it_dir = get_iteration_dir(workspace_dir, iteration_id)
    if not it_dir.exists():
        return {"error": "Iteration not found"}

    snap_dir = get_snapshot_dir(workspace_dir, iteration_id)
    target = snap_dir / snap_id
    target.mkdir(parents=True, exist_ok=True)

    for sub in ["prd", "story", "case", "ui_script"]:
        src = it_dir / sub
        if src.exists():
            shutil.copytree(src, target / sub, dirs_exist_ok=True)

    manifest = {
        "snapshot_id": snap_id,
        "iteration_id": iteration_id,
        "created_at": datetime.utcnow().isoformat(),
        "contents": [d.name for d in target.iterdir() if d.is_dir()],
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    logger.info("Created snapshot %s for iteration %s", snap_id, iteration_id)
    return manifest


def restore_snapshot(workspace_dir: Path, iteration_id: str, snapshot_id: str) -> dict:
    """Restore an iteration from a snapshot."""
    snap_dir = get_snapshot_dir(workspace_dir, iteration_id)
    src = snap_dir / snapshot_id
    if not src.exists():
        return {"error": "Snapshot not found"}

    it_dir = get_iteration_dir(workspace_dir, iteration_id)
    for sub in ["prd", "story", "case", "ui_script"]:
        s = src / sub
        if s.exists():
            d = it_dir / sub
            if d.exists():
                shutil.rmtree(d)
            shutil.copytree(s, d)

    manifest = json.loads((src / "manifest.json").read_text()) if (src / "manifest.json").exists() else {}
    logger.info("Restored snapshot %s to iteration %s", snapshot_id, iteration_id)
    return manifest


def list_snapshots(workspace_dir: Path, iteration_id: str) -> list[dict]:
    """List all snapshots for an iteration."""
    snap_dir = get_snapshot_dir(workspace_dir, iteration_id)
    if not snap_dir.exists():
        return []
    results = []
    for d in sorted(snap_dir.iterdir(), reverse=True):
        if d.is_dir():
            mf = d / "manifest.json"
            if mf.exists():
                results.append(json.loads(mf.read_text()))
    return results
