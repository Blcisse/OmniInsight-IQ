"use client";
import React, { useCallback } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export type LineChartDataPoint = {
  [key: string]: string | number;
  date?: string;
  name?: string;
};

export interface LineChartWidgetProps {
  data: LineChartDataPoint[];
  dataKeys: { key: string; name: string; color: string }[];
  title?: string;
  xAxisKey?: string;
  yAxisLabel?: string;
  height?: number;
  onDataPointClick?: (data: LineChartDataPoint, index: number) => void;
  showLegend?: boolean;
  showGrid?: boolean;
  formatTooltip?: (value: any, name: string) => [string, string];
  formatXAxis?: (value: any) => string;
  formatYAxis?: (value: any) => string;
}

export default function LineChartWidget({
  data,
  dataKeys,
  title,
  xAxisKey = "date",
  yAxisLabel,
  height = 300,
  onDataPointClick,
  showLegend = true,
  showGrid = true,
  formatTooltip,
  formatXAxis,
  formatYAxis,
}: LineChartWidgetProps) {
  const handleClick = useCallback(
    (data: any, index: number) => {
      if (onDataPointClick) {
        onDataPointClick(data.payload, index);
      }
    },
    [onDataPointClick]
  );

  const defaultFormatTooltip = (value: any, name: string) => {
    if (typeof value === "number") {
      return [value.toLocaleString(), name];
    }
    return [String(value), name];
  };

  const defaultFormatXAxis = (value: any) => {
    if (typeof value === "string" && value.length > 10) {
      return value.slice(0, 10);
    }
    return String(value);
  };

  return (
    <div className="glass-card" style={{ width: "100%", height }}>
      {title && (
        <h3 style={{ margin: 0, marginBottom: 16, fontSize: 16, fontWeight: 600, color: "var(--text-primary)" }}>
          {title}
        </h3>
      )}
      <ResponsiveContainer width="100%" height={height - (title ? 60 : 40)}>
        <LineChart
          data={data}
          margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
          onClick={handleClick}
        >
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />}
          <XAxis
            dataKey={xAxisKey}
            tick={{ fontSize: 12, fill: "#64748b" }}
            tickFormatter={formatXAxis || defaultFormatXAxis}
            stroke="#cbd5e1"
          />
          <YAxis
            tick={{ fontSize: 12, fill: "#64748b" }}
            tickFormatter={formatYAxis}
            stroke="#cbd5e1"
            label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: "insideLeft", style: { fill: "#64748b" } } : undefined}
          />
          <Tooltip
            contentStyle={{
              background: "rgba(8, 10, 18, 0.82)",
              border: "1px solid rgba(56, 182, 255, 0.4)",
              borderRadius: 8,
              backdropFilter: "blur(12px)",
              WebkitBackdropFilter: "blur(12px)",
              padding: "10px 14px",
              color: "#f8fafc",
              boxShadow: "0 8px 20px rgba(0,0,0,0.45)",
            }}
            formatter={formatTooltip || defaultFormatTooltip}
            labelFormatter={(label) => `Date: ${label}`}
          />
          {showLegend && (
            <Legend
              wrapperStyle={{ paddingTop: 16 }}
              iconType="line"
            />
          )}
          {dataKeys.map(({ key, name, color }) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              name={name}
              stroke={color}
              strokeWidth={2}
              dot={{ r: 4, fill: color }}
              activeDot={{ r: 6, fill: color }}
              isAnimationActive={true}
              animationDuration={300}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
