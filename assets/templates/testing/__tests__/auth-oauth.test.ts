/* eslint-disable import/first */
jest.mock("expo-auth-session", () => ({
  makeRedirectUri: () => "myapp://auth/callback",
}));

import { buildOAuthProviderConfig, startOAuthSignIn } from "../src/auth/oauthProviders";

describe("auth oauth provider slots", () => {
  it("builds provider configuration with redirect URI", () => {
    const apple = buildOAuthProviderConfig("apple");
    const google = buildOAuthProviderConfig("google");

    expect(apple.redirectUri).toBe("myapp://auth/callback");
    expect(google.redirectUri).toBe("myapp://auth/callback");
    expect(apple.scopes).toContain("email");
    expect(google.scopes).toContain("openid");
  });

  it("returns setup guidance while placeholders are present", async () => {
    const result = await startOAuthSignIn("google");
    expect(result.status).toBe("needs_setup");
    if (result.status === "needs_setup") {
      expect(result.reason.toLowerCase()).toContain("oauth");
    }
  });
});
