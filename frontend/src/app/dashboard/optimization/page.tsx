"use client";
import React, { useEffect } from "react";
import { useOptimizationMetrics, useOptimizationRecommendations } from "@/lib/useOptimization";
import LoadingState from "@/components/LoadingState";
import ErrorDisplay from "@/components/ErrorDisplay";
import RetryButton from "@/components/RetryButton";

export default function OptimizationPage() {
  const { data: metrics, loading: mLoading, error: mErr, refresh: refreshM } = useOptimizationMetrics();
  const { data: recommendations, loading: rLoading, error: rErr, refresh: refreshR } = useOptimizationRecommendations();
  const loading = mLoading || rLoading;
  const error = mErr?.message || rErr?.message || null;

  const handleRetry = () => {
    refreshM();
    refreshR();
  };

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 className="heading-gradient">Optimization</h1>
        <RetryButton onRetry={handleRetry} label="Refresh" variant="outline" disabled={loading} />
      </div>

      <ErrorDisplay error={error} onRetry={handleRetry} variant="card" dismissible={true} onDismiss={() => {}} />

      <LoadingState loading={loading} error={error} message="Loading optimization data...">

      {metrics && (
        <div className="glass-card" style={{ marginTop: 16 }}>
          <h2 style={{ marginBottom: 12 }}>Optimization Metrics</h2>
          <div className="metrics-grid">
            <div>
              <div className="metrics-grid__label">Current Efficiency</div>
              <div className="metrics-grid__value">{(metrics.currentEfficiency * 100).toFixed(1)}%</div>
            </div>
            <div>
              <div className="metrics-grid__label">Target Efficiency</div>
              <div className="metrics-grid__value">{(metrics.targetEfficiency * 100).toFixed(1)}%</div>
            </div>
            <div>
              <div className="metrics-grid__label">Improvement Potential</div>
              <div className="metrics-grid__value">{(metrics.improvementPotential * 100).toFixed(1)}%</div>
            </div>
          </div>
        </div>
      )}

      {Array.isArray(recommendations) && recommendations.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h2>Recommendations</h2>
          <div style={{ display: "grid", gap: 12, marginTop: 12 }}>
            {recommendations.map((rec) => (
              <div
                key={rec.id}
                className="glass-card"
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                  <div>
                    <h3 style={{ margin: 0, marginBottom: 8 }}>{rec.title}</h3>
                    <p style={{ margin: 0, color: "var(--text-secondary)" }}>{rec.description}</p>
                    <div style={{ marginTop: 8, display: "flex", gap: 12, fontSize: 12, color: "var(--text-tertiary)" }}>
                      <span>Type: {rec.type}</span>
                      <span>Impact: {rec.impact}</span>
                      <span>Confidence: {(rec.confidence * 100).toFixed(0)}%</span>
                      <span>Value: ${rec.estimatedValue.toFixed(2)}</span>
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    {rec.status === "pending" && (
                      <>
                        <button
                          onClick={() => {}}
                          className="interactive-button"
                          data-variant="success"
                          data-size="small"
                        >
                          Apply
                        </button>
                        <button
                          onClick={() => {}}
                          className="interactive-button"
                          data-variant="danger"
                          data-size="small"
                        >
                          Reject
                        </button>
                      </>
                    )}
                    {rec.status === "applied" && (
                      <span className="badge badge--success">
                        Applied
                      </span>
                    )}
                    {rec.status === "rejected" && (
                      <span className="badge badge--danger">
                        Rejected
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      </LoadingState>
    </section>
  );
}
