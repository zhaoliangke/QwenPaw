# -*- coding: utf-8 -*-
"""Infrastructure initialization and lifecycle management.

Provides a single entry point to initialize/teardown all infrastructure
components (MySQL, Redis, ReMe) for the test platform.

Usage:
    from qwenpaw.test_extend.infra import init_infra, close_infra

    await init_infra(workspace_dir="/path/to/workspace")
    # ... use the platform ...
    await close_infra()
"""

import logging

logger = logging.getLogger(__name__)


async def init_infra(workspace_dir: str):
    """Initialize all infrastructure services for the test platform.

    Order matters: Redis first (cache), then MySQL (storage),
    then ReMe (knowledge base, which may need cache).

    Each component is optional; failures are logged but not fatal.
    """
    logger.info("Initializing test platform infrastructure...")

    from .redis_cache import init_redis
    await init_redis()

    from .db_session import init_mysql
    await init_mysql()

    from .reme_knowledge import init_knowledge_base
    await init_knowledge_base(workspace_dir)

    logger.info("Test platform infrastructure ready")


async def close_infra():
    """Shut down all infrastructure services in reverse order."""
    logger.info("Shutting down test platform infrastructure...")

    from .reme_knowledge import close_knowledge_base
    await close_knowledge_base()

    from .db_session import close_mysql
    await close_mysql()

    from .redis_cache import close_redis
    await close_redis()

    logger.info("Test platform infrastructure shut down")
