# -*- coding: utf-8 -*-
"""Test Platform storage path helpers.

All test assets are stored under {workspace_dir}/test/ within the
platform's native working directory. This module provides path
resolution utilities that leverage QwenPaw's existing file I/O
and workspace conventions.
"""

from pathlib import Path


def get_test_root(workspace_dir: Path) -> Path:
    """Return the root directory for all test platform assets.

    Args:
        workspace_dir: The per-agent workspace directory, typically
            {WORKING_DIR}/workspaces/{agent_id}/.

    Returns:
        Path to the test/ directory within the workspace.
    """
    return workspace_dir / "test"


def get_iteration_dir(workspace_dir: Path, iteration_id: str) -> Path:
    """Return the directory for a specific iteration's assets.

    Args:
        workspace_dir: Per-agent workspace directory.
        iteration_id: Unique iteration identifier.

    Returns:
        Path: {workspace}/test/iteration/{iteration_id}/
    """
    return get_test_root(workspace_dir) / "iteration" / str(iteration_id)


def get_prd_dir(workspace_dir: Path, iteration_id: str) -> Path:
    """Return the directory where uploaded PRD documents are stored."""
    return get_iteration_dir(workspace_dir, iteration_id) / "prd"


def get_story_dir(workspace_dir: Path, iteration_id: str) -> Path:
    """Return the directory where Story JSON files are stored."""
    return get_iteration_dir(workspace_dir, iteration_id) / "story"


def get_case_dir(workspace_dir: Path, iteration_id: str) -> Path:
    """Return the directory where test case files are stored."""
    return get_iteration_dir(workspace_dir, iteration_id) / "case"


def get_script_dir(workspace_dir: Path, iteration_id: str) -> Path:
    """Return the directory where Playwright automation scripts are stored."""
    return get_iteration_dir(workspace_dir, iteration_id) / "ui_script"


def get_exec_log_dir(workspace_dir: Path, iteration_id: str) -> Path:
    """Return the directory for execution logs, screenshots, and recordings."""
    return get_iteration_dir(workspace_dir, iteration_id) / "exec_log"


def get_report_dir(workspace_dir: Path, iteration_id: str) -> Path:
    """Return the directory where HTML test reports are stored."""
    return get_iteration_dir(workspace_dir, iteration_id) / "report"


def get_snapshot_dir(workspace_dir: Path, iteration_id: str) -> Path:
    """Return the directory for iteration baseline snapshots."""
    return get_iteration_dir(workspace_dir, iteration_id) / "snapshot"


def get_knowledge_dir(workspace_dir: Path) -> Path:
    """Return the root directory for the test knowledge base."""
    return get_test_root(workspace_dir) / "knowledge"


def get_knowledge_docs_dir(workspace_dir: Path) -> Path:
    """Return the directory for archived knowledge documents."""
    return get_knowledge_dir(workspace_dir) / "docs"


def get_vector_store_dir(workspace_dir: Path) -> Path:
    """Return the directory for the test-specific vector store collection.

    This path is used as a logical marker; the actual vector storage is
    managed by the platform's ReMe RAG system with a dedicated collection.
    """
    return get_knowledge_dir(workspace_dir) / "vector_store"


def ensure_test_directories(workspace_dir: Path):
    """Create all required test platform directories under the workspace.

    Args:
        workspace_dir: Per-agent workspace directory.

    Note:
        This is called during the plugin startup hook to ensure the
        directory structure exists before any operations.
    """
    dirs = [
        get_test_root(workspace_dir),
        get_knowledge_dir(workspace_dir),
        get_knowledge_docs_dir(workspace_dir),
        get_vector_store_dir(workspace_dir),
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
