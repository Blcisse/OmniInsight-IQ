"use client";
import React, { useMemo, useState } from "react";

export type TableColumn<T = any> = {
  key: keyof T | string;
  label: string;
  sortable?: boolean;
  format?: (value: any, row: T) => React.ReactNode;
  width?: string | number;
  align?: "left" | "center" | "right";
};

export interface TableWidgetProps<T = any> {
  data: T[];
  columns: TableColumn<T>[];
  title?: string;
  pageSize?: number;
  sortable?: boolean;
  onRowClick?: (row: T, index: number) => void;
  onSort?: (key: string, direction: "asc" | "desc") => void;
  emptyMessage?: string;
  loading?: boolean;
}

export default function TableWidget<T extends Record<string, any>>({
  data,
  columns,
  title,
  pageSize = 10,
  sortable = true,
  onRowClick,
  onSort,
  emptyMessage = "No data available",
  loading = false,
}: TableWidgetProps<T>) {
  const [page, setPage] = useState(0);
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const sortedData = useMemo(() => {
    if (!sortKey || !sortable) return data;
    const copy = [...data];
    copy.sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (aVal === bVal) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      const comparison = aVal < bVal ? -1 : 1;
      return sortDir === "asc" ? comparison : -comparison;
    });
    return copy;
  }, [data, sortKey, sortDir, sortable]);

  const paginatedData = useMemo(() => {
    const start = page * pageSize;
    return sortedData.slice(start, start + pageSize);
  }, [sortedData, page, pageSize]);

  const pageCount = Math.ceil(sortedData.length / pageSize);

  const handleSort = (key: string) => {
    if (!sortable) return;
    if (key === sortKey) {
      const newDir = sortDir === "asc" ? "desc" : "asc";
      setSortDir(newDir);
      if (onSort) {
        onSort(key, newDir);
      }
    } else {
      setSortKey(key);
      setSortDir("asc");
      if (onSort) {
        onSort(key, "asc");
      }
    }
  };

  const getValue = (row: T, column: TableColumn<T>) => {
    const value = row[column.key as keyof T];
    if (column.format) {
      return column.format(value, row);
    }
    if (value == null) return "—";
    if (typeof value === "number") {
      return value.toLocaleString();
    }
    return String(value);
  };

  if (loading) {
    return (
      <div
        style={{
          width: "100%",
          padding: 16,
          border: "1px solid #e2e8f0",
          borderRadius: 8,
          background: "#fff",
        }}
      >
        {title && (
          <h3 style={{ margin: 0, marginBottom: 16, fontSize: 16, fontWeight: 600, color: "#1e293b" }}>
            {title}
          </h3>
        )}
        <div style={{ textAlign: "center", padding: 40, color: "#64748b" }}>Loading...</div>
      </div>
    );
  }

  return (
    <div
      style={{
        width: "100%",
        padding: "16px 8px",
        border: "1px solid #e2e8f0",
        borderRadius: 8,
        background: "#fff",
        overflowX: "auto",
      }}
      className="table-widget"
    >
      {title && (
        <h3 style={{ margin: 0, marginBottom: 16, fontSize: 16, fontWeight: 600, color: "#1e293b" }}>
          {title}
        </h3>
      )}
      {paginatedData.length === 0 ? (
        <div style={{ textAlign: "center", padding: 40, color: "#64748b" }}>{emptyMessage}</div>
      ) : (
        <>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {columns.map((column, index) => (
                    <th
                      key={index}
                      onClick={() => column.sortable !== false && handleSort(column.key as string)}
                      style={{
                        ...thStyle,
                        cursor: column.sortable !== false && sortable ? "pointer" : "default",
                        textAlign: column.align || "left",
                        width: column.width,
                        userSelect: "none",
                        backgroundColor: sortKey === column.key ? "#f1f5f9" : undefined,
                      }}
                    >
                      <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
                        {column.label}
                        {sortable && column.sortable !== false && sortKey === column.key && (
                          <span style={{ fontSize: 10 }}>{sortDir === "asc" ? "▲" : "▼"}</span>
                        )}
                      </span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {paginatedData.map((row, rowIndex) => (
                  <tr
                    key={rowIndex}
                    onClick={() => onRowClick && onRowClick(row, rowIndex)}
                    style={{
                      ...trStyle,
                      cursor: onRowClick ? "pointer" : "default",
                    }}
                    onMouseEnter={(e) => {
                      if (onRowClick) {
                        e.currentTarget.style.backgroundColor = "#f8fafc";
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (onRowClick) {
                        e.currentTarget.style.backgroundColor = "transparent";
                      }
                    }}
                  >
                    {columns.map((column, colIndex) => (
                      <td
                        key={colIndex}
                        style={{
                          ...tdStyle,
                          textAlign: column.align || "left",
                        }}
                      >
                        {getValue(row, column)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {pageCount > 1 && (
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 16, alignItems: "center" }}>
              <button
                disabled={page <= 0}
                onClick={() => setPage(0)}
                style={buttonStyle}
              >
                First
              </button>
              <button
                disabled={page <= 0}
                onClick={() => setPage(page - 1)}
                style={buttonStyle}
              >
                Prev
              </button>
              <span style={{ fontSize: 14, color: "#64748b" }}>
                Page {page + 1} / {pageCount}
              </span>
              <button
                disabled={page + 1 >= pageCount}
                onClick={() => setPage(page + 1)}
                style={buttonStyle}
              >
                Next
              </button>
              <button
                disabled={page + 1 >= pageCount}
                onClick={() => setPage(pageCount - 1)}
                style={buttonStyle}
              >
                Last
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

const thStyle: React.CSSProperties = {
  textAlign: "left",
  padding: "12px 8px",
  borderBottom: "2px solid #e2e8f0",
  color: "#475569",
  fontSize: 12,
  fontWeight: 600,
  textTransform: "uppercase",
  letterSpacing: "0.05em",
};

const trStyle: React.CSSProperties = {
  transition: "background-color 0.2s",
};

const tdStyle: React.CSSProperties = {
  padding: "12px 8px",
  borderBottom: "1px solid #f1f5f9",
  fontSize: 14,
  color: "#1e293b",
};

const buttonStyle: React.CSSProperties = {
  padding: "6px 12px",
  border: "1px solid #e2e8f0",
  borderRadius: 4,
  background: "#fff",
  color: "#475569",
  cursor: "pointer",
  fontSize: 14,
  transition: "all 0.2s",
};

