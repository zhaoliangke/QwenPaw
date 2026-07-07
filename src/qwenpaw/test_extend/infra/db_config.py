# -*- coding: utf-8 -*-
"""Database configuration for the AI Test Platform.

Supports dual-mode storage:
  - file (default): JSON file-based, portable, no external dependencies
  - mysql: SQLAlchemy async MySQL, for production deployments

Switch via environment variable TEST_PLATFORM_DB_BACKEND=mysql.
"""

import os
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    """Connection configuration for the test platform database backend."""

    backend: str = "file"

    mysql_host: str = field(default_factory=lambda: os.getenv("TEST_PLATFORM_MYSQL_HOST", "127.0.0.1"))
    mysql_port: int = field(default_factory=lambda: int(os.getenv("TEST_PLATFORM_MYSQL_PORT", "3306")))
    mysql_user: str = field(default_factory=lambda: os.getenv("TEST_PLATFORM_MYSQL_USER", "root"))
    mysql_password: str = field(default_factory=lambda: os.getenv("TEST_PLATFORM_MYSQL_PASSWORD", ""))
    mysql_database: str = field(default_factory=lambda: os.getenv("TEST_PLATFORM_MYSQL_DATABASE", "test_platform"))
    mysql_pool_size: int = field(default_factory=lambda: int(os.getenv("TEST_PLATFORM_MYSQL_POOL_SIZE", "10")))
    mysql_pool_recycle: int = 3600

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            f"?charset=utf8mb4"
        )

    @property
    def is_mysql(self) -> bool:
        return self.backend == "mysql"

    @property
    def is_file(self) -> bool:
        return self.backend == "file"


_db_config: DatabaseConfig | None = None


def get_db_config() -> DatabaseConfig:
    global _db_config
    if _db_config is None:
        backend = os.getenv("TEST_PLATFORM_DB_BACKEND", "file")
        _db_config = DatabaseConfig(backend=backend)
    return _db_config
