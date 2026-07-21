/**
 * Sidebar.tsx — ENVIX Navigation Sidebar
 *
 * Fixed left sidebar: brand mark, nav links (with 2px active indicator bar),
 * and a footer showing version + backend connection status dot.
 */
import { NavLink } from "react-router-dom";
import envixLogo from "./ENVIX-logo.png";


const NAV_ITEMS: { to: string; label: string; icon: string; badge?: string }[] = [
  { to: "/languages", label: "Languages",      icon: "code" },
  { to: "/tools",     label: "Tools",           icon: "build" },
  { to: "/packages",  label: "Package Hub",     icon: "store" },
  { to: "/presets",   label: "Project Presets", icon: "folder_special" },
  { to: "/doctor",    label: "Doctor",          icon: "health_and_safety" },
  { to: "/assistant", label: "AI Assistant",    icon: "smart_toy", badge: "SOON" },
];

export function Sidebar() {
  return (
    <aside className="flex flex-col fixed left-0 top-0 h-full w-sidebar_width_expanded z-50 bg-surface-container-low border-r border-outline-variant py-panel-padding">
      {/* Brand */}
      <div className="px-6 mb-8 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg overflow-hidden shrink-0 bg-primary shadow-lg shadow-primary/20 flex items-center justify-center">
          <img
            src={envixLogo}
            alt="App logo"
            className="w-full h-full object-cover"
          />
        </div>
        <div>
          <h1 className="font-sans text-[20px] font-semibold text-on-surface tracking-tight leading-none">ENVIX</h1>
          <p className="text-[10px] text-on-surface-variant font-medium tracking-widest uppercase opacity-60">Dev Manager</p>
        </div>
      </div>

      {/* Nav links */}
      <nav className="flex-1 flex flex-col gap-0.5 px-3">
        {NAV_ITEMS.map(({ to, label, icon, badge }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `
              relative flex items-center gap-3 px-4 py-3 rounded-lg text-[13px] font-medium
              transition-all duration-150
              ${isActive
                ? "text-primary bg-secondary-container/30 nav-active-bar"
                : "text-on-surface-variant hover:bg-surface-container-highest hover:text-on-surface"}
            `}
          >
            {({ isActive }) => (
              <>
                <span
                  className="material-symbols-outlined text-[20px] shrink-0"
                  style={isActive ? { fontVariationSettings: "'FILL' 1" } : undefined}
                >
                  {icon}
                </span>
                <span>{label}</span>
                {badge && (
                  <span className="ml-auto text-[9px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded bg-surface-container-highest text-on-surface-variant opacity-70">
                    {badge}
                  </span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer: profile button */}
      <div className="px-2 pt-1 pb-1 -mb-panel-padding border-t border-outline-variant">
        <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg bg-surface-container-highest hover:bg-surface-container transition-colors duration-150 group">
          <div className="w-10 h-10 rounded-lg bg-surface-variant flex items-center justify-center text-on-surface-variant shrink-0">
            <span className="material-symbols-outlined text-[24px]" style={{ fontVariationSettings: "'FILL' 1" }}>account_circle</span>
          </div>
          <div className="flex-1 min-w-0 text-left">
            <p className="font-medium text-on-surface text-[14px]">Profile</p>
            <p className="text-on-surface-variant text-[12px] opacity-70">Settings</p>
          </div>
          <span className="material-symbols-outlined text-[18px] text-on-surface-variant group-hover:text-on-surface transition-colors opacity-60">expand_more</span>
        </button>
      </div>
    </aside>
  );
}
