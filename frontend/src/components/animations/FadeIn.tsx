"use client";
import React from "react";
import { motion, MotionProps } from "framer-motion";

export interface FadeInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  y?: number;
  className?: string;
  style?: React.CSSProperties;
}

export default function FadeIn({
  children,
  delay = 0,
  duration = 0.5,
  y = 20,
  className = "",
  style = {},
}: FadeInProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration, delay, ease: "easeOut" }}
      className={className}
      style={style}
    >
      {children}
    </motion.div>
  );
}

/**
 * Staggered fade-in for lists
 */
export function StaggeredFadeIn({
  children,
  delay = 0,
  staggerDelay = 0.1,
  className = "",
}: {
  children: React.ReactNode[];
  delay?: number;
  staggerDelay?: number;
  className?: string;
}) {
  return (
    <>
      {children.map((child, index) => (
        <FadeIn key={index} delay={delay + index * staggerDelay} className={className}>
          {child}
        </FadeIn>
      ))}
    </>
  );
}

