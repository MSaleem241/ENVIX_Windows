/**
 * StatusBadge.tsx — Tool Installation Status Pill
 *
 * Reused across Languages, Tools, and Doctor pages to show install state.
 */
interface StatusBadgeProps {
  status: "installed" | "missing" | "path_issue" | "checking";
  size?: "sm" | "md";
}

const BADGE_STYLES = {
  installed:  { wrapper: "bg-green-400/10 text-green-400",  icon: "check_circle",     label: "Installed" },
  missing:    { wrapper: "bg-red-400/10 text-red-400",      icon: "cancel",            label: "Missing" },
  path_issue: { wrapper: "bg-yellow-400/10 text-yellow-400", icon: "warning",          label: "Path Issue" },
  checking:   { wrapper: "bg-on-surface-variant/10 text-on-surface-variant animate-pulse", icon: "hourglass_empty", label: "Checking" },
} as const;

export function StatusBadge({ status, size = "md" }: StatusBadgeProps) {
  const style = BADGE_STYLES[status];
  const sizeClasses = size === "sm" ? "text-[10px] px-1.5 py-0.5" : "text-[12px] px-2 py-0.5";

  return (
    <span className={`inline-flex items-center gap-1 rounded-full font-medium ${style.wrapper} ${sizeClasses}`}>
      <span
        className="material-symbols-outlined"
        style={{ fontSize: size === "sm" ? "12px" : "14px", fontVariationSettings: "'FILL' 1" }}
      >
        {style.icon}
      </span>
      {style.label}
    </span>
  );
}
