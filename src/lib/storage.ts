const KEY = "career-copilot-demo-v1";

export function loadStored<T>(fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw) as { version?: number; state?: T };
    return parsed.version === 1 && parsed.state ? parsed.state : fallback;
  } catch {
    return fallback;
  }
}

export function saveStored<T>(state: T) {
  if (typeof window === "undefined") return;
  try { window.localStorage.setItem(KEY, JSON.stringify({ version: 1, state })); } catch { /* storage can be unavailable */ }
}

export function clearStored() {
  if (typeof window === "undefined") return;
  try { window.localStorage.removeItem(KEY); } catch { /* storage can be unavailable */ }
}
