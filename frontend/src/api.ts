import axios from "axios";
import { getToken } from "./auth";

// Default to the backend dev port (common expectation). Use VITE_API_URL to override.
const base = (import.meta as any).env?.VITE_API_URL || "http://localhost:8000";
const api = axios.create({ baseURL: base });

// helpful debug when developers forget to set VITE_API_URL
if ((import.meta as any).env?.VITE_API_URL) {
  console.debug(`[api] using VITE_API_URL=${(import.meta as any).env.VITE_API_URL}`);
} else {
  console.debug(`[api] using default baseURL=${base}`);
}

api.interceptors.request.use((config) => {
  const t = getToken();
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

export default api;