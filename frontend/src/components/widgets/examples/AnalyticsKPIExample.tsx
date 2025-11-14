"use client";
import React, { useEffect, useMemo } from "react";
import { useAnalyticsStore } from "@/store/hooks";
import KPIWidget, { KPIMetric } from "../KPIWidget";

export default function AnalyticsKPIExample() {
  const analytics = useAnalyticsStore();

  useEffect(() => {
    if (!analytics.aggregate && !analytics.loading) {
      analytics.fetchAggregate();
    }
  }, [analytics]);

  const metrics: KPIMetric[] = useMemo(() => {
    if (!analytics.aggregate) return [];
    
    return [
      {
        label: "Total Sales",
        value: analytics.aggregate.total_sales,
        unit: "currency",
        trend: "up",
        onClick: () => {
          console.log("Clicked Total Sales");
          // Can trigger drilldown or filter
        },
      },
      {
        label: "Avg Order Value",
        value: analytics.aggregate.avg_order_value,
        unit: "currency",
        trend: "neutral",
      },
      {
        label: "Orders",
        value: analytics.aggregate.orders_count,
        trend: "up",
      },
      {
        label: "Revenue Growth",
        value: analytics.aggregate.revenue_growth_pct || 0,
        unit: "percentage",
        delta: analytics.aggregate.revenue_growth_pct || 0,
        trend: (analytics.aggregate.revenue_growth_pct || 0) >= 0 ? "up" : "down",
      },
    ];
  }, [analytics.aggregate]);

  if (analytics.loading) {
    return <div>Loading KPI data...</div>;
  }

  if (analytics.error) {
    return <div style={{ color: "red" }}>Error: {analytics.error}</div>;
  }

  return (
    <KPIWidget
      metrics={metrics}
      title="Analytics Overview"
      columns={4}
      onMetricClick={(metric, index) => {
        console.log("Clicked metric:", metric.label, "at index:", index);
      }}
    />
  );
}

