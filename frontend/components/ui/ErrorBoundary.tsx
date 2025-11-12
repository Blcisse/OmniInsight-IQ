"use client";
import React from "react";

type Props = {
  fallback?: React.ReactNode;
  children: React.ReactNode;
};

type State = {
  hasError: boolean;
  error?: Error | null;
};

export default class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // Hook for logging
    if (typeof window !== "undefined") {
      // eslint-disable-next-line no-console
      console.error("ErrorBoundary caught:", error, errorInfo);
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div style={{ border: "1px solid #fecaca", background: "#fef2f2", color: "#991b1b", padding: 16, borderRadius: 8 }}>
            <strong>Something went wrong.</strong>
            <div style={{ marginTop: 8, fontSize: 12 }}>{this.state.error?.message}</div>
          </div>
        )
      );
    }
    return this.props.children;
  }
}

