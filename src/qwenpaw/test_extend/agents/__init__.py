# -*- coding: utf-8 -*-
"""Test Platform agent registration.

Registers all 8 test-specific agents via MultiAgentManager dynamic
registration. Full agent implementations will be added in later
implementation phases.
"""

import logging

logger = logging.getLogger(__name__)


async def register_test_agents():
    """Register all test platform agents via MultiAgentManager.

    This function is called during the plugin startup hook. Each agent
    is created with its own workspace context and memory isolation.
    """
    logger.info("Test Platform agent registration placeholder - "
                 "full agents will be registered in later phases")
