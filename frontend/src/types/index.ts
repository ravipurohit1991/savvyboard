export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  is_public: boolean;
  owner_id: string;
  created_at: string;
  members?: WorkspaceMember[];
}

export interface WorkspaceMember {
  id: string;
  user_id: string;
  role: "owner" | "admin" | "member";
  email: string;
  full_name: string;
}

export interface Board {
  id: string;
  workspace_id: string;
  name: string;
  slug: string;
  description: string | null;
  category_options: string[];
  is_public: boolean;
  created_at: string;
}

export type FeedbackStatus = "under_review" | "planned" | "in_progress" | "shipped" | "closed";

export interface FeedbackAuthor {
  id: string | null;
  name: string | null;
}

export interface FeedbackItem {
  id: string;
  board_id: string;
  title: string;
  description: string | null;
  category: string;
  status: FeedbackStatus;
  vote_count: number;
  user_voted: boolean;
  author: FeedbackAuthor;
  comment_count: number;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: string;
  content: string;
  author: FeedbackAuthor;
  created_at: string;
}

export interface RoadmapColumn {
  status: FeedbackStatus;
  label: string;
  items: FeedbackItem[];
}

export interface ChangelogEntry {
  id: string;
  workspace_id: string;
  title: string;
  content: string;
  shipped_at: string;
  feedback_item_id: string | null;
  created_at: string;
}

export interface DashboardMetrics {
  total_feedback: number;
  total_votes: number;
  total_comments: number;
  shipped_count: number;
  members_count: number;
  category_counts: Record<string, number>;
  top_items: Array<{ id: string; title: string; vote_count: number; category: string }>;
}
