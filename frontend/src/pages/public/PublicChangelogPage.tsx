import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Megaphone } from "lucide-react";

import { publicApi } from "@/api/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Skeleton } from "@/components/ui/Skeleton";

export function PublicChangelogPage() {
  const { slug } = useParams();
  const { data: entries, isLoading } = useQuery({
    queryKey: ["public-changelog", slug],
    queryFn: () => publicApi.changelog(slug!).then((r) => r.data),
    enabled: !!slug,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Changelog</h2>
        <p className="text-sm text-gray-500">Latest product updates and shipped features.</p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : entries && entries.length > 0 ? (
        <div className="space-y-4">
          {entries.map((entry) => (
            <Card key={entry.id}>
              <CardHeader>
                <p className="text-xs text-gray-400">
                  {new Date(entry.shipped_at).toLocaleDateString(undefined, { dateStyle: "long" })}
                </p>
                <CardTitle>{entry.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose">
                  {entry.content.split("\n").map((paragraph, idx) => (
                    <p key={idx}>{paragraph}</p>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Megaphone}
          title="No updates yet"
          description="Check back soon for product announcements."
        />
      )}
    </div>
  );
}
