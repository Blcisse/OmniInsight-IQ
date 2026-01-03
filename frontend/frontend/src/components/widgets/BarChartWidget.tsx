"use client";
import React, { useCallback } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";

export type BarChartDataPoint = {
  [key: string]: string | number;
  name?: string;
  category?: string;
};

export interface BarChartWidgetProps {
  data: BarChartDataPoint[];
  dataKeys: { key: string; name: string; color: string }[];
  title?: string;
  xAxisKey?: string;
  yAxisLabel?: string;
  height?: number;
  onBarClick?: (data: BarChartDataPoint, index: number) => void;
  showLegend?: boolean;
  showGrid?: boolean;
  formatTooltip?: (value: any, name: string) => [string, string];
  formatXAxis?: (value: any) => string;
  formatYAxis?: (value: any) => string;
  layout?: "horizontal" | "vertical";
  colors?: string[];
}

export default function BarChartWidget({
  data,
  dataKeys,
  title,
  xAxisKey = "name",
  yAxisLabel,
  height = 300,
  onBarClick,
  showLegend = true,
  showGrid = true,
  formatTooltip,
  formatXAxis,
  formatYAxis,
  layout = "vertical",
  colors,
}: BarChartWidgetProps) {
  const handleClick = useCallback(
    (data: any, index: number) => {
      if (onBarClick) {
        onBarClick(data.payload, index);
      }
    },
    [onBarClick]
  );

  const defaultFormatTooltip = (value: any, name: string) => {
    if (typeof value === "number") {
      return [value.toLocaleString(), name];
    }
    return [String(value), name];
  };

  const defaultFormatXAxis = (value: any) => {
    if (typeof value === "string" && value.length > 15) {
      return value.slice(0, 12) + "...";
    }
    return String(value);
  };

  const isVertical = layout === "vertical";

  return (
    <div className="glass-card" style={{ width: "100%", height }}>
      {title && (
        <h3 style={{ margin: 0, marginBottom: 16, fontSize: 16, fontWeight: 600, color: "var(--text-primary)" }}>
          {title}
        </h3>
      )}
      <ResponsiveContainer width="100%" height={height - (title ? 60 : 40)}>
        <BarChart
          data={data}
          layout={layout}
          margin={{ top: 5, right: 20, left: 0, bottom: isVertical ? 40 : 5 }}
          onClick={handleClick}
        >
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />}
          <XAxis
            dataKey={isVertical ? xAxisKey : undefined}
            type={isVertical ? "category" : "number"}
            tick={{ fontSize: 12, fill: "#64748b" }}
            tickFormatter={formatXAxis || defaultFormatXAxis}
            stroke="#cbd5e1"
            angle={isVertical ? -20 : 0}
            textAnchor={isVertical ? "end" : "middle"}
            height={isVertical ? 60 : undefined}
          />
          <YAxis
            dataKey={!isVertical ? xAxisKey : undefined}
            type={!isVertical ? "category" : "number"}
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
            labelFormatter={(label) => `${xAxisKey}: ${label}`}
          />
          {showLegend && (
            <Legend
              wrapperStyle={{ paddingTop: 16 }}
              iconType="rect"
            />
          )}
          {dataKeys.map(({ key, name, color }, index) => (
            <Bar
              key={key}
              dataKey={key}
              name={name}
              fill={colors?.[index] || color}
              onClick={handleClick}
              isAnimationActive={true}
              animationDuration={300}
            >
              {colors && data.map((entry, i) => (
                <Cell key={`cell-${i}`} fill={colors[i % colors.length]} />
              ))}
            </Bar>
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
