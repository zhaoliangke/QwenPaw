# -*- coding: utf-8 -*-
"""Iteration storage layer using JSON file-based persistence.

Stores iteration metadata at {workspace}/test/iteration/{id}/iteration.json.
Reuses the platform's native file I/O utilities.
"""

import logging
from pathlib import Path

from common.utils import read_json_file, write_json_file, list_json_files
from models.iteration import Iteration, IterationStatus
from common.trace_id import generate_iteration_id
from .paths import get_iteration_dir, get_story_dir, get_case_dir, get_script_dir, get_exec_log_dir, get_report_dir

logger = logging.getLogger(__name__)


class IterationStore:
    """Persistent storage for iteration metadata using JSON files."""

    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir

    def _get_iteration_file(self, iteration_id: str) -> Path:
        return get_iteration_dir(self._workspace_dir, iteration_id) / "iteration.json"

    def _ensure_dir(self, iteration_id: str):
        d = get_iteration_dir(self._workspace_dir, iteration_id)
        d.mkdir(parents=True, exist_ok=True)

    def create(self, iteration: Iteration) -> Iteration:
        if not iteration.id:
            iteration.id = generate_iteration_id()
        self._ensure_dir(iteration.id)
        write_json_file(self._get_iteration_file(iteration.id), iteration.model_dump())
        logger.info("Created iteration %s", iteration.id)
        return iteration

    def get(self, iteration_id: str) -> Iteration | None:
        data = read_json_file(self._get_iteration_file(iteration_id))
        if not data:
            return None
        return Iteration(**data)

    def list_all(self) -> list[Iteration]:
        root = Path(self._workspace_dir) / "test" / "iteration"
        if not root.exists():
            return []
        result = []
        for d in sorted(root.iterdir()):
            if d.is_dir():
                f = d / "iteration.json"
                if f.exists():
                    data = read_json_file(f)
                    if data:
                        result.append(Iteration(**data))
        return result

    def list_by_status(self, status: IterationStatus | None = None) -> list[Iteration]:
        all_items = self.list_all()
        if status is None:
            return all_items
        return [it for it in all_items if it.status == status]

    def update(self, iteration: Iteration) -> Iteration:
        self._ensure_dir(iteration.id)
        write_json_file(self._get_iteration_file(iteration.id), iteration.model_dump())
        return iteration

    def update_status(self, iteration_id: str, new_status: IterationStatus) -> Iteration | None:
        it = self.get(iteration_id)
        if it is None:
            return None
        it.status = new_status
        return self.update(it)

    def delete(self, iteration_id: str) -> bool:
        f = self._get_iteration_file(iteration_id)
        if f.exists():
            f.unlink()
            return True
        return False

    def exists(self, iteration_id: str) -> bool:
        return self._get_iteration_file(iteration_id).exists()
