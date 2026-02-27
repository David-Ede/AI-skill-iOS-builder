import {
  DEFAULT_CACHE_POLICY,
  DEFAULT_RETRY_POLICY,
  computeRetryDelayMs,
  shouldRetryStatus,
  type CachePolicy,
  type RetryPolicy,
} from "./requestPolicy";

type ApiSuccess<T> = {
  ok: true;
  status: number;
  data: T;
  fromCache: boolean;
  stale: boolean;
};

type ApiFailure = {
  ok: false;
  status?: number;
  error: string;
  fromCache: boolean;
  stale: boolean;
};

export type ApiResponse<T> = ApiSuccess<T> | ApiFailure;

export type ApiClientOptions = {
  baseUrl?: string;
  timeoutMs?: number;
  retry?: Partial<RetryPolicy>;
  cache?: Partial<CachePolicy>;
  headers?: Record<string, string>;
  getAuthToken?: () => Promise<string | null> | string | null;
  allowStaleOnError?: boolean;
};

type CacheEntry<T> = {
  value: T;
  expiresAtEpochMs: number;
  staleUntilEpochMs: number;
};

const responseCache = new Map<string, CacheEntry<unknown>>();
const DEFAULT_TIMEOUT_MS = 10_000;

function mergeRetryPolicy(input?: Partial<RetryPolicy>): RetryPolicy {
  return {
    ...DEFAULT_RETRY_POLICY,
    ...input,
  };
}

function mergeCachePolicy(input?: Partial<CachePolicy>): CachePolicy {
  return {
    ...DEFAULT_CACHE_POLICY,
    ...input,
  };
}

function toAbsoluteUrl(baseUrl: string | undefined, pathOrUrl: string): string {
  if (/^https?:\/\//i.test(pathOrUrl)) {
    return pathOrUrl;
  }

  if (!baseUrl) {
    throw new Error("baseUrl is required when calling apiGet with a relative path.");
  }

  const left = baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
  const right = pathOrUrl.startsWith("/") ? pathOrUrl : `/${pathOrUrl}`;
  return `${left}${right}`;
}

async function resolveAuthHeader(
  getAuthToken: ApiClientOptions["getAuthToken"],
): Promise<Record<string, string>> {
  if (!getAuthToken) {
    return {};
  }

  const token = await getAuthToken();
  if (!token) {
    return {};
  }

  return { authorization: `Bearer ${token}` };
}

function makeCacheKey(url: string, headers: Record<string, string>): string {
  const auth = headers.authorization ?? "";
  return `GET:${url}:auth=${auth}`;
}

async function sleep(ms: number): Promise<void> {
  if (ms <= 0) {
    return;
  }
  await new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs: number,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timeoutId);
  }
}

async function parseResponseBody<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return null as T;
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  }

  const text = await response.text();
  try {
    return JSON.parse(text) as T;
  } catch {
    return text as T;
  }
}

export async function apiGet<T>(
  pathOrUrl: string,
  options: ApiClientOptions = {},
): Promise<ApiResponse<T>> {
  const retryPolicy = mergeRetryPolicy(options.retry);
  const cachePolicy = mergeCachePolicy(options.cache);
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const allowStaleOnError = options.allowStaleOnError ?? true;
  const url = toAbsoluteUrl(options.baseUrl, pathOrUrl);
  const authHeader = await resolveAuthHeader(options.getAuthToken);
  const headers: Record<string, string> = {
    accept: "application/json",
    ...options.headers,
    ...authHeader,
  };
  const cacheKey = makeCacheKey(url, headers);
  const now = Date.now();

  const cachedEntry = responseCache.get(cacheKey) as CacheEntry<T> | undefined;
  if (cachedEntry && cachedEntry.expiresAtEpochMs > now) {
    return {
      ok: true,
      status: 200,
      data: cachedEntry.value,
      fromCache: true,
      stale: false,
    };
  }

  let lastError = "Request failed.";
  let lastStatus: number | undefined;

  for (let attempt = 0; attempt <= retryPolicy.maxRetries; attempt += 1) {
    try {
      const response = await fetchWithTimeout(
        url,
        {
          method: "GET",
          headers,
        },
        timeoutMs,
      );

      if (response.ok) {
        const data = await parseResponseBody<T>(response);
        const cachedAt = Date.now();
        responseCache.set(cacheKey, {
          value: data,
          expiresAtEpochMs: cachedAt + cachePolicy.ttlMs,
          staleUntilEpochMs: cachedAt + cachePolicy.staleIfErrorMs,
        });
        return {
          ok: true,
          status: response.status,
          data,
          fromCache: false,
          stale: false,
        };
      }

      lastStatus = response.status;
      lastError = `HTTP ${response.status}`;

      const retryable = shouldRetryStatus(response.status, retryPolicy.retryableStatusCodes);
      if (!retryable || attempt === retryPolicy.maxRetries) {
        break;
      }
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
      if (attempt === retryPolicy.maxRetries) {
        break;
      }
    }

    const delay = computeRetryDelayMs(attempt + 1, retryPolicy);
    await sleep(delay);
  }

  const staleNow = Date.now();
  if (
    allowStaleOnError &&
    cachedEntry &&
    cachedEntry.staleUntilEpochMs > staleNow
  ) {
    return {
      ok: true,
      status: 200,
      data: cachedEntry.value,
      fromCache: true,
      stale: true,
    };
  }

  return {
    ok: false,
    status: lastStatus,
    error: lastError,
    fromCache: false,
    stale: false,
  };
}

export function clearApiCache(): void {
  responseCache.clear();
}
