/**
 * InstallButton.tsx — Animated Install / Reinstall Button
 *
 * Shared across Language cards, Tool cards, Package Hub cards, Doctor rows.
 * Shows a spinner while loading, switches label based on installed state.
 */
interface InstallButtonProps {
  installed?: boolean;
  loading?: boolean;
  onClick: () => void;
  label?: string;
  variant?: "primary" | "ghost";
  disabled?: boolean;
}

export function InstallButton({
  installed = false, loading = false, onClick, label, variant = "primary", disabled = false,
}: InstallButtonProps) {
  const displayLabel = label ?? (loading ? "Installing..." : installed ? "Reinstall" : "Install");

  const base = "inline-flex items-center gap-2 px-4 py-1.5 rounded-lg text-[13px] font-medium transition-all duration-150 active:scale-95 disabled:opacity-50 disabled:pointer-events-none";
  const variantClasses = variant === "ghost" || installed
    ? "text-primary hover:bg-primary/10 border border-primary/20"
    : "bg-primary hover:bg-primary-container text-on-primary shadow-lg shadow-primary/10";

  return (
    <button onClick={onClick} disabled={disabled || loading} className={`${base} ${variantClasses}`}>
      <span className={`w-3.5 h-3.5 ${loading ? 'border-2 border-current border-t-transparent rounded-full animate-spin' : 'invisible'}`} />
      {displayLabel}
    </button>
  );
}
