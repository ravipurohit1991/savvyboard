import axios, { AxiosError } from "axios";

const API_BASE_URL = "/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  const anonToken = localStorage.getItem("sb_anon_token");
  if (anonToken) {
    config.headers["Anonymous-Token"] = anonToken;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    if (!originalRequest) return Promise.reject(error);
    if (error.response?.status === 401 && !originalRequest.headers["X-Refresh-Retry"]) {
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token } = response.data;
          localStorage.setItem("access_token", access_token);
          localStorage.setItem("refresh_token", refresh_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          originalRequest.headers["X-Refresh-Retry"] = "true";
          return api(originalRequest);
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
      }
    }
    return Promise.reject(error);
  }
);

export function ensureAnonymousToken(): string {
  let token = localStorage.getItem("sb_anon_token");
  if (!token) {
    token = crypto.randomUUID();
    localStorage.setItem("sb_anon_token", token);
  }
  return token;
}
