"use client";
import React, { useEffect, useRef } from "react";
import { useDashboardStore } from "@/store/dashboardStore";
import LoadingState from "@/components/LoadingState";
import ErrorDisplay from "@/components/ErrorDisplay";
import RetryButton from "@/components/RetryButton";
import CollapsiblePod from "@/ui/CollapsiblePod";

export default function ForecastingPage() {
  const metrics = useDashboardStore((state) => state.metrics);
  const forecasts = useDashboardStore((state) => state.forecasts);
  const loading = useDashboardStore((state) => state.loading);
  const error = useDashboardStore((state) => state.error);
  const fetchForecastMetrics = useDashboardStore((state) => state.fetchForecastMetrics);
  const refreshForecasting = useDashboardStore((state) => state.refreshForecasting);
  const setError = useDashboardStore((state) => state.setError);

  const hasFetched = useRef(false);

  useEffect(() => {
    if (!hasFetched.current) {
      hasFetched.current = true;
      fetchForecastMetrics();
    }
  }, []);

  const handleRetry = () => {
    refreshForecasting();
  };

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 className="heading-gradient">Forecasting</h1>
        <RetryButton
          onRetry={handleRetry}
          label="Refresh"
          variant="outline"
          disabled={loading}
        />
      </div>

      <ErrorDisplay
        error={error}
        onRetry={handleRetry}
        variant="card"
        dismissible={true}
        onDismiss={() => setError(null)}
      />

      <LoadingState loading={loading} error={error} message="Loading forecast data...">

      {metrics && (
        <CollapsiblePod title="Forecast Metrics">
          <div className="metrics-grid">
            <div>
              <div className="metrics-grid__label">Forecasted Revenue</div>
              <div className="metrics-grid__value">${metrics.totalForecastedRevenue.toFixed(2)}</div>
            </div>
            <div>
              <div className="metrics-grid__label">Forecasted Growth</div>
              <div className="metrics-grid__value">{(metrics.forecastedGrowth * 100).toFixed(1)}%</div>
            </div>
            <div>
              <div className="metrics-grid__label">Confidence</div>
              <div className="metrics-grid__value">{(metrics.confidence * 100).toFixed(1)}%</div>
            </div>
            <div>
              <div className="metrics-grid__label">Horizon</div>
              <div className="metrics-grid__value">{metrics.horizon} days</div>
            </div>
          </div>
        </CollapsiblePod>
      )}

      {forecasts.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h2>Product Forecasts</h2>
          <div style={{ display: "grid", gap: 12, marginTop: 12 }}>
            {forecasts.map((forecast) => (
              <div
                key={forecast.productId}
                style={{
                  padding: 16,
                  border: "1px solid #e2e8f0",
                  borderRadius: 8,
                  background: "#fff",
                }}
              >
                <h3 style={{ margin: 0, marginBottom: 8 }}>{forecast.productName || forecast.productId}</h3>
                {forecast.accuracy && (
                  <div style={{ marginBottom: 8, fontSize: 12, color: "#64748b" }}>
                    Accuracy: {(forecast.accuracy * 100).toFixed(1)}%
                  </div>
                )}
                <div style={{ display: "flex", alignItems: "flex-end", gap: 4, height: 120, marginTop: 12 }}>
                  {forecast.forecast.map((point, i) => {
                    const max = Math.max(...forecast.forecast.map((p) => p.value), 1);
                    return (
                      <div
                        key={i}
                        title={`${point.date}: ${point.value.toFixed(2)}`}
                        style={{
                          flex: 1,
                          background: "#3b82f6",
                          height: `${(point.value / max) * 100}%`,
                          minHeight: 4,
                          borderRadius: 2,
                        }}
                      />
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {forecasts.length === 0 && !loading && (
        <div style={{ marginTop: 24, padding: 24, textAlign: "center", color: "#64748b" }}>
          <p>No forecasts available. Select products to generate forecasts.</p>
        </div>
      )}
      </LoadingState>
    </section>
  );
}
