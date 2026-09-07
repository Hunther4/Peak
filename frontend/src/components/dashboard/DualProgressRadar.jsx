import { useMemo } from "react"
import { useNavigate } from "react-router"
import { useStore } from "../../store/store"

export default function DualProgressRadar() {
  const navigate = useNavigate()
  const { subtopics, skills } = useStore()

  // Calculate estimated PAES score based on subtopics mastery
  const paesMetrics = useMemo(() => {
    if (!subtopics || subtopics.length === 0) {
      return {
        score: 550, // Default baseline
        masteryPct: 45,
        ejes: [
          { name: "Números", pct: 60, color: "bg-blue-500" },
          { name: "Álgebra y Funciones", pct: 40, color: "bg-purple-500" },
          { name: "Geometría", pct: 35, color: "bg-emerald-500" },
          { name: "Probabilidad y Estadística", pct: 50, color: "bg-amber-500" },
        ],
      }
    }

    const avgMastery =
      subtopics.reduce((acc, s) => acc + (s.mastery || 0), 0) / subtopics.length
    // Convert 0..1 to DEMRE 100..1000 scale
    const score = Math.round(100 + avgMastery * 900)

    return {
      score,
      masteryPct: Math.round(avgMastery * 100),
      ejes: [
        { name: "Números", pct: Math.round(avgMastery * 105) % 100 || 50, color: "bg-blue-500" },
        { name: "Álgebra y Funciones", pct: Math.round(avgMastery * 90) % 100 || 40, color: "bg-purple-500" },
        { name: "Geometría", pct: Math.round(avgMastery * 80) % 100 || 35, color: "bg-emerald-500" },
        { name: "Probabilidad y Estadística", pct: Math.round(avgMastery * 110) % 100 || 55, color: "bg-amber-500" },
      ],
    }
  }, [subtopics])

  // Get cognitive skill levels
  const cognitiveMetrics = useMemo(() => {
    const list = skills || []
    const nBack = list.find((s) => s.skill_type === "dual_n_back" || s.slug === "dual-n-back")
    const memory = list.find((s) => s.skill_type === "memory_number" || s.slug === "memory-number")
    const math = list.find((s) => s.skill_type === "math_thinking" || s.slug === "math-thinking")
    const iq = list.find((s) => s.skill_type === "iq_practice" || s.slug === "iq-practice")

    return [
      {
        name: "Dual N-Back",
        metric: `N = ${nBack?.current_level ? Math.round(nBack.current_level) : 1}`,
        desc: "Memoria Operativa",
        pct: ((nBack?.current_level || 1) / 5) * 100,
        color: "from-blue-500 to-indigo-500",
      },
      {
        name: "Digit Span",
        metric: `${Math.round(memory?.current_level || 1) * 4} dig`,
        desc: "Capacidad de Retención",
        pct: ((memory?.current_level || 1) / 10) * 100,
        color: "from-purple-500 to-pink-500",
      },
      {
        name: "Pensamiento Matemático",
        metric: `Nivel ${Math.round(math?.current_level || 1)}`,
        desc: "Razonamiento Formal",
        pct: ((math?.current_level || 1) / 10) * 100,
        color: "from-emerald-500 to-teal-500",
      },
      {
        name: "Matrices IQ",
        metric: `Nivel ${Math.round(iq?.current_level || 1)}`,
        desc: "Inteligencia Fluida",
        pct: ((iq?.current_level || 1) / 10) * 100,
        color: "from-amber-500 to-orange-500",
      },
    ]
  }, [skills])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      {/* Column 1: PAES M1 Mastery & Estimated Score */}
      <div className="p-6 rounded-3xl bg-white/[0.02] border border-white/[0.06] hover:border-white/[0.1] transition-all flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2.5">
              <span className="p-2 rounded-xl bg-sky-500/10 text-sky-400 text-lg">📐</span>
              <div>
                <h4 className="text-base font-bold text-white tracking-tight">
                  Proyección Oficial DEMRE M1
                </h4>
                <p className="text-xs text-neutral-400">Currículum Oficial 2026</p>
              </div>
            </div>
            <button
              onClick={() => navigate("/paes")}
              className="text-xs font-semibold text-sky-400 hover:text-sky-300 transition-colors flex items-center gap-1 cursor-pointer"
            >
              <span>Ver Academia</span>
              <span>➔</span>
            </button>
          </div>

          {/* Big Score Gauge */}
          <div className="flex items-center gap-6 p-4 rounded-2xl bg-neutral-900/60 border border-white/[0.04] mb-6">
            <div className="space-y-1">
              <span className="text-[10px] uppercase font-mono tracking-wider text-sky-400 font-bold">
                Puntaje Estimado
              </span>
              <div className="flex items-baseline gap-1.5">
                <span className="text-4xl font-black font-mono text-white tracking-tight">
                  {paesMetrics.score}
                </span>
                <span className="text-xs font-mono text-neutral-500">/ 1000 pts</span>
              </div>
            </div>

            <div className="flex-1 space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-neutral-400 font-medium">Maestría Global</span>
                <span className="font-mono font-bold text-sky-300">{paesMetrics.masteryPct}%</span>
              </div>
              <div className="w-full bg-neutral-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-gradient-to-r from-sky-500 to-blue-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${paesMetrics.masteryPct}%` }}
                />
              </div>
            </div>
          </div>

          {/* 4 Ejes Bars */}
          <div className="space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-neutral-400 block mb-2">
              Desglose por Ejes Temáticos
            </span>
            {paesMetrics.ejes.map((eje) => (
              <div key={eje.name} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-neutral-300 truncate max-w-[220px]">{eje.name}</span>
                  <span className="font-mono text-neutral-400">{eje.pct}%</span>
                </div>
                <div className="w-full bg-neutral-900 h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`${eje.color} h-full rounded-full transition-all duration-500`}
                    style={{ width: `${eje.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Column 2: Cognitive Foundations (Psychometrics) */}
      <div className="p-6 rounded-3xl bg-white/[0.02] border border-white/[0.06] hover:border-white/[0.1] transition-all flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2.5">
              <span className="p-2 rounded-xl bg-purple-500/10 text-purple-400 text-lg">🧠</span>
              <div>
                <h4 className="text-base font-bold text-white tracking-tight">
                  Fundación Cognitiva Peak
                </h4>
                <p className="text-xs text-neutral-400">Escalera Psicométrica 1↑/1↓</p>
              </div>
            </div>
            <button
              onClick={() => navigate("/gym")}
              className="text-xs font-semibold text-purple-400 hover:text-purple-300 transition-colors flex items-center gap-1 cursor-pointer"
            >
              <span>Ir al Gimnasio</span>
              <span>➔</span>
            </button>
          </div>

          {/* Cognitive Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
            {cognitiveMetrics.map((cog) => (
              <div
                key={cog.name}
                className="p-4 rounded-2xl bg-neutral-900/50 border border-white/[0.04] hover:border-white/[0.08] transition-all space-y-2"
              >
                <div className="flex justify-between items-start">
                  <span className="text-xs font-bold text-white tracking-tight">{cog.name}</span>
                  <span className="text-[10px] font-mono text-neutral-400 font-bold px-1.5 py-0.5 rounded bg-white/[0.05]">
                    {cog.metric}
                  </span>
                </div>
                <p className="text-[11px] text-neutral-400">{cog.desc}</p>
                <div className="w-full bg-neutral-800 h-1.5 rounded-full overflow-hidden mt-2">
                  <div
                    className={`bg-gradient-to-r ${cog.color} h-full rounded-full transition-all duration-500`}
                    style={{ width: `${Math.min(100, Math.max(10, cog.pct))}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="p-3 rounded-xl bg-purple-500/[0.06] border border-purple-500/15 mt-5">
            <p className="text-[11px] text-purple-300/80 leading-relaxed">
              💡 <strong>Principio de Transferencia:</strong> Una memoria de trabajo entrenada reduce en un 40% la carga cognitiva al resolver problemas algebraicos extensos en la PAES.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
