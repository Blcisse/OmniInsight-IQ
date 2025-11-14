"use client";
import React, { useEffect } from "react";
import { useNutritionIntelligenceStore } from "@/store/hooks";
import LoadingState from "@/components/LoadingState";
import ErrorDisplay from "@/components/ErrorDisplay";
import RetryButton from "@/components/RetryButton";

export default function NutritionPage() {
  const nutrition = useNutritionIntelligenceStore();

  useEffect(() => {
    nutrition.fetchInsights();
    nutrition.fetchProductData();
    nutrition.fetchTrends();
  }, [nutrition.fetchInsights, nutrition.fetchProductData, nutrition.fetchTrends]);

  const handleRetry = () => {
    nutrition.refreshNutritionIntelligence();
  };

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 className="heading-gradient">Nutrition Intelligence</h1>
        <RetryButton
          onRetry={handleRetry}
          label="Refresh"
          variant="outline"
          disabled={nutrition.loading}
        />
      </div>

      <ErrorDisplay
        error={nutrition.error}
        onRetry={handleRetry}
        variant="card"
        dismissible={true}
        onDismiss={() => nutrition.setError(null)}
      />

      <LoadingState loading={nutrition.loading} error={nutrition.error} message="Loading nutrition data...">

      {nutrition.insights.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <h2>Insights</h2>
          <div style={{ display: "grid", gap: 12, marginTop: 12 }}>
            {nutrition.insights.map((insight) => (
              <div
                key={insight.id}
                style={{
                  padding: 16,
                  border: "1px solid #e2e8f0",
                  borderRadius: 8,
                  background: "#fff",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                  <div>
                    <h3 style={{ margin: 0, marginBottom: 8 }}>{insight.title}</h3>
                    <p style={{ margin: 0, color: "#64748b" }}>{insight.description}</p>
                    <div style={{ marginTop: 8, display: "flex", gap: 12, fontSize: 12 }}>
                      <span style={{ color: "#64748b" }}>Type: {insight.type}</span>
                      <span style={{ color: "#64748b" }}>Category: {insight.category}</span>
                      <span style={{ color: "#64748b" }}>Impact: {insight.impact}</span>
                      <span style={{ color: "#64748b" }}>Confidence: {(insight.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {nutrition.trends.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h2>Trends</h2>
          <div style={{ display: "grid", gap: 12, marginTop: 12 }}>
            {nutrition.trends.map((trend, i) => (
              <div
                key={i}
                style={{
                  padding: 16,
                  border: "1px solid #e2e8f0",
                  borderRadius: 8,
                  background: "#fff",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <h3 style={{ margin: 0, marginBottom: 4 }}>{trend.category}</h3>
                    <div style={{ fontSize: 12, color: "#64748b" }}>
                      Trend: {trend.trend} · Change: {(trend.change * 100).toFixed(1)}% · Period: {trend.period}
                    </div>
                    {trend.products.length > 0 && (
                      <div style={{ marginTop: 8, fontSize: 12, color: "#64748b" }}>
                        Products: {trend.products.slice(0, 5).join(", ")}
                        {trend.products.length > 5 && ` +${trend.products.length - 5} more`}
                      </div>
                    )}
                  </div>
                  <div
                    style={{
                      padding: "4px 12px",
                      borderRadius: 4,
                      background:
                        trend.trend === "increasing"
                          ? "#d1fae5"
                          : trend.trend === "decreasing"
                          ? "#fee2e2"
                          : "#e0e7ff",
                      color:
                        trend.trend === "increasing"
                          ? "#065f46"
                          : trend.trend === "decreasing"
                          ? "#991b1b"
                          : "#3730a3",
                      fontSize: 12,
                      fontWeight: 600,
                    }}
                  >
                    {trend.trend.toUpperCase()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {nutrition.productData.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h2>Product Nutrition Data</h2>
          <div style={{ display: "grid", gap: 12, marginTop: 12 }}>
            {nutrition.productData.map((product) => (
              <div
                key={product.productId}
                style={{
                  padding: 16,
                  border: "1px solid #e2e8f0",
                  borderRadius: 8,
                  background: "#fff",
                }}
              >
                <h3 style={{ margin: 0, marginBottom: 8 }}>{product.productName}</h3>
                <div style={{ marginBottom: 8 }}>
                  <div style={{ color: "#64748b", fontSize: 12 }}>Nutrition Score</div>
                  <div style={{ fontSize: 20, fontWeight: 600 }}>{(product.nutritionScore * 100).toFixed(1)}</div>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8, marginTop: 12, fontSize: 12 }}>
                  <div>Calories: {product.healthMetrics.calories}</div>
                  <div>Protein: {product.healthMetrics.protein}g</div>
                  <div>Carbs: {product.healthMetrics.carbs}g</div>
                  <div>Fat: {product.healthMetrics.fat}g</div>
                  <div>Fiber: {product.healthMetrics.fiber}g</div>
                  <div>Sugar: {product.healthMetrics.sugar}g</div>
                </div>
                {product.recommendations.length > 0 && (
                  <div style={{ marginTop: 12 }}>
                    <div style={{ color: "#64748b", fontSize: 12, marginBottom: 4 }}>Recommendations:</div>
                    <ul style={{ margin: 0, paddingLeft: 20, fontSize: 12 }}>
                      {product.recommendations.map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      </LoadingState>
    </section>
  );
}

