# -*- coding: utf-8 -*-
"""Test Platform Storage Management.

Exports:
  - BaseStore: Abstract interface for all domain stores.
  - StorageFactory: Creates domain stores based on backend config.
  - paths: Test asset path utilities.
  - snapshot: Iteration snapshot management.
  - asset_archiver: Asset archive utilities.
  - iteration_store: Legacy file-only store (backward compat).
  - file_stores: New async file-based stores.
  - mysql_stores: New async MySQL-based stores.
"""

from .base_store import BaseStore
from infra.storage_factory import StorageFactory

__all__ = [
    "BaseStore",
    "StorageFactory",
]
