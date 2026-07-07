# -*- coding: utf-8 -*-
"""Test asset archiver for knowledge base integration."""

import json
import logging
import shutil
from pathlib import Path
from datetime import datetime

from .paths import get_iteration_dir, get_knowledge_docs_dir

logger = logging.getLogger(__name__)


def archive_iteration(workspace_dir: Path, iteration_id: str) -> dict:
    """Copy all iteration assets to the knowledge base for long-term storage."""
    it_dir = get_iteration_dir(workspace_dir, iteration_id)
    kb_dir = get_knowledge_docs_dir(workspace_dir)
    kb_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for sub in ["story", "case", "report", "ui_script"]:
        src = it_dir / sub
        if src.exists() and src.is_dir():
            for f in src.glob("*"):
                if f.is_file():
                    dest = kb_dir / f"{iteration_id}_{sub}_{f.name}"
                    shutil.copy2(f, dest)
                    count += 1

    manifest = {
        "iteration_id": iteration_id,
        "archived_at": datetime.utcnow().isoformat(),
        "file_count": count,
    }
    (kb_dir / f"archive_{iteration_id}.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
    )
    logger.info("Archived %d files from iteration %s", count, iteration_id)
    return manifest
