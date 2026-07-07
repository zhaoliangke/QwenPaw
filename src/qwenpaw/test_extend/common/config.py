# -*- coding: utf-8 -*-
"""Test Platform configuration constants."""

# Knowledge base vector collection name suffix
TEST_VECTOR_COLLECTION = "test_knowledge"

# Default concurrency for batch test execution
DEFAULT_BATCH_CONCURRENCY = 4

# Maximum retry count for failed test cases
MAX_RETRY_COUNT = 3

# Default scheduled regression cron expression (daily at 2 AM)
DEFAULT_REGRESSION_CRON = "0 2 * * *"

# File extensions supported for PRD parsing
SUPPORTED_PRD_EXTENSIONS = (".pdf", ".docx", ".doc", ".md", ".txt")

# Maximum PRD file size in bytes (50 MB)
MAX_PRD_FILE_SIZE = 50 * 1024 * 1024

# Agent names used for MultiAgentManager dynamic registration
AGENT_NAMES = {
    "iteration": "test-iteration-agent",
    "prd_parse": "test-prd-parse-agent",
    "story": "test-story-agent",
    "case_gen": "test-case-gen-agent",
    "ui_auto": "test-ui-auto-agent",
    "test_schedule": "test-schedule-agent",
    "report": "test-report-agent",
    "knowledge_arch": "test-knowledge-arch-agent",
}
