import { api } from "./client";
import type {
  Board,
  ChangelogEntry,
  Comment,
  DashboardMetrics,
  FeedbackItem,
  RoadmapColumn,
  User,
  Workspace,
} from "@/types";

export interface LoginInput {
  email: string;
  password: string;
}

export interface RegisterInput {
  email: string;
  password: string;
  full_name: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const authApi = {
  login: (data: LoginInput) =>
    api.post<TokenResponse>(
      "/auth/login",
      new URLSearchParams({ username: data.email, password: data.password }),
      {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      }
    ),
  register: (data: RegisterInput) => api.post<User>("/auth/register", data),
  me: () => api.get<User>("/auth/me"),
  refresh: (refreshToken: string) =>
    api.post<TokenResponse>("/auth/refresh", { refresh_token: refreshToken }),
};

export const workspacesApi = {
  list: () => api.get<Workspace[]>("/workspaces/"),
  get: (id: string) => api.get<Workspace>(`/workspaces/${id}`),
  create: (data: Partial<Workspace>) => api.post<Workspace>("/workspaces/", data),
  update: (id: string, data: Partial<Workspace>) => api.patch<Workspace>(`/workspaces/${id}`, data),
  delete: (id: string) => api.delete(`/workspaces/${id}`),
  addMember: (workspaceId: string, email: string, role: string) =>
    api.post(`/workspaces/${workspaceId}/members`, null, { params: { email, role } }),
  removeMember: (workspaceId: string, userId: string) =>
    api.delete(`/workspaces/${workspaceId}/members/${userId}`),
  changeRole: (workspaceId: string, userId: string, role: string) =>
    api.patch(`/workspaces/${workspaceId}/members/${userId}/role`, null, { params: { role } }),
  dashboardMetrics: (id: string) =>
    api.get<DashboardMetrics>(`/workspaces/${id}/dashboard/metrics`),
};

export const boardsApi = {
  list: (workspaceId: string) => api.get<Board[]>(`/workspaces/${workspaceId}/boards/`),
  create: (workspaceId: string, data: Partial<Board>) =>
    api.post<Board>(`/workspaces/${workspaceId}/boards/`, data),
  update: (workspaceId: string, id: string, data: Partial<Board>) =>
    api.patch<Board>(`/workspaces/${workspaceId}/boards/${id}`, data),
  delete: (workspaceId: string, id: string) =>
    api.delete(`/workspaces/${workspaceId}/boards/${id}`),
};

export interface FeedbackListParams {
  search?: string;
  category?: string;
  status?: string;
  sort?: string;
}

export const feedbackApi = {
  list: (workspaceId: string, boardId: string, params?: FeedbackListParams) =>
    api.get<FeedbackItem[]>(`/workspaces/${workspaceId}/boards/${boardId}/feedback/`, {
      params,
    }),
  create: (workspaceId: string, boardId: string, data: object) =>
    api.post<FeedbackItem>(`/workspaces/${workspaceId}/boards/${boardId}/feedback/`, data),
  update: (workspaceId: string, boardId: string, id: string, data: object) =>
    api.patch<FeedbackItem>(`/workspaces/${workspaceId}/boards/${boardId}/feedback/${id}`, data),
  delete: (workspaceId: string, boardId: string, id: string) =>
    api.delete(`/workspaces/${workspaceId}/boards/${boardId}/feedback/${id}`),
  vote: (workspaceId: string, boardId: string, id: string, anonToken?: string) =>
    api.post<FeedbackItem>(`/workspaces/${workspaceId}/boards/${boardId}/feedback/${id}/vote`, {
      anonymous_token: anonToken,
    }),
  listComments: (workspaceId: string, boardId: string, id: string) =>
    api.get<Comment[]>(`/workspaces/${workspaceId}/boards/${boardId}/feedback/${id}/comments`),
  addComment: (workspaceId: string, boardId: string, id: string, data: object) =>
    api.post<Comment>(`/workspaces/${workspaceId}/boards/${boardId}/feedback/${id}/comments`, data),
};

export const roadmapApi = {
  list: (workspaceId: string) => api.get<RoadmapColumn[]>(`/workspaces/${workspaceId}/roadmap/`),
};

export const changelogApi = {
  list: (workspaceId: string) => api.get<ChangelogEntry[]>(`/workspaces/${workspaceId}/changelog/`),
  create: (workspaceId: string, data: Partial<ChangelogEntry>) =>
    api.post<ChangelogEntry>(`/workspaces/${workspaceId}/changelog/`, data),
  update: (workspaceId: string, id: string, data: Partial<ChangelogEntry>) =>
    api.patch<ChangelogEntry>(`/workspaces/${workspaceId}/changelog/${id}`, data),
  delete: (workspaceId: string, id: string) =>
    api.delete(`/workspaces/${workspaceId}/changelog/${id}`),
};

export const publicApi = {
  workspace: (slug: string) =>
    api.get<{ workspace: Workspace; boards: Board[] }>(`/public/workspaces/${slug}`),
  feedback: (slug: string, boardSlug: string, params?: FeedbackListParams) =>
    api.get<FeedbackItem[]>(`/public/workspaces/${slug}/feedback/${boardSlug}`, {
      params,
    }),
  submitFeedback: (slug: string, boardSlug: string, data: object) =>
    api.post<FeedbackItem>(`/public/workspaces/${slug}/feedback/${boardSlug}`, data),
  vote: (slug: string, boardSlug: string, itemId: string, anonToken?: string) =>
    api.post<FeedbackItem>(`/public/workspaces/${slug}/feedback/${boardSlug}/${itemId}/vote`, {
      anonymous_token: anonToken,
    }),
  comments: (slug: string, boardSlug: string, itemId: string) =>
    api.get<Comment[]>(`/public/workspaces/${slug}/feedback/${boardSlug}/${itemId}/comments`),
  addComment: (slug: string, boardSlug: string, itemId: string, data: object) =>
    api.post<Comment>(`/public/workspaces/${slug}/feedback/${boardSlug}/${itemId}/comments`, data),
  roadmap: (slug: string) => api.get<RoadmapColumn[]>(`/public/workspaces/${slug}/roadmap`),
  changelog: (slug: string) => api.get<ChangelogEntry[]>(`/public/workspaces/${slug}/changelog`),
};
