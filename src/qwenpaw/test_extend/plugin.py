# -*- coding: utf-8 -*-
"""Test Platform Plugin Entry.

Registers the AI end-to-end testing platform as a QwenPaw bundle plugin.
All test capabilities are injected via the PluginApi without modifying
any kernel code.
"""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_PLUGIN_DIR = Path(__file__).resolve().parent

# Ensure plugin directory is in sys.path for absolute imports
if str(_PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_DIR))


class TestPlatformPlugin:
    """Main plugin class for the AI Test Platform bundle.

    Registers HTTP routes, MCP tools, and test agents through the
    standard PluginApi hooks. All code is isolated under test_extend/
    and console/src/pages/test/ directories.
    """

    def register(self, api):
        """Register all test platform capabilities with the plugin system.

        Args:
            api: PluginApi instance provided by the QwenPaw plugin loader.
        """
        self._api = api

        from .routers import create_test_router
        from .mcp_tools import register_test_mcp_tools

        api.register_http_router(
            create_test_router(),
            prefix="/test",
            tags=["Test Platform"],
        )

        register_test_mcp_tools(api)

        api.register_startup_hook(
            hook_name="test_platform_init",
            callback=self._on_startup,
            priority=50,
        )

        api.register_shutdown_hook(
            hook_name="test_platform_shutdown",
            callback=self._on_shutdown,
            priority=100,
        )

        logger.info("Test Platform plugin registered successfully")

    async def _on_startup(self):
        """Initialize test agents, storage, and infrastructure on app startup."""
        from .infra import init_infra
        from .agents import register_test_agents

        await init_infra(workspace_dir="/root/.qwenpaw/workspaces/default")
        await register_test_agents()
        logger.info("Test Platform agents and infrastructure initialized")

    async def _on_shutdown(self):
        """Clean up test platform resources on app shutdown."""
        from .infra import close_infra
        await close_infra()
        logger.info("Test Platform shutdown complete")


plugin = TestPlatformPlugin()
