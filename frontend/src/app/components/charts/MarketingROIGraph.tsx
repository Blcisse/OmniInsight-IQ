"use client";
import React from "react";
import LineChartWidget, { LineChartDataPoint } from "@/components/widgets/LineChartWidget";

type Props = {
  data: { name: string; roi: number }[];
};

export default function MarketingROIGraph({ data }: Props) {
  const chartData: LineChartDataPoint[] = data.map((item) => ({
    name: item.name,
    roi: item.roi,
  }));

  return (
    <LineChartWidget
      data={chartData}
      dataKeys={[{ key: "roi", name: "ROI", color: "#38B6FF" }]}
      title="Campaign ROI"
      xAxisKey="name"
      yAxisLabel="ROI"
      height={280}
      showLegend={false}
      formatTooltip={(value) => [`${Number(value).toFixed(2)}x`, "ROI"]}
    />
  );
}

