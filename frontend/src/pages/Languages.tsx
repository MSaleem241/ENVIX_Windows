/**
 * Languages.tsx — Languages Page
 *
 * 3-column card grid of programming language runtimes (Node, Python, Java, Go).
 * Fetches /api/tools, filters to category="language", streams installs via SSE.
 */
import { useEffect, useState, useCallback } from "react";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { InstallButton } from "@/components/InstallButton";
import { useInstall } from "@/hooks/useInstall";
import { fetchTools, Tool } from "@/services/api";
import { getLogo } from "@/assets/logos/logoMap";

const LANGUAGE_META: Record<string, { label: string; desc: string; color: string; mark: string }> = {
  node:   { label: "Node.js",     desc: "JavaScript runtime",      color: "#339933", mark: "N" },
  python: { label: "Python 3",    desc: "Scripting & backend",     color: "#3776AB", mark: "Py" },
  java:   { label: "Java 21 JDK", desc: "Java development kit",    color: "#EA2D2E", mark: "J" },
  go:     { label: "Go",          desc: "Systems & cloud backend", color: "#00ADD8", mark: "Go" },
};

export function LanguagesPage() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);
  const [installingTool, setInstallingTool] = useState<string | null>(null);
  const { install } = useInstall();

  const loadTools = useCallback(async () => {
    setLoading(true);
    try {
      const all = await fetchTools();
      setTools(all.filter((t) => t.category === "language"));
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { loadTools(); }, [loadTools]);

  const handleInstall = (tool: Tool) => {
    setInstallingTool(tool.name);
    install(`/api/tools/${tool.name}/install`, { method: "POST" }, LANGUAGE_META[tool.name]?.label ?? tool.name,
      async (success) => { setInstallingTool(null); if (success) await loadTools(); });
  };

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Languages" onRefresh={loadTools}>
        <button className="px-4 py-1.5 rounded-lg bg-surface-container hover:bg-surface-container-high text-on-surface-variant text-[13px] transition-colors border border-outline-variant">
          Check Updates
        </button>
      </PageHeader>

      <div className="flex-1 overflow-y-auto px-4 pb-4">
        {loading && tools.length === 0 ? (
          <div className="grid grid-cols-3 gap-stack-gap pt-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="card-square rounded-xl bg-surface-container border border-outline-variant animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-[repeat(auto-fit,320px)] justify-start gap-6 pt-4">
            {tools.map((tool) => {
              const meta = LANGUAGE_META[tool.name];
              const isInstalling = installingTool === tool.name;
              return (
                <div key={tool.name} className="card-square bg-surface-container p-panel-padding rounded-xl border border-outline-variant hover:border-primary-container/50 transition-all duration-200 group flex flex-col">
                  <div className="flex justify-between items-start mb-4">
                    <div className="w-12 h-12 flex items-center justify-center rounded-lg border border-outline-variant overflow-hidden bg-surface-container-highest">
                      <img src={getLogo(tool.name)} alt={`${meta?.label ?? tool.name} logo`} className="w-12 h-12 object-contain" />
                    </div>
                    <StatusBadge status={isInstalling ? "checking" : tool.installed ? "installed" : "missing"} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-sans text-[18px] font-medium text-on-surface mb-0.5">{meta?.label ?? tool.name}</h3>
                    <p className="text-on-surface-variant text-[14px] opacity-70 line-clamp-2">{meta?.desc ?? ""}</p>
                  </div>
                  <div className="mt-auto pt-4 border-t border-outline-variant/30 flex justify-end">
                    <InstallButton installed={tool.installed} loading={isInstalling} onClick={() => handleInstall(tool)} variant={tool.installed ? "ghost" : "primary"} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
