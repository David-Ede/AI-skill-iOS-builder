export function reportError(error: unknown, context?: Record<string, string>) {
  // Replace with crash reporter SDK integration.
  console.error("[crash-report]", error, context ?? {});
}
