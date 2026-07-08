# -*- coding: utf-8 -*-
"""Case version tracker — snapshot, diff, and rollback."""

import copy
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from common.utils import read_json_file, write_json_file
from common.trace_id import generate_trace_id
from models.case_version import (
    CaseDiff,
    CaseVersion,
    ChangeType,
    FieldChange,
)
from storage.paths import get_case_version_dir

logger = logging.getLogger(__name__)

_COMPARED_FIELDS = {"name", "description", "steps", "expected_result", "priority", "tags", "module", "assertions", "url", "method", "body", "headers"}


class CaseVersionTracker:
    def __init__(self, workspace_dir: str | Path):
        self._workspace = Path(workspace_dir)
        self._version_dir = get_case_version_dir(self._workspace)
        self._version_dir.mkdir(parents=True, exist_ok=True)

    def create_version(
        self,
        case_id: str,
        case_data: dict[str, Any],
        change_type: ChangeType = ChangeType.UPDATED,
        comment: str = "",
        created_by: str = "",
        previous_data: dict[str, Any] | None = None,
    ) -> CaseVersion:
        versions = self.list_versions(case_id)
        max_ver = max((v.version for v in versions), default=0)
        new_version = max_ver + 1

        changes = []
        if previous_data:
            changes = self._compute_changes(previous_data, case_data)

        version = CaseVersion(
            id=generate_trace_id("CV"),
            case_id=case_id,
            version=new_version,
            case_data=copy.deepcopy(case_data),
            change_type=change_type,
            changes=changes,
            comment=comment,
            created_by=created_by,
        )

        self._save_version(version)
        return version

    def list_versions(self, case_id: str) -> list[CaseVersion]:
        results = []
        for f in sorted(self._version_dir.glob(f"{case_id}_v*.json")):
            data = read_json_file(f)
            if data:
                results.append(CaseVersion(**data))
        return results

    def get_version(self, case_id: str, version: int) -> CaseVersion | None:
        f = self._version_dir / f"{case_id}_v{version}.json"
        if f.exists():
            data = read_json_file(f)
            return CaseVersion(**data) if data else None
        return None

    def get_latest_version(self, case_id: str) -> CaseVersion | None:
        versions = self.list_versions(case_id)
        return versions[-1] if versions else None

    def diff_versions(self, case_id: str, from_ver: int, to_ver: int) -> CaseDiff:
        v1 = self.get_version(case_id, from_ver)
        v2 = self.get_version(case_id, to_ver)
        if not v1 or not v2:
            return CaseDiff(case_id=case_id, from_version=from_ver, to_version=to_ver)

        changes = self._compute_changes(v1.case_data, v2.case_data)
        return CaseDiff(
            case_id=case_id,
            from_version=from_ver,
            to_version=to_ver,
            changes=changes,
            has_differences=len(changes) > 0,
        )

    def rollback(self, case_id: str, version: int, comment: str = "") -> CaseVersion | None:
        target = self.get_version(case_id, version)
        if not target:
            return None
        return self.create_version(
            case_id=case_id,
            case_data=target.case_data,
            change_type=ChangeType.ROLLED_BACK,
            comment=comment or f"Rolled back to v{version}",
        )

    def _compute_changes(self, old: dict, new: dict) -> list[FieldChange]:
        changes = []
        keys = _COMPARED_FIELDS & (set(old.keys()) | set(new.keys()))
        for key in sorted(keys):
            old_val = old.get(key)
            new_val = new.get(key)
            if old_val != new_val:
                changes.append(FieldChange(field=key, old_value=old_val, new_value=new_val))
        return changes

    def _save_version(self, version: CaseVersion):
        f = self._version_dir / f"{version.case_id}_v{version.version}.json"
        write_json_file(f, version.model_dump())
