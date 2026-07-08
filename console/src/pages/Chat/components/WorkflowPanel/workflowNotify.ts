/**
 * Utility functions for workflow panel integration.
 *
 * These functions bridge the gap between QwenPaw tool_call completion
 * and the workflow panel's state management.
 */

import type { StepStatus } from "./workflowStore";

export interface WorkflowStepNotify {
  step_id: string;
  status: StepStatus;
  result_summary?: Record<string, unknown>;
  error?: string;
  iteration_id?: string;
}

/**
 * Notify the workflow panel that a step has been updated.
 *
 * Call this function when an MCP tool completes execution.
 * The WorkflowPanel listens for this event and updates its state.
 *
 * @example
 * ```ts
 * // In a tool_call result handler:
 * notifyWorkflowStep({
 *   step_id: "requirement",
 *   status: "completed",
 *   iteration_id: "iter-123",
 *   result_summary: { modules: 5, flows: 3 }
 * });
 * ```
 */
export function notifyWorkflowStep(notify: WorkflowStepNotify): void {
  window.dispatchEvent(
    new CustomEvent("workflow-step-update", { detail: notify })
  );
}

/**
 * Map MCP tool names to workflow step IDs.
 */
export const TOOL_STEP_MAP: Record<string, string> = {
  parse_document: "requirement",
  parse_openapi: "requirement",
  parse_figma: "requirement",
  identify_ambiguities: "requirement",
  generate_stories: "functional",
  generate_cases: "functional",
  generate_ui_cases: "ui-auto",
  generate_script: "ui-auto",
  debug_script: "ui-auto",
  review_cases: "review",
  enhance_with_kb: "review",
  execute_script: "execution",
  run_batch: "execution",
  run_single: "execution",
  retry_failed: "execution",
  generate_report: "report",
};

/**
 * Get the workflow step ID for a given MCP tool name.
 */
export function getStepIdForTool(toolName: string): string | null {
  return TOOL_STEP_MAP[toolName] || null;
}
