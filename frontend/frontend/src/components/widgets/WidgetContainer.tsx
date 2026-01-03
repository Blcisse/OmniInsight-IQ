"use client";
import React from "react";

export interface WidgetContainerProps {
  children: React.ReactNode;
  title?: string;
  className?: string;
  responsive?: boolean;
}

/**
 * Responsive container for widgets that adapts to screen size
 */
export default function WidgetContainer({
  children,
  title,
  className,
  responsive = true,
}: WidgetContainerProps) {
  const containerStyle: React.CSSProperties = {
    width: "100%",
    padding: responsive ? "16px 8px" : 16,
    marginBottom: 16,
  };

  const gridStyle: React.CSSProperties = responsive
    ? {
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
        gap: 16,
      }
    : {
        display: "block",
      };

  return (
    <div style={containerStyle} className={className}>
      {title && (
        <h2
          style={{
            margin: 0,
            marginBottom: 16,
            fontSize: 20,
            fontWeight: 600,
            color: "#1e293b",
          }}
        >
          {title}
        </h2>
      )}
      <div style={gridStyle}>{children}</div>
    </div>
  );
}

