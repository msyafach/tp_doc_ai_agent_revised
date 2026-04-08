import api from "./client";
import type { AuthUser } from "../store/authStore";

export interface LoginResponse {
  access: string;
  refresh: string;
  user: AuthUser;
}

export interface UserListItem {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
  date_joined: string;
  last_login: string | null;
}

export async function loginApi(username: string, password: string): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>("/auth/login/", { username, password });
  return data;
}

export async function logoutApi(refreshToken: string): Promise<void> {
  await api.post("/auth/logout/", { refresh: refreshToken });
}

export async function getUsersApi(): Promise<UserListItem[]> {
  const { data } = await api.get<UserListItem[]>("/admin/users/");
  return data;
}

export async function createUserApi(payload: {
  username: string;
  password: string;
  email: string;
  is_staff: boolean;
}): Promise<AuthUser> {
  const { data } = await api.post<AuthUser>("/admin/users/", payload);
  return data;
}

export async function deleteUserApi(id: number): Promise<void> {
  await api.delete(`/admin/users/${id}/`);
}
