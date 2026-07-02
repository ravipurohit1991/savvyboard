import { Link, Outlet, useParams } from "react-router-dom";
import { Button } from "@fluentui/react-components";
import { Lightbulb, ListTodo, Megaphone, Sparkles } from "lucide-react";

import { useQuery } from "@tanstack/react-query";
import { publicApi } from "@/api/api";
import { Skeleton } from "@/components/ui/Skeleton";

export function PublicLayout() {
  const { slug } = useParams();
  const { data, isLoading } = useQuery({
    queryKey: ["public-workspace", slug],
    queryFn: () => publicApi.workspace(slug!).then((r) => r.data),
    enabled: !!slug,
  });

  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-gray-200">
        <div className="mx-auto max-w-5xl px-4 py-5">
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-8 w-64" />
              <Skeleton className="h-4 w-96" />
            </div>
          ) : data ? (
            <div className="flex items-start justify-between">
              <div>
                <div className="mb-2 flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600 text-white">
                    <Sparkles className="h-5 w-5" />
                  </div>
                  <h1 className="text-2xl font-bold text-gray-900">{data.workspace.name}</h1>
                </div>
                {data.workspace.description && (
                  <p className="text-gray-600">{data.workspace.description}</p>
                )}
              </div>
              <div className="flex items-center gap-2">
                <Link to={`/w/${slug}`}>
                  <Button appearance="subtle" icon={<Lightbulb className="h-4 w-4" />}>
                    Feedback
                  </Button>
                </Link>
                <Link to={`/w/${slug}/roadmap`}>
                  <Button appearance="subtle" icon={<ListTodo className="h-4 w-4" />}>
                    Roadmap
                  </Button>
                </Link>
                <Link to={`/w/${slug}/changelog`}>
                  <Button appearance="subtle" icon={<Megaphone className="h-4 w-4" />}>
                    Changelog
                  </Button>
                </Link>
              </div>
            </div>
          ) : null}
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-gray-200 py-6">
        <div className="mx-auto max-w-5xl px-4 text-center text-sm text-gray-500">
          Powered by{" "}
          <a
            href="https://github.com/ravipurohit1991/savvyboard"
            target="_blank"
            rel="noreferrer"
            className="text-primary-600 hover:underline"
          >
            SavvyBoard
          </a>
        </div>
      </footer>
    </div>
  );
}
