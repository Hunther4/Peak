import React, { useState } from "react"
import { useStore } from "../../store/store"
import { MathRenderer } from "./MathRenderer"

export function PaesExamResults({ onNewExam, onBackToStudy }) {
  const { paesExamResults } = useStore()
  const [filter, setFilter] = useState("all") // all | errors | correct | unanswered
  const [expandedId, setExpandedId] = useState(null)

  if (!paesExamResults) return null

  const {
    total_questions,
    correct_count,
    incorrect_count,
    unanswered_count,
    accuracy_pct,
    total_time_seconds,
    avg_time_per_question,
    demre,
    ejes_breakdown,
    review = [],
  } = paesExamResults

  // Format time (MM:SS)
  const formatTime = (secs) => {
    const m = Math.floor(secs / 60)
    const s = secs % 60
    return `${m}m ${s}s`
  }

  const filteredReview = review.filter((item) => {
    if (filter === "errors") return !item.is_correct && !item.is_unanswered
    if (filter === "correct") return item.is_correct
    if (filter === "unanswered") return item.is_unanswered
    return true
  })

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in pb-16">
      {/* Top Banner: Official DEMRE Score Hero */}
      <div className="p-8 rounded-3xl bg-gradient-to-br from-neutral-900 via-neutral-900 to-sky-950/40 border border-white/[0.1] relative overflow-hidden shadow-2xl">
        <div className="absolute -right-8 -top-8 w-48 h-48 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="space-y-2 text-center md:text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/15 border border-sky-500/25 text-sky-400 text-xs font-bold tracking-wider uppercase font-mono">
              <span>🎯</span>
              <span>Puntaje Proyectado Admisión 2026</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-black text-white tracking-tight">
              Resultado Oficial DEMRE M1
            </h2>
            <p className="text-xs text-neutral-400 max-w-md leading-relaxed">
              Basado en la Tabla de Transformación oficial DEMRE para la prueba de Competencia Matemática 1 regular.
            </p>
          </div>

          {/* Big Score Gauge */}
          <div className="p-6 rounded-3xl bg-neutral-950/80 border border-white/[0.08] text-center min-w-[240px] shadow-xl">
            <span className="text-[11px] uppercase font-mono tracking-widest text-sky-400 font-bold block mb-1">
              Escala 100 - 1000 pts
            </span>
            <div className="text-5xl md:text-6xl font-black font-mono text-white tracking-tight">
              {demre.estimated_score}
            </div>
            <div className="text-xs text-neutral-400 font-mono mt-1">
              Rango: <span className="text-neutral-200 font-bold">{demre.estimated_range_str}</span>
            </div>
            <div className="mt-3 pt-3 border-t border-white/[0.06] text-[11px] text-sky-300/90 font-medium">
              Percentil Aprox: <strong>~{demre.percentile_approx}%</strong>
            </div>
          </div>
        </div>

        {/* Quick Metrics Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-8 pt-6 border-t border-white/[0.06]">
          <div className="p-3.5 rounded-2xl bg-neutral-900/60 border border-white/[0.04]">
            <span className="text-[10px] text-neutral-400 uppercase font-mono">Aciertos</span>
            <div className="text-xl font-bold font-mono text-emerald-400 mt-0.5">
              {correct_count} <span className="text-xs text-neutral-500">/ {total_questions}</span>
            </div>
          </div>
          <div className="p-3.5 rounded-2xl bg-neutral-900/60 border border-white/[0.04]">
            <span className="text-[10px] text-neutral-400 uppercase font-mono">Errores</span>
            <div className="text-xl font-bold font-mono text-rose-400 mt-0.5">
              {incorrect_count}
            </div>
          </div>
          <div className="p-3.5 rounded-2xl bg-neutral-900/60 border border-white/[0.04]">
            <span className="text-[10px] text-neutral-400 uppercase font-mono">Omitidas</span>
            <div className="text-xl font-bold font-mono text-amber-400 mt-0.5">
              {unanswered_count}
            </div>
          </div>
          <div className="p-3.5 rounded-2xl bg-neutral-900/60 border border-white/[0.04]">
            <span className="text-[10px] text-neutral-400 uppercase font-mono">Tiempo Promedio</span>
            <div className="text-xl font-bold font-mono text-white mt-0.5">
              {formatTime(avg_time_per_question)}
            </div>
          </div>
        </div>
      </div>

      {/* 4 DEMRE Ejes Thematic Breakdown */}
      <div className="p-6 md:p-8 rounded-3xl bg-neutral-900/60 border border-white/[0.08] space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-xl bg-purple-500/10 text-purple-400 text-lg font-bold">
              📊
            </span>
            <div>
              <h4 className="text-base font-bold text-white tracking-tight">
                Desglose por Ejes Temáticos DEMRE
              </h4>
              <p className="text-xs text-neutral-400">Rendimiento específico por área curricular</p>
            </div>
          </div>
          <span className="text-xs font-mono text-neutral-400">
            Precisión Global: <strong>{accuracy_pct}%</strong>
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {ejes_breakdown.map((eje) => (
            <div
              key={eje.name}
              className="p-4 rounded-2xl bg-neutral-950/60 border border-white/[0.04] space-y-2"
            >
              <div className="flex justify-between items-center text-xs">
                <span className="font-bold text-neutral-200">{eje.name}</span>
                <span className="font-mono text-neutral-400">
                  {eje.correct}/{eje.total} ({eje.percentage}%)
                </span>
              </div>
              <div className="w-full bg-neutral-800 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    eje.percentage >= 70
                      ? "bg-emerald-500"
                      : eje.percentage >= 50
                      ? "bg-amber-500"
                      : "bg-rose-500"
                  }`}
                  style={{ width: `${eje.percentage}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-neutral-900/40 border border-white/[0.06]">
        <button
          onClick={onBackToStudy}
          className="px-5 py-2.5 rounded-xl border border-white/[0.08] hover:bg-neutral-800 text-neutral-300 text-xs font-bold transition-all cursor-pointer"
        >
          ← Volver a la Academia PAES
        </button>
        <button
          onClick={onNewExam}
          className="px-6 py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-neutral-950 font-bold text-xs transition-all shadow-lg shadow-sky-500/20 cursor-pointer"
        >
          Nuevo Simulacro ➔
        </button>
      </div>

      {/* Interactive Solucionario (Question by Question Review) */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <span>📖</span>
            <span>Solucionario Detallado & Análisis de Distractores</span>
          </h3>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 p-1 bg-neutral-900/80 rounded-xl border border-white/[0.06] text-xs">
            {[
              { key: "all", label: `Todas (${review.length})` },
              { key: "errors", label: `Errores (${incorrect_count})` },
              { key: "correct", label: `Aciertos (${correct_count})` },
              { key: "unanswered", label: `Omitidas (${unanswered_count})` },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key)}
                className={`px-3 py-1.5 rounded-lg font-semibold transition-all cursor-pointer ${
                  filter === tab.key
                    ? "bg-white text-neutral-950 shadow"
                    : "text-neutral-400 hover:text-white"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* List of Review Cards */}
        <div className="space-y-3">
          {filteredReview.map((item, idx) => {
            const isExpanded = expandedId === item.question_id
            const isCorrect = item.is_correct
            const isUnanswered = item.is_unanswered

            let statusBadge = (
              <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-xs font-bold font-mono">
                ✓ Correcta
              </span>
            )
            if (isUnanswered) {
              statusBadge = (
                <span className="px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/25 text-amber-400 text-xs font-bold font-mono">
                  - Omitida
                </span>
              )
            } else if (!isCorrect) {
              statusBadge = (
                <span className="px-2.5 py-1 rounded-lg bg-rose-500/10 border border-rose-500/25 text-rose-400 text-xs font-bold font-mono">
                  ✕ Incorrecta
                </span>
              )
            }

            return (
              <div
                key={item.question_id}
                className="rounded-2xl bg-neutral-900/60 border border-white/[0.06] overflow-hidden transition-all hover:border-white/[0.1]"
              >
                {/* Accordion Bar */}
                <div
                  onClick={() => setExpandedId(isExpanded ? null : item.question_id)}
                  className="p-5 flex items-center justify-between gap-4 cursor-pointer select-none"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-8 h-8 rounded-xl bg-neutral-800 text-neutral-300 font-mono font-bold text-xs flex items-center justify-center shrink-0">
                      {idx + 1}
                    </span>
                    <div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-neutral-400 font-medium">{item.eje_name}</span>
                        <span className="text-neutral-600">•</span>
                        <span className="text-neutral-500">{item.subtopic_name}</span>
                      </div>
                      <p className="text-sm font-semibold text-neutral-200 line-clamp-1 mt-0.5">
                        {item.stem.replace(/[$]/g, "")}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    {statusBadge}
                    <span className="text-neutral-500 text-xs transition-transform duration-200">
                      {isExpanded ? "▲" : "▼"}
                    </span>
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="p-6 pt-2 border-t border-white/[0.04] bg-neutral-950/40 space-y-6 animate-fade-in">
                    {/* Stem */}
                    <div className="p-4 rounded-xl bg-neutral-900/50 border border-white/[0.04] text-sm md:text-base text-neutral-100 leading-relaxed">
                      <MathRenderer text={item.stem} />
                    </div>

                    {/* Options Breakdown */}
                    <div className="space-y-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-neutral-400 block mb-2">
                        Alternativas
                      </span>
                      {item.options.map((opt) => {
                        const key = opt.id || opt.key
                        const wasSelected = item.selected_option === key
                        const isThisCorrect = opt.is_correct || item.correct_option === key

                        let optClass = "bg-neutral-900/40 border-white/[0.04] text-neutral-400"
                        if (isThisCorrect) {
                          optClass = "bg-emerald-500/15 border-emerald-500 text-emerald-200 font-semibold"
                        } else if (wasSelected && !isThisCorrect) {
                          optClass = "bg-rose-500/15 border-rose-500 text-rose-200"
                        }

                        return (
                          <div
                            key={key}
                            className={`p-3.5 rounded-xl border flex items-start gap-3 text-sm ${optClass}`}
                          >
                            <div className="font-bold font-mono text-xs w-6 h-6 rounded-lg bg-black/30 flex items-center justify-center shrink-0">
                              {key}
                            </div>
                            <div className="flex-1">
                              <MathRenderer text={opt.content || opt.text} />
                            </div>
                            {isThisCorrect && (
                              <span className="text-xs text-emerald-400 font-bold font-mono">
                                Correcta
                              </span>
                            )}
                            {wasSelected && !isThisCorrect && (
                              <span className="text-xs text-rose-400 font-bold font-mono">
                                Tu Selección
                              </span>
                            )}
                          </div>
                        )
                      })}
                    </div>

                    {/* Mathematical Solution & Explanation */}
                    {item.explanation && (
                      <div className="p-4 rounded-xl bg-sky-500/[0.06] border border-sky-500/20 space-y-2">
                        <div className="text-xs font-bold text-sky-400 uppercase tracking-wider flex items-center gap-1.5">
                          <span>💡</span>
                          <span>Solución Paso a Paso</span>
                        </div>
                        <div className="text-xs text-neutral-300 leading-relaxed">
                          <MathRenderer
                            text={
                              item.explanation.correct_solution ||
                              item.explanation.short_summary ||
                              "Explicación formal disponible en el solucionario oficial."
                            }
                          />
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
