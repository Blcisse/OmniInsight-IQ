"use client";
import React from "react";
import { motion } from "framer-motion";
import GlassContainer, { GlassContainerProps } from "./GlassContainer";
import FadeIn from "@/components/animations/FadeIn";

export interface PodContainerProps extends Omit<GlassContainerProps, "children"> {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  headerAction?: React.ReactNode;
  footer?: React.ReactNode;
  variant?: "default" | "elevated" | "minimal";
}

export default function PodContainer({
  children,
  title,
  subtitle,
  headerAction,
  footer,
  variant = "default",
  className = "",
  style = {},
  ...glassProps
}: PodContainerProps) {
  const variantStyles = {
    default: {
      background: "var(--glass-bg)",
      boxShadow: "var(--shadow-glow)",
    },
    elevated: {
      background: "linear-gradient(135deg, rgba(20, 199, 208, 0.1), rgba(56, 182, 255, 0.05))",
      boxShadow: "var(--shadow-glow-strong)",
    },
    minimal: {
      background: "rgba(255, 255, 255, 0.02)",
      boxShadow: "var(--shadow-subtle)",
    },
  };

  const combinedStyle: React.CSSProperties = {
    ...variantStyles[variant],
    ...style,
  };

  return (
    <FadeIn delay={0.1} duration={0.4}>
      <GlassContainer
        className={`pod-container ${className}`}
        style={combinedStyle}
        glow={variant !== "minimal"}
        {...glassProps}
      >
      {(title || subtitle || headerAction) && (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            marginBottom: subtitle ? "0.5rem" : "1rem",
            paddingBottom: "1rem",
            borderBottom: "1px solid var(--glass-border)",
          }}
        >
          <div>
            {title && (
              <h3
                style={{
                  margin: 0,
                  fontSize: "1.25rem",
                  fontWeight: 600,
                  background: "var(--primary-gradient)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                }}
              >
                {title}
              </h3>
            )}
            {subtitle && (
              <p
                style={{
                  margin: "0.25rem 0 0 0",
                  fontSize: "0.875rem",
                  color: "var(--text-secondary)",
                }}
              >
                {subtitle}
              </p>
            )}
          </div>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}

      <div style={{ flex: 1 }}>{children}</div>

      {footer && (
        <div
          style={{
            marginTop: "1rem",
            paddingTop: "1rem",
            borderTop: "1px solid var(--glass-border)",
          }}
        >
          {footer}
        </div>
      )}
      </GlassContainer>
    </FadeIn>
  );
}

