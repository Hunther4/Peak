import { useLocation } from "react-router"
import { useStore } from "../../store/store"
import { StatusIndicator } from "../StatusIndicator"

const ROUTE_NAMES = {
  "/": { title: "Centro de Mando", tag: "Dashboard", color: "from-emerald-400 to-teal-500" },
  "/gym": { title: "Gimnasio Cognitivo", tag: "Peak Psychometrics", color: "from-purple-400 to-indigo-500" },
  "/paes": { title: "Academia PAES M1", tag: "Adaptativo DEMRE", color: "from-sky-400 to-blue-600" },
  "/lab": { title: "Laboratorio Metacognitivo", tag: "Telemetría & RAG", color: "from-amber-400 to-orange-500" },
  "/settings": { title: "Ajustes & Sistema", tag: "Hardware & Modelos", color: "from-neutral-400 to-neutral-200" },
}

export default function TopNavBar() {
  const location = useLocation()
  const { profile, summary } = useStore()

  // Match root or nested route
  const basePath = Object.keys(ROUTE_NAMES).find(
    (p) => p === location.pathname || (p !== "/" && location.pathname.startsWith(p))
  ) || "/"

  const routeMeta = ROUTE_NAMES[basePath] || ROUTE_NAMES["/"]
  const streak = summary?.streak_days ?? profile?.streak ?? 0

  return (
    <header className="sticky top-0 z-30 w-full border-b border-white/[0.06] bg-neutral-950/75 backdrop-blur-xl transition-all">
      <div className="max-w-[1440px] mx-auto px-4 lg:px-8 py-3 flex items-center justify-between gap-4">
        {/* Left: View title & badge */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex flex-col">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold tracking-tight text-white">
                {routeMeta.title}
              </span>
              <span className="text-[10px] uppercase font-mono font-bold px-1.5 py-0.5 rounded-md bg-white/[0.05] border border-white/[0.08] text-neutral-300">
                {routeMeta.tag}
              </span>
            </div>
            <span className="text-[11px] text-neutral-500 font-medium">
              Filosofía Anders Ericsson · Feedback Inmediato
            </span>
          </div>
        </div>

        {/* Center: Deliberate telemetry badges */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Streak pill */}
          <div
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-orange-500/[0.08] border border-orange-500/20 text-orange-400 text-xs font-semibold"
            title={`${streak} días consecutivos de entrenamiento deliberado`}
          >
            <span className="text-sm">🔥</span>
            <span className="font-mono font-bold">{streak}</span>
            <span className="hidden md:inline text-[11px] text-orange-300/80 font-normal">días</span>
          </div>

          {/* Deliberate Practice Ratio badge */}
          <div
            className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/[0.08] border border-emerald-500/20 text-emerald-400 text-xs font-semibold"
            title="Calidad de práctica deliberada auditada"
          >
            <span className="text-sm">🎯</span>
            <span className="font-medium text-emerald-300/90 text-[11px]">Enfoque Deliberado</span>
          </div>

          {/* PAES Projection badge */}
          <div
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-sky-500/[0.08] border border-sky-500/20 text-sky-400 text-xs font-semibold"
            title="Escala Oficial DEMRE M1 (100 - 1000 pts)"
          >
            <span className="text-sm">📐</span>
            <span className="font-mono font-bold">M1</span>
            <span className="hidden sm:inline text-[11px] text-sky-300/80 font-normal">DEMRE 2026</span>
          </div>
        </div>

        {/* Right: Status Indicator + Profile */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:block">
            <StatusIndicator />
          </div>

          {/* Profile mini avatar */}
          <div
            className="flex items-center gap-2 pl-2 border-l border-white/[0.08]"
            title={profile?.name || "Usuario Peak"}
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-green-500 to-emerald-400 flex items-center justify-center text-black font-bold text-xs shadow-md shadow-green-500/20">
              {profile?.name ? profile.name.slice(0, 2).toUpperCase() : "PK"}
            </div>
            {profile?.name && (
              <span className="hidden lg:block text-xs font-medium text-neutral-300 max-w-[100px] truncate">
                {profile.name}
              </span>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
