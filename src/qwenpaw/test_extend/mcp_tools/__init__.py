# -*- coding: utf-8 -*-
"""Test Platform MCP tool registration.

Registers all 9 test platform MCP tools with the QwenPaw plugin system.
Each tool is registered via PluginApi.register_tool() and becomes
available to agents through the standard tool pipeline.
"""

import logging

logger = logging.getLogger(__name__)


def register_test_mcp_tools(api):
    """Register all test MCP tools with the plugin API.

    Args:
        api: PluginApi instance provided by the QwenPaw plugin loader.
    """
    from .iteration_mgr import (
        create_iteration_tool,
        get_iteration_tool,
        list_iterations_tool,
        update_iteration_status_tool,
        create_snapshot_tool,
        diff_iterations_tool,
        sync_from_jira_tool,
        schedule_regression_tool,
    )
    from .prd_parser import (
        parse_document_tool,
        parse_openapi_tool,
        parse_figma_tool,
        identify_ambiguities_tool,
    )
    from .story_generator import (
        generate_stories_tool,
        validate_story_tool,
        generate_traceability_tool,
    )
    from .case_generator import (
        generate_cases_tool,
        enhance_with_kb_tool,
        calculate_coverage_tool,
        export_cases_tool,
    )
    from .ui_auto_tool import (
        generate_script_tool,
        debug_script_tool,
        execute_script_tool,
        capture_screenshot_tool,
    )
    from .test_scheduler import (
        run_batch_tool,
        run_single_tool,
        retry_failed_tool,
        get_progress_tool,
    )
    from .report_builder import (
        generate_report_tool,
        analyze_failures_tool,
        push_report_tool,
        export_report_tool,
    )
    from .defect_sync import (
        submit_defect_tool,
        sync_defect_status_tool,
    )
    from .knowledge_rag import (
        archive_iteration_tool,
        search_knowledge_tool,
        upload_document_tool,
        distill_knowledge_tool,
        schedule_backup_tool,
    )

    tools = [
        ("create_iteration", create_iteration_tool, "Create a new test iteration with version, dates, module"),
        ("get_iteration", get_iteration_tool, "Get iteration details by ID"),
        ("list_iterations", list_iterations_tool, "List all iterations, optionally filtered by status"),
        ("update_iteration_status", update_iteration_status_tool, "Update the status of a test iteration"),
        ("create_snapshot", create_snapshot_tool, "Create a baseline snapshot of an iteration"),
        ("diff_iterations", diff_iterations_tool, "Compare two iterations and show story changes"),
        ("sync_from_jira", sync_from_jira_tool, "Sync iteration requirements from Jira by project key"),
        ("schedule_regression", schedule_regression_tool, "Schedule a timed regression test task"),

        ("parse_document", parse_document_tool, "Parse a PRD document (PDF/Word/Markdown)"),
        ("parse_openapi", parse_openapi_tool, "Parse an OpenAPI specification document"),
        ("parse_figma", parse_figma_tool, "Parse a Figma design link"),
        ("identify_ambiguities", identify_ambiguities_tool, "Identify requirement ambiguities and risk points"),

        ("generate_stories", generate_stories_tool, "Generate user stories from parsed PRD"),
        ("validate_story", validate_story_tool, "AI-validate story completeness and check acceptance criteria"),
        ("generate_traceability", generate_traceability_tool, "Generate full-chain traceability IDs"),

        ("generate_cases", generate_cases_tool, "Generate test cases across functional/boundary/exception/security/UI"),
        ("enhance_with_kb", enhance_with_kb_tool, "Enhance case generation with knowledge base retrieval"),
        ("calculate_coverage", calculate_coverage_tool, "Calculate story and requirement coverage rates"),
        ("export_cases", export_cases_tool, "Batch export test cases to Excel format"),

        ("generate_script", generate_script_tool, "Generate Playwright automation script from natural language"),
        ("debug_script", debug_script_tool, "Debug a single Playwright script with screenshots"),
        ("execute_script", execute_script_tool, "Execute a Playwright script in sandbox"),
        ("capture_screenshot", capture_screenshot_tool, "Capture a screenshot during script execution"),

        ("run_batch", run_batch_tool, "Batch execute test cases with configurable concurrency"),
        ("run_single", run_single_tool, "Execute a single test case manually"),
        ("retry_failed", retry_failed_tool, "Auto-retry failed test cases from a run"),
        ("get_progress", get_progress_tool, "Get real-time execution progress of a test run"),

        ("generate_report", generate_report_tool, "Generate HTML test report from execution results"),
        ("analyze_failures", analyze_failures_tool, "AI-classify failures as product defect/script error/environment fault"),
        ("push_report", push_report_tool, "Push report summary to DingTalk/Feishu/WeCom"),
        ("export_report", export_report_tool, "Export test report for download"),

        ("submit_defect", submit_defect_tool, "Submit a defect to Jira/ZenTao with screenshots"),
        ("sync_defect_status", sync_defect_status_tool, "Sync defect status from external tracker"),

        ("archive_iteration", archive_iteration_tool, "Archive all iteration assets to knowledge base"),
        ("search_knowledge", search_knowledge_tool, "Search test knowledge base with natural language"),
        ("upload_document", upload_document_tool, "Upload a test standard/business manual to knowledge base"),
        ("distill_knowledge", distill_knowledge_tool, "AI-distill knowledge base into test best practices"),
        ("schedule_backup", schedule_backup_tool, "Schedule periodic knowledge base backups"),
    ]

    for tool_name, tool_func, description in tools:
        try:
            api.register_tool(
                tool_name=tool_name,
                tool_func=tool_func,
                description=description,
                enabled=False,
            )
            logger.debug("Registered MCP tool: %s", tool_name)
        except Exception as e:
            logger.error("Failed to register tool %s: %s", tool_name, e)

    logger.info("Registered %d test platform MCP tools", len(tools))
