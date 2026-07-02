import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { BarChart, MessageSquare, ThumbsUp, Users, CheckCircle } from "lucide-react";

import { workspacesApi } from "@/api/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { Badge } from "@/components/ui/Badge";
import { Bar, BarChart as ReBarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function AdminDashboardPage() {
  const { workspaceId } = useParams();
  const { data: metrics, isLoading } = useQuery({
    queryKey: ["dashboard-metrics", workspaceId],
    queryFn: () => workspacesApi.dashboardMetrics(workspaceId!).then((r) => r.data),
    enabled: !!workspaceId,
  });

  const categoryData = metrics
    ? Object.entries(metrics.category_counts).map(([name, value]) => ({ name, value }))
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500">Overview of feedback, votes, and shipped features.</p>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            icon={MessageSquare}
            label="Feedback items"
            value={metrics?.total_feedback || 0}
          />
          <MetricCard icon={ThumbsUp} label="Total votes" value={metrics?.total_votes || 0} />
          <MetricCard icon={CheckCircle} label="Shipped" value={metrics?.shipped_count || 0} />
          <MetricCard icon={Users} label="Team members" value={metrics?.members_count || 0} />
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart className="h-5 w-5 text-primary-600" />
              Feedback by category
            </CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            {categoryData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <ReBarChart data={categoryData}>
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                </ReBarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-sm text-gray-500">No feedback yet.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top voted items</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {metrics?.top_items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between rounded-lg border border-gray-100 p-3"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium text-gray-900">{item.title}</p>
                    <Badge variant="neutral">{item.category}</Badge>
                  </div>
                  <div className="flex items-center gap-1 text-sm font-semibold text-primary-600">
                    <ThumbsUp className="h-4 w-4" />
                    {item.vote_count}
                  </div>
                </div>
              ))}
              {metrics?.top_items.length === 0 && (
                <p className="text-sm text-gray-500">No votes yet.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof MessageSquare;
  label: string;
  value: number;
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-center gap-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100">
            <Icon className="h-5 w-5 text-primary-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            <p className="text-sm text-gray-500">{label}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
