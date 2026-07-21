/**
 * Layout.tsx — Main Application Layout
 *
 * Root wrapper: fixed sidebar + scrollable main content + pinned output console.
 */
import { Outlet } from "react-router-dom";
import { Sidebar } from "@/components/Sidebar";
import { OutputConsole } from "@/components/OutputConsole";
import { useApp } from "@/AppContext";

export function Layout() {
  const { consoleHeight, consoleCollapsed } = useApp();
  const bottomPad = consoleCollapsed ? 44 : consoleHeight + 4;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-on-surface">
      <Sidebar />
      <main
        className="flex-1 ml-sidebar_width_expanded flex flex-col min-h-0 overflow-hidden"
        style={{ paddingBottom: bottomPad }}
      >
        <div className="flex-1 overflow-hidden flex flex-col page-enter">
          <Outlet />
        </div>
      </main>
      <OutputConsole />
    </div>
  );
}
