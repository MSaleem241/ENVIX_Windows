/**
 * PackageHub.tsx — Package Hub Page
 *
 * Searchable, filterable marketplace of 83+ developer packages.
 * All packages fetched once on mount; search/filter is pure client-side
 * state filtering (debounced 200ms) — no re-fetching on every keystroke,
 * which keeps the grid smooth even with hundreds/thousands of packages.
 */
import { useEffect, useState, useCallback, useRef } from "react";
import { open } from "@tauri-apps/plugin-dialog";
import { PageHeader } from "@/components/PageHeader";
import { InstallButton } from "@/components/InstallButton";
import { useInstall } from "@/hooks/useInstall";
import { fetchPackages, Package } from "@/services/api";
import { useApp } from "@/AppContext";
import { getLogo } from "@/assets/logos/logoMap";

const LANGUAGE_TABS = [
  { id: "all", label: "All" }, { id: "python", label: "Python" },
  { id: "node", label: "Node.js" }, { id: "java", label: "Java" }, { id: "go", label: "Go" },
] as const;

const LANG_COLORS: Record<string, string> = { python: "#3776AB", node: "#339933", java: "#EA2D2E", go: "#00ADD8" };
const LANG_ICON: Record<string, string> = { python: "Py", node: "N", java: "J", go: "Go" };

type FilterLang = "all" | "python" | "node" | "java" | "go";

export function PackageHubPage() {
  const [allPackages, setAllPackages] = useState<Package[]>([]);
  const [filtered, setFiltered] = useState<Package[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<FilterLang>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [installingPkg, setInstallingPkg] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const { install } = useInstall();
  const { addLog } = useApp();

  const loadPackages = useCallback(async () => {
    setLoading(true);
    try {
      const pkgs = await fetchPackages();
      setAllPackages(pkgs);
      setFiltered(pkgs);
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { loadPackages(); }, [loadPackages]);

  const applyFilters = useCallback((query: string, lang: FilterLang, packages: Package[]) => {
    let result = packages;
    if (lang !== "all") result = result.filter((p) => p.language === lang);
    const q = query.toLowerCase().trim();
    if (q) result = result.filter((p) => p.name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q) || p.description.toLowerCase().includes(q));
    setFiltered(result);
  }, []);

  const handleTabChange = (lang: FilterLang) => { setActiveTab(lang); applyFilters(searchQuery, lang, allPackages); };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => applyFilters(value, activeTab, allPackages), 200);
  };

  const handleInstall = async (pkg: Package) => {
    let installDir: string | null;
    try {
      const choice = await open({ directory: true, multiple: false, title: `Choose the project folder for ${pkg.name}` });
      if (typeof choice !== "string") {
        addLog({ level: "info", message: `Package install cancelled — no folder selected for ${pkg.name}.` });
        return;
      }
      installDir = choice;
    } catch (err) {
      addLog({ level: "error", message: `Folder picker failed: ${err instanceof Error ? err.message : String(err)}` });
      return;
    }

    setInstallingPkg(pkg.id);
    addLog({ level: "info", message: `Installing ${pkg.name} into: ${installDir}` });
    install("/api/packages/install", { method: "POST", body: JSON.stringify({ package_id: pkg.id, install_dir: installDir }) },
      pkg.name, () => { setInstallingPkg(null); });
  };

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Package Hub" onRefresh={loadPackages} />
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 pt-4 pb-4 sticky top-0 z-10 bg-background border-b border-outline-variant">
          <div className="relative">
            <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]">search</span>
            <input type="text" value={searchQuery} onChange={(e) => handleSearch(e.target.value)} placeholder="Search languages, frameworks, libraries..."
              className="w-full pl-12 pr-4 py-3 bg-surface-container border border-outline-variant rounded-xl text-on-surface placeholder-on-surface-variant/50 focus:outline-none focus:border-primary/50 focus:bg-surface-container-high transition-all duration-150 text-[15px]" />
          </div>
          <div className="flex items-center justify-between mt-4">
            <div className="flex gap-2">
              {LANGUAGE_TABS.map((tab) => (
                <button key={tab.id} onClick={() => handleTabChange(tab.id as FilterLang)}
                  className={`px-4 py-1.5 rounded-full text-[13px] font-medium transition-all duration-150 ${activeTab === tab.id ? "bg-primary text-on-primary font-bold shadow-md shadow-primary/20" : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high border border-outline-variant"}`}>
                  {tab.label}
                </button>
              ))}
            </div>
            <span className="text-on-surface-variant text-[12px]">{loading ? "Loading..." : `${filtered.length} packages`}</span>
          </div>
        </div>

        <div className="px-4 py-4">
          {loading ? (
            <div className="grid grid-cols-3 gap-stack-gap">
              {Array.from({ length: 6 }).map((_, i) => <div key={i} className="card-square rounded-xl bg-surface-container border border-outline-variant animate-pulse" />)}
            </div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-24">
              <span className="material-symbols-outlined text-[48px] text-on-surface-variant opacity-30">search_off</span>
              <p className="text-on-surface-variant mt-4">No packages found for "{searchQuery}"</p>
            </div>
          ) : (
            <div className="grid grid-cols-[repeat(auto-fit,320px)] justify-start gap-6 animate-fade-in">
              {filtered.map((pkg) => {
                const color = LANG_COLORS[pkg.language] ?? "#adc6ff";
                const icon = LANG_ICON[pkg.language] ?? pkg.language[0].toUpperCase();
                const isInstalling = installingPkg === pkg.id;
                return (
                  <div key={pkg.id} className="card-square glass-card rounded-xl p-panel-padding flex flex-col hover:translate-y-[-1px] transition-all duration-200 group">
                    <div className="flex justify-between items-start mb-3">
                      <div className="w-12 h-12 rounded-lg overflow-hidden border border-outline-variant bg-surface-container-highest flex items-center justify-center group-hover:border-current transition-colors">
                        <img src={getLogo(pkg.id)} alt={`${pkg.name} logo`} className="w-12 h-12 object-contain" />
                      </div>
                      <span className="font-mono text-[12px] text-on-surface-variant opacity-60">latest</span>
                    </div>
                    <h3 className="font-sans text-on-surface font-semibold text-[15px] mb-1">{pkg.name}</h3>
                    <p className="text-on-surface-variant text-[13px] line-clamp-2 flex-1 leading-relaxed">{pkg.description}</p>
                    <div className="mt-3 mb-4">
                      <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded border" style={{ color, borderColor: `${color}40`, backgroundColor: `${color}10` }}>
                        {pkg.category}
                      </span>
                    </div>
                    <div className="flex items-center justify-between pt-3 border-t border-outline-variant/40">
                      <div className="flex items-center gap-1.5 text-on-surface-variant text-[12px]">
                        <span className="material-symbols-outlined text-[14px]">download</span><span className="font-mono">—</span>
                      </div>
                      <InstallButton loading={isInstalling} onClick={() => handleInstall(pkg)} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
