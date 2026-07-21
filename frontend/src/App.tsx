/**
 * App.tsx — Root Application Component
 *
 * 1. Polls /api/health every 250ms until the Python sidecar responds (1-3s startup)
 * 2. Shows LoadingScreen while waiting
 * 3. Once backend is ready, renders the full router with all page routes
 */
import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppProvider, useApp } from "@/AppContext";
import { waitForBackend } from "@/services/api";
import { LoadingScreen } from "@/components/LoadingScreen";
import { Layout } from "@/components/Layout";
import { LanguagesPage }   from "@/pages/Languages";
import { ToolsPage }       from "@/pages/Tools";
import { PackageHubPage }  from "@/pages/PackageHub";
import { PresetsPage }     from "@/pages/Presets";
import { DoctorPage }      from "@/pages/Doctor";
import { AIAssistantPage } from "@/pages/AIAssistant";

function AppShell() {
  const { backendReady, setBackendReady, addLog } = useApp();
  const [loadStatus, setLoadStatus] = useState("Starting backend...");

  useEffect(() => {
    setLoadStatus("Connecting to ENVIX backend...");
    waitForBackend(15_000).then((ready) => {
      if (ready) {
        setBackendReady(true);
        addLog({ level: "success", message: "✓  ENVIX backend connected and ready" });
      } else {
        setLoadStatus("Backend failed to start — ensure Python is installed and api_server.py exists.");
        addLog({ level: "error", message: "✗  Backend did not respond after 15 seconds" });
      }
    });
  }, [setBackendReady, addLog]);

  if (!backendReady) return <LoadingScreen status={loadStatus} />;

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/languages" replace />} />
        <Route path="languages" element={<LanguagesPage />} />
        <Route path="tools"     element={<ToolsPage />} />
        <Route path="packages"  element={<PackageHubPage />} />
        <Route path="presets"   element={<PresetsPage />} />
        <Route path="doctor"    element={<DoctorPage />} />
        <Route path="assistant" element={<AIAssistantPage />} />
        <Route path="*"         element={<Navigate to="/languages" replace />} />
      </Route>
    </Routes>
  );
}

export function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    </AppProvider>
  );
}
