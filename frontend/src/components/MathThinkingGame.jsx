import { useState, useEffect, useRef, useCallback } from "react"
import { useStore } from "../store/store"
import { GameShell } from "./layout/GameShell"

function MathThinkingGame({ skillId, onClose }) {
  const {
    mathSession,
    mathCurrentRound,
    mathLastAttempt,
    mathPhase,
    mathError,
    startMathThinking,
    createMathRound,
    submitMathAttempt,
    consolidateMathThinking,
    resetMathThinking,
  } = useStore()

  const [userAnswer, setUserAnswer] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [consolidating, setConsolidating] = useState(false)
  const [error, setError] = useState(null)
  const [problemsCompleted, setProblemsCompleted] = useState(0)
  const inputRef = useRef(null)

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // reset handled in handleBack
    }
  }, [])

  // --- Start ---
  const handleStart = useCallback(async () => {
    setError(null)
    try {
      if (!skillId) throw new Error("No se especificó el skill")
      await startMathThinking(skillId)
      await createMathRound()
    } catch (e) {
      setError(e.message)
    }
  }, [skillId, startMathThinking, createMathRound])

  // --- Submit answer ---
  const handleSubmit = useCallback(async () => {
    if (!mathCurrentRound || submitting || !userAnswer.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      await submitMathAttempt(mathCurrentRound.id, parseFloat(userAnswer))
      setProblemsCompleted(prev => prev + 1)
    } catch (e) {
      setError(e.message)
    } finally {
      setSubmitting(false)
    }
  }, [mathCurrentRound, submitting, userAnswer, submitMathAttempt])

  // --- Next problem ---
  const handleNext = useCallback(async () => {
    setError(null)
    try {
      await createMathRound()
      setUserAnswer("")
    } catch (e) {
      setError(e.message)
    }
  }, [createMathRound])

  // --- Consolidate ---
  const handleConsolidate = useCallback(async () => {
    setConsolidating(true)
    setError(null)
    try {
      await consolidateMathThinking()
    } catch (e) {
      setError(e.message)
    } finally {
      setConsolidating(false)
    }
  }, [consolidateMathThinking])

  // --- Back ---
  const handleBack = useCallback(() => {
    resetMathThinking()
    onClose?.()
  }, [resetMathThinking, onClose])

  // --- Derived values ---
  const level = mathSession?.level ?? mathLastAttempt?.staircase_result?.new_level ?? 1
  const correct = mathLastAttempt?.correct
  const isCorrect = correct === true
  const solutionSteps = mathLastAttempt?.solution_steps ?? []
  const staircaseMsg = mathLastAttempt?.staircase_result?.message ?? ""
  const canFinish = problemsCompleted >= 3

  const displayError = error || mathError

  // --- RENDER ---
  return (
    <GameShell
      title="Pensamiento Matemático"
      subtitle={`Nivel ${level}/10 · ${problemsCompleted} problemas`}
      icon="∑"
      accentColor="blue"
      level={level}
      phase={mathPhase === "idle" ? null : mathPhase}
      onBack={handleBack}
      error={displayError}
      onClearError={() => setError(null)}
    >
      <main className="max-w-[600px] mx-auto px-6 py-12">
        {/* ===== IDLE ===== */}
        {mathPhase === "idle" && (
          <div className="text-center" style={{ animation: "fadeInUp 0.6s ease-out both" }}>
            <div className="card p-10 md:p-12">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-400/20 to-indigo-600/20 border border-blue-500/20 flex items-center justify-center text-4xl mx-auto mb-6 shadow-lg shadow-blue-500/10">
                🧮
              </div>

              <h2 className="text-2xl md:text-3xl font-black text-white mb-3">
                Pensamiento Matemático
              </h2>
              <p className="text-neutral-400 text-sm leading-relaxed max-w-md mx-auto mb-8">
                Resolvé problemas matemáticos generados por IA adaptados a tu nivel actual.
                Cada acierto te acerca al siguiente nivel. ¿Hasta dónde podés llegar?
              </p>

              <div className="flex flex-col gap-3 max-w-xs mx-auto mb-8">
                <div className="flex items-center gap-3 bg-white/[0.03] rounded-xl px-4 py-3 border border-white/[0.06]">
                  <span className="text-lg">📐</span>
                  <span className="text-xs text-neutral-400 text-left">
                    Problemas según tu nivel actual
                  </span>
                </div>
                <div className="flex items-center gap-3 bg-white/[0.03] rounded-xl px-4 py-3 border border-white/[0.06]">
                  <span className="text-lg">📈</span>
                  <span className="text-xs text-neutral-400 text-left">
                    Dificultad adaptativa del 1 al 10
                  </span>
                </div>
                <div className="flex items-center gap-3 bg-white/[0.03] rounded-xl px-4 py-3 border border-white/[0.06]">
                  <span className="text-lg">💡</span>
                  <span className="text-xs text-neutral-400 text-left">
                    Solución paso a paso si te equivocás
                  </span>
                </div>
              </div>

              <button onClick={handleStart} className="btn btn-primary text-base px-10 py-3">
                Comenzar
              </button>
            </div>
          </div>
        )}

        {/* ===== READY (loading / generating problem) ===== */}
        {mathPhase === "ready" && (
          <div className="text-center" style={{ animation: "fadeInUp 0.4s ease-out both" }}>
            <div className="card p-12 md:p-16">
              <div className="w-16 h-16 mx-auto mb-6 border-4 border-blue-500/30 border-t-blue-400 rounded-full animate-spin" />
              <p className="text-lg font-semibold text-neutral-300 mb-2">
                Generando problema...
              </p>
              <p className="text-sm text-neutral-500">
                La IA está preparando un problema para tu nivel
              </p>
            </div>
          </div>
        )}

        {/* ===== ANSWERING ===== */}
        {mathPhase === "answering" && mathCurrentRound && (
          <div className="text-center" style={{ animation: "fadeInUp 0.4s ease-out both" }}>
            {/* Level indicator */}
            <div className="mb-6">
              <div className="flex items-center justify-center gap-3 mb-3">
                <span className="text-xs text-neutral-500 uppercase tracking-wider">
                  Nivel {level}/10
                </span>
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
                    <div
                      key={n}
                      className={`w-2 h-2 rounded-full transition-all duration-500 ${
                        n <= level
                          ? "bg-blue-400 shadow-lg shadow-blue-500/50"
                          : "bg-white/[0.06]"
                      }`}
                    />
                  ))}
                </div>
              </div>
              <span className="text-[11px] text-neutral-600 uppercase tracking-wider">
                Problema {problemsCompleted + 1}
              </span>
            </div>

            {/* Problem card */}
            <div className="card p-8 md:p-10 mb-6">
              {/* Problem text */}
              <div className="mb-8">
                <p className="text-2xl md:text-3xl font-bold text-white leading-relaxed">
                  {mathCurrentRound.problem_text}
                </p>
              </div>

              {/* Number input */}
              <div className="max-w-xs mx-auto mb-8">
                <label className="block text-xs text-neutral-500 uppercase tracking-wider mb-3 text-left">
                  Tu respuesta
                </label>
                <input
                  ref={inputRef}
                  type="text"
                  inputMode="decimal"
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !submitting) handleSubmit()
                  }}
                  placeholder="0"
                  className="w-full h-16 text-center text-3xl font-bold bg-white/[0.04] border border-white/[0.1] rounded-xl text-white focus:outline-none focus:border-blue-500/50 focus:bg-white/[0.06] transition-all duration-300"
                  style={{
                    boxShadow: userAnswer
                      ? "0 0 20px rgba(59, 130, 246, 0.08)"
                      : "none",
                  }}
                  autoFocus
                />
              </div>

              <button
                onClick={handleSubmit}
                disabled={submitting || !userAnswer.trim()}
                className="btn btn-primary text-base px-10"
              >
                {submitting ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-black/30 border-t-black/80 rounded-full animate-spin" />
                    Verificando...
                  </span>
                ) : (
                  "Enviar respuesta"
                )}
              </button>
            </div>
          </div>
        )}

        {/* ===== FEEDBACK ===== */}
        {mathPhase === "feedback" && mathLastAttempt && (
          <div className="text-center" style={{ animation: "fadeInUp 0.4s ease-out both" }}>
            {/* Staircase message */}
            {staircaseMsg && (
              <div
                className={`card mb-6 p-5 ${
                  isCorrect
                    ? "border-green-500/20 bg-green-500/[0.04]"
                    : "border-yellow-500/20 bg-yellow-500/[0.04]"
                }`}
              >
                <p
                  className={`font-semibold text-sm ${
                    isCorrect ? "text-green-400" : "text-yellow-400"
                  }`}
                >
                  {staircaseMsg}
                </p>
              </div>
            )}

            <div className="card p-8 md:p-10">
              <h3 className="text-lg font-bold text-white mb-6">Resultados</h3>

              {/* Correct/incorrect badge */}
              <div className="mb-8 flex justify-center">
                <div
                  className={`inline-flex items-center gap-3 px-6 py-4 rounded-2xl border ${
                    isCorrect
                      ? "bg-green-500/[0.06] border-green-500/30"
                      : "bg-red-500/[0.06] border-red-500/30"
                  }`}
                >
                  <span className="text-3xl">{isCorrect ? "✅" : "❌"}</span>
                  <div className="text-left">
                    <p
                      className={`text-lg font-bold ${
                        isCorrect ? "text-green-400" : "text-red-400"
                      }`}
                    >
                      {isCorrect ? "¡Correcto!" : "Incorrecto"}
                    </p>
                    <p className="text-xs text-neutral-500">
                      {isCorrect
                        ? "Tu respuesta es correcta"
                        : "Revisá la solución paso a paso"}
                    </p>
                  </div>
                </div>
              </div>

              {/* Solution steps (on error) */}
              {!isCorrect && solutionSteps.length > 0 && (
                <div className="mb-8 bg-white/[0.03] rounded-xl p-6 border border-white/[0.06] text-left">
                  <h4 className="text-sm font-bold text-neutral-300 mb-4 flex items-center gap-2">
                    <span>📝</span> Solución paso a paso
                  </h4>
                  <ol className="space-y-3">
                    {solutionSteps.map((step, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <span className="w-6 h-6 rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-xs text-blue-400 font-bold shrink-0 mt-0.5">
                          {i + 1}
                        </span>
                        <span className="text-sm text-neutral-400 leading-relaxed">
                          {step}
                        </span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Stats row */}
              <div className="flex items-center justify-center gap-4 mb-8">
                <div className="flex items-center gap-2 bg-white/[0.03] rounded-xl px-4 py-2.5 border border-white/[0.06]">
                  <span className="text-lg font-bold text-white">{level}</span>
                  <span className="text-[10px] text-neutral-500 uppercase">
                    nivel
                  </span>
                </div>
                <div className="flex items-center gap-2 bg-white/[0.03] rounded-xl px-4 py-2.5 border border-white/[0.06]">
                  <span className="text-lg font-bold text-white">
                    {problemsCompleted}
                  </span>
                  <span className="text-[10px] text-neutral-500 uppercase">
                    problemas
                  </span>
                </div>
                <div className="flex items-center gap-2 bg-white/[0.03] rounded-xl px-4 py-2.5 border border-white/[0.06]">
                  <span
                    className={`text-lg font-bold ${
                      isCorrect ? "text-green-400" : "text-red-400"
                    }`}
                  >
                    {isCorrect ? "✓" : "✕"}
                  </span>
                  <span className="text-[10px] text-neutral-500 uppercase">
                    {isCorrect ? "correcto" : "incorrecto"}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-center gap-4">
                <button onClick={handleNext} className="btn btn-primary text-base px-8">
                  Siguiente problema
                </button>
                {canFinish && (
                  <button
                    onClick={handleConsolidate}
                    disabled={consolidating}
                    className="btn btn-ghost text-base px-8"
                  >
                    {consolidating ? (
                      <span className="flex items-center gap-2">
                        <span className="w-4 h-4 border-2 border-neutral-400/30 border-t-neutral-300 rounded-full animate-spin" />
                        Finalizando...
                      </span>
                    ) : (
                      "Finalizar sesión"
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ===== DONE ===== */}
        {mathPhase === "done" && (
          <div className="text-center" style={{ animation: "fadeInUp 0.6s ease-out both" }}>
            <div className="card p-10 md:p-12">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-400/20 to-indigo-600/20 border border-blue-500/20 flex items-center justify-center text-4xl mx-auto mb-6 shadow-lg shadow-blue-500/10">
                🏆
              </div>

              <h2 className="text-2xl md:text-3xl font-black text-white mb-3">
                ¡Sesión completada!
              </h2>
              <p className="text-neutral-400 text-sm mb-8">
                Seguí practicando para mejorar tu nivel de pensamiento matemático.
              </p>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 mb-8">
                <div className="bg-white/[0.03] rounded-xl p-4 border border-white/[0.06]">
                  <span className="block text-2xl font-black text-white">
                    {problemsCompleted}
                  </span>
                  <span className="text-[10px] text-neutral-500 uppercase tracking-wider">
                    Problemas
                  </span>
                </div>
                <div className="bg-white/[0.03] rounded-xl p-4 border border-white/[0.06]">
                  <span className="block text-2xl font-black text-blue-400">
                    {level}
                  </span>
                  <span className="text-[10px] text-neutral-500 uppercase tracking-wider">
                    Mejor nivel
                  </span>
                </div>
                <div className="bg-white/[0.03] rounded-xl p-4 border border-white/[0.06]">
                  <span className="block text-2xl font-black text-white">
                    10
                  </span>
                  <span className="text-[10px] text-neutral-500 uppercase tracking-wider">
                    Nivel máximo
                  </span>
                </div>
              </div>

              <button onClick={handleBack} className="btn btn-primary text-base px-10">
                Volver al inicio
              </button>
            </div>
          </div>
        )}
      </main>
    </GameShell>
  )
}

export default MathThinkingGame