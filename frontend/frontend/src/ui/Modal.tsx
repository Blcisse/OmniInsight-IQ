"use client";
import React, { useEffect, useState } from "react";
import { createPortal } from "react-dom";

type ModalProps = {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
};

export default function Modal({ open, onClose, title, children }: ModalProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  if (!mounted || !open) return null;

  return createPortal(
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby={title ? "modal-title" : undefined}>
      <div className="modal-content">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          {title && (
            <h2 id="modal-title" style={{ margin: 0 }}>
              {title}
            </h2>
          )}
          <button
            className="interactive-button"
            data-size="small"
            data-variant="outline"
            aria-label="Close modal"
            onClick={onClose}
          >
            ×
          </button>
        </div>
        <div>{children}</div>
      </div>
    </div>,
    document.body
  );
}

