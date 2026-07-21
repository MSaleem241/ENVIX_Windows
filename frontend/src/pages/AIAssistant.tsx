/**
 * AIAssistant.tsx — AI Assistant Page (Coming Soon)
 *
 * Placeholder with a clean empty state. Sidebar shows "SOON" badge.
 */
import { PageHeader } from "@/components/PageHeader";

export function AIAssistantPage() {
  return (
    <div className="flex flex-col h-full">
      <PageHeader title="AI Assistant" />
      <div className="flex-1 flex flex-col items-center justify-center text-center pb-20">
        <div className="w-20 h-20 rounded-2xl bg-surface-container border border-outline-variant flex items-center justify-center mb-6">
          <span className="material-symbols-outlined text-[40px] text-on-surface-variant opacity-40" style={{ fontVariationSettings: "'FILL' 1" }}>smart_toy</span>
        </div>
        <h2 className="font-sans font-bold text-[20px] text-on-surface mb-3">AI Assistant</h2>
        <p className="text-on-surface-variant text-[14px] max-w-sm leading-relaxed mb-6">
          An intelligent assistant that helps you configure environments, debug installation issues, and suggests packages based on your project.
        </p>
        <span className="text-[10px] font-mono uppercase tracking-widest px-3 py-1.5 rounded-full border border-outline-variant text-on-surface-variant opacity-60">Coming Soon</span>
      </div>
    </div>
  );
}
