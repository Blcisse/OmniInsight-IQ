"use client";
import React from "react";
import BarChartWidget, { BarChartDataPoint } from "../widgets/BarChartWidget";
import type { Cluster } from "@/api/clusteringApi";

interface ClusterVisualizationProps {
  clusters: Cluster[];
  onClusterClick?: (cluster: Cluster) => void;
}

const clusterColors = [
  "#3b82f6", // blue
  "#22c55e", // green
  "#f59e0b", // amber
  "#ef4444", // red
  "#8b5cf6", // purple
  "#ec4899", // pink
  "#06b6d4", // cyan
  "#f97316", // orange
];

export default function ClusterVisualization({
  clusters,
  onClusterClick,
}: ClusterVisualizationProps) {
  const distributionData: BarChartDataPoint[] = clusters.map((cluster) => ({
    name: `Cluster ${cluster.cluster}`,
    count: cluster.size,
    cluster: cluster.cluster,
  }));

  const handleBarClick = (data: BarChartDataPoint) => {
    const cluster = clusters.find((c) => c.cluster === data.cluster);
    if (cluster && onClusterClick) {
      onClusterClick(cluster);
    }
  };

  return (
    <div>
      <BarChartWidget
        data={distributionData}
        dataKeys={[{ key: "count", name: "Items", color: "#3b82f6" }]}
        title="Cluster Distribution"
        xAxisKey="name"
        yAxisLabel="Count"
        height={300}
        onBarClick={handleBarClick}
        colors={clusterColors}
      />
      <div style={{ marginTop: 16, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
        {clusters.map((cluster) => (
          <div
            key={cluster.cluster}
            onClick={() => onClusterClick && onClusterClick(cluster)}
            style={{
              padding: 16,
              border: "2px solid",
              borderColor: clusterColors[cluster.cluster % clusterColors.length],
              borderRadius: 8,
              background: "#fff",
              cursor: onClusterClick ? "pointer" : "default",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <div
                style={{
                  width: 16,
                  height: 16,
                  borderRadius: "50%",
                  background: clusterColors[cluster.cluster % clusterColors.length],
                }}
              />
              <strong>Cluster {cluster.cluster}</strong>
            </div>
            <div style={{ fontSize: 14, color: "#64748b" }}>
              Size: {cluster.size} items
            </div>
            {cluster.members && cluster.members.length > 0 && (
              <div style={{ marginTop: 8, fontSize: 12, color: "#94a3b8" }}>
                Members: {cluster.members.slice(0, 3).join(", ")}
                {cluster.members.length > 3 && ` +${cluster.members.length - 3} more`}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

