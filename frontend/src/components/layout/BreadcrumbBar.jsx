/**
 * BreadcrumbBar — Game back navigation.
 * Extracted from App.jsx to prevent re-creation on every render.
 */
export function BreadcrumbBar({ onBack, label = "Volver al panel" }) {
  return (
    <header
      className="sticky top-0 z-50 border-b border-white/[0.06] glass-panel"
      style={{ backdropFilter: "blur(24px) saturate(1.8)" }}
    >
      <div className="max-w-[1400px] mx-auto flex items-center px-8 py-4">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-xs text-neutral-500 hover:text-white transition-colors px-4 py-2 rounded-lg border border-white/[0.08] hover:border-white/[0.2]"
        >
          <span className="text-base leading-none">←</span>
          {label}
        </button>
      </div>
    </header>
  )
}