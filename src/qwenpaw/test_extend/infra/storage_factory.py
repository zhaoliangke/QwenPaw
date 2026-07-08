# -*- coding: utf-8 -*-
"""Dual-mode storage factory.

Creates domain stores (File or MySQL) based on the configured backend.
Domain stores share the same BaseStore interface defined in storage/base_store.py.
"""

import logging

logger = logging.getLogger(__name__)

__all__ = ["StorageFactory"]


class StorageFactory:
    """Creates domain stores based on the configured backend.

    Usage:
        factory = StorageFactory(workspace_dir="/path/to/workspace")
        iteration_store = factory.create_iteration_store()
        stories = await iteration_store.list_all(status="active")
    """

    def __init__(self, workspace_dir: str):
        self._workspace_dir = workspace_dir
        from .db_config import get_db_config
        self._db_config = get_db_config()

    @property
    def use_mysql(self) -> bool:
        return self._db_config.is_mysql

    def create_iteration_store(self):
        if self.use_mysql:
            from storage.mysql_stores import MySQLIterationStore
            return MySQLIterationStore()
        from storage.file_stores import FileIterationStore
        return FileIterationStore(self._workspace_dir)

    def create_story_store(self):
        if self.use_mysql:
            from storage.mysql_stores import MySQLStoryStore
            return MySQLStoryStore()
        from storage.file_stores import FileStoryStore
        return FileStoryStore(self._workspace_dir)

    def create_case_store(self):
        if self.use_mysql:
            from storage.mysql_stores import MySQLCaseStore
            return MySQLCaseStore()
        from storage.file_stores import FileCaseStore
        return FileCaseStore(self._workspace_dir)

    def create_project_store(self):
        if self.use_mysql:
            from storage.mysql_stores import MySQLProjectStore
            return MySQLProjectStore()
        from storage.file_stores import FileProjectStore
        return FileProjectStore(self._workspace_dir)

    def create_element_map_store(self):
        if self.use_mysql:
            from storage.mysql_stores import MySQLElementMapStore
            return MySQLElementMapStore()
        from storage.file_stores import FileElementMapStore
        return FileElementMapStore(self._workspace_dir)

    def create_test_run_store(self):
        if self.use_mysql:
            from storage.mysql_stores import MySQLTestRunStore
            return MySQLTestRunStore()
        from storage.file_stores import FileTestRunStore
        return FileTestRunStore(self._workspace_dir)

    def create_report_store(self):
        if self.use_mysql:
            from storage.mysql_stores import MySQLReportStore
            return MySQLReportStore()
        from storage.file_stores import FileReportStore
        return FileReportStore(self._workspace_dir)

    def create_trace_store(self):
        if self.use_mysql:
            from storage.mysql_stores import MySQLTraceStore
            return MySQLTraceStore()
        from storage.file_stores import FileTraceStore
        return FileTraceStore(self._workspace_dir)

    def create_knowledge_store(self):
        if self.use_mysql:
            from storage.mysql_stores import MySQLKnowledgeStore
            return MySQLKnowledgeStore()
        from storage.file_stores import FileKnowledgeStore
        return FileKnowledgeStore(self._workspace_dir)

    def create_workflow_store(self):
        """Create a workflow state store (file-based or MySQL)."""
        if self.use_mysql:
            try:
                from storage.mysql_stores import MySQLWorkflowStore
                return MySQLWorkflowStore()
            except ImportError:
                logger.warning("MySQLWorkflowStore not found, falling back to file-based")
        from storage.file_stores import FileWorkflowStore
        return FileWorkflowStore(self._workspace_dir)

