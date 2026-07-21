/**
 * useInstall.ts — Streaming Install Hook
 *
 * Manages the full install lifecycle for any backend operation:
 *   1. Opens an SSE stream to the backend
 *   2. Routes each event to the Output Console
 *   3. Returns {install, cancel, loading} for the calling component
 *
 * Used by: Languages, Tools, Doctor, PackageHub, Presets pages.
 */
import { useState, useCallback, useRef } from "react";
import { useApp } from "@/AppContext";
import { subscribeToStream, StreamEvent } from "@/services/api";

export function useInstall() {
  const { addLog } = useApp();
  const [loading, setLoading] = useState(false);
  const cancelRef = useRef<(() => void) | null>(null);

  const install = useCallback(
    (path: string, fetchOpts: RequestInit, label: string, onDone?: (success: boolean) => void) => {
      if (loading) return;
      setLoading(true);
      addLog({ level: "info", message: `▶  ${label}...` });

      const onMessage = (event: StreamEvent) => {
        if (event.type === "log")      addLog({ level: "info",     message: `   ${event.message ?? ""}` });
        if (event.type === "progress") addLog({ level: "progress", message: `   ${event.message ?? ""}` });
        if (event.type === "error")    addLog({ level: "error",    message: `✗  ${event.message ?? "Error"}` });
      };

      const onComplete = (success: boolean) => {
        setLoading(false);
        cancelRef.current = null;
        addLog({
          level: success ? "success" : "error",
          message: success ? `✓  ${label} complete` : `✗  ${label} failed — check output above`,
        });
        onDone?.(success);
      };

      cancelRef.current = subscribeToStream(path, fetchOpts, onMessage, onComplete);
    },
    [loading, addLog]
  );

  const cancel = useCallback(() => {
    cancelRef.current?.();
    cancelRef.current = null;
    setLoading(false);
  }, []);

  return { install, cancel, loading };
}
