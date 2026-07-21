/**
 * Doctor.tsx — Doctor Page
 *
 * Summary bento (Installed / Missing / Issues / Run Scan) + health table.
 * GET /api/doctor/scan returns full diagnosis (non-streamed, fast).
 * Fixing a broken/missing tool streams the install via POST /api/tools/{name}/install.
 */
import { useState, useCallback } from "react";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { InstallButton } from "@/components/InstallButton";
import { useInstall } from "@/hooks/useInstall";
import { runDoctorScan, DoctorResult, DoctorSummary } from "@/services/api";
import { useApp } from "@/AppContext";
import { getLogo } from "@/assets/logos/logoMap";

const TOOL_COLORS: Record<string, { bg: string; label: string; desc: string }> = {
  node:   { bg: "#339933", label: "Node.js",     desc: "JavaScript runtime" },
  python: { bg: "#3776AB", label: "Python 3",    desc: "Scripting & backend" },
  git:    { bg: "#F05032", label: "Git",          desc: "Version control" },
  vscode: { bg: "#007ACC", label: "VS Code",      desc: "IDE installation" },
  docker: { bg: "#2496ED", label: "Docker",       desc: "Container engine" },
  java:   { bg: "#EA2D2E", label: "Java 21 JDK",  desc: "Java development kit" },
  go:     { bg: "#00ADD8", label: "Go",            desc: "Systems & cloud backend" },
};

export function DoctorPage() {
  const { addLog } = useApp();
  const [results, setResults] = useState<DoctorResult[]>([]);
  const [summary, setSummary] = useState<DoctorSummary | null>(null);
  const [scanning, setScanning] = useState(false);
  const [installingTool, setInstallingTool] = useState<string | null>(null);
  const { install } = useInstall();

  const runScan = useCallback(async () => {
    setScanning(true);
    addLog({ level: "info", message: "▶  Doctor scan running..." });
    try {
      const data = await runDoctorScan();
      setResults(data.results);
      setSummary(data.summary);
      addLog({ level: "success", message: `✓  Scan complete: ${data.summary.ok} ok, ${data.summary.missing} missing, ${data.summary.broken} issues` });
    } catch {
      addLog({ level: "error", message: "✗  Doctor scan failed — is the backend running?" });
    } finally { setScanning(false); }
  }, [addLog]);

  const handleFix = (result: DoctorResult) => {
    setInstallingTool(result.name);
    install(`/api/tools/${result.name}/install`, { method: "POST" }, TOOL_COLORS[result.name]?.label ?? result.name,
      async (success) => { setInstallingTool(null); if (success) await runScan(); });
  };

  const mapStatus = (r: DoctorResult): "installed" | "missing" | "path_issue" | "checking" => {
    if (installingTool === r.name) return "checking";
    if (r.status === "ok") return "installed";
    if (r.status === "path_issue") return "path_issue";
    return "missing";
  };

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Doctor">
        <button onClick={runScan} disabled={scanning}
          className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-bold text-white transition-all duration-200 active:scale-95 shadow-lg shadow-primary/20 disabled:opacity-60"
          style={{ backgroundColor: "#3882F6" }}>
          {scanning ? <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <span className="material-symbols-outlined text-[20px]">bolt</span>}
          {scanning ? "Scanning..." : "Run Full Scan"}
        </button>
      </PageHeader>
      <div className="flex-1 overflow-y-auto px-margin-main pb-4">
        <div className="flex gap-4 mb-8 pt-4 overflow-x-auto">
          <div className="flex gap-4 flex-none">
            <StatCard label="Installed" value={summary?.ok ?? 0} sublabel="Packages verified" color="text-green-400" icon="check_circle" />
            <StatCard label="Missing"   value={summary?.missing ?? 0} sublabel="Required dependencies" color="text-error" icon="error" />
            <StatCard label="Issues"    value={summary?.broken ?? 0} sublabel="Path configuration errors" color="text-tertiary" icon="warning" />
          </div>
        </div>

        {results.length === 0 ? (
          <div className="bg-surface-container border border-outline-variant rounded-xl p-12 text-center">
            <span className="material-symbols-outlined text-[48px] text-on-surface-variant opacity-30">health_and_safety</span>
            <p className="text-on-surface-variant mt-4">Run a scan to check your environment.</p>
          </div>
        ) : (
          <div className="bg-surface-container border border-outline-variant rounded-xl overflow-hidden animate-fade-in">
            <div className="px-6 py-4 border-b border-outline-variant bg-surface-container-high flex items-center justify-between">
              <span className="font-sans text-[18px] font-medium">Core Environment</span>
              <div className="flex items-center gap-4 text-[12px] text-on-surface-variant">
                <span>VERSION</span><span className="w-24 text-right">STATUS</span>
              </div>
            </div>
            <div className="divide-y divide-outline-variant">
              {results.map((result) => {
                const meta = TOOL_COLORS[result.name];
                return (
                  <div key={result.name} className="px-6 py-4 flex items-center hover:bg-surface-container-highest transition-colors group">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center mr-4 shrink-0 overflow-hidden bg-surface-container-highest border border-outline-variant">
                      <img src={getLogo(result.name)} alt={`${meta?.label ?? result.name} logo`} className="w-10 h-10 object-contain" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold text-on-surface group-hover:text-primary transition-colors text-[14px]">{meta?.label ?? result.name}</h3>
                      <p className="text-[12px] text-on-surface-variant truncate">{meta?.desc ?? result.note}</p>
                      {result.fix && result.status !== "ok" && <p className="text-[11px] text-yellow-400 mt-0.5 truncate">{result.fix}</p>}
                    </div>
                    <div className="font-mono text-[13px] text-on-surface-variant mr-8 w-24 text-right">
                      {result.status === "ok" ? <span className="text-primary">{result.version?.split(" ")[0] ?? "—"}</span> : <span className="italic opacity-50">not found</span>}
                    </div>
                    <div className="flex items-center gap-3 w-36 justify-end">
                      <StatusBadge status={mapStatus(result)} size="sm" />
                      {result.status !== "ok" && <InstallButton loading={installingTool === result.name} onClick={() => handleFix(result)} label="Fix" variant="ghost" />}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, sublabel, color, icon }: { label: string; value: number; sublabel: string; color: string; icon: string }) {
  return (
    <div className="bg-surface-container p-4 rounded-xl border border-outline-variant transition-colors group w-[180px] min-w-[180px] max-w-[180px] h-[180px] min-h-[180px] max-h-[180px] flex flex-col justify-between">
      <div className="flex justify-between items-start mb-2">
        <span className={`${color} font-medium text-[12px] uppercase tracking-wider`}>{label}</span>
        <span className={`material-symbols-outlined ${color} group-hover:scale-110 transition-transform text-[20px]`} style={{ fontVariationSettings: "'FILL' 1" }}>{icon}</span>
      </div>
      <div className="text-[32px] font-bold text-on-surface leading-none">{value}</div>
      <div className="text-on-surface-variant text-[12px] mt-1">{sublabel}</div>
    </div>
  );
}
