import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, MessageSquare, ThumbsUp } from "lucide-react";

import { publicApi } from "@/api/api";
import { ensureAnonymousToken } from "@/api/client";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Select } from "@/components/ui/Select";
import { Skeleton } from "@/components/ui/Skeleton";
import { Textarea } from "@/components/ui/Textarea";
import type { FeedbackItem } from "@/types";

const STATUS_VARIANTS: Record<
  FeedbackItem["status"],
  "neutral" | "warning" | "info" | "success" | "danger"
> = {
  under_review: "warning",
  planned: "info",
  in_progress: "info",
  shipped: "success",
  closed: "danger",
};

export function PublicBoardPage() {
  const { slug, boardSlug } = useParams();
  const queryClient = useQueryClient();
  const [isSubmitOpen, setIsSubmitOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<FeedbackItem | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("feature");
  const [authorName, setAuthorName] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["public-workspace", slug],
    queryFn: () => publicApi.workspace(slug!).then((r) => r.data),
    enabled: !!slug,
  });

  const board = data?.boards.find((b) => b.slug === boardSlug);

  const { data: items, isLoading: itemsLoading } = useQuery({
    queryKey: ["public-feedback", slug, boardSlug],
    queryFn: () => publicApi.feedback(slug!, boardSlug!).then((r) => r.data),
    enabled: !!slug && !!boardSlug,
  });

  const submitMutation = useMutation({
    mutationFn: (payload: object) => publicApi.submitFeedback(slug!, boardSlug!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["public-feedback", slug, boardSlug] });
      resetSubmit();
    },
  });

  const voteMutation = useMutation({
    mutationFn: (itemId: string) =>
      publicApi.vote(slug!, boardSlug!, itemId, ensureAnonymousToken()),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["public-feedback", slug, boardSlug] }),
  });

  const resetSubmit = () => {
    setIsSubmitOpen(false);
    setTitle("");
    setDescription("");
    setCategory("feature");
    setAuthorName("");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitMutation.mutate({
      title,
      description,
      category,
      author_name: authorName || undefined,
    });
  };

  if (isLoading) {
    return <Skeleton className="h-96" />;
  }

  if (!board) {
    return <EmptyState icon={MessageSquare} title="Board not found" />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link
          to={`/w/${slug}`}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="mr-1 h-4 w-4" />
          Back to workspace
        </Link>
        <Button onClick={() => setIsSubmitOpen(true)}>Submit feedback</Button>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-gray-900">{board.name}</h2>
        <p className="text-sm text-gray-500">{board.description}</p>
      </div>

      {itemsLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : items && items.length > 0 ? (
        <div className="space-y-3">
          {items.map((item) => (
            <Card key={item.id} className="cursor-pointer" onClick={() => setSelectedItem(item)}>
              <CardContent className="p-5">
                <div className="flex items-start gap-4">
                  <Button
                    variant={item.user_voted ? "primary" : "outline"}
                    size="sm"
                    className="flex flex-col items-center gap-0.5 px-3 py-2"
                    onClick={(e) => {
                      e.stopPropagation();
                      voteMutation.mutate(item.id);
                    }}
                  >
                    <ThumbsUp className="h-4 w-4" />
                    <span className="text-xs">{item.vote_count}</span>
                  </Button>
                  <div className="flex-1">
                    <div className="mb-1 flex flex-wrap items-center gap-2">
                      <Badge variant={STATUS_VARIANTS[item.status]}>
                        {item.status.replace("_", " ")}
                      </Badge>
                      <Badge variant="neutral">{item.category}</Badge>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900">{item.title}</h3>
                    <p className="mt-1 line-clamp-2 text-sm text-gray-600">{item.description}</p>
                    <div className="mt-2 flex items-center gap-3 text-xs text-gray-500">
                      <span>by {item.author.name || "Anonymous"}</span>
                      <span className="flex items-center gap-1">
                        <MessageSquare className="h-3 w-3" />
                        {item.comment_count}
                      </span>
                    </div>
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
          description="Be the first to submit an idea."
        />
      )}

      <Modal isOpen={isSubmitOpen} onClose={resetSubmit} title="Submit feedback">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Title" required value={title} onChange={(e) => setTitle(e.target.value)} />
          <Textarea
            label="Description"
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <Select
            label="Category"
            required
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            options={board.category_options.map((c) => ({ value: c, label: c }))}
          />
          <Input
            label="Your name (optional)"
            value={authorName}
            onChange={(e) => setAuthorName(e.target.value)}
          />
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={resetSubmit}>
              Cancel
            </Button>
            <Button type="submit" isLoading={submitMutation.isPending}>
              Submit
            </Button>
          </div>
        </form>
      </Modal>

      {selectedItem && (
        <FeedbackDetailModal
          slug={slug!}
          boardSlug={boardSlug!}
          item={selectedItem}
          onClose={() => setSelectedItem(null)}
        />
      )}
    </div>
  );
}

function FeedbackDetailModal({
  slug,
  boardSlug,
  item,
  onClose,
}: {
  slug: string;
  boardSlug: string;
  item: FeedbackItem;
  onClose: () => void;
}) {
  const queryClient = useQueryClient();
  const [comment, setComment] = useState("");
  const [commentName, setCommentName] = useState("");

  const { data: comments, isLoading } = useQuery({
    queryKey: ["public-comments", slug, boardSlug, item.id],
    queryFn: () => publicApi.comments(slug, boardSlug, item.id).then((r) => r.data),
    enabled: !!item,
  });

  const commentMutation = useMutation({
    mutationFn: (payload: object) => publicApi.addComment(slug, boardSlug, item.id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["public-comments", slug, boardSlug, item.id] });
      setComment("");
    },
  });

  const handleComment = (e: React.FormEvent) => {
    e.preventDefault();
    commentMutation.mutate({ content: comment, author_name: commentName || undefined });
  };

  return (
    <Modal isOpen={!!item} onClose={onClose} title={item.title}>
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={STATUS_VARIANTS[item.status]}>{item.status.replace("_", " ")}</Badge>
          <Badge variant="neutral">{item.category}</Badge>
        </div>
        <p className="text-sm text-gray-700">{item.description}</p>
        <p className="text-xs text-gray-400">Submitted by {item.author.name || "Anonymous"}</p>

        <div className="border-t border-gray-100 pt-4">
          <h4 className="mb-2 text-sm font-semibold text-gray-900">
            Comments ({item.comment_count})
          </h4>
          {isLoading ? (
            <Skeleton className="h-16" />
          ) : (
            <div className="max-h-64 space-y-3 overflow-y-auto">
              {comments?.map((c) => (
                <div key={c.id} className="rounded-lg bg-gray-50 p-3">
                  <p className="text-sm text-gray-700">{c.content}</p>
                  <p className="mt-1 text-xs text-gray-400">by {c.author.name || "Anonymous"}</p>
                </div>
              ))}
              {!comments?.length && <p className="text-sm text-gray-500">No comments yet.</p>}
            </div>
          )}
        </div>

        <form onSubmit={handleComment} className="space-y-3">
          <Textarea
            placeholder="Add a comment..."
            rows={3}
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            required
          />
          <Input
            placeholder="Your name (optional)"
            value={commentName}
            onChange={(e) => setCommentName(e.target.value)}
          />
          <div className="flex justify-end">
            <Button type="submit" size="sm" isLoading={commentMutation.isPending}>
              Comment
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
