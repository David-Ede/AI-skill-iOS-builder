export type AuthStatus = "anonymous" | "authenticated";

export type OAuthProvider = "apple" | "google";

export type Session = {
  token: string;
  userId: string;
  provider: "password" | OAuthProvider;
  expiresAtEpochMs?: number;
};

export type OAuthResult =
  | { status: "success"; sessionToken: string; userId: string }
  | { status: "cancelled" }
  | { status: "needs_setup"; reason: string };
