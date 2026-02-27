const DEEP_LINK_KEYS = ["deepLink", "deeplink", "url", "path"] as const;

export function normalizeDeepLink(rawValue: string): string {
  const trimmed = rawValue.trim();
  if (!trimmed) {
    return "";
  }
  if (trimmed.includes("://")) {
    return trimmed;
  }
  if (trimmed.startsWith("/")) {
    return trimmed;
  }
  return `/${trimmed}`;
}

export function extractNotificationDeepLink(
  data: Record<string, unknown> | null | undefined,
): string | null {
  if (!data) {
    return null;
  }

  for (const key of DEEP_LINK_KEYS) {
    const value = data[key];
    if (typeof value !== "string") {
      continue;
    }

    const deepLink = normalizeDeepLink(value);
    if (deepLink) {
      return deepLink;
    }
  }

  return null;
}
