import { Route, Routes } from "react-router-dom";

import { AdminLayout } from "@/components/layout/AdminLayout";
import { PublicLayout } from "@/components/layout/PublicLayout";
import { AdminWorkspaceListPage } from "@/pages/admin/AdminWorkspaceListPage";
import { AdminDashboardPage } from "@/pages/admin/AdminDashboardPage";
import { AdminBoardsPage } from "@/pages/admin/AdminBoardsPage";
import { AdminFeedbackPage } from "@/pages/admin/AdminFeedbackPage";
import { AdminRoadmapPage } from "@/pages/admin/AdminRoadmapPage";
import { AdminChangelogPage } from "@/pages/admin/AdminChangelogPage";
import { AdminWorkspaceSettingsPage } from "@/pages/admin/AdminWorkspaceSettingsPage";
import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterPage } from "@/pages/auth/RegisterPage";
import { PublicWorkspacePage } from "@/pages/public/PublicWorkspacePage";
import { PublicBoardPage } from "@/pages/public/PublicBoardPage";
import { PublicRoadmapPage } from "@/pages/public/PublicRoadmapPage";
import { PublicChangelogPage } from "@/pages/public/PublicChangelogPage";
import { LandingPage } from "@/pages/LandingPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<AdminWorkspaceListPage />} />
        <Route path="workspaces/:workspaceId" element={<AdminDashboardPage />} />
        <Route path="workspaces/:workspaceId/boards" element={<AdminBoardsPage />} />
        <Route path="workspaces/:workspaceId/feedback" element={<AdminFeedbackPage />} />
        <Route path="workspaces/:workspaceId/roadmap" element={<AdminRoadmapPage />} />
        <Route path="workspaces/:workspaceId/changelog" element={<AdminChangelogPage />} />
        <Route path="workspaces/:workspaceId/settings" element={<AdminWorkspaceSettingsPage />} />
      </Route>

      <Route path="/w/:slug" element={<PublicLayout />}>
        <Route index element={<PublicWorkspacePage />} />
        <Route path="boards/:boardSlug" element={<PublicBoardPage />} />
        <Route path="roadmap" element={<PublicRoadmapPage />} />
        <Route path="changelog" element={<PublicChangelogPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
