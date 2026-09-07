import React from "react"
import { MathRenderer } from "./MathRenderer"
import { PaesReadingStimulus } from "./PaesReadingStimulus"

export function PaesQuestionCard({
  question,
  selectedOption,
  onSelectOption,
  confidence,
  onChangeConfidence,
  onSubmit,
  lastResult,
  onNext,
  loading = false,
}) {
  if (!question) return null

  const isSubmitted = !!lastResult

  return (
    <div className="bg-neutral-900/60 border border-white/[0.08] rounded-2xl p-6 backdrop-blur-xl shadow-2xl">
      {/* Header tags */}
      <div className="flex items-center justify-between gap-2 mb-4 pb-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
            {question.provenance_type || "PAES"}
          </span>
          {question.is_pilot && (
            <span className="text-[11px] font-bold uppercase tracking-wider text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded-md border border-purple-500/20">
              Experimental
            </span>
          )}
        </div>
        <div className="text-xs text-neutral-400 font-mono">
          Dificultad est: {Math.round((question.difficulty_estimate || 0.5) * 100)}%
        </div>
      </div>

      {/* Reading Stimulus / Text if available */}
      {question.stimulus_text && (
        <PaesReadingStimulus title={question.stimulus_title} text={question.stimulus_text} />
      )}

      {/* Stem */}
      <div className="mb-6 text-sm md:text-base">
        <MathRenderer text={question.stem} />
      </div>

      {/* Options */}
      <div className="space-y-3 mb-6">
        {question.options.map((opt) => {
          const key = opt.key || opt.id
          const isSelected = selectedOption === key

          let optionStyle = "bg-neutral-800/40 border-white/[0.08] hover:bg-neutral-800/70 text-neutral-200"
          if (isSubmitted) {
            if (lastResult.correct_option === key) {
              optionStyle = "bg-emerald-500/20 border-emerald-500 text-emerald-200"
            } else if (isSelected && !lastResult.is_correct) {
              optionStyle = "bg-rose-500/20 border-rose-500 text-rose-200"
            } else {
              optionStyle = "bg-neutral-900/40 border-white/[0.04] text-neutral-500 opacity-60"
            }
          } else if (isSelected) {
            optionStyle = "bg-emerald-500/15 border-emerald-500 text-white ring-1 ring-emerald-500/50"
          }

          return (
            <button
              key={key}
              type="button"
              disabled={isSubmitted}
              onClick={() => onSelectOption(key)}
              className={`w-full text-left p-4 rounded-xl border transition-all flex items-start gap-3.5 ${optionStyle}`}
            >
              <div
                className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 ${
                  isSelected
                    ? "bg-emerald-500 text-black shadow-md shadow-emerald-500/25"
                    : "bg-neutral-800 text-neutral-300 border border-white/[0.08]"
                }`}
              >
                {key}
              </div>
              <div className="flex-1 pt-0.5 text-sm">
                <MathRenderer text={opt.content || opt.text} />
              </div>
            </button>
          )
        })}
      </div>

      {/* Metacognitive Confidence Selector */}
      {!isSubmitted && (
        <div className="mb-6 p-4 rounded-xl bg-neutral-800/30 border border-white/[0.04] flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <div className="text-xs font-bold text-neutral-300 uppercase tracking-wider">
              Seguridad Metacognitiva
            </div>
            <div className="text-[11px] text-neutral-500">
              Alimenta el cálculo de dominio FSRS y detección de descuidos.
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            {[1, 2, 3, 4, 5].map((lvl) => (
              <button
                key={lvl}
                type="button"
                onClick={() => onChangeConfidence(lvl)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  confidence === lvl
                    ? "bg-emerald-500 text-black shadow-sm"
                    : "bg-neutral-800 text-neutral-400 hover:text-white"
                }`}
              >
                {lvl}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Submit / Next Actions */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/[0.06]">
        {!isSubmitted ? (
          <button
            type="button"
            disabled={!selectedOption || loading}
            onClick={onSubmit}
            className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 disabled:opacity-40 text-black font-bold text-sm rounded-xl shadow-lg shadow-emerald-500/20 transition-all"
          >
            {loading ? "Evaluando..." : "Confirmar Respuesta"}
          </button>
        ) : (
          <div className="w-full">
            {/* Feedback alert */}
            <div
              className={`p-4 rounded-xl border mb-4 ${
                lastResult.is_correct
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                  : "bg-rose-500/10 border-rose-500/30 text-rose-300"
              }`}
            >
              <div className="flex items-center gap-2 font-bold text-sm mb-1">
                <span>{lastResult.is_correct ? "✅ ¡Correcto!" : "❌ Respuesta incorrecta"}</span>
                {lastResult.distractor_cause && (
                  <span className="text-[11px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-200 uppercase font-mono">
                    Causa: {lastResult.distractor_cause}
                  </span>
                )}
              </div>
              {lastResult.explanation?.short_summary && (
                <MathRenderer text={lastResult.explanation.short_summary} className="text-xs mt-1" />
              )}
            </div>

            <div className="flex justify-end">
              <button
                type="button"
                onClick={onNext}
                className="px-6 py-3 bg-white text-black hover:bg-neutral-200 font-bold text-sm rounded-xl shadow-lg transition-all"
              >
                Siguiente Pregunta →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
