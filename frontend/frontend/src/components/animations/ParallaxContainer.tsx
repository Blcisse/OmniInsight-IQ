"use client";
import React, { useEffect, useState } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

export interface ParallaxContainerProps {
  children: React.ReactNode;
  speed?: number;
  disabled?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

export default function ParallaxContainer({
  children,
  speed = 0.5,
  disabled = false,
  className = "",
  style = {},
}: ParallaxContainerProps) {
  const [isMobile, setIsMobile] = useState(false);
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 1000], [0, 1000 * speed]);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // Disable parallax on mobile or if explicitly disabled
  if (disabled || isMobile) {
    return <div className={className} style={style}>{children}</div>;
  }

  return (
    <motion.div
      style={{
        ...style,
        y,
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

