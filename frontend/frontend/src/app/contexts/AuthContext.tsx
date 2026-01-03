"use client";
import React, { createContext, useContext, useMemo, useState } from "react";

type Role = "admin" | "analyst" | "viewer";
type User = { id: string; name: string; email: string; role: Role } | null;

type AuthContextValue = {
  user: User;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  role: Role;
  can: (perm: "manage" | "analyze" | "view") => boolean;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User>(null);

  async function login(email: string, _password: string) {
    // Mock auth: accept any non-empty email
    if (!email) throw new Error("Email is required");
    // Simple role assignment by email prefix for demo purposes
    const prefix = (email.split("@")[0] || "user").toLowerCase();
    const role: Role = prefix.includes("admin") ? "admin" : prefix.includes("analyst") ? "analyst" : "viewer";
    setUser({ id: "u_1", name: prefix || "User", email, role });
  }

  function logout() {
    setUser(null);
  }

  function can(perm: "manage" | "analyze" | "view") {
    const r: Role = user?.role || "viewer";
    if (perm === "view") return true; // everyone can view
    if (perm === "analyze") return r === "admin" || r === "analyst";
    if (perm === "manage") return r === "admin";
    return false;
  }

  const value = useMemo(
    () => ({ user, login, logout, role: user?.role || "viewer", can }),
    [user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
