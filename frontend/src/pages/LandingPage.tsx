import { Link } from "react-router-dom";
import {
  BarChart3,
  CheckCircle,
  LayoutGrid,
  ListTodo,
  Megaphone,
  MessageSquare,
  Sparkles,
  Users,
} from "lucide-react";

import { Button } from "@/components/ui/Button";

export function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-gray-100">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600 text-white">
              <Sparkles className="h-5 w-5" />
            </div>
            <span className="text-xl font-bold">SavvyBoard</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="text-sm font-medium text-gray-700 hover:text-gray-900">
              Sign in
            </Link>
            <Link to="/register">
              <Button size="sm">Get started</Button>
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-4 py-20 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-6xl">
          Product feedback, roadmap & changelog
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600">
          SavvyBoard is the open-source platform for collecting user feedback, prioritizing what to
          build, and keeping users in the loop.
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <Link to="/register">
            <Button size="lg">Start for free</Button>
          </Link>
          <a href="https://github.com/ravipurohit1991/savvyboard" target="_blank" rel="noreferrer">
            <Button size="lg" variant="outline">
              View on GitHub
            </Button>
          </a>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16">
        <div className="grid gap-8 md:grid-cols-3">
          <Feature
            icon={MessageSquare}
            title="Collect feedback"
            description="Public or private boards for features, bugs, and ideas. Anonymous submissions included."
          />
          <Feature
            icon={ListTodo}
            title="Public roadmap"
            description="Show users what's under review, planned, in progress, and shipped."
          />
          <Feature
            icon={Megaphone}
            title="Changelog"
            description="Announce shipped features with a beautiful, public changelog page."
          />
          <Feature
            icon={BarChart3}
            title="Insights"
            description="See top-voted ideas, feedback by category, and engagement metrics."
          />
          <Feature
            icon={Users}
            title="Team workspaces"
            description="Invite product, engineering, and support teams with role-based access."
          />
          <Feature
            icon={CheckCircle}
            title="Self-hosted"
            description="Deploy with Docker in minutes. Your data stays under your control."
          />
        </div>
      </section>

      <footer className="border-t border-gray-100 py-8">
        <div className="mx-auto max-w-6xl px-4 text-center text-sm text-gray-500">
          © {new Date().getFullYear()} SavvyBoard. Open source under the MIT License.
        </div>
      </footer>
    </div>
  );
}

function Feature({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof LayoutGrid;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-gray-100 bg-gray-50 p-6">
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-white shadow-sm">
        <Icon className="h-5 w-5 text-primary-600" />
      </div>
      <h3 className="mb-2 text-lg font-semibold text-gray-900">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}
