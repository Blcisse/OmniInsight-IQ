"use client";

import React, { useMemo } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

type NavItem = {
  href: string;
  label: string;
  exact?: boolean;
};
const linkStyle: React.CSSProperties = {
  display: "block",
  padding: "0.75rem 1rem",
  borderRadius: "var(--radius-md)",
  textDecoration: "none",
  color: "var(--text-secondary)",
  fontWeight: 500,
  transition: "all var(--transition-base)",
  marginBottom: "0.25rem",
  background: "transparent",
  border: "1px solid transparent",
};

const activeLinkStyle: React.CSSProperties = {
  ...linkStyle,
  background: "var(--glass-bg)",
  color: "var(--text-primary)",
  fontWeight: 600,
  border: "1px solid var(--accent-glow)",
  boxShadow: "var(--shadow-glow)",
};

export default function Sidebar() {
  const pathname = usePathname();

  /** -------------------------
   * Active link highlighting
   * ------------------------- */
  const isActive = ({ href, exact }: NavItem) => {
    if (href === "/dashboard") {
      return pathname === "/dashboard" || pathname === "/";
    }

    if (exact) {
      return pathname === href;
    }

    return pathname?.startsWith(href);
  };

  const navItems = useMemo<NavItem[]>(
    () => [
      { href: "/dashboard", label: "Dashboard" },
      { href: "/dashboard/analytics", label: "Analytics" },
      { href: "/dashboard/marketing", label: "Marketing" },
      { href: "/dashboard/optimization", label: "Optimization" },
      { href: "/dashboard/forecasting", label: "Forecasting" },
      { href: "/dashboard/nutrition", label: "Nutrition Intelligence" },
      { href: "/dashboard/sales", label: "Sales" },
      { href: "/dashboard/ai-insights", label: "AI Insights" },
      { href: "/insightops", label: "InsightOps Studio (Executive)", exact: true },
      { href: "/insightops/analyst", label: "InsightOps Studio (Analyst)" },
    ],
    []
  );

  return (
    <motion.aside
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      style={{
        width: 240,
        padding: "1rem",
        background: "var(--base-dark-lighter)",
        borderRight: "1px solid var(--glass-border)",
        backdropFilter: "var(--glass-blur)",
        WebkitBackdropFilter: "var(--glass-blur)",
      }}
    >
      <nav>
        <motion.h2
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          style={{
            fontSize: "0.875rem",
            fontWeight: 600,
            color: "var(--text-secondary)",
            marginBottom: "1rem",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
          }}
        >
          Navigation
        </motion.h2>

        {navItems.map((item) => {
          const { href, label } = item;
          const active = isActive(item);
          return (
            <motion.div
              key={href}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2 }}
              whileHover={{ x: 4 }}
              whileTap={{ scale: 0.98 }}
            >
              <Link
                href={href}
                style={active ? activeLinkStyle : linkStyle}
                onMouseEnter={(e) => {
                  if (!active) {
                    e.currentTarget.style.background = "var(--glass-bg)";
                    e.currentTarget.style.borderColor = "var(--glass-border)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!active) {
                    e.currentTarget.style.background = "transparent";
                    e.currentTarget.style.borderColor = "transparent";
                  }
                }}
              >
                {label}
              </Link>
            </motion.div>
          );
        })}
      </nav>
    </motion.aside>
  );
}
