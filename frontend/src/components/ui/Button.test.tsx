import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Button } from "./Button";

describe("Button", () => {
  it("renders children", () => {
    const html = renderToStaticMarkup(<Button>Click me</Button>);
    expect(html).toContain("Click me");
    expect(html).toContain("<button");
  });

  it("applies variant and size classes", () => {
    const html = renderToStaticMarkup(
      <Button variant="danger" size="lg">
        Delete
      </Button>
    );
    expect(html).toContain("bg-red-600");
    expect(html).toContain("text-base");
  });

  it("shows a loading spinner when isLoading is true", () => {
    const html = renderToStaticMarkup(<Button isLoading>Loading</Button>);
    expect(html).toContain("Loading");
    expect(html).toContain("animate-spin");
  });
});
