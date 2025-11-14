"use client";
import React from "react";
import { motion } from "framer-motion";
import type { RecommendationResponse } from "@/api/recommendationsApi";

interface RecommendationCardsProps {
  recommendations: RecommendationResponse | null;
  onRecommendationClick?: (recommendation: { item: string; score: number }) => void;
  maxCards?: number;
}

export default function RecommendationCards({
  recommendations,
  onRecommendationClick,
  maxCards = 5,
}: RecommendationCardsProps) {
  if (!recommendations || !recommendations.recommendations || recommendations.recommendations.length === 0) {
    return (
      <div style={{ padding: 24, textAlign: "center", color: "#64748b" }}>
        No recommendations available
      </div>
    );
  }

  const items = recommendations.recommendations.slice(0, maxCards);

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "#22c55e"; // green
    if (score >= 0.6) return "#3b82f6"; // blue
    if (score >= 0.4) return "#f59e0b"; // amber
    return "#ef4444"; // red
  };

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16, color: "#1e293b" }}>
        AI Recommendations
      </h3>
      <div style={{ display: "grid", gap: 12 }}>
        {items.map((rec, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            onClick={() => onRecommendationClick && onRecommendationClick(rec)}
            style={{
              padding: 16,
              border: "1px solid #e2e8f0",
              borderRadius: 8,
              background: "#fff",
              cursor: onRecommendationClick ? "pointer" : "default",
              transition: "all 0.2s",
            }}
            onMouseEnter={(e) => {
              if (onRecommendationClick) {
                e.currentTarget.style.borderColor = "#3b82f6";
                e.currentTarget.style.boxShadow = "0 4px 6px -1px rgba(0, 0, 0, 0.1)";
              }
            }}
            onMouseLeave={(e) => {
              if (onRecommendationClick) {
                e.currentTarget.style.borderColor = "#e2e8f0";
                e.currentTarget.style.boxShadow = "none";
              }
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, marginBottom: 4, color: "#1e293b" }}>
                  {rec.item}
                </div>
                {rec.reason && (
                  <div style={{ fontSize: 12, color: "#64748b", marginTop: 4 }}>
                    {rec.reason}
                  </div>
                )}
                {rec.category && (
                  <div
                    style={{
                      display: "inline-block",
                      marginTop: 8,
                      padding: "2px 8px",
                      borderRadius: 4,
                      background: "#f1f5f9",
                      color: "#475569",
                      fontSize: 11,
                    }}
                  >
                    {rec.category}
                  </div>
                )}
              </div>
              <div
                style={{
                  padding: "8px 12px",
                  borderRadius: 6,
                  background: getScoreColor(rec.score) + "20",
                  color: getScoreColor(rec.score),
                  fontSize: 14,
                  fontWeight: 600,
                  minWidth: 60,
                  textAlign: "center",
                }}
              >
                {(rec.score * 100).toFixed(0)}%
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

