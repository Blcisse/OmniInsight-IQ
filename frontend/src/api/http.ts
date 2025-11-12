import axios, { AxiosError, AxiosInstance } from "axios";

const baseURL = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export type ApiOk<T> = { ok: true; data: T; status: number };
export type ApiErr = { ok: false; error: string; status?: number };
export type ApiResponse<T> = ApiOk<T> | ApiErr;

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

function shouldRetry(status?: number): boolean {
  if (!status) return true; // network/timeout
  if (status === 429) return true;
  if (status >= 500) return true;
  return false;
}

export function createHttpClient(): AxiosInstance {
  const client = axios.create({ baseURL, timeout: 15000, headers: { "Content-Type": "application/json" } });

  client.interceptors.response.use(
    (resp) => resp,
    async (error: AxiosError) => {
      const cfg: any = error.config || {};
      cfg.__retryCount = cfg.__retryCount || 0;
      const status = error.response?.status;
      if (cfg.__retryCount < 3 && shouldRetry(status)) {
        const backoff = 200 * Math.pow(2, cfg.__retryCount);
        cfg.__retryCount += 1;
        await sleep(backoff);
        return client(cfg);
      }
      return Promise.reject(error);
    }
  );

  return client;
}

export const http = createHttpClient();

export async function toApiResponse<T>(p: Promise<any>): Promise<ApiResponse<T>> {
  try {
    const resp = await p;
    return { ok: true, data: resp.data as T, status: resp.status };
  } catch (e: any) {
    const err = e as AxiosError;
    const msg = (err.response?.data as any)?.detail || err.message || "Request failed";
    return { ok: false, error: String(msg), status: err.response?.status };
  }
}

