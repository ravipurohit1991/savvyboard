import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { FeedbackFilterBar } from "./FeedbackFilterBar";
import { DEFAULT_FILTER_VALUES } from "./feedback-filter-types";

const CATEGORY_OPTIONS = ["feature", "bug", "improvement"];
const STATUS_OPTIONS = [
  { value: "under_review", label: "Under Review" },
  { value: "planned", label: "Planned" },
  { value: "shipped", label: "Shipped" },
];

describe("FeedbackFilterBar", () => {
  it("renders search input and filter dropdowns", () => {
    const html = renderToStaticMarkup(
      <FeedbackFilterBar
        categoryOptions={CATEGORY_OPTIONS}
        statusOptions={STATUS_OPTIONS}
        values={DEFAULT_FILTER_VALUES}
        onValuesChange={() => {}}
      />,
    );
    expect(html).toContain("Search feedback");
    expect(html).toContain("All categories");
    expect(html).toContain("All statuses");
    expect(html).toContain("Top Voted");
  });

  it("includes all category options", () => {
    const html = renderToStaticMarkup(
      <FeedbackFilterBar
        categoryOptions={CATEGORY_OPTIONS}
        statusOptions={STATUS_OPTIONS}
        values={DEFAULT_FILTER_VALUES}
        onValuesChange={() => {}}
      />,
    );
    for (const cat of CATEGORY_OPTIONS) {
      expect(html).toContain(cat);
    }
  });

  it("includes all status options", () => {
    const html = renderToStaticMarkup(
      <FeedbackFilterBar
        categoryOptions={CATEGORY_OPTIONS}
        statusOptions={STATUS_OPTIONS}
        values={DEFAULT_FILTER_VALUES}
        onValuesChange={() => {}}
      />,
    );
    for (const status of STATUS_OPTIONS) {
      expect(html).toContain(status.label);
    }
  });

  it("includes all sort options", () => {
    const html = renderToStaticMarkup(
      <FeedbackFilterBar
        categoryOptions={CATEGORY_OPTIONS}
        statusOptions={STATUS_OPTIONS}
        values={DEFAULT_FILTER_VALUES}
        onValuesChange={() => {}}
      />,
    );
    expect(html).toContain("Newest");
    expect(html).toContain("Oldest");
    expect(html).toContain("Recently Updated");
  });

  it("does not show clear button when no filters are active", () => {
    const html = renderToStaticMarkup(
      <FeedbackFilterBar
        categoryOptions={CATEGORY_OPTIONS}
        statusOptions={STATUS_OPTIONS}
        values={DEFAULT_FILTER_VALUES}
        onValuesChange={() => {}}
      />,
    );
    expect(html).not.toContain("Clear");
  });

  it("shows clear button when filters are active", () => {
    const activeFilters = {
      search: "dark mode",
      category: "",
      status: "",
      sort: "top_voted" as const,
    };
    const html = renderToStaticMarkup(
      <FeedbackFilterBar
        categoryOptions={CATEGORY_OPTIONS}
        statusOptions={STATUS_OPTIONS}
        values={activeFilters}
        onValuesChange={() => {}}
      />,
    );
    expect(html).toContain("Clear");
    expect(html).toContain("dark mode");
  });

  it("shows result count when provided", () => {
    const html = renderToStaticMarkup(
      <FeedbackFilterBar
        categoryOptions={CATEGORY_OPTIONS}
        statusOptions={STATUS_OPTIONS}
        values={DEFAULT_FILTER_VALUES}
        onValuesChange={() => {}}
        resultCount={5}
      />,
    );
    expect(html).toContain("5");
    expect(html).toContain("items");
  });

  it("uses singular item label when result count is 1", () => {
    const html = renderToStaticMarkup(
      <FeedbackFilterBar
        categoryOptions={CATEGORY_OPTIONS}
        statusOptions={STATUS_OPTIONS}
        values={DEFAULT_FILTER_VALUES}
        onValuesChange={() => {}}
        resultCount={1}
      />,
    );
    expect(html).toContain("1 item");
    expect(html).not.toContain("1 items");
  });
});