"use client";
import React from "react";
import { motion } from "framer-motion";

export interface GlassContainerProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  hover?: boolean;
  glow?: boolean;
  padding?: "none" | "sm" | "md" | "lg" | "xl";
  rounded?: "sm" | "md" | "lg" | "xl";
  gradient?: boolean;
  onClick?: () => void;
  animate?: boolean;
}

const paddingMap = {
  none: 0,
  sm: "0.5rem",
  md: "1rem",
  lg: "1.5rem",
  xl: "2rem",
};

const radiusMap = {
  sm: "var(--radius-sm)",
  md: "var(--radius-md)",
  lg: "var(--radius-lg)",
  xl: "var(--radius-xl)",
};

export default function GlassContainer({
  children,
  className = "",
  style = {},
  hover = true,
  glow = true,
  padding = "md",
  rounded = "lg",
  gradient = false,
  onClick,
  animate = true,
}: GlassContainerProps) {
  const containerStyle: React.CSSProperties = {
    background: gradient
      ? "linear-gradient(135deg, rgba(20, 199, 208, 0.1), rgba(56, 182, 255, 0.05))"
      : "var(--glass-bg)",
    backdropFilter: "var(--glass-blur)",
    WebkitBackdropFilter: "var(--glass-blur)",
    border: "1px solid var(--glass-border)",
    borderRadius: radiusMap[rounded],
    padding: paddingMap[padding],
    boxShadow: glow ? "var(--shadow-glow)" : "var(--shadow-subtle)",
    transition: "all var(--transition-base)",
    cursor: onClick ? "pointer" : "default",
    ...style,
  };

  const hoverStyle: React.CSSProperties = hover
    ? {
        ":hover": {
          background: gradient
            ? "linear-gradient(135deg, rgba(20, 199, 208, 0.15), rgba(56, 182, 255, 0.1))"
            : "var(--glass-bg-hover)",
          boxShadow: glow ? "var(--shadow-glow-hover)" : "var(--shadow-medium)",
          borderColor: "var(--accent-glow)",
          transform: "translateY(-2px)",
        },
      }
    : {};

  const MotionComponent = animate ? motion.div : "div";

  return (
    <MotionComponent
      className={`glass-container ${className}`}
      style={containerStyle}
      onClick={onClick}
      whileHover={hover && animate ? { y: -2, scale: 1.01 } : undefined}
      whileTap={onClick && animate ? { scale: 0.98 } : undefined}
      transition={{ duration: 0.2 }}
    >
      {children}
    </MotionComponent>
  );
}

