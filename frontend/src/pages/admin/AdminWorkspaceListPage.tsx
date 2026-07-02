import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Users } from "lucide-react";

import { workspacesApi } from "@/api/api";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import type { Workspace } from "@/types";

export function AdminWorkspaceListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");

  const { data: workspaces, isLoading } = useQuery({
    queryKey: ["workspaces"],
    queryFn: () => workspacesApi.list().then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: Partial<Workspace>) => workspacesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
      setIsModalOpen(false);
      setName("");
      setSlug("");
      setDescription("");
    },
  });

  const createError = createMutation.error
    ? (createMutation.error as { response?: { data?: { detail?: string } } }).response?.data
        ?.detail || "Failed to create workspace. Please try again."
    : null;

  const handleNameChange = (value: string) => {
    setName(value);
    setSlug(
      value
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "")
    );
  };

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({ name, slug, description, is_public: true });
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workspaces</h1>
          <p className="text-sm text-gray-500">Manage your product feedback workspaces.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New workspace
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : workspaces && workspaces.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {workspaces.map((workspace) => (
            <Card
              key={workspace.id}
              className="cursor-pointer transition-shadow hover:shadow-md"
              onClick={() => navigate(`/admin/workspaces/${workspace.id}`)}
            >
              <CardHeader>
                <CardTitle>{workspace.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="line-clamp-2 text-sm text-gray-500">
                  {workspace.description || "No description"}
                </p>
                <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    {workspace.is_public ? "Public" : "Private"}
                  </span>
                  <span className="text-xs text-gray-400">/{workspace.slug}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Users}
          title="No workspaces yet"
          description="Create your first workspace to start collecting feedback."
        />
      )}

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create workspace">
        <form onSubmit={handleCreate} className="space-y-4">
          <Input
            label="Name"
            required
            value={name}
            onChange={(e) => handleNameChange(e.target.value)}
          />
          <Input label="Slug" required value={slug} onChange={(e) => setSlug(e.target.value)} />
          <Input
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          {createError && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{createError}</p>
          )}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={createMutation.isPending}>
              Create
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
