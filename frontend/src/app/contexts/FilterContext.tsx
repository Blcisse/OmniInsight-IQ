"use client";
import React, { createContext, useCallback, useContext, useMemo, useState } from "react";

export type FilterState = {
  region?: string;
  startDate?: string; // YYYY-MM-DD
  endDate?: string;   // YYYY-MM-DD
  productId?: string;
};

type FilterContextValue = FilterState & {
  setRegion: (v?: string) => void;
  setProductId: (v?: string) => void;
  setDateRange: (start?: string, end?: string) => void;
  clear: () => void;
  isActive: boolean;
};

const FilterContext = createContext<FilterContextValue | undefined>(undefined);

export function FilterProvider({ children }: { children: React.ReactNode }) {
  const [region, setRegion] = useState<string | undefined>(undefined);
  const [startDate, setStartDate] = useState<string | undefined>(undefined);
  const [endDate, setEndDate] = useState<string | undefined>(undefined);
  const [productId, setProductId] = useState<string | undefined>(undefined);

  const setDateRange = useCallback((start?: string, end?: string) => {
    setStartDate(start || undefined);
    setEndDate(end || undefined);
  }, []);

  const clear = useCallback(() => {
    setRegion(undefined);
    setStartDate(undefined);
    setEndDate(undefined);
    setProductId(undefined);
  }, []);

  const value = useMemo<FilterContextValue>(() => {
    const isActive = Boolean(region || startDate || endDate || productId);
    return {
      region,
      startDate,
      endDate,
      productId,
      setRegion,
      setProductId,
      setDateRange,
      clear,
      isActive,
    };
  }, [region, startDate, endDate, productId, setDateRange, clear]);

  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;
}

export function useFilter() {
  const ctx = useContext(FilterContext);
  if (!ctx) throw new Error("useFilter must be used within FilterProvider");
  return ctx;
}

