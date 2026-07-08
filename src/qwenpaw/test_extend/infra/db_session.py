# -*- coding: utf-8 -*-
"""Async MySQL engine and session management for the test platform.

Uses aiomysql driver for full async support compatible with FastAPI.
Session lifecycle is managed via async context manager.
"""

import logging
from typing import TYPE_CHECKING, Optional

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
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("MySQL engine disposed")


class _DbSession:
    """Async context manager wrapping an AsyncSession.

    Supports both `async with` and `async for` patterns for compatibility.
    """

    def __init__(self):
        global _session_factory
        self._session: Optional[AsyncSession] = None
        if _session_factory is not None:
            self._session = _session_factory()

    def __aiter__(self):
        return self._AsyncIter(self._session)

    class _AsyncIter:
        def __init__(self, session):
            self._session = session
            self._done = False

        async def __anext__(self):
            if self._done:
                raise StopAsyncIteration
            self._done = True
            if self._session is None:
                global _session_factory
                if _session_factory is None:
                    from .db_config import get_db_config
                    if get_db_config().is_mysql:
                        await init_mysql()
                        if _session_factory is not None:
                            self._session = _session_factory()
            return self._session

    async def __aenter__(self):
        global _session_factory
        if self._session is None and _session_factory is None:
            from .db_config import get_db_config
            if get_db_config().is_mysql:
                await init_mysql()
                if _session_factory is not None:
                    self._session = _session_factory()
        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session is None:
            return
        if exc_type is not None:
            await self._session.rollback()
        await self._session.close()


def get_db_session() -> _DbSession:
    return _DbSession()


def get_session_factory():
    global _session_factory
    return _session_factory


def is_mysql_available() -> bool:
    global _session_factory
    return _session_factory is not None

__all__ = ["init_mysql", "close_mysql", "get_db_session", "is_mysql_available", "get_session_factory"]