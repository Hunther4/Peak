import { useMemo } from "react"
import { useStore } from "../../store/store"

export default function DeliberatePracticeHero() {
  const { summary, timeline, skills } = useStore()

  // Compute Ericsson deliberate metrics
  const stats = useMemo(() => {
    const total = summary?.total_sessions ?? timeline?.length ?? 0
    if (!total || !timeline?.length) {
      return {
        total: total || 0,
        deliberate: 0,
        purposeful: 0,
        naive: 0,
        ratio: 0,
        plateauSkills: [],
      }
    }

    let deliberate = 0
    let purposeful = 0
    let naive = 0

    timeline.forEach((s) => {
      if (s.was_deliberate === true) deliberate++
      else if (s.was_deliberate === false) purposeful++
      else naive++
    })

    const ratio = total > 0 ? Math.round((deliberate / total) * 100) : 0

    // Check for skills currently flagged with a plateau
    const plateauSkills = (skills || []).filter((sk) => sk.plateau || sk.is_plateau)

    return {
      total,
      deliberate,
      purposeful,
      naive,
      ratio,
      plateauSkills,
    }
  }, [summary, timeline, skills])

  return (
    <div className="space-y-4 mb-6">
      {/* Plateau Alert Banner (if any skill is plateaued) */}
      {stats.plateauSkills.length > 0 && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 text-amber-300">
          <span className="text-xl">⚠️</span>
          <div className="space-y-1">
            <h4 className="text-sm font-bold tracking-tight text-amber-200">
              Alerta de Meseta Detectada (Anders Ericsson)
            </h4>
            <p className="text-xs text-amber-300/80 leading-relaxed">
              Has alcanzado una meseta de rendimiento en{" "}
              <strong>{stats.plateauSkills.map((s) => s.name).join(", ")}</strong>. Repetir la misma rutina no generará progreso. Se recomienda cambiar de técnica, aislar el micro-error o consultar el Tutor Socrático.
            </p>
          </div>
        </div>
      )}

      {/* Main Deliberate Matrix Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 lg:gap-4">
        {/* Card 1: Total & Ratio */}
        <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.1] transition-all">
          <div className="flex items-center justify-between text-neutral-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Índice Ericsson</span>
            <span className="text-base">🎯</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl lg:text-3xl font-black font-mono text-emerald-400">
              {stats.ratio}%
            </span>
            <span className="text-xs text-neutral-500">deliberado</span>
          </div>
          <div className="w-full bg-white/[0.06] h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(5, stats.ratio))}%` }}
            />
          </div>
        </div>

        {/* Card 2: Deliberate Sessions */}
        <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.1] transition-all">
          <div className="flex items-center justify-between text-neutral-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Deliberadas</span>
            <span className="text-base">🔬</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl lg:text-3xl font-black font-mono text-white">
              {stats.deliberate}
            </span>
            <span className="text-xs text-neutral-500">sesiones</span>
          </div>
          <span className="text-[10px] text-emerald-400/90 font-medium mt-2 block">
            Con objetivo & micro-errores
          </span>
        </div>

        {/* Card 3: Purposeful Sessions */}
        <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.1] transition-all">
          <div className="flex items-center justify-between text-neutral-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Con Propósito</span>
            <span className="text-base">⚡</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl lg:text-3xl font-black font-mono text-white">
              {stats.purposeful}
            </span>
            <span className="text-xs text-neutral-500">sesiones</span>
          </div>
          <span className="text-[10px] text-sky-400/90 font-medium mt-2 block">
            Estructuradas en la frontera
          </span>
        </div>

        {/* Card 4: Streak & Discipline */}
        <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.1] transition-all">
          <div className="flex items-center justify-between text-neutral-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Disciplina</span>
            <span className="text-base">🔥</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl lg:text-3xl font-black font-mono text-orange-400">
              {summary?.streak_days ?? 0}
            </span>
            <span className="text-xs text-neutral-500">días racha</span>
          </div>
          <span className="text-[10px] text-neutral-400 font-medium mt-2 block">
            {stats.total} entrenamientos totales
          </span>
        </div>
      </div>
    </div>
  )
}
