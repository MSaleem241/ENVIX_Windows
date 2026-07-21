/**
 * Presets.tsx — Project Presets Page
 *
 * 3-column preset cards (icon, badge, name, desc, tech tags, Create Project button).
 * Clicking Create: Tauri folder picker → name prompt → SSE stream to console.
 */
import { useEffect, useState, useCallback } from "react";
import { open } from "@tauri-apps/plugin-dialog";
import { PageHeader } from "@/components/PageHeader";
import { useInstall } from "@/hooks/useInstall";
import { fetchPresets, Preset } from "@/services/api";
import { useApp } from "@/AppContext";
import { getLogo } from "@/assets/logos/logoMap";

const PRESET_META: Record<string, { icon: string; iconColor: string; iconBg: string; badge?: string; tags: string[] }> = {
  web:             { icon: "public",         iconColor: "#adc6ff", iconBg: "#adc6ff18", badge: "POPULAR", tags: ["Node.js", "React", "Git", "VS Code"] },
  backend_python:  { icon: "dns",             iconColor: "#3776AB", iconBg: "#3776AB18", tags: ["Python 3.12", "Docker", "PostgreSQL", "Git"] },
  ai_ml:           { icon: "psychology",      iconColor: "#ea580c", iconBg: "#ea580c18", tags: ["PyTorch", "NVIDIA CUDA", "Jupyter", "Python"] },
  data_science:    { icon: "bar_chart",       iconColor: "#0891b2", iconBg: "#0891b218", tags: ["Pandas", "NumPy", "R-Lang"] },
  fullstack:       { icon: "stacks",          iconColor: "#059669", iconBg: "#05906918", badge: "ENTERPRISE", tags: ["TypeScript", "Go", "Redis"] },
  game_dev:        { icon: "sports_esports",  iconColor: "#db2777", iconBg: "#db277718", tags: ["Python", "Pygame"] },
  backend_node:    { icon: "hub",             iconColor: "#339933", iconBg: "#33993318", tags: ["Node.js", "Express", "Git"] },
};

async function askProjectName(label: string): Promise<string | null> {
  const name = window.prompt(`Name your "${label}" project folder:`, label.toLowerCase().replace(/\s+/g, "-"));
  return name?.trim() ?? null;
}

export function PresetsPage() {
  const [presets, setPresets] = useState<Preset[]>([]);
  const [loading, setLoading] = useState(true);
  const [creatingPreset, setCreatingPreset] = useState<string | null>(null);
  const { install } = useInstall();
  const { addLog } = useApp();

  const loadPresets = useCallback(async () => {
    setLoading(true);
    try { setPresets(await fetchPresets()); } finally { setLoading(false); }
  }, []);

  useEffect(() => { loadPresets(); }, [loadPresets]);

  const handleCreate = async (preset: Preset) => {
    let parentFolder: string;
    try {
      const choice = await open({ directory: true, multiple: false, title: `Choose where to create the "${preset.label}" project` });
      if (typeof choice !== "string") {
        addLog({ level: "info", message: `Project creation cancelled — no folder selected for ${preset.label}.` });
        return;
      }
      parentFolder = choice;
    } catch (err) {
      addLog({ level: "error", message: `Folder picker failed: ${err instanceof Error ? err.message : String(err)}` });
      return;
    }

    const projectName = await askProjectName(preset.label);
    if (!projectName) {
      addLog({ level: "info", message: `Project creation cancelled — no project name entered for ${preset.label}.` });
      return;
    }

    const fullPath = `${parentFolder}\\${projectName}`;
    setCreatingPreset(preset.id);
    addLog({ level: "info", message: `▶  Creating ${preset.label} project at ${fullPath}...` });

    install("/api/presets/create", { method: "POST", body: JSON.stringify({ preset_name: preset.id, folder_path: fullPath }) },
      `${preset.label} project`,
      (success) => {
        setCreatingPreset(null);
        if (success) addLog({ level: "success", message: `✓  ${preset.label} project ready at: ${fullPath}` });
      });
  };

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Project Presets" subtitle={`${presets.length} Templates Available`} />
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        <p className="text-on-surface-variant text-[15px] max-w-2xl mt-4 mb-8 leading-relaxed">
          Jumpstart your development with pre-configured environments. Each preset installs the required runtimes, frameworks, and tools for a seamless start.
        </p>

        {loading ? (
          <div className="grid grid-cols-3 gap-stack-gap">
            {Array.from({ length: 6 }).map((_, i) => <div key={i} className="card-8x7 rounded-xl bg-surface-container border border-outline-variant animate-pulse" />)}
          </div>
        ) : (
          <div className="grid grid-cols-[repeat(auto-fit,320px)] justify-start gap-6 animate-fade-in">
            {presets.map((preset) => {
              const meta = PRESET_META[preset.id];
              const isCreating = creatingPreset === preset.id;
              // Apply compact layout for all presets to ensure visual consistency
              const compact = true;
              const tagsToShow = meta?.tags ? meta.tags.slice(0, 3) : meta?.tags;

              return (
                <div key={preset.id} className="card-8x7 bg-surface-container border border-outline-variant rounded-xl p-panel-padding flex flex-col hover:border-primary-container/50 hover:bg-surface-container-high transition-all duration-200 group">
                  <div className={`flex justify-between items-start ${compact ? 'mb-4' : 'mb-6'}`}>
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center overflow-hidden border border-outline-variant bg-surface-container-highest`}>
                      <img src={getLogo(preset.id)} alt={`${preset.label} logo`} className="w-12 h-12 object-contain" />
                    </div>
                    {meta?.badge && <span className={`text-[9px] font-mono uppercase tracking-widest px-2 py-1 rounded border border-outline-variant text-on-surface-variant ${compact ? 'opacity-80' : ''}`}>{meta.badge}</span>}
                  </div>

                  <h3 className={`font-sans font-bold text-on-surface ${compact ? 'text-[16px] mb-1' : 'text-[18px] mb-2'}`}>{preset.label}</h3>

                  <p className={`${compact ? 'text-[12px] leading-tight line-clamp-2 mb-2 text-on-surface-variant' : 'text-on-surface-variant text-[14px] leading-relaxed mb-4 line-clamp-3'}`}>{preset.desc}</p>

                  {meta?.tags && (
                    <div className={`flex flex-wrap gap-1.5 ${compact ? 'mb-3' : 'mb-4'}`}>
                      {tagsToShow?.map((tag) => (
                        <span key={tag} className={`${compact ? 'text-[10px] px-1.5 py-0.5' : 'text-[11px] px-2 py-0.5'} font-mono rounded bg-surface-container-highest border border-outline-variant text-on-surface-variant`}>{tag}</span>
                      ))}
                      {compact && meta?.tags && meta.tags.length > 3 && (
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded border border-outline-variant text-on-surface-variant">+{meta.tags.length - 3}</span>
                      )}
                    </div>
                  )}

                  <button onClick={() => handleCreate(preset)} disabled={isCreating || !!creatingPreset}
                    className="mt-auto w-full flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-white text-[13px] transition-all duration-150 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none shadow-lg shadow-primary/10"
                    style={{ backgroundColor: "#3882F6" }}>
                    {isCreating ? (<><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Creating...</>) : (<>Create Project<span className="material-symbols-outlined text-[18px]">arrow_forward</span></>)}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
