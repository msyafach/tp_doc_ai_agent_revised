import api from "./client";
import type { ApiSettings } from "../types";

/** Authenticated users — read non-sensitive settings status */
export async function getSettingsStatusApi(): Promise<{
  llm_provider: string;
  model: string;
  langsmith_project: string;
  has_api_key: boolean;
  has_tavily_key: boolean;
  has_langsmith_key: boolean;
}> {
  const { data } = await api.get("/settings/");
  return data;
}

/** Admin only — read full settings including key values */
export async function getAdminSettingsApi(): Promise<ApiSettings> {
  const { data } = await api.get("/admin/settings/");
  return data;
}

/** Admin only — save settings */
export async function updateAdminSettingsApi(settings: Partial<ApiSettings>): Promise<ApiSettings> {
  const { data } = await api.put("/admin/settings/", settings);
  return data;
}
