"use client";
import React, { useMemo } from "react";
import LineChartWidget, { LineChartDataPoint } from "../widgets/LineChartWidget";
import type { ForecastResponse } from "@/api/forecastingApi";

interface ForecastOverlayProps {
  forecast: ForecastResponse;
  history?: Array<{ date: string; value: number }>;
  onForecastPointClick?: (point: { date: string; value: number }) => void;
}

export default function ForecastOverlay({
  forecast,
  history,
  onForecastPointClick,
}: ForecastOverlayProps) {
  const chartData: LineChartDataPoint[] = useMemo(() => {
    const data: LineChartDataPoint[] = [];

    // Add history data
    if (history) {
      history.forEach((point) => {
        data.push({
          date: point.date,
          historical: point.value,
        });
      });
    }

    // Add forecast data
    forecast.forecast.forEach((point) => {
      const existing = data.find((d) => d.date === point.date);
      if (existing) {
        existing.forecast = point.value;
        if (point.lower_bound !== undefined) existing.lowerBound = point.lower_bound;
        if (point.upper_bound !== undefined) existing.upperBound = point.upper_bound;
      } else {
        data.push({
          date: point.date,
          forecast: point.value,
          lowerBound: point.lower_bound,
          upperBound: point.upper_bound,
        });
      }
    });

    return data.sort((a, b) => {
      const dateA = new Date(a.date as string).getTime();
      const dateB = new Date(b.date as string).getTime();
      return dateA - dateB;
    });
  }, [forecast, history]);

  return (
    <div>
      <LineChartWidget
        data={chartData}
        dataKeys={[
          { key: "historical", name: "Historical", color: "#3b82f6" },
          { key: "forecast", name: "Forecast", color: "#6366f1" },
        ]}
        title={`Forecast (Confidence: ${(forecast.confidence * 100).toFixed(1)}%)`}
        xAxisKey="date"
        yAxisLabel="Value"
        height={350}
        onDataPointClick={(data) => {
          if (data.forecast && onForecastPointClick) {
            onForecastPointClick({ date: data.date as string, value: data.forecast as number });
          }
        }}
        formatTooltip={(value, name) => {
          if (typeof value === "number") {
            return [value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }), name];
          }
          return [String(value), name];
        }}
      />
      {forecast.model_type && (
        <div style={{ marginTop: 8, fontSize: 12, color: "#64748b", textAlign: "center" }}>
          Model: {forecast.model_type}
        </div>
      )}
    </div>
  );
}

