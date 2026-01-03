"use client";
import React, { useEffect, useState, useRef } from "react";
import { useDashboardStore } from "@/store/dashboardStore";
import ClusterVisualization from "@/components/ai/ClusterVisualization";
import AnomalyVisualization from "@/components/ai/AnomalyVisualization";
import ForecastOverlay from "@/components/ai/ForecastOverlay";
import RecommendationCards from "@/components/ai/RecommendationCards";
import WidgetContainer from "@/components/widgets/WidgetContainer";
import LoadingState from "@/components/LoadingState";
import ErrorDisplay from "@/components/ErrorDisplay";
import RetryButton from "@/components/RetryButton";

export default function AIInsightsPage() {
  // Individual selectors to avoid infinite loops
  const clusters = useDashboardStore((state) => state.clusters);
  const anomalies = useDashboardStore((state) => state.anomalies);
  const selectedForecast = useDashboardStore((state) => state.selectedForecast);
  const recommendations = useDashboardStore((state) => state.recommendations);
  const aiLoading = useDashboardStore((state) => state.aiLoading);
  const aiError = useDashboardStore((state) => state.aiError);
  const currentDataset = useDashboardStore((state) => state.currentDataset);
  const availableDatasets = useDashboardStore((state) => state.availableDatasets);
  const aggregate = useDashboardStore((state) => state.aggregate);
  
  const fetchClusters = useDashboardStore((state) => state.fetchClusters);
  const detectSalesAnomalies = useDashboardStore((state) => state.detectSalesAnomalies);
  const fetchRecommendations = useDashboardStore((state) => state.fetchRecommendations);
  const setCurrentDataset = useDashboardStore((state) => state.setCurrentDataset);
  const refreshAIInsights = useDashboardStore((state) => state.refreshAIInsights);
  const setError = useDashboardStore((state) => state.setError);
  const fetchForecast = useDashboardStore((state) => state.fetchForecast);

  const [selectedDataset, setSelectedDataset] = useState<string | null>(null);
  const hasFetched = useRef(false);

  useEffect(() => {
    if (!hasFetched.current) {
      hasFetched.current = true;
      // Initial load
      fetchClusters("campaign", 3);
      detectSalesAnomalies(2.0);
      fetchRecommendations(5);
    }
  }, []);

  // When dataset changes, trigger AI computation
  useEffect(() => {
    if (selectedDataset && selectedDataset !== currentDataset) {
      setCurrentDataset(selectedDataset);
    }
  }, [selectedDataset, currentDataset, setCurrentDataset]);

  // Fetch forecast when analytics data is available
  useEffect(() => {
    if (aggregate?.by_day && aggregate.by_day.length > 0) {
      const history = aggregate.by_day.map((point) => ({
        date: point.date,
        value: point.sales,
      }));
      fetchForecast(history, "date", "value", 7);
    }
  }, [aggregate, fetchForecast]);

  const handleDatasetChange = async (dataset: string) => {
    setSelectedDataset(dataset);
    // This will trigger setCurrentDataset which calls refreshAIInsights
  };

  const handleRetry = () => {
    refreshAIInsights();
  };

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 className="heading-gradient">AI Insights Dashboard</h1>
        <RetryButton
          onRetry={handleRetry}
          label="Refresh"
          variant="outline"
          disabled={aiLoading}
        />
        {availableDatasets && availableDatasets.length > 0 && (
          <select
            value={selectedDataset || currentDataset || ""}
            onChange={(e) => handleDatasetChange(e.target.value)}
            style={{
              padding: "8px 12px",
              borderRadius: 6,
              border: "1px solid #e2e8f0",
              fontSize: 14,
            }}
          >
            <option value="">Select Dataset</option>
            {availableDatasets.map((dataset) => (
              <option key={dataset} value={dataset}>
                {dataset}
              </option>
            ))}
          </select>
        )}
      </div>

      <ErrorDisplay
        error={aiError}
        onRetry={handleRetry}
        variant="card"
        dismissible={true}
        onDismiss={() => setError(null)}
      />

      <LoadingState loading={aiLoading} error={aiError} message="Loading AI insights...">
      <WidgetContainer title="Clustering Analysis">
        {clusters.length > 0 ? (
          <ClusterVisualization
            clusters={clusters}
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
        {anomalies.length > 0 ? (
          <AnomalyVisualization
            anomalies={anomalies}
            history={aggregate?.by_day.map((p) => ({ date: p.date, value: p.sales }))}
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
        {selectedForecast ? (
          <ForecastOverlay
            forecast={selectedForecast}
            history={aggregate?.by_day.map((p) => ({ date: p.date, value: p.sales }))}
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
          recommendations={recommendations}
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

