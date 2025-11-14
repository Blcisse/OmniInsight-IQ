"use client";
import React from "react";
import { motion } from "framer-motion";
import RetryButton from "./RetryButton";

export interface ErrorDisplayProps {
  error: string | null;
  onRetry?: () => void;
  title?: string;
  variant?: "inline" | "card" | "full";
  dismissible?: boolean;
  onDismiss?: () => void;
}

export default function ErrorDisplay({
  error,
  onRetry,
  title = "Error",
  variant = "card",
  dismissible = false,
  onDismiss,
}: ErrorDisplayProps) {
  if (!error) return null;

  const getVariantStyles = () => {
    switch (variant) {
      case "inline":
        return {
          container: {
            padding: 8,
            background: "#fef2f2",
            border: "1px solid #fecaca",
            borderRadius: 4,
            fontSize: 14,
          },
        };
      case "card":
        return {
          container: {
            padding: 16,
            background: "#fff",
            border: "1px solid #fecaca",
            borderRadius: 8,
            marginBottom: 16,
          },
        };
      case "full":
        return {
          container: {
            padding: 32,
            background: "#fff",
            border: "2px solid #fecaca",
            borderRadius: 12,
            textAlign: "center" as const,
            minHeight: 200,
            display: "flex",
            flexDirection: "column" as const,
            alignItems: "center",
            justifyContent: "center",
          },
        };
      default:
        return {
          container: {
            padding: 16,
            background: "#fef2f2",
            border: "1px solid #fecaca",
            borderRadius: 8,
          },
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      style={styles.container}
    >
      <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between" }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <span style={{ fontSize: 20 }}>⚠️</span>
            <h3
              style={{
                margin: 0,
                fontSize: variant === "inline" ? 14 : 16,
                fontWeight: 600,
                color: "#991b1b",
              }}
            >
              {title}
            </h3>
          </div>
          <p
            style={{
              margin: 0,
              color: "#7f1d1d",
              fontSize: variant === "inline" ? 12 : 14,
              lineHeight: 1.5,
            }}
          >
            {error}
          </p>
        </div>
        {dismissible && onDismiss && (
          <button
            onClick={onDismiss}
            className="interactive-button"
            data-variant="danger"
            data-size="small"
            style={{ marginLeft: 12, width: 32, height: 32, justifyContent: "center" }}
            aria-label="Dismiss error"
          >
            ×
          </button>
        )}
      </div>
      {onRetry && (
        <div style={{ marginTop: 12 }}>
          <RetryButton onRetry={onRetry} />
        </div>
      )}
    </motion.div>
  );
}
