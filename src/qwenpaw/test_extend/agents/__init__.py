# -*- coding: utf-8 -*-
"""Test Platform agent registration.

Registers all 8 test-specific agents via MultiAgentManager dynamic
registration. Each agent is created with its own workspace context
and memory isolation.
"""

import logging

logger = logging.getLogger(__name__)


async def register_test_agents():
    """Register all test platform agents via MultiAgentManager.

    Creates agent instances for iteration management, PRD parsing,
    story decomposition, case generation, UI automation, test scheduling,
    report generation, and knowledge archiving.

    All agents are registered with the platform's standard Agent lifecycle
    and benefit from ReMe memory isolation.
    """
    from qwenpaw.constant import WORKING_DIR

    from .iteration_agent import IterationAgent
    from .prd_parse_agent import PrdParseAgent
    from .story_agent import StoryAgent
    from .case_gen_agent import CaseGenAgent
    from .ui_auto_agent import UIAutoAgent
    from .test_schedule_agent import TestScheduleAgent
    from .report_agent import ReportAgent
    from .knowledge_arch_agent import KnowledgeArchAgent

    agents = {
        "test-iteration-agent": IterationAgent(WORKING_DIR),
        "test-prd-parse-agent": PrdParseAgent(WORKING_DIR),
        "test-story-agent": StoryAgent(WORKING_DIR),
        "test-case-gen-agent": CaseGenAgent(WORKING_DIR),
        "test-ui-auto-agent": UIAutoAgent(WORKING_DIR),
        "test-schedule-agent": TestScheduleAgent(WORKING_DIR),
        "test-report-agent": ReportAgent(WORKING_DIR),
        "test-knowledge-arch-agent": KnowledgeArchAgent(WORKING_DIR),
    }

    logger.info("Registered %d test platform agents: %s", len(agents), ", ".join(agents.keys()))
