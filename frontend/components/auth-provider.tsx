"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "@/services/api";
import { getMe } from "@/services/auth";
import { tokenStorage } from "@/services/token";
import type { User } from "@/types/auth";

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

interface AuthContextValue {
  user: User | null;
  status: AuthStatus;
  signIn: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const [token, setToken] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Reading localStorage (an external, non-React store) can only happen after mount
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setToken(tokenStorage.get());
    setReady(true);
  }, []);

  const { data: user, error } = useQuery({
    queryKey: ["me"],
    queryFn: getMe,
    enabled: !!token,
    retry: false,
  });

  const logout = useCallback(() => {
    tokenStorage.clear();
    setToken(null);
    queryClient.clear();
  }, [queryClient]);

  useEffect(() => {
    // Reacting to an expired/invalid token reported by the server, not a pure render sync
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (error instanceof ApiError && error.status === 401) logout();
  }, [error, logout]);

  const signIn = useCallback((newToken: string) => {
    tokenStorage.set(newToken);
    setToken(newToken);
  }, []);

  const status: AuthStatus = !ready
    ? "loading"
    : !token
      ? "unauthenticated"
      : user
        ? "authenticated"
        : error
          ? "unauthenticated"
          : "loading";

  const value = useMemo(() => ({ user: user ?? null, status, signIn, logout }), [user, status, signIn, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
