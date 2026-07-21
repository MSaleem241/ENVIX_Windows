/**
 * LoadingScreen.tsx — Backend Startup Loader
 *
 * Shown while waiting for the Python sidecar to respond to /api/health.
 */
interface LoadingScreenProps { status?: string; }

export function LoadingScreen({ status = "Starting backend..." }: LoadingScreenProps) {
  return (
    <div className="flex h-screen w-screen items-center justify-center bg-background flex-col gap-6">
      <div className="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center shadow-2xl shadow-primary/30">
        <span className="material-symbols-outlined text-on-primary text-[36px]" style={{ fontVariationSettings: "'FILL' 1" }}>
          terminal
        </span>
      </div>
      <div className="text-center">
        <h1 className="font-sans font-semibold text-[24px] text-on-surface mb-1">ENVIX</h1>
        <p className="text-on-surface-variant text-[14px] opacity-70">Dev Environment Manager</p>
      </div>
      <div className="flex gap-1.5">
        {[0, 1, 2].map((i) => (
          <div key={i} className="w-1.5 h-1.5 rounded-full bg-primary opacity-60 animate-pulse" style={{ animationDelay: `${i * 0.2}s` }} />
        ))}
      </div>
      <p className="text-on-surface-variant text-[12px] font-mono opacity-50">{status}</p>
    </div>
  );
}
