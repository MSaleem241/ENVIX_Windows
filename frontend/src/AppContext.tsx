/**
 * AppContext.tsx — ENVIX Shared Application State
 *
 * Provides:
 *  - Output Console log lines (any page can write here)
 *  - Backend readiness flag
 *  - Console panel height + collapsed state (for the resizable console)
 *
 * Uses React Context — lightweight, no extra dependency needed for this
 * small shared state. Migrate to Zustand if the state grows significantly.
 */
import React, { createContext, useCallback, useContext, useState, useRef } from "react";

export type LogLevel = "info" | "success" | "warning" | "error" | "muted" | "progress";

export interface LogEntry {
  id: number;
  timestamp: string;
  message: string;
  level: LogLevel;
}

interface AppContextValue {
  logs: LogEntry[];
  addLog: (entry: Omit<LogEntry, "id" | "timestamp">) => void;
  clearLog: () => void;
  backendReady: boolean;
  setBackendReady: (ready: boolean) => void;
  consoleHeight: number;
  setConsoleHeight: (h: number) => void;
  consoleCollapsed: boolean;
  setConsoleCollapsed: (c: boolean) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [backendReady, setBackendReady] = useState(false);
  const [consoleHeight, setConsoleHeight] = useState(200);
  const [consoleCollapsed, setConsoleCollapsed] = useState(false);
  const idRef = useRef(0);

  const getTimestamp = () => new Date().toTimeString().slice(0, 8);

  const addLog = useCallback((entry: Omit<LogEntry, "id" | "timestamp">) => {
    const newEntry: LogEntry = { id: ++idRef.current, timestamp: getTimestamp(), ...entry };
    // Keep max 500 lines to prevent memory growth during long installs
    setLogs((prev) => [...(prev.length >= 500 ? prev.slice(-499) : prev), newEntry]);
  }, []);

  const clearLog = useCallback(() => setLogs([]), []);

  return (
    <AppContext.Provider value={{
      logs, addLog, clearLog,
      backendReady, setBackendReady,
      consoleHeight, setConsoleHeight,
      consoleCollapsed, setConsoleCollapsed,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used inside <AppProvider>");
  return ctx;
}
