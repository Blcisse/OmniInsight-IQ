"use client";
import React, { useId, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

type Props = {
  title: string;
  defaultOpen?: boolean;
  rightSlot?: React.ReactNode;
  children: React.ReactNode;
};

export default function CollapsiblePod({ title, defaultOpen = true, rightSlot, children }: Props) {
  const [open, setOpen] = useState(defaultOpen);
  const id = useId();
  const contentId = `${id}-content`;

  return (
    <section className="glass-card" role="region" aria-labelledby={`${id}-hdr`}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <h3 id={`${id}-hdr`} style={{ margin: 0 }}>{title}</h3>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          {rightSlot}
          <button
            className="interactive-button"
            data-size="small"
            aria-expanded={open}
            aria-controls={contentId}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? "Collapse" : "Expand"}
          </button>
        </div>
      </header>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            id={contentId}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
            style={{ overflow: "hidden", marginTop: 12 }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}

