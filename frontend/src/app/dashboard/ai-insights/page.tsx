"use client";
import React, { useEffect, useState } from "react";
import { useDashboardStore } from "@/store/dashboardStore";
import ClusterVisualization from "@/components/ai/ClusterVisualization";
import AnomalyVisualization from "@/components/ai/AnomalyVisualization";
import ForecastOverlay from "@/components/ai/ForecastOverlay";
import RecommendationCards from "@/components/ai/RecommendationCards";
import { useAnalyticsStore, useAIInsightsStore } from "@/store/hooks";
import WidgetContainer from "@/components/widgets/WidgetContainer";
import LoadingState from "@/components/LoadingState";
import ErrorDisplay from "@/components/ErrorDisplay";
import RetryButton from "@/components/RetryButton";

export default function AIInsightsPage() {
  const aiInsights = useAIInsightsStore();

  const analytics = useAnalyticsStore();
  const [selectedDataset, setSelectedDataset] = useState<string | null>(null);

  useEffect(() => {
    // Initial load
    aiInsights.fetchClusters("campaign", 3);
    aiInsights.detectSalesAnomalies(2.0);
    aiInsights.fetchRecommendations(5);
  }, []);

  // When dataset changes, trigger AI computation
  useEffect(() => {
    if (selectedDataset && selectedDataset !== aiInsights.currentDataset) {
      aiInsights.setCurrentDataset(selectedDataset);
    }
  }, [selectedDataset]);

  // Fetch forecast when analytics data is available
  useEffect(() => {
    if (analytics.aggregate?.by_day && analytics.aggregate.by_day.length > 0) {
      const history = analytics.aggregate.by_day.map((point) => ({
        date: point.date,
        value: point.sales,
      }));
      aiInsights.fetchForecast(history, "date", "value", 7);
    }
  }, [analytics.aggregate]);

  const handleDatasetChange = async (dataset: string) => {
    setSelectedDataset(dataset);
    // This will trigger setCurrentDataset which calls refreshAIInsights
  };

  const handleRetry = () => {
    aiInsights.refreshAIInsights();
  };

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 className="heading-gradient">AI Insights Dashboard</h1>
        <RetryButton
          onRetry={handleRetry}
          label="Refresh"
          variant="outline"
          disabled={aiInsights.aiLoading}
        />
        {aiInsights.availableDatasets.length > 0 && (
          <select
            value={selectedDataset || aiInsights.currentDataset || ""}
            onChange={(e) => handleDatasetChange(e.target.value)}
            style={{
              padding: "8px 12px",
              borderRadius: 6,
              border: "1px solid #e2e8f0",
              fontSize: 14,
            }}
          >
            <option value="">Select Dataset</option>
            {aiInsights.availableDatasets.map((dataset) => (
              <option key={dataset} value={dataset}>
                {dataset}
              </option>
            ))}
          </select>
        )}
      </div>

      <ErrorDisplay
        error={aiInsights.aiError}
        onRetry={handleRetry}
        variant="card"
        dismissible={true}
        onDismiss={() => aiInsights.setError(null)}
      />

      <LoadingState loading={aiInsights.aiLoading} error={aiInsights.aiError} message="Loading AI insights...">
      <WidgetContainer title="Clustering Analysis">
        {aiInsights.clusters.length > 0 ? (
          <ClusterVisualization
            clusters={aiInsights.clusters}
            onClusterClick={(cluster) => {
              console.log("Selected cluster:", cluster);
            }}
          />
        ) : (
          <div style={{ padding: 24, textAlign: "center", color: "#64748b" }}>
            No clusters available. Click refresh to generate clusters.
          </div>
        )}
      </WidgetContainer>

      <WidgetContainer title="Anomaly Detection">
        {aiInsights.anomalies.length > 0 ? (
          <AnomalyVisualization
            anomalies={aiInsights.anomalies}
            history={analytics.aggregate?.by_day.map((p) => ({ date: p.date, value: p.sales }))}
            onAnomalyClick={(anomaly) => {
              console.log("Selected anomaly:", anomaly);
            }}
          />
        ) : (
          <div style={{ padding: 24, textAlign: "center", color: "#64748b" }}>
            No anomalies detected.
          </div>
        )}
      </WidgetContainer>

      <WidgetContainer title="Forecasting">
        {aiInsights.selectedForecast ? (
          <ForecastOverlay
            forecast={aiInsights.selectedForecast}
            history={analytics.aggregate?.by_day.map((p) => ({ date: p.date, value: p.sales }))}
            onForecastPointClick={(point) => {
              console.log("Selected forecast point:", point);
            }}
          />
        ) : (
          <div style={{ padding: 24, textAlign: "center", color: "#64748b" }}>
            No forecast available. Forecast will be generated from analytics data.
          </div>
        )}
      </WidgetContainer>

      <WidgetContainer title="Recommendations">
        <RecommendationCards
          recommendations={aiInsights.recommendations}
          onRecommendationClick={(rec) => {
            console.log("Selected recommendation:", rec);
          }}
          maxCards={5}
        />
      </WidgetContainer>
      </LoadingState>
    </section>
  );
}

