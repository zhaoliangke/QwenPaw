import { request } from "../request";

export interface GenerateScriptPayload {
  test_case: Record<string, unknown>;
  page_name?: string;
  iteration_id?: string;
  base_url?: string;
  element_map?: Record<string, string>;
  mode?: "template" | "ai";
  project_id?: string;
}

export async function generateScript(payload: GenerateScriptPayload) {
  return request("/test/ui-auto/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function debugScript(scriptContent: string, testCaseId: string) {
  return request("/test/ui-auto/debug", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ script_content: scriptContent, test_case_id: testCaseId }),
  });
}

export const uiAutoApi = {
  generateScript,
  debugScript,
};
