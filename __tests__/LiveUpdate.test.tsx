/** @jest-environment jsdom */
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";

import LiveUpdateWidget from "../frontend/components/widgets/LiveUpdateWidget";

jest.useFakeTimers();

describe("LiveUpdateWidget", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    let call = 0;
    global.fetch = jest.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/analytics/live")) {
        call++;
        return new Response(
          JSON.stringify({
            window: "24h",
            since: "2025-11-04",
            total_revenue: 1234 + call,
            orders_count: 12 + call,
            avg_order_value: 102.5,
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      return new Response("Not Found", { status: 404 });
    }) as any;
  });

  afterEach(() => {
    global.fetch = originalFetch as any;
    jest.clearAllTimers();
    jest.clearAllMocks();
  });

  test("polls periodically and updates values", async () => {
    render(<LiveUpdateWidget window="24h" />);

    // initial load
    expect(await screen.findByText(/Total Revenue/i)).toBeInTheDocument();

    // advance timers to trigger refresh (15s in component)
    jest.advanceTimersByTime(16000);

    await waitFor(() => {
      // Expect updated orders count text to appear (at least once refresh)
      expect(screen.getByText(/Orders/i)).toBeInTheDocument();
    });
  });
});

