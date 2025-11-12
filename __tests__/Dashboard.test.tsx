/** @jest-environment jsdom */
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";

// Components under test
import SalesOverviewChart from "../src/app/components/charts/SalesOverviewChart";
import ForecastVisualization from "../src/app/components/charts/ForecastVisualization";

// Mock global fetch
const originalFetch = global.fetch;

beforeEach(() => {
  global.fetch = jest.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.includes("/api/analytics/predict")) {
      return new Response(
        JSON.stringify({
          forecast: [
            { date: "2025-11-05", predicted_sales: 1200 },
            { date: "2025-11-06", predicted_sales: 1215 },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    }
    if (url.includes("/api/analytics")) {
      return new Response(
        JSON.stringify({
          by_day: [
            { date: "2025-11-01", sales: 1000 },
            { date: "2025-11-02", sales: 1100 },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    }
    return new Response("Not Found", { status: 404 });
  }) as any;
});

afterEach(() => {
  global.fetch = originalFetch as any;
  jest.clearAllMocks();
});

describe("Dashboard Charts", () => {
  test("SalesOverviewChart renders bars after data load", async () => {
    render(<SalesOverviewChart />);
    expect(screen.getByText(/Loading sales overview/i)).toBeInTheDocument();

    await waitFor(() => {
      // Bars are divs with title attribute including date and value
      const bar = screen.getByTitle(/2025-11-01: 1000/i);
      expect(bar).toBeInTheDocument();
    });
  });

  test("ForecastVisualization renders forecast bars", async () => {
    render(<ForecastVisualization horizon={2} />);
    expect(screen.getByText(/Loading forecast/i)).toBeInTheDocument();

    await waitFor(() => {
      const bar = screen.getByTitle(/2025-11-05: 1200/i);
      expect(bar).toBeInTheDocument();
    });

    // Header shows horizon days
    expect(screen.getByText(/Forecast \(2 days\)/i)).toBeInTheDocument();
  });
});

