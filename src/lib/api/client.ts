import { createClient as createAuthClient } from "@/lib/auth/client";
import { demoApiRequest, isDemoSession } from "@/lib/demo-session";

export type ApiErrorBody = { error?: { code?: string; message?: string; request_id?: string } };

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (isDemoSession()) return demoApiRequest<T>(path, init);
  const authClient = createAuthClient();
  const { data: { session } } = await authClient.auth.getSession();
  if (!session) throw new Error("Your session has expired. Sign in again.");
  const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
  let response: Response;
  try {
    response = await fetch(`${base}/api/v1${path}`, {
      ...init,
      credentials: "include",
      headers: {
        Authorization: `Bearer ${session.access_token}`,
        ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
        ...init.headers,
      },
    });
  } catch {
    throw new Error(
      "Could not reach the API. Start the backend (npm run dev) and confirm NEXT_PUBLIC_API_BASE_URL.",
    );
  }
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorBody;
    if (response.status === 503) {
      throw new Error(
        body.error?.message ||
          "The service is temporarily unavailable. Please try again in a moment.",
      );
    }
    throw new Error(body.error?.message || `Request failed (${response.status}).`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
