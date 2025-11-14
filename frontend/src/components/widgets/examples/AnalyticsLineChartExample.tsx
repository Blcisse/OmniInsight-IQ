"use client";
import React, { useEffect, useMemo } from "react";
import { useAnalyticsStore } from "@/store/hooks";
import LineChartWidget, { LineChartDataPoint } from "../LineChartWidget";

export default function AnalyticsLineChartExample() {
  const analytics = useAnalyticsStore();

  useEffect(() => {
    if (!analytics.aggregate && !analytics.loading) {
      analytics.fetchAggregate();
    }
  }, [analytics]);

  const chartData: LineChartDataPoint[] = useMemo(() => {
    if (!analytics.aggregate?.by_day) return [];
    return analytics.aggregate.by_day.map((point) => ({
      date: point.date,
      sales: point.sales,
    }));
  }, [analytics.aggregate]);

  const handleDataPointClick = (data: LineChartDataPoint, index: number) => {
    console.log("Clicked data point:", data, "at index:", index);
    // You can add drilldown functionality here
  };

  if (analytics.loading) {
    return <div>Loading chart data...</div>;
  }

  if (analytics.error) {
    return <div style={{ color: "red" }}>Error: {analytics.error}</div>;
  }

  return (
    <LineChartWidget
      data={chartData}
      dataKeys={[
        { key: "sales", name: "Sales", color: "#3b82f6" },
      ]}
      title="Sales Trends"
      xAxisKey="date"
      yAxisLabel="Sales ($)"
      height={300}
      onDataPointClick={handleDataPointClick}
      formatTooltip={(value) => [`$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, "Sales"]}
      formatXAxis={(value) => {
        if (typeof value === "string") {
          const date = new Date(value);
          return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
        }
        return String(value);
      }}
    />
  );
}

