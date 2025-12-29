"use client";
import React, { useEffect, useState } from "react";
import SalesOverviewChart from "@/app/components/charts/SalesOverviewChart";
import ForecastVisualization from "@/app/components/charts/ForecastVisualization";
import KPICard from "@/app/components/cards/KPICard";
import { useAnalyticsAggregate, useAnalyticsForecast } from "@/lib/useAnalytics";
import LoadingState from "@/components/LoadingState";
import ErrorDisplay from "@/components/ErrorDisplay";
import RetryButton from "@/components/RetryButton";
import CollapsiblePod from "@/ui/CollapsiblePod";
import Modal from "@/ui/Modal";

export default function AnalyticsPage() {
  const { data: aggregate, error: aggError, loading: aggLoading, refresh: refreshAgg } = useAnalyticsAggregate();
  const { data: forecast, error: fError, loading: fLoading, refresh: refreshForecast } = useAnalyticsForecast(5);
  const [modalOpen, setModalOpen] = useState(false);

  const loading = aggLoading || fLoading;
  const error = aggError?.message || fError?.message || null;

  const handleRetry = () => {
    refreshAgg();
    refreshForecast();
  };

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 className="heading-gradient">Thryvion Health - Analytics</h1>
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
        onDismiss={() => {}}
      />

      <LoadingState loading={loading} error={error} message="Loading analytics data...">
        {aggregate && (
          <>
            <div className="grid grid-cols-12 gap-4 md:gap-6 mt-3">
              <div className="col-span-12 md:col-span-4">
                <KPICard label="Total Sales" value={`$${aggregate.total_sales.toFixed(2)}`} />
              </div>
              <div className="col-span-12 md:col-span-4">
                <KPICard label="Avg Order Value" value={`$${aggregate.avg_order_value.toFixed(2)}`} />
              </div>
              <div className="col-span-12 md:col-span-4">
                <KPICard label="Orders" value={aggregate.orders_count} />
              </div>
            </div>

            <div className="grid grid-cols-12 gap-4 md:gap-6 mt-4">
              <div className="col-span-12 md:col-span-6">
                <CollapsiblePod
                  title="Sales Overview"
                  rightSlot={
                    <button
                      className="interactive-button"
                      data-size="small"
                      onClick={() => setModalOpen(true)}
                    >
                      View Breakdown
                    </button>
                  }
                >
                  <SalesOverviewChart />
                </CollapsiblePod>
              </div>
              <div className="col-span-12 md:col-span-6">
                <CollapsiblePod title="Forecast">
                  <ForecastVisualization />
                </CollapsiblePod>
              </div>
            </div>
          </>
        )}
      </LoadingState>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Revenue by Day">
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {aggregate?.by_day?.length ? (
            aggregate.by_day.map((entry) => (
              <div key={entry.date} className="glass-card" style={{ padding: 12 }}>
                <div className="metrics-grid__label" style={{ textTransform: "none" }}>{entry.date}</div>
                <div className="metrics-grid__value">${Number(entry.sales).toFixed(2)}</div>
              </div>
            ))
          ) : (
            <p>No revenue data available.</p>
          )}
        </div>
      </Modal>
    </section>
  );
}
