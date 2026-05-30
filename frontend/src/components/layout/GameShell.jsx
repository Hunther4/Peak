import { BreadcrumbBar } from "./BreadcrumbBar"
import AmbientParticles from "../AmbientParticles"

/**
 * GameShell — Shared game wrapper component.
 * Extracts duplicated layout boilerplate from all 5 game components.
 *
 * Props:
 * - title: string — game title
 * - subtitle: string — game subtitle
 * - icon: string/element — icon to display
 * - accentColor: string — Tailwind color class for accent (default: green)
 * - level: number — current level (shown in header)
 * - phase: string — current phase (if not 'idle' or 'done', show "Presioná Escape")
 * - onBack: () => void — back button handler
 * - error: string | null — error message to display
 * - onClearError: () => void — clear error handler
 * - children: React node — the phase content
 */
export function GameShell({
  title,
  subtitle,
  icon,
  accentColor = "green",
  level,
  phase,
  onBack,
  error,
  onClearError,
  children,
}) {
  const accentStyles = {
    green: "from-green-400 to-emerald-600",
    purple: "from-purple-400 to-violet-600",
    blue: "from-blue-400 to-cyan-600",
    amber: "from-amber-400 to-orange-600",
  }

  const accentGlow = {
    green: "shadow-green-500/25",
    purple: "shadow-purple-500/25",
    blue: "shadow-blue-500/25",
    amber: "shadow-amber-500/25",
  }

  const accentText = {
    green: "text-green-400",
    purple: "text-purple-400",
    blue: "text-blue-400",
    amber: "text-amber-400",
  }

  const styles = accentStyles[accentColor] || accentStyles.green
  const glow = accentGlow[accentColor] || accentGlow.green
  const textColor = accentText[accentColor] || accentText.green

  return (
    <div className="min-h-screen bg-neutral-950 relative overflow-hidden">
      {/* Ambient background — the 4 blur blobs */}
      <AmbientBackground />

      {/* Floating particles */}
      <AmbientParticles />

      {/* Header */}
      <header
        className="sticky top-0 z-50 border-b border-white/[0.06] glass-panel"
        style={{ backdropFilter: "blur(24px) saturate(1.8)" }}
      >
        <div className="max-w-[1400px] mx-auto flex items-center justify-between px-8 py-4">
          <div className="flex items-center gap-4">
            <div
              className={`w-10 h-10 rounded-xl bg-gradient-to-br ${styles} flex items-center justify-center text-black font-black text-lg ${glow} transition-all`}
            >
              {icon}
            </div>
            <div>
              <h1 className="text-xl font-black tracking-tight text-white leading-none">
                {title}
              </h1>
              <p className="text-[10px] uppercase tracking-[0.25em] text-neutral-500 font-medium mt-0.5">
                {subtitle}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {level !== undefined && (
              <span className="text-sm font-mono text-neutral-400">
                Nivel <span className="text-white font-bold">{level}</span>
              </span>
            )}
            {phase && phase !== "idle" && phase !== "done" && (
              <span className="text-[10px] text-neutral-600 italic">
                Presioná Escape para salir
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Back button (breadcrumb) */}
      <BreadcrumbBar onBack={onBack} />

      {/* Error banner */}
      {error && (
        <div className="max-w-[1400px] mx-auto px-6 pt-6">
          <div className="mb-6 p-4 bg-red-500/[0.08] border border-red-500/20 rounded-2xl flex items-center justify-between">
            <p className="text-sm text-red-400">{error}</p>
            {onClearError && (
              <button
                onClick={onClearError}
                className="text-xs text-red-500/60 hover:text-red-400 transition-colors"
              >
                Cerrar
              </button>
            )}
          </div>
        </div>
      )}

      {/* Main content slot */}
      <main className="relative z-10">{children}</main>
    </div>
  )
}