"use client";
import React, { useEffect } from "react";

type Side = "left" | "right";

type Props = {
  open: boolean;
  side?: Side;
  title?: string;
  onClose: () => void;
  width?: number; // px
  children: React.ReactNode;
};

export default function Drawer({ open, side = "right", title, onClose, width = 360, children }: Props) {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    if (open) document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const panelStyle: React.CSSProperties = {
    position: "fixed",
    top: 0,
    bottom: 0,
    [side]: 0 as any,
    width,
    background: "#fff",
    boxShadow: side === "right" ? "-4px 0 16px rgba(0,0,0,0.15)" : "4px 0 16px rgba(0,0,0,0.15)",
    zIndex: 60,
    display: "flex",
    flexDirection: "column",
  };

  return (
    <div style={backdrop} onClick={onClose}>
      <div style={panelStyle} onClick={(e) => e.stopPropagation()}>
        <div style={header}>
          <strong>{title}</strong>
          <button onClick={onClose} aria-label="Close">✕</button>
        </div>
        <div style={{ padding: 16, overflow: "auto" }}>{children}</div>
      </div>
    </div>
  );
}

const backdrop: React.CSSProperties = {
  position: "fixed",
  inset: 0,
  background: "rgba(0,0,0,0.3)",
  zIndex: 50,
};

const header: React.CSSProperties = {
  padding: 12,
  borderBottom: "1px solid #e2e8f0",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
};

