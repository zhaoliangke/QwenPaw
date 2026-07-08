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
    from .file_processor import (
        process_uploaded_file_tool,
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
    from .test_data import (
        create_test_data_tool,
        generate_test_data_tool,
        list_test_data_tool,
        get_test_data_tool,
        delete_test_data_tool,
        substitute_variables_tool,
    )
    from .coverage import (
        run_coverage_tool,
        list_coverage_reports_tool,
        get_coverage_gaps_tool,
    )
    from .regression import (
        analyze_diff_tool,
        select_cases_tool,
        list_regression_plans_tool,
        get_regression_plan_tool,
    )
    from .notification import (
        send_notification_tool,
        dispatch_notification_tool,
        create_notify_rule_tool,
        list_notify_rules_tool,
    )
    from .api_test import (
        create_api_case_tool,
        run_api_case_tool,
        run_api_suite_tool,
        list_api_results_tool,
    )
    from .environment import (
        register_env_tool,
        health_check_env_tool,
        list_envs_tool,
        delete_env_tool,
    )
    from .case_version import (
        create_case_snapshot_tool,
        list_case_versions_tool,
        diff_case_versions_tool,
        rollback_case_tool,
    )
    from .masking import (
        mask_data_tool,
        mask_string_tool,
        detect_sensitive_tool,
    )
    from .recording import (
        start_recording_tool,
        stop_recording_tool,
        get_recording_report_tool,
        list_recordings_tool,
    )
    from .execution_queue import (
        enqueue_job_tool,
        enqueue_batch_tool,
        get_queue_stats_tool,
        cancel_job_tool,
        list_queue_jobs_tool,
    )
    from .performance import (
        create_perf_test_tool,
        run_perf_test_tool,
        list_perf_results_tool,
    )
    from .collaboration import (
        add_comment_tool,
        list_comments_tool,
        create_assignment_tool,
        list_assignments_tool,
        log_audit_tool,
        list_audit_logs_tool,
    )
    from .visual_diff import (
        create_visual_test_tool,
        run_visual_test_tool,
        update_baseline_tool,
        list_visual_results_tool,
    )
    from .ab_test import (
        create_ab_test_tool,
        analyze_ab_test_tool,
        list_ab_results_tool,
    )
    from .chaos import (
        create_chaos_experiment_tool,
        run_chaos_experiment_tool,
        list_chaos_results_tool,
    )
    from .analytics import (
        get_dashboard_tool,
        get_asset_metrics_tool,
        get_execution_trend_tool,
    )
    from .element_map_tool import (
        list_element_maps_tool,
        get_element_map_tool,
        create_element_map_tool,
        update_element_map_tool,
        delete_element_map_tool,
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

        ("process_uploaded_file", process_uploaded_file_tool, "Process uploaded documents (md/csv/excel/word/pdf) and extract text content for the model"),

        ("generate_stories", generate_stories_tool, "Generate user stories from parsed PRD"),
        ("validate_story", validate_story_tool, "AI-validate story completeness and check acceptance criteria"),
        ("generate_traceability", generate_traceability_tool, "Generate full-chain traceability IDs"),

        ("generate_cases", generate_cases_tool, "Generate test cases across functional/boundary/exception/security/UI"),
        ("enhance_with_kb", enhance_with_kb_tool, "Enhance case generation with knowledge base retrieval"),
        ("calculate_coverage", calculate_coverage_tool, "Calculate story and requirement coverage rates"),
        ("export_cases", export_cases_tool, "Batch export test cases to Excel format"),

        ("generate_script", generate_script_tool, "Generate Playwright script from test case. Pass test_case dict with id/title/steps. Supports element_map (name→selector), mode=template|ai, project_id to auto-resolve target URL. Before calling, consider listing element maps with list_element_maps if a project has element mappings."),
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

        ("create_test_data", create_test_data_tool, "Create a test data set with schema-defined fields"),
        ("generate_test_data", generate_test_data_tool, "Generate synthetic test data from schema or faker"),
        ("list_test_data", list_test_data_tool, "List all test data sets"),
        ("get_test_data", get_test_data_tool, "Get test data set by ID"),
        ("delete_test_data", delete_test_data_tool, "Delete a test data set"),
        ("substitute_variables", substitute_variables_tool, "Apply variable substitution to test steps"),

        ("run_coverage", run_coverage_tool, "Run coverage.py and generate coverage report"),
        ("list_coverage_reports", list_coverage_reports_tool, "List coverage reports"),
        ("get_coverage_gaps", get_coverage_gaps_tool, "Get uncovered code paths from a report"),

        ("analyze_diff", analyze_diff_tool, "Analyze git diff and generate regression plan"),
        ("select_cases", select_cases_tool, "Select test cases based on code changes"),
        ("list_regression_plans", list_regression_plans_tool, "List regression test plans"),
        ("get_regression_plan", get_regression_plan_tool, "Get regression plan details"),

        ("send_notification", send_notification_tool, "Send notification to DingTalk/Feishu/WeCom/webhook"),
        ("dispatch_notification", dispatch_notification_tool, "Dispatch notification by trigger rule"),
        ("create_notify_rule", create_notify_rule_tool, "Create a notification rule with triggers and channels"),
        ("list_notify_rules", list_notify_rules_tool, "List notification rules"),

        ("create_api_case", create_api_case_tool, "Create an API test case with assertions"),
        ("run_api_case", run_api_case_tool, "Execute an API test case and validate assertions"),
        ("run_api_suite", run_api_suite_tool, "Execute a suite of API test cases"),
        ("list_api_results", list_api_results_tool, "List API test execution results"),

        ("register_env", register_env_tool, "Register a test environment with base URL and health check"),
        ("health_check_env", health_check_env_tool, "Run health check on a registered environment"),
        ("list_envs", list_envs_tool, "List registered test environments"),
        ("delete_env", delete_env_tool, "Delete a registered environment"),

        ("create_case_snapshot", create_case_snapshot_tool, "Create a version snapshot of a test case"),
        ("list_case_versions", list_case_versions_tool, "List version history of a test case"),
        ("diff_case_versions", diff_case_versions_tool, "Compare two versions of a test case"),
        ("rollback_case", rollback_case_tool, "Roll back a test case to a previous version"),

        ("mask_data", mask_data_tool, "Mask sensitive data in strings, dicts, or lists"),
        ("mask_string", mask_string_tool, "Mask sensitive patterns in a plain string"),
        ("detect_sensitive", detect_sensitive_tool, "Detect sensitive fields in data without masking"),

        ("start_recording", start_recording_tool, "Start Playwright trace recording for a test case"),
        ("stop_recording", stop_recording_tool, "Stop recording and finalize trace file"),
        ("get_recording_report", get_recording_report_tool, "Get embeddable report data for a recording"),
        ("list_recordings", list_recordings_tool, "List video recordings"),

        ("enqueue_job", enqueue_job_tool, "Enqueue a test case for execution with priority"),
        ("enqueue_batch", enqueue_batch_tool, "Batch enqueue with optional sharding"),
        ("get_queue_stats", get_queue_stats_tool, "Get real-time queue statistics"),
        ("cancel_job", cancel_job_tool, "Cancel a queued or pending job"),
        ("list_queue_jobs", list_queue_jobs_tool, "List execution queue jobs"),

        ("create_perf_test", create_perf_test_tool, "Create a k6 performance test"),
        ("run_perf_test", run_perf_test_tool, "Execute a k6 performance test and collect metrics"),
        ("list_perf_results", list_perf_results_tool, "List performance test results"),

        ("add_comment", add_comment_tool, "Add a comment to a case/run/report/defect"),
        ("list_comments", list_comments_tool, "List comments for a resource"),
        ("create_assignment", create_assignment_tool, "Assign a test task to a team member"),
        ("list_assignments", list_assignments_tool, "List task assignments"),
        ("log_audit", log_audit_tool, "Log an audit trail entry"),
        ("list_audit_logs", list_audit_logs_tool, "List audit trail logs"),

        ("create_visual_test", create_visual_test_tool, "Create a visual regression test with URL and threshold"),
        ("run_visual_test", run_visual_test_tool, "Capture screenshot and compare against baseline"),
        ("update_baseline", update_baseline_tool, "Update baseline screenshot for visual test"),
        ("list_visual_results", list_visual_results_tool, "List visual diff results"),

        ("create_ab_test", create_ab_test_tool, "Create an A/B test with control and treatment variants"),
        ("analyze_ab_test", analyze_ab_test_tool, "Analyze A/B test data for statistical significance"),
        ("list_ab_results", list_ab_results_tool, "List A/B test analysis results"),

        ("create_chaos_experiment", create_chaos_experiment_tool, "Create a chaos engineering experiment"),
        ("run_chaos_experiment", run_chaos_experiment_tool, "Inject failures and measure system resilience"),
        ("list_chaos_results", list_chaos_results_tool, "List chaos experiment results"),

        ("get_dashboard", get_dashboard_tool, "Generate test asset analytics dashboard"),
        ("get_asset_metrics", get_asset_metrics_tool, "Get aggregated asset metrics"),
        ("get_execution_trend", get_execution_trend_tool, "Get execution trend data"),

        ("list_element_maps", list_element_maps_tool, "List element maps for UI automation, optionally filtered by project_id/page_name"),
        ("get_element_map", get_element_map_tool, "Get a single element map by ID"),
        ("create_element_map", create_element_map_tool, "Create a new element map (name→selector dict) for a project page"),
        ("update_element_map", update_element_map_tool, "Update element map's mapping dict, project_id, or page_name"),
        ("delete_element_map", delete_element_map_tool, "Delete an element map by ID"),
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
