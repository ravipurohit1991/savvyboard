import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, MessageSquare } from "lucide-react";

import { publicApi } from "@/api/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";

export function PublicWorkspacePage() {
  const { slug } = useParams();
  const { data, isLoading } = useQuery({
    queryKey: ["public-workspace", slug],
    queryFn: () => publicApi.workspace(slug!).then((r) => r.data),
    enabled: !!slug,
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
      </div>
    );
  }

  if (!data) {
    return <EmptyState icon={MessageSquare} title="Workspace not found" />;
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-900">Feedback boards</h2>
        <p className="text-sm text-gray-500">
          Choose a board to submit ideas, report bugs, and vote.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {data.boards.map((board) => (
          <Link key={board.id} to={`/w/${slug}/boards/${board.slug}`}>
            <Card className="transition-shadow hover:shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  {board.name}
                  <ArrowRight className="h-4 w-4 text-gray-400" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="line-clamp-2 text-sm text-gray-500">
                  {board.description || "Submit and vote on feedback."}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {board.category_options.slice(0, 4).map((cat) => (
                    <span
                      key={cat}
                      className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
                    >
                      {cat}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Link to={`/w/${slug}/roadmap`}>
          <Card className="transition-shadow hover:shadow-md">
            <CardContent className="p-6">
              <h3 className="mb-1 text-lg font-semibold text-gray-900">Roadmap</h3>
              <p className="text-sm text-gray-500">See what we're building next.</p>
            </CardContent>
          </Card>
        </Link>
        <Link to={`/w/${slug}/changelog`}>
          <Card className="transition-shadow hover:shadow-md">
            <CardContent className="p-6">
              <h3 className="mb-1 text-lg font-semibold text-gray-900">Changelog</h3>
              <p className="text-sm text-gray-500">Read about our latest releases.</p>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
}
