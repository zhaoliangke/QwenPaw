import { request } from "../request";

export interface WorkflowStepUpdatePayload {
  step_id: string;
  status: "pending" | "running" | "completed" | "error" | "skipped";
  result_summary?: Record<string, unknown>;
  error?: string;
  iteration_id?: string;
  chat_session_id?: string;
}

export async function updateWorkflowStep(payload: WorkflowStepUpdatePayload) {
  return request("/test/workflow/update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function resetWorkflow(iterationId?: string, chatSessionId?: string) {
  const params = new URLSearchParams();
  if (iterationId) params.set("iteration_id", iterationId);
  if (chatSessionId) params.set("chat_session_id", chatSessionId);
  const qs = params.toString();
  return request(`/test/workflow/reset${qs ? `?${qs}` : ""}`, {
    method: "POST",
  });
}

export const workflowApi = {
  updateWorkflowStep,
  resetWorkflow,
};
