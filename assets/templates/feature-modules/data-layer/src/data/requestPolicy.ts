export type RetryPolicy = {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
  retryableStatusCodes: number[];
};

export type CachePolicy = {
  ttlMs: number;
  staleIfErrorMs: number;
};

export const DEFAULT_RETRY_POLICY: RetryPolicy = {
  maxRetries: 2,
  baseDelayMs: 250,
  maxDelayMs: 2000,
  retryableStatusCodes: [408, 425, 429, 500, 502, 503, 504],
};

export const DEFAULT_CACHE_POLICY: CachePolicy = {
  ttlMs: 30_000,
  staleIfErrorMs: 5 * 60_000,
};

export function shouldRetryStatus(status: number, retryableStatusCodes: number[]): boolean {
  return retryableStatusCodes.includes(status);
}

export function computeRetryDelayMs(attempt: number, policy: RetryPolicy): number {
  const exponential = policy.baseDelayMs * 2 ** Math.max(attempt - 1, 0);
  return Math.min(exponential, policy.maxDelayMs);
}
