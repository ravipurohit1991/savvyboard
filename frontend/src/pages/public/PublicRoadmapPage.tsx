import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ListTodo, ThumbsUp } from "lucide-react";

import { publicApi } from "@/api/api";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";
import type { FeedbackStatus } from "@/types";

const STATUS_COLORS: Record<FeedbackStatus, string> = {
  under_review: "bg-yellow-100 text-yellow-700",
  planned: "bg-blue-100 text-blue-700",
  in_progress: "bg-primary-100 text-primary-700",
  shipped: "bg-green-100 text-green-700",
  closed: "bg-red-100 text-red-700",
};

export function PublicRoadmapPage() {
  const { slug } = useParams();
  const { data: columns, isLoading } = useQuery({
    queryKey: ["public-roadmap", slug],
    queryFn: () => publicApi.roadmap(slug!).then((r) => r.data),
    enabled: !!slug,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Roadmap</h2>
        <p className="text-sm text-gray-500">What we're planning, building, and shipping.</p>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      ) : columns && columns.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {columns.map((column) => (
            <Card key={column.status} className="flex flex-col">
              <CardHeader>
                <CardTitle className="flex items-center justify-between text-base">
                  {column.label}
                  <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                    {column.items.length}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 space-y-3">
                {column.items.length === 0 && (
                  <p className="text-sm text-gray-400">No items yet.</p>
                )}
                {column.items.map((item) => (
                  <div key={item.id} className="rounded-lg border border-gray-100 bg-gray-50 p-3">
                    <p className="font-medium text-gray-900">{item.title}</p>
                    <div className="mt-2 flex items-center justify-between">
                      <Badge variant="neutral" className={STATUS_COLORS[item.status]}>
                        {item.category}
                      </Badge>
                      <span className="flex items-center gap-1 text-xs font-medium text-gray-600">
                        <ThumbsUp className="h-3 w-3" />
                        {item.vote_count}
                      </span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState icon={ListTodo} title="No roadmap data" />
      )}
    </div>
  );
}
