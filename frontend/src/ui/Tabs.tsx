"use client";
import React from "react";

type Tab = {
  id: string;
  label: string;
};

type TabsProps = {
  tabs: Tab[];
  activeId: string;
  onChange: (id: string) => void;
};

export default function Tabs({ tabs, activeId, onChange }: TabsProps) {
  return (
    <div role="tablist" aria-label="Dashboard sections" style={{ display: "flex", gap: 8 }}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          role="tab"
          aria-selected={tab.id === activeId}
          tabIndex={tab.id === activeId ? 0 : -1}
          className="interactive-tab"
          data-active={tab.id === activeId}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

