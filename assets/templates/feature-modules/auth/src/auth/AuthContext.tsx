import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { clearSessionToken, loadSessionToken, saveSessionToken } from "./secureSession";

type AuthStatus = "anonymous" | "authenticated";

type AuthContextValue = {
  status: AuthStatus;
  initialize: () => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("anonymous");

  async function initialize() {
    const token = await loadSessionToken();
    setStatus(token ? "authenticated" : "anonymous");
  }

  async function signIn(email: string, password: string) {
    const fakeToken = `${email}:${password}:session-token`;
    await saveSessionToken(fakeToken);
    setStatus("authenticated");
  }

  async function signOut() {
    await clearSessionToken();
    setStatus("anonymous");
  }

  const value = useMemo<AuthContextValue>(
    () => ({ status, initialize, signIn, signOut }),
    [status],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside AuthProvider.");
  }
  return ctx;
}
