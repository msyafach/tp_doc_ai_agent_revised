import api from "./client";
import type { Project, ProjectListItem, ProjectState, AgentTask, AppConfig, ApiSettings } from "../types";

// ─── Config ───────────────────────────────────────────────────────────────────

export async function fetchConfig(): Promise<AppConfig> {
  const { data } = await api.get<AppConfig>("/config/");
  return data;
}

// ─── Projects ─────────────────────────────────────────────────────────────────

export async function listProjects(): Promise<ProjectListItem[]> {
  const { data } = await api.get<ProjectListItem[]>("/projects/");
  return data;
}

export async function createProject(name?: string): Promise<Project> {
  const { data } = await api.post<Project>("/projects/", { name: name ?? "" });
  return data;
}

export async function getProject(id: string): Promise<Project> {
  const { data } = await api.get<Project>(`/projects/${id}/`);
  return data;
}

export async function saveProject(id: string, updates: Partial<{ name: string; state: Partial<ProjectState> }>): Promise<Project> {
  const { data } = await api.patch<Project>(`/projects/${id}/`, updates);
  return data;
}

export async function deleteProject(id: string): Promise<void> {
  await api.delete(`/projects/${id}/`);
}

export async function exportProjectJson(id: string): Promise<Blob> {
  const { data } = await api.get(`/projects/${id}/export-json/`, {
    responseType: "blob",
  });
  return data;
}

export async function loadProjectJson(id: string, file: File): Promise<Project> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<Project>(`/projects/${id}/load-json/`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

// ─── Document upload ──────────────────────────────────────────────────────────

export async function uploadDocuments(
  projectId: string,
  files: File[],
  settings: ApiSettings,
): Promise<{ task_id: number }> {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  form.append("llm_provider", settings.llm_provider);
  form.append("api_key", settings.api_key);
  form.append("model", settings.model);
  form.append("tavily_key", settings.tavily_key);

  const { data } = await api.post<{ task_id: number }>(
    `/projects/${projectId}/upload-documents/`,
    form,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return data;
}

// ─── AI agents ────────────────────────────────────────────────────────────────

export async function runAgents(
  projectId: string,
  settings: ApiSettings,
): Promise<{ task_id: number }> {
  const { data } = await api.post<{ task_id: number }>(
    `/projects/${projectId}/run-agents/`,
    {
      llm_provider: settings.llm_provider,
      api_key: settings.api_key,
      model: settings.model,
      tavily_key: settings.tavily_key,
      langsmith_api_key: settings.langsmith_api_key,
      langsmith_project: settings.langsmith_project,
    },
  );
  return data;
}

export async function runSingleAgent(
  projectId: string,
  agentKey: string,
  settings: ApiSettings,
): Promise<{ task_id: number }> {
  const { data } = await api.post<{ task_id: number }>(
    `/projects/${projectId}/run-single-agent/`,
    {
      agent_key: agentKey,
      llm_provider: settings.llm_provider,
      api_key: settings.api_key,
      model: settings.model,
      tavily_key: settings.tavily_key,
      langsmith_api_key: settings.langsmith_api_key,
      langsmith_project: settings.langsmith_project,
    },
  );
  return data;
}

export async function pollTaskStatus(taskId: number): Promise<AgentTask> {
  const { data } = await api.get<AgentTask>(`/tasks/${taskId}/`);
  return data;
}

// ─── DOCX export ─────────────────────────────────────────────────────────────

export async function exportDocx(projectId: string, type: "builder" | "template" = "builder"): Promise<Blob> {
  const { data } = await api.get(
    `/projects/${projectId}/export-docx/?type=${type}`,
    { responseType: "blob" },
  );
  return data;
}
