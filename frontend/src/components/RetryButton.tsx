"use client";
import React, { useState } from "react";
import { motion } from "framer-motion";

export interface RetryButtonProps {
  onRetry: () => void | Promise<void>;
  label?: string;
  variant?: "primary" | "secondary" | "outline";
  size?: "small" | "medium" | "large";
  disabled?: boolean;
}

export default function RetryButton({
  onRetry,
  label = "Retry",
  variant = "primary",
  size = "medium",
  disabled = false,
}: RetryButtonProps) {
  const [retrying, setRetrying] = useState(false);

  const handleRetry = async () => {
    if (disabled || retrying) return;
    
    setRetrying(true);
    try {
      await onRetry();
    } finally {
      // Small delay to show retry state
      setTimeout(() => setRetrying(false), 300);
    }
  };

  return (
    <motion.button
      onClick={handleRetry}
      disabled={disabled || retrying}
      whileHover={{
        scale: disabled || retrying ? 1 : 1.05,
        boxShadow: disabled || retrying ? undefined : "var(--shadow-glow-hover)",
      }}
      whileTap={{ scale: disabled || retrying ? 1 : 0.95 }}
      transition={{ duration: 0.2, ease: "easeInOut" }}
      className="interactive-button"
      data-variant={variant}
      data-size={size}
      style={{
        cursor: disabled || retrying ? "not-allowed" : "pointer",
        fontWeight: 500,
        opacity: disabled || retrying ? 0.6 : 1,
      }}
    >
      {retrying ? (
        <>
          <div
            style={{
              width: 12,
              height: 12,
              border: "2px solid currentColor",
              borderTop: "2px solid transparent",
              borderRadius: "50%",
              animation: "spin 0.6s linear infinite",
            }}
          />
          Retrying...
        </>
      ) : (
        <>
          <span>↻</span>
          {label}
        </>
      )}
      <style jsx>{`
        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </motion.button>
  );
}
