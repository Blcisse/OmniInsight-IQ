"use client";
import React from "react";
import { motion, MotionProps } from "framer-motion";

export interface HoverScaleProps {
  children: React.ReactNode;
  scale?: number;
  glow?: boolean;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}

export default function HoverScale({
  children,
  scale = 1.05,
  glow = true,
  className = "",
  style = {},
  onClick,
}: HoverScaleProps) {
  return (
    <motion.div
      whileHover={{
        scale,
        ...(glow && {
          boxShadow: "var(--shadow-glow-hover)",
        }),
      }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2, ease: "easeInOut" }}
      className={className}
      style={style}
      onClick={onClick}
    >
      {children}
    </motion.div>
  );
}

