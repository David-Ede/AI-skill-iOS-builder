export type AnalyticsEvent = {
  name: string;
  properties?: Record<string, string | number | boolean | null>;
};

export function trackEvent(event: AnalyticsEvent) {
  // Replace with provider SDK integration.
  console.log(`[analytics] ${event.name}`, event.properties ?? {});
}
