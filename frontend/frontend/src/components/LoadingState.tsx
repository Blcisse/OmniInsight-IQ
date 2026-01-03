"use client";
import React from "react";
import { motion } from "framer-motion";

export interface LoadingStateProps {
  loading: boolean;
  error: string | null;
  children?: React.ReactNode;
  message?: string;
  size?: "small" | "medium" | "large";
  fullScreen?: boolean;
}

export default function LoadingState({
  loading,
  error,
  children,
  message = "Loading...",
  size = "medium",
  fullScreen = false,
}: LoadingStateProps) {
  if (error) {
    return null; // Error should be handled by ErrorDisplay component
  }

  if (!loading) {
    return <>{children}</>;
  }

  const sizeStyles = {
    small: { width: 24, height: 24, borderWidth: 2 },
    medium: { width: 40, height: 40, borderWidth: 3 },
    large: { width: 60, height: 60, borderWidth: 4 },
  };

  const spinnerStyle: React.CSSProperties = {
    ...sizeStyles[size],
    border: `${sizeStyles[size].borderWidth}px solid transparent`,
    borderTop: `${sizeStyles[size].borderWidth}px solid var(--accent-blue)`,
    borderRight: `${sizeStyles[size].borderWidth}px solid var(--accent-cyan)`,
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
    boxShadow: "0 0 10px rgba(56, 182, 255, 0.5), inset 0 0 10px rgba(20, 199, 208, 0.3)",
  };

  const containerStyle: React.CSSProperties = fullScreen
    ? {
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(13, 13, 13, 0.95)",
        zIndex: 9999,
      }
    : {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: 32,
        minHeight: 200,
      };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={containerStyle}
    >
      <div style={spinnerStyle} />
      {message && (
        <p style={{ marginTop: 16, color: "var(--text-secondary)", fontSize: 14 }}>{message}</p>
      )}
      <style jsx>{`
        @keyframes spin {
          0% {
            transform: rotate(0deg);
            box-shadow: 0 0 10px rgba(56, 182, 255, 0.5), inset 0 0 10px rgba(20, 199, 208, 0.3);
          }
          50% {
            box-shadow: 0 0 20px rgba(56, 182, 255, 0.8), inset 0 0 15px rgba(20, 199, 208, 0.5);
          }
          100% {
            transform: rotate(360deg);
            box-shadow: 0 0 10px rgba(56, 182, 255, 0.5), inset 0 0 10px rgba(20, 199, 208, 0.3);
          }
        }
      `}</style>
    </motion.div>
  );
}

/**
 * Inline loading spinner for smaller components
 */
export function InlineLoader({ size = "small" }: { size?: "small" | "medium" | "large" }) {
  const sizeStyles = {
    small: { width: 16, height: 16, borderWidth: 2 },
    medium: { width: 24, height: 24, borderWidth: 2 },
    large: { width: 32, height: 32, borderWidth: 3 },
  };

  return (
    <div
      style={{
        ...sizeStyles[size],
        border: `${sizeStyles[size].borderWidth}px solid transparent`,
        borderTop: `${sizeStyles[size].borderWidth}px solid var(--accent-blue)`,
        borderRight: `${sizeStyles[size].borderWidth}px solid var(--accent-cyan)`,
        borderRadius: "50%",
        animation: "spin 0.6s linear infinite",
        display: "inline-block",
        boxShadow: "0 0 8px rgba(56, 182, 255, 0.4)",
      }}
    >
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
    </div>
  );
}

/**
 * Futuristic pulsing dot loader
 */
export function PulsingDotLoader({ size = "medium" }: { size?: "small" | "medium" | "large" }) {
  const sizeMap = {
    small: 8,
    medium: 12,
    large: 16,
  };

  const dotSize = sizeMap[size];

  return (
    <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          style={{
            width: dotSize,
            height: dotSize,
            borderRadius: "50%",
            background: "var(--primary-gradient)",
            boxShadow: "0 0 10px var(--accent-glow)",
          }}
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: i * 0.2,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}

