import { request } from "../request";

export interface ProjectPayload {
  name: string;
  target_url: string;
  description?: string;
  env?: string;
  tags?: string[];
  owner?: string;
}

export async function createProject(payload: ProjectPayload) {
  return request("/test/project/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function listProjects(isActive?: boolean, env?: string) {
  const params = new URLSearchParams();
  if (isActive !== undefined) params.set("is_active", String(isActive));
  if (env) params.set("env", env);
  const qs = params.toString();
  return request(`/test/project/${qs ? `?${qs}` : ""}`);
}

export async function getProject(projectId: string) {
  return request(`/test/project/${projectId}`);
}

export async function updateProject(projectId: string, payload: Partial<ProjectPayload>) {
  return request(`/test/project/${projectId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function deleteProject(projectId: string) {
  return request(`/test/project/${projectId}`, { method: "DELETE" });
}

export async function saveCases(cases: Record<string, unknown>[], iterationId: string) {
  return request("/test/case/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cases, iteration_id: iterationId }),
  });
}

export const projectApi = {
  createProject,
  listProjects,
  getProject,
  updateProject,
  deleteProject,
  saveCases,
};
