# -*- coding: utf-8 -*-
"""Test Platform MCP tool registration.

Registers all test platform MCP tools with the QwenPaw plugin system.
Each tool is registered via PluginApi.register_tool() and becomes
available to agents through the standard tool pipeline.

Full tool implementations will be added in later implementation phases.
"""

import logging

logger = logging.getLogger(__name__)


def register_test_mcp_tools(api):
    """Register all test MCP tools with the plugin API.

    Args:
        api: PluginApi instance provided by the QwenPaw plugin loader.
    """
    logger.info("Test Platform MCP tools registration placeholder - "
                 "full tools will be registered in later phases")
