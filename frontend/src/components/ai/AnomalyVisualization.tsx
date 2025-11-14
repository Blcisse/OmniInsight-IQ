"use client";
import React, { useMemo } from "react";
import LineChartWidget, { LineChartDataPoint } from "../widgets/LineChartWidget";
import type { AnomalyData } from "@/api/anomalyApi";

interface AnomalyVisualizationProps {
  anomalies: AnomalyData[];
  history?: Array<{ date: string; value: number }>;
  onAnomalyClick?: (anomaly: AnomalyData) => void;
}

export default function AnomalyVisualization({
  anomalies,
  history,
  onAnomalyClick,
}: AnomalyVisualizationProps) {
  const chartData: LineChartDataPoint[] = useMemo(() => {
    if (!history) return [];
    return history.map((point) => {
      const anomaly = anomalies.find((a) => a.date === point.date);
      return {
        date: point.date,
        value: point.value,
        isAnomaly: anomaly?.is_anomaly || false,
        anomalyScore: anomaly?.score,
      };
    });
  }, [history, anomalies]);

  const anomalyPoints: LineChartDataPoint[] = useMemo(() => {
    return anomalies
      .filter((a) => a.is_anomaly)
      .map((a) => ({
        date: a.date,
        anomalyValue: a.value,
        score: a.score,
      }));
  }, [anomalies]);

  return (
    <div>
      <LineChartWidget
        data={chartData}
        dataKeys={[
          { key: "value", name: "Value", color: "#3b82f6" },
          { key: "anomalyValue", name: "Anomaly", color: "#ef4444" },
        ]}
        title="Anomaly Detection"
        xAxisKey="date"
        yAxisLabel="Value"
        height={300}
        onDataPointClick={(data) => {
          if (data.isAnomaly && onAnomalyClick) {
            const anomaly = anomalies.find((a) => a.date === data.date);
            if (anomaly) onAnomalyClick(anomaly);
          }
        }}
      />
      <div style={{ marginTop: 16 }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>Detected Anomalies</h3>
        <div style={{ display: "grid", gap: 8 }}>
          {anomalies
            .filter((a) => a.is_anomaly)
            .slice(0, 10)
            .map((anomaly, index) => (
              <div
                key={index}
                onClick={() => onAnomalyClick && onAnomalyClick(anomaly)}
                style={{
                  padding: 12,
                  border: "1px solid #fee2e2",
                  borderRadius: 6,
                  background: "#fef2f2",
                  cursor: onAnomalyClick ? "pointer" : "default",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <div style={{ fontWeight: 600, color: "#991b1b" }}>Anomaly Detected</div>
                    <div style={{ fontSize: 12, color: "#64748b", marginTop: 4 }}>
                      Date: {anomaly.date} · Value: {anomaly.value.toLocaleString()}
                    </div>
                  </div>
                  {anomaly.score !== undefined && (
                    <div
                      style={{
                        padding: "4px 8px",
                        borderRadius: 4,
                        background: "#fee2e2",
                        color: "#991b1b",
                        fontSize: 12,
                        fontWeight: 600,
                      }}
                    >
                      Score: {anomaly.score.toFixed(2)}
                    </div>
                  )}
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

