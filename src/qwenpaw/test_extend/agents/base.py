# -*- coding: utf-8 -*-
"""Test Platform Agent base class.

Provides a common base for all 8 test-specific agents, inheriting from
the platform's QwenPawAgent to reuse all native capabilities.
"""

from pathlib import Path

from qwenpaw.agents.react_agent import QwenPawAgent


class TestBaseAgent(QwenPawAgent):
    """Base class for all test platform agents.

    Extends QwenPawAgent with test-specific storage awareness and
    iteration context. All test agents inherit from this class and
    are registered via MultiAgentManager without modifying the
    original Agent base class.
    """

    test_storage_root: Path
    iteration_id: str | None

    def __init__(
        self,
        *,
        test_storage_root: Path,
        iteration_id: str | None = None,
        **kwargs,
    ):
        self.test_storage_root = test_storage_root
        self.iteration_id = iteration_id
        super().__init__(**kwargs)

    def set_iteration_context(self, iteration_id: str):
        """Set the current iteration context for this agent.

        Args:
            iteration_id: The iteration ID to operate within.
        """
        self.iteration_id = iteration_id

    def get_iteration_dir(self) -> Path:
        """Return the directory for the current iteration's assets.

        Raises:
            ValueError: If no iteration context is set.
        """
        if not self.iteration_id:
            raise ValueError("No iteration context set on agent")
        return self.test_storage_root / "iteration" / self.iteration_id
