"use client";
import React from "react";
import { motion } from "framer-motion";
import PodContainer from "@/components/containers/PodContainer";

export interface KPIMetric {
  label: string;
  value: number | string;
  delta?: number; // percentage change
  unit?: string;
  trend?: "up" | "down" | "neutral";
  formatValue?: (value: number | string) => string;
  onClick?: () => void;
}

export interface KPIWidgetProps {
  metrics: KPIMetric[];
  title?: string;
  columns?: number;
  onMetricClick?: (metric: KPIMetric, index: number) => void;
}

export default function KPIWidget({
  metrics,
  title,
  columns = 3,
  onMetricClick,
}: KPIWidgetProps) {
  // Responsive columns based on screen size
  const [responsiveColumns, setResponsiveColumns] = React.useState(columns);

  React.useEffect(() => {
    const updateColumns = () => {
      const width = window.innerWidth;
      if (width < 640) {
        // Mobile
        setResponsiveColumns(1);
      } else if (width < 1024) {
        // Tablet
        setResponsiveColumns(2);
      } else {
        // Desktop
        setResponsiveColumns(columns);
      }
    };

    updateColumns();
    window.addEventListener("resize", updateColumns);
    return () => window.removeEventListener("resize", updateColumns);
  }, [columns]);
  const formatValue = (metric: KPIMetric): string => {
    if (metric.formatValue) {
      return metric.formatValue(metric.value);
    }
    if (typeof metric.value === "number") {
      if (metric.unit === "currency") {
        return `$${metric.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      }
      if (metric.unit === "percentage") {
        return `${metric.value.toFixed(1)}%`;
      }
      return metric.value.toLocaleString();
    }
    return String(metric.value);
  };

  const getDeltaColor = (delta?: number, trend?: "up" | "down" | "neutral") => {
    if (trend === "up") return "var(--accent-cyan)";
    if (trend === "down") return "#ef4444";
    if (trend === "neutral") return "var(--text-tertiary)";
    if (typeof delta === "number") {
      return delta >= 0 ? "var(--accent-cyan)" : "#ef4444";
    }
    return "var(--text-tertiary)";
  };

  const getDeltaIcon = (delta?: number, trend?: "up" | "down" | "neutral") => {
    if (trend === "up") return "▲";
    if (trend === "down") return "▼";
    if (trend === "neutral") return "—";
    if (typeof delta === "number") {
      return delta >= 0 ? "▲" : "▼";
    }
    return "";
  };

  return (
    <PodContainer title={title} padding="lg" variant="default" style={{ width: "100%" }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${responsiveColumns}, 1fr)`,
          gap: 16,
        }}
      >
        {metrics.map((metric, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            whileHover={{
              scale: 1.02,
              boxShadow: "var(--shadow-glow-hover)",
              borderColor: "var(--accent-glow)",
            }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            onClick={() => {
              if (onMetricClick) {
                onMetricClick(metric, index);
              }
              if (metric.onClick) {
                metric.onClick();
              }
            }}
            style={{
              padding: "1rem",
              border: "1px solid var(--glass-border)",
              borderRadius: "var(--radius-md)",
              background: "var(--glass-bg)",
              cursor: onMetricClick || metric.onClick ? "pointer" : "default",
              transition: "all var(--transition-base)",
              backdropFilter: "var(--glass-blur)",
              WebkitBackdropFilter: "var(--glass-blur)",
            }}
          >
            <div style={{ color: "var(--text-secondary)", fontSize: "0.75rem", marginBottom: "0.5rem" }}>
              {metric.label}
            </div>
            <div
              style={{
                fontSize: "1.5rem",
                fontWeight: 700,
                background: "var(--primary-gradient)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
                marginBottom: metric.delta !== undefined || metric.trend ? "0.5rem" : 0,
              }}
            >
              {formatValue(metric)}
            </div>
            {(metric.delta !== undefined || metric.trend) && (
              <div
                style={{
                  fontSize: 12,
                  color: getDeltaColor(metric.delta, metric.trend),
                  fontWeight: 500,
                }}
              >
                {getDeltaIcon(metric.delta, metric.trend)}{" "}
                {metric.delta !== undefined && `${Math.abs(metric.delta).toFixed(2)}%`}
                {metric.trend && !metric.delta && "Change"}
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </PodContainer>
  );
}

