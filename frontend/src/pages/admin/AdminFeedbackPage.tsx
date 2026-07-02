import { useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { MessageSquare, Trash2 } from "lucide-react";

import { boardsApi, feedbackApi } from "@/api/api";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Select } from "@/components/ui/Select";
import { Skeleton } from "@/components/ui/Skeleton";
import type { FeedbackStatus } from "@/types";

const STATUS_OPTIONS: { value: FeedbackStatus; label: string }[] = [
  { value: "under_review", label: "Under Review" },
  { value: "planned", label: "Planned" },
  { value: "in_progress", label: "In Progress" },
  { value: "shipped", label: "Shipped" },
  { value: "closed", label: "Closed" },
];

const STATUS_VARIANTS: Record<
  FeedbackStatus,
  "neutral" | "warning" | "info" | "success" | "danger"
> = {
  under_review: "warning",
  planned: "info",
  in_progress: "info",
  shipped: "success",
  closed: "danger",
};

export function AdminFeedbackPage() {
  const { workspaceId } = useParams();
  const queryClient = useQueryClient();
  const [selectedBoardId, setSelectedBoardId] = useState<string | null>(null);

  const { data: boards, isLoading: boardsLoading } = useQuery({
    queryKey: ["boards", workspaceId],
    queryFn: () => boardsApi.list(workspaceId!).then((r) => r.data),
    enabled: !!workspaceId,
  });

  const boardId = selectedBoardId || boards?.[0]?.id;

  const { data: items, isLoading: itemsLoading } = useQuery({
    queryKey: ["feedback", workspaceId, boardId],
    queryFn: () => feedbackApi.list(workspaceId!, boardId!).then((r) => r.data),
    enabled: !!workspaceId && !!boardId,
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: object }) =>
      feedbackApi.update(workspaceId!, boardId!, id, data),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["feedback", workspaceId, boardId] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => feedbackApi.delete(workspaceId!, boardId!, id),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["feedback", workspaceId, boardId] }),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Feedback</h1>
          <p className="text-sm text-gray-500">Review, triage, and manage submitted feedback.</p>
        </div>
        {boards && boards.length > 0 && (
          <Select
            className="w-64"
            value={boardId}
            onChange={(e) => setSelectedBoardId(e.target.value)}
            options={boards.map((b) => ({ value: b.id, label: b.name }))}
          />
        )}
      </div>

      {boardsLoading || itemsLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      ) : items && items.length > 0 ? (
        <div className="space-y-3">
          {items.map((item) => (
            <Card key={item.id}>
              <CardContent className="p-5">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div className="flex-1">
                    <div className="mb-2 flex flex-wrap items-center gap-2">
                      <Badge variant={STATUS_VARIANTS[item.status]}>
                        {STATUS_OPTIONS.find((s) => s.value === item.status)?.label}
                      </Badge>
                      <Badge variant="neutral">{item.category}</Badge>
                      <span className="text-xs text-gray-400">
                        by {item.author.name || "Anonymous"}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900">{item.title}</h3>
                    <p className="mt-1 text-sm text-gray-600">{item.description}</p>
                    <div className="mt-3 flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">{item.vote_count} votes</span>
                      <span className="flex items-center gap-1">{item.comment_count} comments</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Select
                      value={item.status}
                      onChange={(e) =>
                        updateMutation.mutate({ id: item.id, data: { status: e.target.value } })
                      }
                      options={STATUS_OPTIONS}
                      className="w-40"
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteMutation.mutate(item.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={MessageSquare}
          title="No feedback yet"
          description="Share your public board link to start collecting ideas."
        />
      )}
    </div>
  );
}
