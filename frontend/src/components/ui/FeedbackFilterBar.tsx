import { Search, X } from "lucide-react";
import { useEffect, useState } from "react";

import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import {
  DEFAULT_FILTER_VALUES,
  SORT_OPTIONS,
  type FeedbackFilterValues,
} from "@/components/ui/feedback-filter-types";

interface FeedbackFilterBarProps {
  categoryOptions: string[];
  statusOptions: Array<{ value: string; label: string }>;
  values: FeedbackFilterValues;
  onValuesChange: (values: FeedbackFilterValues) => void;
  resultCount?: number;
}

/**
 * Search, category, status, and sort controls for a feedback board.
 *
 * The search field is debounced — onValuesChange fires 300ms after typing
 * stops, so the parent can pass the query directly to the API without
 * spamming requests on every keystroke.
 */
export function FeedbackFilterBar({
  categoryOptions,
  statusOptions,
  values,
  onValuesChange,
  resultCount,
}: FeedbackFilterBarProps) {
  const [searchInput, setSearchInput] = useState(values.search);

  // Keep the local input in sync if the parent resets filters (e.g. "clear").
  useEffect(() => {
    setSearchInput(values.search);
  }, [values.search]);

  // Debounce search — notify parent 300ms after the last keystroke.
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== values.search) {
        onValuesChange({ ...values, search: searchInput });
      }
    }, 300);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput]);

  const hasActiveFilters =
    values.search || values.category || values.status || values.sort !== "top_voted";

  const handleClear = () => {
    setSearchInput("");
    onValuesChange({ ...DEFAULT_FILTER_VALUES });
  };

  return (
    <div className="space-y-3 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            placeholder="Search feedback..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex gap-2">
          <Select
            aria-label="Filter by category"
            value={values.category}
            onChange={(e) => onValuesChange({ ...values, category: e.target.value })}
            options={[
              { value: "", label: "All categories" },
              ...categoryOptions.map((c) => ({ value: c, label: c })),
            ]}
            className="w-40"
          />
          <Select
            aria-label="Filter by status"
            value={values.status}
            onChange={(e) => onValuesChange({ ...values, status: e.target.value })}
            options={[
              { value: "", label: "All statuses" },
              ...statusOptions,
            ]}
            className="w-40"
          />
          <Select
            aria-label="Sort feedback"
            value={values.sort}
            onChange={(e) =>
              onValuesChange({ ...values, sort: e.target.value as FeedbackFilterValues["sort"] })
            }
            options={SORT_OPTIONS}
            className="w-40"
          />
          {hasActiveFilters && (
            <button
              onClick={handleClear}
              className="inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm text-gray-500 hover:bg-gray-100 hover:text-gray-700"
              aria-label="Clear all filters"
            >
              <X className="h-4 w-4" />
              Clear
            </button>
          )}
        </div>
      </div>
      {typeof resultCount === "number" && (
        <p className="text-xs text-gray-500">
          {resultCount} {resultCount === 1 ? "item" : "items"}
        </p>
      )}
    </div>
  );
}