/**
 * Tools.tsx — Tools Page
 *
 * Same card grid pattern as Languages, filtered to category="tool" (Git, VS Code, Docker).
 */
import { useEffect, useState, useCallback } from "react";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { InstallButton } from "@/components/InstallButton";
import { useInstall } from "@/hooks/useInstall";
import { fetchTools, Tool } from "@/services/api";
import { getLogo } from "@/assets/logos/logoMap";

const TOOL_META: Record<string, { label: string; desc: string; color: string; mark: string }> = {
  git:    { label: "Git",     desc: "Version control",  color: "#F05032", mark: "G" },
  vscode: { label: "VS Code", desc: "IDE installation", color: "#007ACC", mark: "VS" },
  docker: { label: "Docker",  desc: "Container engine", color: "#2496ED", mark: "D" },
};

export function ToolsPage() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true); // true for initial load
  const [installingTool, setInstallingTool] = useState<string | null>(null);
  const { install } = useInstall();

  const loadTools = useCallback(async () => {
    // Only show loading placeholders on the very first load
    const isFirstLoad = tools.length === 0;
    if (isFirstLoad) setLoading(true);
    try {
      const all = await fetchTools();
      setTools(all.filter((t) => t.category === "tool"));
    } finally {
      if (isFirstLoad) setLoading(false);
    }
  }, [tools]);
  useEffect(() => { loadTools(); }, [loadTools]);

  const handleInstall = (tool: Tool) => {
    setInstallingTool(tool.name);
    install(`/api/tools/${tool.name}/install`, { method: "POST" }, TOOL_META[tool.name]?.label ?? tool.name,
      async (success) => { setInstallingTool(null); if (success) await loadTools(); });
  };

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Tools" onRefresh={loadTools} />
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        {loading && tools.length === 0 ? (
          <div className="grid grid-cols-3 gap-stack-gap pt-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="card-square rounded-xl bg-surface-container border border-outline-variant animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-[repeat(auto-fit,320px)] justify-start gap-6 pt-4">
            {tools.map((tool) => {
              const meta = TOOL_META[tool.name];
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
                    <p className="text-on-surface-variant text-[14px] opacity-70 line-clamp-2">{meta?.desc}</p>
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
