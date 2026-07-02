import { useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Megaphone, Plus, Trash2 } from "lucide-react";

import { changelogApi } from "@/api/api";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import { Textarea } from "@/components/ui/Textarea";
import type { ChangelogEntry } from "@/types";

export function AdminChangelogPage() {
  const { workspaceId } = useParams();
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEntry, setEditingEntry] = useState<ChangelogEntry | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  const { data: entries, isLoading } = useQuery({
    queryKey: ["changelog", workspaceId],
    queryFn: () => changelogApi.list(workspaceId!).then((r) => r.data),
    enabled: !!workspaceId,
  });

  const createMutation = useMutation({
    mutationFn: (data: Partial<ChangelogEntry>) => changelogApi.create(workspaceId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["changelog", workspaceId] });
      resetForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ChangelogEntry> }) =>
      changelogApi.update(workspaceId!, id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["changelog", workspaceId] });
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => changelogApi.delete(workspaceId!, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["changelog", workspaceId] }),
  });

  const resetForm = () => {
    setIsModalOpen(false);
    setEditingEntry(null);
    setTitle("");
    setContent("");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = { title, content };
    if (editingEntry) {
      updateMutation.mutate({ id: editingEntry.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const openEdit = (entry: ChangelogEntry) => {
    setEditingEntry(entry);
    setTitle(entry.title);
    setContent(entry.content);
    setIsModalOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Changelog</h1>
          <p className="text-sm text-gray-500">Announce shipped features to your users.</p>
        </div>
        <Button
          onClick={() => {
            resetForm();
            setIsModalOpen(true);
          }}
        >
          <Plus className="mr-2 h-4 w-4" />
          New entry
        </Button>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : entries && entries.length > 0 ? (
        <div className="space-y-3">
          {entries.map((entry) => (
            <Card key={entry.id} className="cursor-pointer" onClick={() => openEdit(entry)}>
              <CardHeader className="flex flex-row items-start justify-between">
                <div>
                  <p className="text-xs text-gray-400">
                    {new Date(entry.shipped_at).toLocaleDateString()}
                  </p>
                  <CardTitle>{entry.title}</CardTitle>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteMutation.mutate(entry.id);
                  }}
                >
                  <Trash2 className="h-4 w-4 text-red-600" />
                </Button>
              </CardHeader>
              <CardContent>
                <p className="whitespace-pre-line text-sm text-gray-600">{entry.content}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Megaphone}
          title="No changelog entries"
          description="Publish your first update when a feature ships."
        />
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={resetForm}
        title={editingEntry ? "Edit changelog" : "New changelog entry"}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Title" required value={title} onChange={(e) => setTitle(e.target.value)} />
          <Textarea
            label="Content"
            required
            rows={6}
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={resetForm}>
              Cancel
            </Button>
            <Button type="submit" isLoading={createMutation.isPending || updateMutation.isPending}>
              {editingEntry ? "Save" : "Publish"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
