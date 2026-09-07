import React, { useState, useEffect, useRef } from "react"
import { useStore } from "../../store/store"
import { MathRenderer } from "./MathRenderer"

export function PaesExamRunner() {
  const {
    paesQuestions,
    paesCurrentIndex,
    paesActiveQuestion,
    paesExamAnswers,
    paesExamFlags,
    paesExamTimeLimitMinutes,
    paesLoading,
    setExamAnswer,
    toggleExamFlag,
    jumpToPaesQuestion,
    finalizePaesExam,
    exitPaesExam,
  } = useStore()

  // Countdown timer in seconds
  const [secondsRemaining, setSecondsRemaining] = useState(
    (paesExamTimeLimitMinutes || 32) * 60
  )
  const [showConfirmModal, setShowConfirmModal] = useState(false)
  const questionStartTimeRef = useRef(Date.now())

  // Timer interval
  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          finalizePaesExam()
          return 0
        }
        return prev - 1
      })
    }, 1000)
    return () => clearInterval(timer)
  }, [finalizePaesExam])

  // Track time spent per question on question change
  const currentQuestionId = paesActiveQuestion?.id
  const selectedOption = currentQuestionId
    ? paesExamAnswers[currentQuestionId]?.selectedOption || null
    : null
  const isFlagged = currentQuestionId
    ? paesExamFlags.includes(currentQuestionId)
    : false

  const handleSelectOption = (key) => {
    if (!currentQuestionId) return
    const elapsedSeconds = Math.round(
      (Date.now() - questionStartTimeRef.current) / 1000
    )
    setExamAnswer(currentQuestionId, key, elapsedSeconds)
    questionStartTimeRef.current = Date.now()
  }

  const handleNavigate = (newIdx) => {
    if (newIdx < 0 || newIdx >= paesQuestions.length) return
    const elapsedSeconds = Math.round(
      (Date.now() - questionStartTimeRef.current) / 1000
    )
    if (currentQuestionId) {
      setExamAnswer(currentQuestionId, selectedOption, elapsedSeconds)
    }
    questionStartTimeRef.current = Date.now()
    jumpToPaesQuestion(newIdx)
  }

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (showConfirmModal) return
      const key = e.key.toUpperCase()

      if (["A", "B", "C", "D"].includes(key)) {
        handleSelectOption(key)
      } else if (["1", "2", "3", "4"].includes(key)) {
        const mapping = { "1": "A", "2": "B", "3": "C", "4": "D" }
        handleSelectOption(mapping[key])
      } else if (e.key === "ArrowRight") {
        handleNavigate(paesCurrentIndex + 1)
      } else if (e.key === "ArrowLeft") {
        handleNavigate(paesCurrentIndex - 1)
      } else if (e.key === "f" || e.key === "F") {
        if (currentQuestionId) toggleExamFlag(currentQuestionId)
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [paesCurrentIndex, currentQuestionId, selectedOption, showConfirmModal])

  // Format MM:SS or HH:MM:SS
  const formatTime = (secs) => {
    const h = Math.floor(secs / 3600)
    const m = Math.floor((secs % 3600) / 60)
    const s = secs % 60
    if (h > 0) {
      return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`
    }
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`
  }

  const totalQuestions = paesQuestions.length
  const answeredCount = Object.values(paesExamAnswers).filter(
    (a) => a.selectedOption
  ).length
  const isUrgent = secondsRemaining < 300 // < 5 mins

  if (!paesActiveQuestion) return null

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in pb-12">
      {/* Top Exam Header */}
      <header className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-neutral-900/80 border border-white/[0.08] backdrop-blur-md">
        <div className="flex items-center gap-3">
          <span className="p-2.5 rounded-xl bg-sky-500/10 text-sky-400 font-bold text-lg">
            ⏱️
          </span>
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight">
              Simulacro Oficial DEMRE M1
            </h3>
            <p className="text-xs text-neutral-400">
              Respondidas: <strong className="text-emerald-400">{answeredCount}</strong> de {totalQuestions}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Live Timer */}
          <div
            className={`px-4 py-2 rounded-xl border font-mono font-bold text-sm tracking-wider flex items-center gap-2 ${
              isUrgent
                ? "bg-rose-500/15 border-rose-500 text-rose-300 animate-pulse"
                : "bg-neutral-800/80 border-white/[0.08] text-white"
            }`}
          >
            <span className="text-xs text-neutral-400 font-sans font-normal">Restante:</span>
            <span>{formatTime(secondsRemaining)}</span>
          </div>

          <button
            onClick={() => setShowConfirmModal(true)}
            className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-neutral-950 font-bold text-xs rounded-xl transition-all shadow-lg shadow-emerald-500/20 cursor-pointer"
          >
            Finalizar Ensayo ➔
          </button>
        </div>
      </header>

      {/* Main Grid: Navigation Sidebar (Left) + Question Workspace (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Navigation Grid (4 Cols on desktop) */}
        <div className="lg:col-span-4 p-5 rounded-2xl bg-neutral-900/60 border border-white/[0.08] flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/[0.06]">
              <span className="text-xs font-bold uppercase tracking-wider text-neutral-300">
                Matriz de Respuestas
              </span>
              <span className="text-[11px] text-neutral-400 font-mono">
                {answeredCount}/{totalQuestions}
              </span>
            </div>

            {/* Quick Legend */}
            <div className="flex items-center gap-3 text-[10px] text-neutral-400 mb-4">
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded bg-emerald-500" /> Respondida
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded bg-neutral-800 border border-white/20" /> Pendiente
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded bg-amber-500" /> Revisar 🚩
              </span>
            </div>

            {/* Question Buttons Matrix */}
            <div className="grid grid-cols-5 gap-2 max-h-[420px] overflow-y-auto pr-1">
              {paesQuestions.map((q, idx) => {
                const isCurrent = idx === paesCurrentIndex
                const hasAnswer = !!paesExamAnswers[q.id]?.selectedOption
                const isQFlagged = paesExamFlags.includes(q.id)

                let btnClass = "bg-neutral-850 border-white/[0.08] text-neutral-400 hover:border-white/20"
                if (hasAnswer) {
                  btnClass = "bg-emerald-500/20 border-emerald-500/60 text-emerald-300 font-bold"
                }
                if (isQFlagged) {
                  btnClass = "bg-amber-500/25 border-amber-500 text-amber-200 font-bold"
                }
                if (isCurrent) {
                  btnClass += " ring-2 ring-sky-400 border-sky-400 text-white"
                }

                return (
                  <button
                    key={q.id}
                    onClick={() => handleNavigate(idx)}
                    className={`h-9 rounded-xl border text-xs font-mono transition-all flex items-center justify-center relative cursor-pointer ${btnClass}`}
                  >
                    <span>{idx + 1}</span>
                    {isQFlagged && (
                      <span className="absolute -top-1 -right-1 text-[9px]">🚩</span>
                    )}
                  </button>
                )
              })}
            </div>
          </div>

          <div className="pt-4 mt-4 border-t border-white/[0.06] flex items-center justify-between text-[11px] text-neutral-400">
            <span>Atajo: [A, B, C, D] o [1, 2, 3, 4]</span>
            <span>[F] Marcar 🚩</span>
          </div>
        </div>

        {/* Question Workspace (8 Cols) */}
        <div className="lg:col-span-8 p-6 md:p-8 rounded-2xl bg-neutral-900/60 border border-white/[0.08] flex flex-col justify-between backdrop-blur-xl">
          <div>
            {/* Question Header */}
            <div className="flex items-center justify-between gap-3 mb-6 pb-4 border-b border-white/[0.06]">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-bold font-mono">
                  Pregunta {paesCurrentIndex + 1} de {totalQuestions}
                </span>
                {paesActiveQuestion.is_pilot && (
                  <span className="px-2 py-0.5 rounded-md bg-purple-500/10 border border-purple-500/20 text-purple-400 text-[10px] font-bold uppercase tracking-wider">
                    Piloto DEMRE
                  </span>
                )}
              </div>

              <button
                onClick={() => toggleExamFlag(currentQuestionId)}
                className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                  isFlagged
                    ? "bg-amber-500/20 border-amber-500 text-amber-300"
                    : "bg-neutral-800/60 border-white/[0.08] text-neutral-400 hover:text-white"
                }`}
              >
                <span>🚩</span>
                <span>{isFlagged ? "Marcada para Revisión" : "Marcar para Revisar"}</span>
              </button>
            </div>

            {/* Stem */}
            <div className="text-base text-neutral-100 leading-relaxed mb-8 select-text">
              <MathRenderer text={paesActiveQuestion.stem} />
            </div>

            {/* Options List */}
            <div className="space-y-3 mb-8">
              {paesActiveQuestion.options.map((opt) => {
                const key = opt.id || opt.key
                const isSelected = selectedOption === key

                return (
                  <button
                    key={key}
                    onClick={() => handleSelectOption(key)}
                    className={`w-full text-left p-4 rounded-2xl border transition-all flex items-start gap-4 cursor-pointer ${
                      isSelected
                        ? "bg-sky-500/15 border-sky-500 text-white ring-1 ring-sky-500/50 shadow-md shadow-sky-500/10"
                        : "bg-neutral-800/30 border-white/[0.06] hover:bg-neutral-800/60 text-neutral-300"
                    }`}
                  >
                    <div
                      className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs shrink-0 transition-colors ${
                        isSelected
                          ? "bg-sky-400 text-neutral-950 font-black shadow"
                          : "bg-neutral-800 text-neutral-400 border border-white/[0.08]"
                      }`}
                    >
                      {key}
                    </div>
                    <div className="flex-1 pt-1 text-sm md:text-base">
                      <MathRenderer text={opt.content || opt.text} />
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Navigation Controls */}
          <div className="flex items-center justify-between gap-4 pt-6 border-t border-white/[0.06]">
            <button
              onClick={() => handleNavigate(paesCurrentIndex - 1)}
              disabled={paesCurrentIndex === 0}
              className="px-4 py-2.5 rounded-xl border border-white/[0.08] bg-neutral-800/80 hover:bg-neutral-750 disabled:opacity-40 text-neutral-300 text-xs font-bold transition-all cursor-pointer"
            >
              ← Anterior
            </button>

            <div className="text-xs font-mono text-neutral-500 hidden sm:block">
              Navegá con [←] y [→]
            </div>

            {paesCurrentIndex < totalQuestions - 1 ? (
              <button
                onClick={() => handleNavigate(paesCurrentIndex + 1)}
                className="px-5 py-2.5 rounded-xl bg-white hover:bg-neutral-200 text-neutral-950 text-xs font-bold transition-all shadow cursor-pointer"
              >
                Siguiente →
              </button>
            ) : (
              <button
                onClick={() => setShowConfirmModal(true)}
                className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-neutral-950 text-xs font-bold transition-all shadow-lg shadow-emerald-500/20 cursor-pointer"
              >
                Revisar y Entregar ➔
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="max-w-md w-full p-6 rounded-3xl bg-neutral-900 border border-white/[0.1] space-y-5 shadow-2xl">
            <div className="flex items-center gap-3">
              <span className="p-3 rounded-2xl bg-amber-500/10 text-amber-400 text-xl font-bold">
                ⚠️
              </span>
              <div>
                <h4 className="text-base font-bold text-white">¿Finalizar el Ensayo?</h4>
                <p className="text-xs text-neutral-400">
                  Una vez entregado, se calculará tu puntaje oficial DEMRE M1.
                </p>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-neutral-800/50 border border-white/[0.04] space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-neutral-400">Preguntas Respondidas:</span>
                <strong className="text-emerald-400 font-mono">{answeredCount}</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-400">Preguntas Omitidas:</span>
                <strong className="text-amber-400 font-mono">{totalQuestions - answeredCount}</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-400">Marcadas para Revisión:</span>
                <strong className="text-sky-400 font-mono">{paesExamFlags.length}</strong>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="flex-1 py-3 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-xs font-bold transition-colors cursor-pointer"
              >
                Seguir Respondiendo
              </button>
              <button
                onClick={() => {
                  setShowConfirmModal(false)
                  finalizePaesExam()
                }}
                disabled={paesLoading}
                className="flex-1 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-neutral-950 text-xs font-bold transition-all shadow-lg shadow-emerald-500/20 cursor-pointer"
              >
                {paesLoading ? "Calculando..." : "Sí, Entregar Ensayo"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
