/** @jest-environment jsdom */
import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

import SalesTrendChart from "../frontend/components/charts/SalesTrendChart";
import MarketingROIGraph from "../frontend/components/charts/MarketingROIGraph";
import RevenueByRegion from "../frontend/components/charts/RevenueByRegion";

describe("Charts render", () => {
  test("SalesTrendChart shows lines for data", () => {
    const data = [
      { date: "2025-11-01", sales: 1000 },
      { date: "2025-11-02", sales: 1100 },
    ];
    render(<SalesTrendChart data={data} />);
    // Recharts renders SVG paths; assert presence of SVG
    expect(document.querySelector("svg")).toBeInTheDocument();
  });

  test("MarketingROIGraph renders bars", () => {
    const data = [
      { name: "Campaign A", roi: 2.1 },
      { name: "Campaign B", roi: 3.4 },
    ];
    render(<MarketingROIGraph data={data} />);
    expect(document.querySelector("svg")).toBeInTheDocument();
  });

  test("RevenueByRegion renders pie segments", () => {
    const data = [
      { region: "NA", revenue: 10000 },
      { region: "EU", revenue: 8000 },
    ];
    render(<RevenueByRegion data={data} />);
    expect(document.querySelector("svg")).toBeInTheDocument();
  });
});

