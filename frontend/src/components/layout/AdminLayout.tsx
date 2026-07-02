import { Link, Navigate, Outlet, useParams } from "react-router-dom";
import { Avatar } from "@fluentui/react-components";
import {
  BarChart3,
  ChevronLeft,
  LayoutGrid,
  ListTodo,
  LogOut,
  Megaphone,
  MessageSquare,
  Settings,
  Sparkles,
} from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/Button";

export function AdminLayout() {
  const { user, isLoading, logout } = useAuth();
  const { workspaceId } = useParams();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="fixed inset-y-0 left-0 z-20 w-64 border-r border-gray-200 bg-white">
        <div className="flex h-full flex-col">
          <div className="flex items-center gap-2 border-b border-gray-100 px-6 py-4">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600 text-white">
              <Sparkles className="h-5 w-5" />
            </div>
            <span className="text-lg font-bold text-gray-900">SavvyBoard</span>
          </div>

          <nav className="flex-1 space-y-1 px-4 py-4">
            <Link
              to="/admin"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
            >
              <LayoutGrid className="h-4 w-4" />
              Workspaces
            </Link>
            {workspaceId && (
              <>
                <Link
                  to={`/admin/workspaces/${workspaceId}`}
                  className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
                >
                  <BarChart3 className="h-4 w-4" />
                  Dashboard
                </Link>
                <Link
                  to={`/admin/workspaces/${workspaceId}/boards`}
                  className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
                >
                  <MessageSquare className="h-4 w-4" />
                  Boards & Feedback
                </Link>
                <Link
                  to={`/admin/workspaces/${workspaceId}/roadmap`}
                  className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
                >
                  <ListTodo className="h-4 w-4" />
                  Roadmap
                </Link>
                <Link
                  to={`/admin/workspaces/${workspaceId}/changelog`}
                  className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
                >
                  <Megaphone className="h-4 w-4" />
                  Changelog
                </Link>
                <Link
                  to={`/admin/workspaces/${workspaceId}/settings`}
                  className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
                >
                  <Settings className="h-4 w-4" />
                  Settings
                </Link>
              </>
            )}
          </nav>

          <div className="border-t border-gray-100 p-4">
            <div className="mb-3 flex items-center gap-3 px-3">
              <Avatar
                name={user.full_name}
                initials={user.full_name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .toUpperCase()}
                size={28}
                color="brand"
                aria-label={user.full_name}
              />
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-gray-900">{user.full_name}</p>
                <p className="truncate text-xs text-gray-500">{user.email}</p>
              </div>
            </div>
            <Button variant="outline" size="sm" className="w-full" onClick={logout}>
              <LogOut className="mr-2 h-4 w-4" />
              Log out
            </Button>
          </div>
        </div>
      </aside>

      <main className="ml-64 flex-1">
        <div className="border-b border-gray-200 bg-white px-8 py-4">
          <Link
            to="/admin"
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <ChevronLeft className="mr-1 h-4 w-4" />
            Back to workspaces
          </Link>
        </div>
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
