/**
 * PageHeader.tsx — Page Header Bar
 *
 * Top bar shown on every page: title, optional badge, and page-specific actions.
 */
interface PageHeaderProps {
  title: string;
  subtitle?: string;
  onRefresh?: () => void;
  children?: React.ReactNode;
}

export function PageHeader({ title, subtitle, onRefresh, children }: PageHeaderProps) {
  return (
    <header className="flex items-center justify-between px-margin-main h-16 bg-background shrink-0">
      <div className="flex items-center gap-3">
        <h1 className="font-sans text-[24px] font-semibold text-on-surface tracking-tight">{title}</h1>
        {subtitle && (
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-primary/10 text-primary text-[12px]">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
            {subtitle}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        {children}
        {onRefresh && (
          <button onClick={onRefresh} className="p-2 text-on-surface-variant hover:text-primary transition-all duration-100 active:scale-95 rounded-lg hover:bg-surface-container-highest" title="Refresh">
            <span className="material-symbols-outlined text-[20px]">refresh</span>
          </button>
        )}
      </div>
    </header>
  );
}
