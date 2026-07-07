# -*- coding: utf-8 -*-
"""Async MySQL engine and session management for the test platform.

Uses aiomysql driver for full async support compatible with FastAPI.
Session lifecycle is managed via async context manager.
"""

import logging
from typing import TYPE_CHECKING, AsyncGenerator

try:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    AsyncSession = type("AsyncSession", (), {})

from .db_config import get_db_config
from .db_models import Base

logger = logging.getLogger(__name__)

_engine = None
_session_factory = None


async def init_mysql():
    """Initialize the MySQL engine and create all tables.

    Safe to call even if MySQL is not configured; it will be a no-op
    when the backend is 'file'.
    """
    global _engine, _session_factory
    cfg = get_db_config()
    if not cfg.is_mysql:
        logger.info("MySQL backend not enabled, skipping init")
        return

    _engine = create_async_engine(
        cfg.mysql_url,
        pool_size=cfg.mysql_pool_size,
        pool_recycle=cfg.mysql_pool_recycle,
        echo=False,
    )

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    logger.info("MySQL engine initialized: %s:%d/%s", cfg.mysql_host, cfg.mysql_port, cfg.mysql_database)


async def close_mysql():
    """Dispose the MySQL engine and release all connections."""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("MySQL engine disposed")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session.

    For file backend, yields None; callers should fall back to file operations.
    """
    if _session_factory is None:
        yield None
        return

    async with _session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def is_mysql_available() -> bool:
    return _session_factory is not None
