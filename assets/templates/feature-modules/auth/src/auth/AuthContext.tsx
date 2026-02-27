import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { startOAuthSignIn } from "./oauthProviders";
import { clearSessionToken, loadSessionToken, saveSessionToken } from "./secureSession";
import type { AuthStatus, OAuthProvider } from "./types";

type AuthContextValue = {
  status: AuthStatus;
  lastError: string | null;
  initialize: () => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signInWithOAuth: (provider: OAuthProvider) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("anonymous");
  const [lastError, setLastError] = useState<string | null>(null);

  async function initialize() {
    const token = await loadSessionToken();
    setStatus(token ? "authenticated" : "anonymous");
  }

  async function signIn(email: string, password: string) {
    setLastError(null);
    const fakeToken = `${email}:${password}:session-token`;
    await saveSessionToken(fakeToken);
    setStatus("authenticated");
  }

  async function signInWithOAuth(provider: OAuthProvider) {
    setLastError(null);
    const result = await startOAuthSignIn(provider);
    if (result.status === "success") {
      await saveSessionToken(result.sessionToken);
      setStatus("authenticated");
      return;
    }

    if (result.status === "cancelled") {
      setLastError(`${provider} sign-in was cancelled.`);
      return;
    }

    setLastError(result.reason);
  }

  async function signOut() {
    await clearSessionToken();
    setLastError(null);
    setStatus("anonymous");
  }

  const value = useMemo<AuthContextValue>(
    () => ({ status, lastError, initialize, signIn, signInWithOAuth, signOut }),
    [status, lastError],
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
