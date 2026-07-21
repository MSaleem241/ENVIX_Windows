/**
 * OutputConsole.tsx — ENVIX Output Console
 *
 * Always-visible, resizable terminal panel pinned to the bottom of the window.
 * Auto-scrolls, color-codes log levels, supports Clear and Collapse.
 */
import { useEffect, useRef, useState } from "react";
import { useApp, LogEntry } from "@/AppContext";

const LEVEL_CLASSES: Record<LogEntry["level"], string> = {
  muted:    "text-on-surface-variant opacity-60",
  info:     "text-on-surface-variant",
  success:  "text-green-400",
  warning:  "text-yellow-400",
  error:    "text-red-400",
  progress: "text-primary",
};

export function OutputConsole() {
  const { logs, clearLog, consoleHeight, setConsoleHeight, consoleCollapsed, setConsoleCollapsed } = useApp();
  const [isLive, setIsLive] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const isResizing = useRef(false);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);

  useEffect(() => {
    const hasProgress = logs.length > 0 && logs[logs.length - 1].level === "progress";
    if (hasProgress) {
      setIsLive(true);
      const t = setTimeout(() => setIsLive(false), 2500);
      return () => clearTimeout(t);
    }
  }, [logs]);

  const handleResizeStart = (e: React.MouseEvent) => {
    e.preventDefault();
    isResizing.current = true;
    document.body.style.cursor = "ns-resize";
    const onMove = (ev: MouseEvent) => {
      if (!isResizing.current) return;
      const newH = window.innerHeight - ev.clientY;
      if (newH >= 100 && newH <= 600) setConsoleHeight(newH);
    };
    const onUp = () => {
      isResizing.current = false;
      document.body.style.cursor = "default";
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  };

  const panelHeight = consoleCollapsed ? 40 : consoleHeight;

  return (
    <footer
      className="fixed bottom-0 right-0 left-sidebar_width_expanded bg-surface-container-lowest border-t border-outline-variant z-40 transition-[height] duration-150 flex flex-col"
      style={{ height: panelHeight }}
    >
      <div id="console-resize-handle" className="absolute top-0 left-0 right-0 h-1 cursor-ns-resize" onMouseDown={handleResizeStart} />

      <div className="flex items-center justify-between px-panel-padding py-2 h-10 shrink-0">
        <div className="flex items-center gap-3">
          <span className="font-mono text-[12px] text-on-surface-variant opacity-80">Output Console</span>
          <div className={`flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono uppercase ${isLive ? "bg-surface-container-high text-green-400" : "bg-surface-container text-on-surface-variant opacity-60"}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${isLive ? "bg-green-500 animate-pulse" : "bg-on-surface-variant"}`} />
            {isLive ? "Live" : "Ready"}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={clearLog} className="text-primary hover:bg-surface-container-high px-2 py-1 rounded transition-colors font-mono text-[12px]">Clear</button>
          <button onClick={() => setConsoleCollapsed(!consoleCollapsed)} className="text-on-surface-variant hover:text-on-surface p-1 transition-colors" title={consoleCollapsed ? "Expand" : "Collapse"}>
            <span className="material-symbols-outlined text-[18px]">{consoleCollapsed ? "keyboard_arrow_up" : "keyboard_arrow_down"}</span>
          </button>
        </div>
      </div>

      {!consoleCollapsed && (
        <div className="flex-1 overflow-y-auto px-panel-padding pb-2 space-y-0.5">
          {logs.length === 0 ? (
            <div className="flex gap-4 text-on-surface-variant opacity-30 font-mono text-[12px]">
              <span className="shrink-0 opacity-40">--:--:--</span>
              <span>Waiting for input...</span>
            </div>
          ) : (
            logs.map((entry) => (
              <div key={entry.id} className={`flex gap-4 font-mono text-[12px] ${LEVEL_CLASSES[entry.level]}`}>
                <span className="text-on-surface-variant opacity-40 shrink-0 w-16">{entry.timestamp}</span>
                <span className="break-all">{entry.message}</span>
              </div>
            ))
          )}
          <div className="flex gap-4 font-mono text-[12px] text-on-surface">
            <span className="text-on-surface-variant opacity-40 shrink-0 w-16" />
            <span className="border-l-2 border-primary pl-2 cursor-blink">_</span>
          </div>
          <div ref={bottomRef} />
        </div>
      )}
    </footer>
  );
}
