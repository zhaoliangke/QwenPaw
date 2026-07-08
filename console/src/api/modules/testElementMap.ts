import { request } from "../request";

export interface ElementMapPayload {
  project_id: string;
  page_name: string;
  mapping: Record<string, string>;
}

export async function createElementMap(payload: ElementMapPayload) {
  return request("/test/element-map/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function listElementMaps(projectId?: string, pageName?: string) {
  const params = new URLSearchParams();
  if (projectId) params.set("project_id", projectId);
  if (pageName) params.set("page_name", pageName);
  const qs = params.toString();
  return request(`/test/element-map/${qs ? `?${qs}` : ""}`);
}

export async function getElementMap(mapId: string) {
  return request(`/test/element-map/${mapId}`);
}

export async function updateElementMap(mapId: string, payload: Partial<ElementMapPayload>) {
  return request(`/test/element-map/${mapId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function deleteElementMap(mapId: string) {
  return request(`/test/element-map/${mapId}`, { method: "DELETE" });
}

export const elementMapApi = {
  createElementMap,
  listElementMaps,
  getElementMap,
  updateElementMap,
  deleteElementMap,
};
