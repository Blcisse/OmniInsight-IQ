"use client";
import React, { useEffect, useMemo } from "react";
import { useMarketingStore } from "@/store/hooks";
import BarChartWidget, { BarChartDataPoint } from "../BarChartWidget";

export default function MarketingBarChartExample() {
  const marketing = useMarketingStore();

  useEffect(() => {
    if (marketing.campaigns.length === 0 && !marketing.loading) {
      marketing.fetchCampaigns();
    }
  }, [marketing]);

  const chartData: BarChartDataPoint[] = useMemo(() => {
    return marketing.campaigns.slice(0, 10).map((campaign) => ({
      name: campaign.campaign_name || campaign.name || `Campaign ${campaign.id}`,
      roi: campaign.roi || 0,
      spend: campaign.spend,
      clicks: campaign.clicks,
    }));
  }, [marketing.campaigns]);

  const handleBarClick = (data: BarChartDataPoint, index: number) => {
    console.log("Clicked bar:", data, "at index:", index);
    // You can navigate to campaign details or show more info
  };

  if (marketing.loading) {
    return <div>Loading marketing data...</div>;
  }

  if (marketing.error) {
    return <div style={{ color: "red" }}>Error: {marketing.error}</div>;
  }

  return (
    <BarChartWidget
      data={chartData}
      dataKeys={[
        { key: "roi", name: "ROI", color: "#22c55e" },
      ]}
      title="Campaign ROI Comparison"
      xAxisKey="name"
      yAxisLabel="ROI (x)"
      height={300}
      onBarClick={handleBarClick}
      formatTooltip={(value) => [`${Number(value).toFixed(2)}x`, "ROI"]}
      formatXAxis={(value) => {
        if (typeof value === "string" && value.length > 20) {
          return value.slice(0, 17) + "...";
        }
        return String(value);
      }}
    />
  );
}

