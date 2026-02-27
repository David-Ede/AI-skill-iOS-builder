export type ApiResponse<T> = {
  ok: boolean;
  data?: T;
  error?: string;
};

export async function apiGet<T>(url: string): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      return { ok: false, error: `HTTP ${response.status}` };
    }
    const data = (await response.json()) as T;
    return { ok: true, data };
  } catch (error) {
    return { ok: false, error: String(error) };
  }
}
