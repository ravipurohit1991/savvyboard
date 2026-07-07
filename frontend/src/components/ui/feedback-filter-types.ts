export type FeedbackSortOption = "top_voted" | "newest" | "oldest" | "recently_updated";

export interface FeedbackFilterValues {
  search: string;
  category: string;
  status: string;
  sort: FeedbackSortOption;
}

export const DEFAULT_FILTER_VALUES: FeedbackFilterValues = {
  search: "",
  category: "",
  status: "",
  sort: "top_voted",
};

export const SORT_OPTIONS: Array<{ value: FeedbackSortOption; label: string }> = [
  { value: "top_voted", label: "Top Voted" },
  { value: "newest", label: "Newest" },
  { value: "oldest", label: "Oldest" },
  { value: "recently_updated", label: "Recently Updated" },
];