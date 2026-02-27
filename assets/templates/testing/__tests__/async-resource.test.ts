import { apiGet, clearApiCache } from "../src/data/apiClient";

type MockResponseShape = {
  status: number;
  body: unknown;
  contentType?: string;
};

function mockResponse({ status, body, contentType = "application/json" }: MockResponseShape) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: {
      get: (name: string) => (name.toLowerCase() === "content-type" ? contentType : null),
    },
    json: async () => body,
    text: async () => (typeof body === "string" ? body : JSON.stringify(body)),
  } as Response;
}

describe("data layer api client", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    clearApiCache();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it("retries transient failures and then succeeds", async () => {
    const fetchMock = jest
      .fn()
      .mockResolvedValueOnce(mockResponse({ status: 503, body: { error: "busy" } }))
      .mockResolvedValueOnce(mockResponse({ status: 200, body: { id: "u_1" } }));
    globalThis.fetch = fetchMock as typeof fetch;

    const result = await apiGet<{ id: string }>("/users/me", {
      baseUrl: "https://api.example.test",
      retry: { maxRetries: 1, baseDelayMs: 0, maxDelayMs: 0 },
      cache: { ttlMs: 1000 },
    });

    expect(result.ok).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    if (result.ok) {
      expect(result.data.id).toBe("u_1");
      expect(result.fromCache).toBe(false);
    }
  });

  it("uses cached response for repeated GETs inside TTL", async () => {
    const fetchMock = jest
      .fn()
      .mockResolvedValueOnce(mockResponse({ status: 200, body: { featureFlag: true } }));
    globalThis.fetch = fetchMock as typeof fetch;

    const first = await apiGet<{ featureFlag: boolean }>("/flags", {
      baseUrl: "https://api.example.test",
      cache: { ttlMs: 60_000, staleIfErrorMs: 60_000 },
    });
    const second = await apiGet<{ featureFlag: boolean }>("/flags", {
      baseUrl: "https://api.example.test",
      cache: { ttlMs: 60_000, staleIfErrorMs: 60_000 },
    });

    expect(first.ok).toBe(true);
    expect(second.ok).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    if (second.ok) {
      expect(second.fromCache).toBe(true);
      expect(second.stale).toBe(false);
    }
  });

  it("serves stale cache when network fails and stale fallback is enabled", async () => {
    const fetchMock = jest
      .fn()
      .mockResolvedValueOnce(mockResponse({ status: 200, body: { value: 42 } }))
      .mockRejectedValueOnce(new Error("network down"));
    globalThis.fetch = fetchMock as typeof fetch;

    const first = await apiGet<{ value: number }>("/metrics", {
      baseUrl: "https://api.example.test",
      cache: { ttlMs: 0, staleIfErrorMs: 10_000 },
      retry: { maxRetries: 0 },
    });
    const second = await apiGet<{ value: number }>("/metrics", {
      baseUrl: "https://api.example.test",
      cache: { ttlMs: 0, staleIfErrorMs: 10_000 },
      retry: { maxRetries: 0 },
      allowStaleOnError: true,
    });

    expect(first.ok).toBe(true);
    expect(second.ok).toBe(true);
    if (second.ok) {
      expect(second.fromCache).toBe(true);
      expect(second.stale).toBe(true);
      expect(second.data.value).toBe(42);
    }
  });
});
