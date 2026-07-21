/**
 * services/api.ts — ENVIX Frontend API Client
 *
 * Single source of truth for all backend communication.
 * No component imports fetch() directly — everything goes through here.
 *
 * STREAMING: subscribeToStream() opens an SSE connection and calls
 * onMessage() for every log line the Python backend produces in real time.
 */

const API_BASE = "http://127.0.0.1:39291";

// ── Types ──────────────────────────────────────────────────────────────────
export interface Tool {
  name: string;
  category: "language" | "tool";
  installed: boolean;
  winget_id: string;
}

export interface Package {
  id: string;
  name: string;
  language: string;
  category: string;
  description: string;
  install_cmd: string;
  global_cmd: string;
  recommends: string[];
}

export interface DoctorResult {
  name: string;
  status: "ok" | "missing" | "path_issue";
  version: string | null;
  note: string;
  fix: string | null;
}

export interface DoctorSummary {
  total: number;
  ok: number;
  missing: number;
  broken: number;
}

export interface Preset {
  id: string;
  label: string;
  desc: string;
  languages: string[];
  file_count: number;
}

export interface StreamEvent {
  type: "log" | "progress" | "done" | "error" | "timeout";
  message?: string;
}

// ── Health check ────────────────────────────────────────────────────────────
/**
 * Poll until the Python sidecar responds. Tauri starts it automatically
 * but uvicorn takes 1-3 seconds to initialize.
 */
export async function waitForBackend(maxWaitMs = 15000): Promise<boolean> {
  const interval = 250;
  for (let i = 0; i < maxWaitMs / interval; i++) {
    try {
      const res = await fetch(`${API_BASE}/api/health`, { signal: AbortSignal.timeout(500) });
      if (res.ok) return true;
    } catch { /* not ready yet */ }
    await new Promise((r) => setTimeout(r, interval));
  }
  return false;
}

// ── Tools ────────────────────────────────────────────────────────────────────
export async function fetchTools(): Promise<Tool[]> {
  const res = await fetch(`${API_BASE}/api/tools`);
  const data = await res.json();
  return data.tools;
}

export async function fetchToolStatus(name: string): Promise<boolean> {
  const res = await fetch(`${API_BASE}/api/tools/${name}/status`);
  const data = await res.json();
  return data.installed;
}

// ── Doctor ────────────────────────────────────────────────────────────────────
export async function runDoctorScan(): Promise<{ results: DoctorResult[]; summary: DoctorSummary }> {
  const res = await fetch(`${API_BASE}/api/doctor/scan`);
  return res.json();
}

// ── Packages ──────────────────────────────────────────────────────────────────
export async function fetchPackages(opts?: { language?: string; search?: string }): Promise<Package[]> {
  const params = new URLSearchParams();
  if (opts?.language) params.set("language", opts.language);
  if (opts?.search) params.set("search", opts.search);
  const res = await fetch(`${API_BASE}/api/packages?${params}`);
  const data = await res.json();
  return data.packages;
}

// ── Presets ───────────────────────────────────────────────────────────────────
export async function fetchPresets(): Promise<Preset[]> {
  const res = await fetch(`${API_BASE}/api/presets`);
  const data = await res.json();
  return data.presets;
}

// ── SSE streaming ─────────────────────────────────────────────────────────────
/**
 * Opens a long-lived HTTP connection and calls onMessage() for every SSE event.
 * Each event is a JSON object: { type, message }.
 * Returns a cancel function — call it to abort the stream early.
 */
export function subscribeToStream(
  path: string,
  fetchOptions: RequestInit,
  onMessage: (event: StreamEvent) => void,
  onDone: (success: boolean) => void
): () => void {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        ...fetchOptions,
        headers: { "Content-Type": "application/json", Accept: "text/event-stream", ...fetchOptions.headers },
        signal: controller.signal,
      });

      if (!res.ok || !res.body) { onMessage({ type: "error", message: `HTTP ${res.status}` }); onDone(false); return; }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const event: StreamEvent = JSON.parse(line.slice(6));
            onMessage(event);
            if (event.type === "done") { onDone(true); return; }
            if (event.type === "error") { onDone(false); return; }
          } catch { /* malformed JSON, skip */ }
        }
      }
      onDone(true);
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== "AbortError") {
        onMessage({ type: "error", message: String(err) });
        onDone(false);
      }
    }
  })();

  return () => controller.abort();
}
