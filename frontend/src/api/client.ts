import axios from "axios";
import { useAuthStore } from "../store/authStore";

const BASE = import.meta.env.VITE_API_BASE_URL || "/api";

const api = axios.create({
  baseURL: BASE,
  headers: { "Content-Type": "application/json" },
});

// ── Request: attach access token ──────────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response: silent token refresh on 401 ────────────────────────────────────
let isRefreshing = false;
let pendingQueue: Array<(token: string) => void> = [];

function flushQueue(token: string) {
  pendingQueue.forEach((cb) => cb(token));
  pendingQueue = [];
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;

    // Skip retry for login / refresh endpoints to avoid infinite loops
    const isAuthUrl =
      original.url?.includes("/auth/login/") ||
      original.url?.includes("/auth/refresh/");

    if (error.response?.status === 401 && !original._retry && !isAuthUrl) {
      if (isRefreshing) {
        // Queue requests while refresh is in flight
        return new Promise((resolve) => {
          pendingQueue.push((token) => {
            original.headers.Authorization = `Bearer ${token}`;
            resolve(api(original));
          });
        });
      }

      original._retry = true;
      isRefreshing = true;

      try {
        const { refreshToken, setAccessToken, logout } = useAuthStore.getState();
        if (!refreshToken) throw new Error("No refresh token");

        const { data } = await axios.post(`${BASE}/auth/refresh/`, {
          refresh: refreshToken,
        });

        setAccessToken(data.access);
        flushQueue(data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch {
        useAuthStore.getState().logout();
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
