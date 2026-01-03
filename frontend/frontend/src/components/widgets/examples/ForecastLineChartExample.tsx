"use client";
import React, { useEffect, useMemo } from "react";
import { useAnalyticsStore } from "@/store/hooks";
import LineChartWidget, { LineChartDataPoint } from "../LineChartWidget";

export default function ForecastLineChartExample({ horizon = 7 }: { horizon?: number }) {
  const analytics = useAnalyticsStore();

  useEffect(() => {
    if (!analytics.predictions && !analytics.loading) {
      analytics.fetchPredictions(horizon);
    }
  }, [analytics, horizon]);

  const chartData: LineChartDataPoint[] = useMemo(() => {
    if (!analytics.predictions) return [];
    const { forecast, dates } = analytics.predictions;
    return forecast.map((value, index) => ({
      date: dates?.[index] || `Day ${index + 1}`,
      forecast: value,
    }));
  }, [analytics.predictions]);

  if (analytics.loading) {
    return <div>Loading forecast data...</div>;
  }

  if (analytics.error) {
    return <div style={{ color: "red" }}>Error: {analytics.error}</div>;
  }

  return (
    <LineChartWidget
      data={chartData}
      dataKeys={[
        { key: "forecast", name: "Forecasted Sales", color: "#6366f1" },
      ]}
      title={`Sales Forecast (${horizon} days)`}
      xAxisKey="date"
      yAxisLabel="Forecasted Sales ($)"
      height={300}
      formatTooltip={(value) => [`$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, "Forecast"]}
    />
  );
}

