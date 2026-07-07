# -*- coding: utf-8 -*-
"""Iteration Agent - manages test iteration lifecycle.

Inherits from TestBaseAgent, registered via MultiAgentManager.
Handles iteration CRUD, snapshots, diff comparison, and Jira sync.
"""

import json
import logging
from pathlib import Path
from datetime import datetime

from ..storage.iteration_store import IterationStore
from ..storage.paths import get_iteration_dir, get_story_dir, get_case_dir
from ..models.iteration import Iteration, IterationStatus
from ..common.trace_id import generate_iteration_id, generate_snapshot_id

logger = logging.getLogger(__name__)


class IterationAgent:
    """Agent responsible for test iteration lifecycle management.

    Note: This agent is not directly instantiated but registered as a
    handler that operates within the QwenPaw MultiAgentManager framework.
    """

    def __init__(self, workspace_dir: Path):
        self._workspace_dir = workspace_dir
        self._store = IterationStore(workspace_dir)

    @property
    def store(self) -> IterationStore:
        return self._store

    async def create_iteration(
        self,
        name: str,
        version: str,
        module: str,
        start_date: str,
        end_date: str,
        description: str | None = None,
        git_branch: str | None = None,
        test_environment: str | None = None,
    ) -> dict:
        it = Iteration(
            id=generate_iteration_id(),
            name=name,
            version=version,
            module=module,
            description=description,
            start_date=start_date,
            end_date=end_date,
            git_branch=git_branch,
            test_environment=test_environment,
        )
        self._store.create(it)
        return it.model_dump()

    async def get_iteration(self, iteration_id: str) -> dict | None:
        it = self._store.get(iteration_id)
        return it.model_dump() if it else None

    async def list_iterations(self, status: str | None = None) -> list[dict]:
        st = IterationStatus(status) if status else None
        items = self._store.list_by_status(st)
        return [it.model_dump() for it in items]

    async def update_iteration_status(self, iteration_id: str, new_status: str) -> dict | None:
        st = IterationStatus(new_status)
        it = self._store.update_status(iteration_id, st)
        return it.model_dump() if it else None

    async def create_snapshot(self, iteration_id: str) -> dict:
        import shutil
        import tempfile
        from datetime import datetime as dt

        snap_id = generate_snapshot_id()
        it_dir = get_iteration_dir(self._workspace_dir, iteration_id)
        snap_dir = it_dir / "snapshot" / snap_id
        snap_dir.mkdir(parents=True, exist_ok=True)

        for sub in ["prd", "story", "case"]:
            src = it_dir / sub
            if src.exists():
                dst = snap_dir / sub
                shutil.copytree(src, dst, dirs_exist_ok=True)

        manifest = {
            "snapshot_id": snap_id,
            "iteration_id": iteration_id,
            "created_at": dt.utcnow().isoformat(),
        }
        (snap_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

        logger.info("Created snapshot %s for iteration %s", snap_id, iteration_id)
        return manifest

    async def diff_iterations(self, id_a: str, id_b: str) -> dict:
        it_a = self._store.get(id_a)
        it_b = self._store.get(id_b)
        if not it_a or not it_b:
            return {"error": "One or both iterations not found"}

        stories_a = set()
        stories_b = set()
        for it_id, path in [(id_a, get_story_dir(self._workspace_dir, id_a)),
                             (id_b, get_story_dir(self._workspace_dir, id_b))]:
            if path.exists():
                for f in path.glob("*.json"):
                    data = json.loads(f.read_text())
                    tid = data.get("traceability_id", f.stem)
                    if it_id == id_a:
                        stories_a.add(tid)
                    else:
                        stories_b.add(tid)

        return {
            "iteration_a": it_a.name,
            "iteration_b": it_b.name,
            "added": sorted(stories_b - stories_a),
            "removed": sorted(stories_a - stories_b),
            "unchanged": sorted(stories_a & stories_b),
        }
