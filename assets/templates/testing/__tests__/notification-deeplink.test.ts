import {
  extractNotificationDeepLink,
  normalizeDeepLink,
} from "../src/notifications/notificationDeepLink";

describe("notification deep link parsing", () => {
  it("normalizes relative paths to route-like values", () => {
    expect(normalizeDeepLink("settings")).toBe("/settings");
    expect(normalizeDeepLink("/profile")).toBe("/profile");
  });

  it("keeps absolute URLs untouched", () => {
    expect(normalizeDeepLink("https://example.test/path")).toBe("https://example.test/path");
    expect(normalizeDeepLink("myapp://promo/123")).toBe("myapp://promo/123");
  });

  it("extracts deep link from known payload keys", () => {
    const payload = {
      title: "New promo",
      deepLink: "promo/summer",
    };

    expect(extractNotificationDeepLink(payload)).toBe("/promo/summer");
  });

  it("returns null for payloads without link fields", () => {
    expect(extractNotificationDeepLink({ title: "No route" })).toBeNull();
  });
});
