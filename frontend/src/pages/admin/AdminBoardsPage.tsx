import { useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { MessageSquare, Plus, Trash2 } from "lucide-react";

import { boardsApi } from "@/api/api";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
import type { Board } from "@/types";

export function AdminBoardsPage() {
  const { workspaceId } = useParams();
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingBoard, setEditingBoard] = useState<Board | null>(null);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [categories, setCategories] = useState("feature, bug, improvement, integration");

  const { data: boards, isLoading } = useQuery({
    queryKey: ["boards", workspaceId],
    queryFn: () => boardsApi.list(workspaceId!).then((r) => r.data),
    enabled: !!workspaceId,
  });

  const createMutation = useMutation({
    mutationFn: (data: Partial<Board>) => boardsApi.create(workspaceId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["boards", workspaceId] });
      resetForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Board> }) =>
      boardsApi.update(workspaceId!, id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["boards", workspaceId] });
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => boardsApi.delete(workspaceId!, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["boards", workspaceId] }),
  });

  const resetForm = () => {
    setIsModalOpen(false);
    setEditingBoard(null);
    setName("");
    setSlug("");
    setDescription("");
    setCategories("feature, bug, improvement, integration");
  };

  const handleNameChange = (value: string) => {
    setName(value);
    if (!editingBoard) {
      setSlug(
        value
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/^-|-$/g, "")
      );
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      name,
      slug,
      description,
      category_options: categories
        .split(",")
        .map((c) => c.trim())
        .filter(Boolean),
      is_public: true,
    };
    if (editingBoard) {
      updateMutation.mutate({ id: editingBoard.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const openEdit = (board: Board) => {
    setEditingBoard(board);
    setName(board.name);
    setSlug(board.slug);
    setDescription(board.description || "");
    setCategories(board.category_options.join(", "));
    setIsModalOpen(true);
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Boards</h1>
          <p className="text-sm text-gray-500">Create feedback boards for different areas.</p>
        </div>
        <Button
          onClick={() => {
            resetForm();
            setIsModalOpen(true);
          }}
        >
          <Plus className="mr-2 h-4 w-4" />
          New board
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : boards && boards.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {boards.map((board) => (
            <Card key={board.id} className="cursor-pointer" onClick={() => openEdit(board)}>
              <CardHeader className="flex flex-row items-start justify-between">
                <div>
                  <CardTitle>{board.name}</CardTitle>
                  <p className="text-xs text-gray-400">/{board.slug}</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteMutation.mutate(board.id);
                  }}
                >
                  <Trash2 className="h-4 w-4 text-red-600" />
                </Button>
              </CardHeader>
              <CardContent>
                <p className="line-clamp-2 text-sm text-gray-500">
                  {board.description || "No description"}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {board.category_options.map((cat) => (
                    <Badge key={cat} variant="neutral">
                      {cat}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={MessageSquare}
          title="No boards yet"
          description="Create a board so users can submit feedback."
        />
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={resetForm}
        title={editingBoard ? "Edit board" : "Create board"}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
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
          <Input
            label="Categories (comma separated)"
            value={categories}
            onChange={(e) => setCategories(e.target.value)}
          />
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={resetForm}>
              Cancel
            </Button>
            <Button type="submit" isLoading={createMutation.isPending || updateMutation.isPending}>
              {editingBoard ? "Save" : "Create"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
