import * as AuthSession from "expo-auth-session";
import type { OAuthProvider, OAuthResult } from "./types";

export type OAuthProviderConfig = {
  provider: OAuthProvider;
  clientId: string;
  discoveryUrl: string;
  redirectUri: string;
  scopes: string[];
};

const PLACEHOLDER_CLIENT_IDS: Record<OAuthProvider, string> = {
  apple: "YOUR_APPLE_SERVICE_ID",
  google: "YOUR_GOOGLE_CLIENT_ID",
};

export function buildOAuthProviderConfig(provider: OAuthProvider): OAuthProviderConfig {
  const redirectUri = AuthSession.makeRedirectUri({ path: "auth/callback" });
  if (provider === "apple") {
    return {
      provider,
      clientId: PLACEHOLDER_CLIENT_IDS.apple,
      discoveryUrl: "https://appleid.apple.com",
      redirectUri,
      scopes: ["name", "email"],
    };
  }

  return {
    provider,
    clientId: PLACEHOLDER_CLIENT_IDS.google,
    discoveryUrl: "https://accounts.google.com",
    redirectUri,
    scopes: ["openid", "profile", "email"],
  };
}

function hasRealProviderConfiguration(config: OAuthProviderConfig): boolean {
  return !config.clientId.startsWith("YOUR_");
}

export async function startOAuthSignIn(provider: OAuthProvider): Promise<OAuthResult> {
  const config = buildOAuthProviderConfig(provider);

  if (!hasRealProviderConfiguration(config)) {
    return {
      status: "needs_setup",
      reason:
        `${provider} OAuth is not configured yet. Replace placeholder client IDs in ` +
        "src/auth/oauthProviders.ts and add backend token exchange.",
    };
  }

  return {
    status: "needs_setup",
    reason:
      `${provider} OAuth wiring requires backend token exchange and provider app setup. ` +
      "Replace startOAuthSignIn with your provider SDK flow.",
  };
}
