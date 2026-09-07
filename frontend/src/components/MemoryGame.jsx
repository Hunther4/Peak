import { useState, useEffect, useRef, useCallback } from "react"
import { useStore } from "../store/store"
import { useSessionTimer } from "../hooks"
import { GameShell } from "./layout/GameShell"
import { MemoryTips } from "./MemoryTips"

const PHASE_LABELS = {
  acquisition: "Adquisición",
  retention: "Retención",
  consolidation: "Consolidación",
}

const STRATEGY_OPTIONS = [
  { value: "chunking", label: "Chunking (agrupar)" },
  { value: "rehearsal", label: "Repetición" },
  { value: "method_of_loci", label: "Método de loci" },
  { value: "grouping", label: "Agrupar" },
  { value: "none", label: "Ninguna" },
  { value: "other", label: "Otra" },
]

function MemoryGame({ skillId, onClose }) {
  const {
    gameSession,
    currentRound,
    lastAttempt,
    gamePhase,
    gameError,
    consolidationResult,
    sessionMeta,
    metaSaved,
    createMemoryRound,
    submitMemoryAttempt,
    consolidateMemoryGame,
    logRoundStrategy,
    saveSessionMeta,
    updateSessionMeta,
    resetMemoryGame,
  } = useStore()

  const [presentingIndex, setPresentingIndex] = useState(0)
  const [showNumber, setShowNumber] = useState(true)
  const [recallValues, setRecallValues] = useState([])
  const [submitting, setSubmitting] = useState(false)
  const [consolidating, setConsolidating] = useState(false)
  const [error, setError] = useState(null)
  const [showTips, setShowTips] = useState(false)
  const [tipPhase, setTipPhase] = useState("idle")
  const [countdown, setCountdown] = useState(null)
  const [bestSpan, setBestSpan] = useState(null)
  const [bestPhase, setBestPhase] = useState(null)
  const [roundStrategy, setRoundStrategy] = useState(null)
  const presentingTimerRef = useRef(null)

  const sessionTimer = useSessionTimer()

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (presentingTimerRef.current) clearTimeout(presentingTimerRef.current)
    }
  }, [])

  // --- Idle: Start Game ---
  const handleStart = useCallback(async () => {
    setError(null)
    sessionTimer.reset()
    try {
      const store = useStore.getState()
      if (!skillId) throw new Error("No se especificó el skill")
      await store.startMemoryGame(skillId)
      setBestSpan(null)
      setBestPhase(null)
      await store.createMemoryRound()
    } catch (e) {
      setError(e.message)
    }
  }, [skillId, sessionTimer])

  // --- Presenting: Show numbers one at a time (with 3-2-1 countdown) ---
  useEffect(() => {
    if (gamePhase !== "presenting" || !currentRound) return

    const numbers = currentRound.numbers || []
    if (numbers.length === 0) return

    const timing = currentRound.timing || {}
    const perNumberMs = timing.base_ms || 1000

    setPresentingIndex(0)
    setShowNumber(true)
    setRecallValues([])

    // 3-2-1 countdown before first number
    let countdownVal = 3
    setCountdown(countdownVal)
    const countdownInterval = setInterval(() => {
      countdownVal--
      if (countdownVal <= 0) {
        clearInterval(countdownInterval)
        setCountdown(null)
        // Start showing numbers
        let idx = 0
        const showNext = () => {
          if (idx >= numbers.length) {
            presentingTimerRef.current = setTimeout(() => {
              useStore.setState({ gamePhase: "recalling" })
            }, 400)
            return
          }
          setPresentingIndex(idx)
          setShowNumber(true)
          idx++
          presentingTimerRef.current = setTimeout(() => {
            setShowNumber(false)
            presentingTimerRef.current = setTimeout(showNext, 150)
          }, perNumberMs)
        }
        showNext()
      } else {
        setCountdown(countdownVal)
      }
    }, 600)

    return () => {
      if (presentingTimerRef.current) clearTimeout(presentingTimerRef.current)
      clearInterval(countdownInterval)
    }
  }, [gamePhase, currentRound])

  // --- Recalling: Initialize recall values ---
  useEffect(() => {
    if (gamePhase === "recalling" && currentRound) {
      const n = (currentRound.numbers || []).length
      setRecallValues(new Array(n).fill(""))
    }
  }, [gamePhase, currentRound])

  // --- Track best span/phase from staircase results ---
  useEffect(() => {
    if (lastAttempt?.staircase_result) {
      const newSpan = lastAttempt.staircase_result.new_span
      const newPhase = lastAttempt.staircase_result.new_phase
      if (bestSpan === null || newSpan > bestSpan) setBestSpan(newSpan)
      if (bestPhase === null || newPhase > bestPhase) setBestPhase(newPhase)
    }
  }, [lastAttempt])

  // --- Recalling: Submit attempt ---
  const handleSubmitRecall = useCallback(async () => {
    if (!currentRound || submitting) return

    const parsed = recallValues.map((v) => {
      const n = parseInt(v.trim(), 10)
      return isNaN(n) ? null : n
    })

    if (parsed.some((v) => v === null)) {
      setError("Completá todos los campos con números válidos")
      return
    }

    setSubmitting(true)
    setError(null)
    try {
      await submitMemoryAttempt(currentRound.id, parsed)
    } catch (e) {
      setError(e.message)
    } finally {
      setSubmitting(false)
    }
  }, [currentRound, recallValues, submitting, submitMemoryAttempt])

  // --- Feedback: Next round ---
  const handleNextRound = useCallback(async () => {
    setError(null)
    try {
      if (roundStrategy && currentRound) {
        await logRoundStrategy(currentRound.id, roundStrategy)
      }
      setRoundStrategy(null)
      await createMemoryRound()
    } catch (e) {
      setError(e.message)
    }
  }, [createMemoryRound, logRoundStrategy, roundStrategy, currentRound])

  // --- Feedback: Consolidate ---
  const handleConsolidate = useCallback(async () => {
    setConsolidating(true)
    setError(null)
    try {
      if (roundStrategy && currentRound) {
        await logRoundStrategy(currentRound.id, roundStrategy)
      }
      await consolidateMemoryGame(sessionTimer.elapsedSeconds)
    } catch (e) {
      setError(e.message)
    } finally {
      setConsolidating(false)
    }
  }, [consolidateMemoryGame, logRoundStrategy, roundStrategy, currentRound, sessionTimer])

  // --- Done: Back to dashboard ---
  const handleBack = useCallback(() => {
    resetMemoryGame()
    onClose?.()
  }, [resetMemoryGame, onClose])

  // --- Handle recall input change with auto-advance ---
  const handleRecallChange = useCallback((index, value) => {
    const sanitized = value.replace(/\D/g, "").slice(-1) // single digit only
    setRecallValues((prev) => {
      const next = [...prev]
      next[index] = sanitized
      return next
    })
    // Auto-advance to next input when a digit is typed
    if (sanitized) {
      const inputs = document.querySelectorAll('[data-recall-input]')
      if (index < inputs.length - 1) {
        setTimeout(() => inputs[index + 1]?.focus(), 0)
      }
    }
  }, [])

  // --- Keyboard handler for recall ---
  const handleRecallKeyDown = useCallback(
    (e, index) => {
      if (e.key === "Enter") {
        const inputs = document.querySelectorAll('[data-recall-input]')
        if (index < inputs.length - 1) {
          inputs[index + 1].focus()
        } else {
          handleSubmitRecall()
        }
      }
    },
    [handleSubmitRecall]
  )

  // --- Compute derived values ---
  const numbers = currentRound?.numbers || []
  // After submission, prefer the NEW values from staircase_result
  const span = lastAttempt?.staircase_result?.new_span ?? currentRound?.span ?? "-"
  const phase = lastAttempt?.staircase_result?.new_phase ?? currentRound?.phase ?? ""
  const roundsCompleted = gameSession?.rounds_completed ?? 0

  const correctPositions = numbers.map((num, i) => {
    const recall = parseInt(recallValues[i], 10)
    return !isNaN(recall) && recall === num
  })
  const allCorrect = lastAttempt?.correct ?? false
  const streakMessage = lastAttempt?.staircase_result?.message ?? ""

  // --- RENDER ---
  return (
    <GameShell
      title="Memoria de Números"
      subtitle={`Span ${span} · ${PHASE_LABELS[phase] || phase || ""}`}
      icon="🧠"
      accentColor="green"
      level={Number(span) || undefined}
      phase={gamePhase}
      sessionTimer={gamePhase !== "idle" ? sessionTimer.formatTime() : null}
      onBack={handleBack}
      error={error || gameError}
      onClearError={() => setError(null)}
    >
      <main className="max-w-[600px] mx-auto px-6 py-12">
        {/* ===== IDLE ===== */}
        {gamePhase === "idle" && (
          <div className="text-center" style={{ animation: "fadeInUp 0.6s ease-out both" }}>
            <div className="mb-6 flex justify-center">
              {showTips ? (
                <button
                  type="button"
                  onClick={() => setShowTips(false)}
                  className="text-xs text-neutral-500 uppercase tracking-wider hover:text-neutral-300 transition-colors"
                  aria-label="Ocultar consejos de memoria"
                >
                  Ocultar consejos de memoria
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    setTipPhase("idle")
                    setShowTips(true)
                  }}
                  className="text-xs text-neutral-500 uppercase tracking-wider hover:text-neutral-300 transition-colors"
                  aria-label="Ver consejos de memoria"
                >
                  Ver consejos de memoria
                </button>
              )}
            </div>

            {showTips && (
              <div className="max-w-3xl mx-auto mb-10 text-left">
                <MemoryTips
                  phase={tipPhase}
                  compact={false}
                  onDismiss={() => setShowTips(false)}
                />
              </div>
            )}

            <div className="card p-10 md:p-12">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-green-400/20 to-emerald-600/20 border border-green-500/20 flex items-center justify-center text-4xl mx-auto mb-6 shadow-lg shadow-green-500/10">
                🧠
              </div>

              <h2 className="text-2xl md:text-3xl font-black text-white mb-3">
                Memoria de Números
              </h2>
              <p className="text-neutral-400 text-sm leading-relaxed max-w-md mx-auto mb-8">
                Te mostraremos secuencias de números para que los recuerdes y repitas en orden.
                Cada ronda aumenta la dificultad. ¿Cuántos números podés recordar?
              </p>

              <div className="flex flex-col gap-3 max-w-xs mx-auto mb-8">
                <div className="flex items-center gap-3 bg-white/[0.03] rounded-xl px-4 py-3 border border-white/[0.06]">
                  <span className="text-lg">🔢</span>
                  <span className="text-xs text-neutral-400 text-left">Secuencias cada vez más largas</span>
                </div>
                <div className="flex items-center gap-3 bg-white/[0.03] rounded-xl px-4 py-3 border border-white/[0.06]">
                  <span className="text-lg">⏱️</span>
                  <span className="text-xs text-neutral-400 text-left">Tiempo ajustado por dígito</span>
                </div>
                <div className="flex items-center gap-3 bg-white/[0.03] rounded-xl px-4 py-3 border border-white/[0.06]">
                  <span className="text-lg">📈</span>
                  <span className="text-xs text-neutral-400 text-left">Seguimiento de progreso</span>
                </div>
              </div>

              <button onClick={handleStart} className="btn btn-primary text-base px-10 py-3">
                Comenzar
              </button>
            </div>
          </div>
        )}

        {/* ===== PRESENTING ===== */}
        {gamePhase === "presenting" && numbers.length > 0 && (
          <div className="text-center" style={{ animation: "fadeInUp 0.4s ease-out both" }}>
            {/* Countdown before first number */}
            {countdown !== null && (
              <div className="card p-16 md:p-20" style={{ minHeight: "200px" }}>
                <span
                  key={countdown}
                  className="text-9xl font-black text-green-400"
                  style={{
                    animation: "countdownPulse 0.6s ease-out",
                    textShadow: "0 0 60px rgba(34, 197, 94, 0.5)",
                  }}
                >
                  {countdown}
                </span>
                <p className="text-sm text-neutral-500 mt-4">Prepará tu memoria...</p>
              </div>
            )}

            {/* Number display (after countdown) */}
            {countdown === null && (<>
            <div className="mb-6">
              <span className="text-xs text-neutral-500 uppercase tracking-wider">
                Número {Math.min(presentingIndex + 1, numbers.length)} de {numbers.length}
              </span>
              <div className="mt-2 w-full max-w-xs mx-auto h-1 bg-white/[0.06] rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-green-400 to-emerald-500 rounded-full transition-all duration-300"
                  style={{ width: `${((presentingIndex + 1) / numbers.length) * 100}%` }}
                />
              </div>
            </div>

            <div className="mb-8">
              <span className="text-[11px] text-neutral-500 uppercase tracking-wider">
                Span {span} · {PHASE_LABELS[phase] || phase}
              </span>
            </div>

            <div className="card p-12 md:p-16" style={{ minHeight: "200px" }}>
              {showNumber ? (
                <div key={presentingIndex} style={{ animation: "fadeIn 0.15s ease-out" }}>
                  <span className="text-7xl md:text-8xl font-black text-white" style={{ textShadow: "0 0 40px rgba(34, 197, 94, 0.3)" }}>
                    {numbers[presentingIndex]}
                  </span>
                </div>
              ) : (
                <div className="flex items-center justify-center h-[120px]">
                  <div className="w-8 h-8 border-2 border-green-500/30 border-t-green-400 rounded-full animate-spin" />
                </div>
              )}

              <div className="mt-8 flex justify-center gap-1.5">
                {numbers.map((_, i) => (
                  <div
                    key={i}
                    className={`w-2 h-2 rounded-full transition-all duration-300 ${
                      i === presentingIndex && showNumber
                        ? "bg-green-400 shadow-lg shadow-green-500/50 scale-125"
                        : i < presentingIndex
                          ? "bg-green-500/40"
                          : "bg-white/[0.06]"
                    }`}
                  />
                ))}
              </div>
            </div>
            </>)}
          </div>
        )}

        {/* ===== RECALLING ===== */}
        {gamePhase === "recalling" && (
          <div className="text-center" style={{ animation: "fadeInUp 0.4s ease-out both" }}>
            <div className="mb-6">
              <span className="text-xs text-neutral-500 uppercase tracking-wider">
                Ronda {roundsCompleted + 1} · Span {span}
              </span>
              <p className="text-sm text-neutral-400 mt-2">
                Recordá los números en orden
              </p>
            </div>

            <div className="card p-8 md:p-10">
              <div className="flex justify-center gap-3 md:gap-4 flex-wrap mb-8">
                {recallValues.map((val, i) => (
                  <div key={i} className="flex flex-col items-center gap-1">
                    <span className="text-[10px] text-neutral-600 uppercase tracking-wider">
                      #{i + 1}
                    </span>
                    <input
                      data-recall-input
                      type="text"
                      inputMode="numeric"
                      value={val}
                      onChange={(e) => handleRecallChange(i, e.target.value)}
                      onKeyDown={(e) => handleRecallKeyDown(e, i)}
                      autoFocus={i === 0}
                      className="w-16 h-16 md:w-20 md:h-20 text-center text-2xl md:text-3xl font-bold bg-white/[0.04] border border-white/[0.1] rounded-xl text-white focus:outline-none focus:border-green-500/50 focus:bg-white/[0.06] transition-all duration-300"
                      style={{ boxShadow: val ? "0 0 20px rgba(34, 197, 94, 0.08)" : "none" }}
                    />
                  </div>
                ))}
              </div>

              <button
                onClick={handleSubmitRecall}
                disabled={submitting}
                className="btn btn-primary text-base px-10"
              >
                {submitting ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-black/30 border-t-black/80 rounded-full animate-spin" />
                    Enviando...
                  </span>
                ) : (
                  "Enviar"
                )}
              </button>
            </div>
          </div>
        )}

        {/* ===== FEEDBACK ===== */}
        {gamePhase === "feedback" && lastAttempt && (
          <div className="text-center" style={{ animation: "fadeInUp 0.4s ease-out both" }}>
            {streakMessage && (
              <div className="card mb-6 p-5 border-green-500/20 bg-green-500/[0.04]">
                <p className="text-green-400 font-semibold text-sm">{streakMessage}</p>
              </div>
            )}

            <div className="card p-8 md:p-10">
              <h3 className="text-lg font-bold text-white mb-6">Resultados</h3>

              <div className="flex justify-center gap-3 md:gap-4 flex-wrap mb-8">
                {numbers.map((num, i) => {
                  const isCorrect = correctPositions[i]
                  return (
                    <div
                      key={i}
                      className={`flex flex-col items-center gap-2 p-3 rounded-xl border transition-all duration-300 ${
                        isCorrect
                          ? "bg-green-500/[0.06] border-green-500/30"
                          : "bg-red-500/[0.06] border-red-500/30"
                      }`}
                    >
                      <span className="text-[10px] text-neutral-500 uppercase tracking-wider">
                        #{i + 1}
                      </span>
                      <div className="flex items-center gap-2">
                        <span
                          className={`text-2xl md:text-3xl font-bold ${
                            isCorrect ? "text-green-400" : "text-red-400"
                          }`}
                        >
                          {recallValues[i] || "—"}
                        </span>
                        {!isCorrect && (
                          <span className="text-xs text-neutral-500">
                            ({num})
                          </span>
                        )}
                      </div>
                      <span
                        className={`text-[10px] ${
                          isCorrect
                            ? "text-green-500/70"
                            : "text-red-500/70"
                        }`}
                      >
                        {isCorrect ? "✓ Correcto" : "✕ Incorrecto"}
                      </span>
                    </div>
                  )
                })}
              </div>

              <div className="flex items-center justify-center gap-6 mb-8">
                <div className="flex items-center gap-2 bg-white/[0.03] rounded-xl px-4 py-2.5 border border-white/[0.06]">
                  <span className="text-lg font-bold text-white">{span}</span>
                  <span className="text-[10px] text-neutral-500 uppercase">span</span>
                </div>
                <div className="flex items-center gap-2 bg-white/[0.03] rounded-xl px-4 py-2.5 border border-white/[0.06]">
                  <span className="text-lg font-bold text-white">{PHASE_LABELS[phase] || phase}</span>
                  <span className="text-[10px] text-neutral-500 uppercase">fase</span>
                </div>
                <div className="flex items-center gap-2 bg-white/[0.03] rounded-xl px-4 py-2.5 border border-white/[0.06]">
                  <span
                    className={`text-lg font-bold ${
                      allCorrect ? "text-green-400" : "text-orange-400"
                    }`}
                  >
                    {allCorrect ? "✓" : `${correctPositions.filter(Boolean).length}/${numbers.length}`}
                  </span>
                  <span className="text-[10px] text-neutral-500 uppercase">
                    {allCorrect ? "completo" : "aciertos"}
                  </span>
                </div>
              </div>

              {/* Strategy selection — RECOMENDADO, no obligatorio */}
              <div className="mb-6 max-w-md mx-auto">
                <label className="block text-xs text-neutral-500 uppercase tracking-wider mb-3">
                  ¿Qué estrategia usaste? <span className="text-green-500/70 normal-case">(recomendado)</span>
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {STRATEGY_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => setRoundStrategy(opt.value)}
                      className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                        roundStrategy === opt.value
                          ? "bg-green-500/15 border-green-500/50 text-green-300"
                          : "bg-white/[0.03] border-white/[0.06] text-neutral-300 hover:bg-white/[0.06]"
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
                <p className="text-[11px] text-neutral-600 mt-2 text-center">Si la marcás, la IA puede darte mejor feedback sobre tu proceso</p>
              </div>

              <div className="flex items-center justify-center gap-4">
                <button onClick={handleNextRound} className="btn btn-primary text-base px-8">
                  Siguiente ronda
                </button>
                {roundsCompleted >= 2 && (
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

            <div className="mt-6 max-w-xl mx-auto text-left">
              <MemoryTips phase="feedback" compact={true} />
            </div>
          </div>
        )}

        {/* ===== DONE ===== */}
        {gamePhase === "done" && (
          <div className="text-center" style={{ animation: "fadeInUp 0.6s ease-out both" }}>
            <div className="card p-10 md:p-12">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-green-400/20 to-emerald-600/20 border border-green-500/20 flex items-center justify-center text-4xl mx-auto mb-6 shadow-lg shadow-green-500/10">
                🏆
              </div>

              <h2 className="text-2xl md:text-3xl font-black text-white mb-3">
                ¡Sesión completada!
              </h2>
              <p className="text-neutral-400 text-sm mb-8">
                Tu entrenamiento de memoria ha finalizado. Seguí practicando para mejorar tu span.
              </p>

              <div className="grid grid-cols-3 gap-4 mb-8">
                <div className="bg-white/[0.03] rounded-xl p-4 border border-white/[0.06]">
                  <span className="block text-2xl font-black text-white">{roundsCompleted}</span>
                  <span className="text-[10px] text-neutral-500 uppercase tracking-wider">Rondas</span>
                </div>
                <div className="bg-white/[0.03] rounded-xl p-4 border border-white/[0.06]">
                  <span className="block text-2xl font-black text-green-400">{bestSpan ?? gameSession?.best_span ?? span}</span>
                  <span className="text-[10px] text-neutral-500 uppercase tracking-wider">Mejor span</span>
                </div>
                <div className="bg-white/[0.03] rounded-xl p-4 border border-white/[0.06]">
                  <span className="block text-2xl font-black text-white">{PHASE_LABELS[bestPhase ?? gameSession?.best_phase] || bestPhase || phase}</span>
                  <span className="text-[10px] text-neutral-500 uppercase tracking-wider">Mejor fase</span>
                </div>
              </div>

              {/* AI Coaching */}
              {consolidationResult?.coaching_message && (
                <div className="mb-8 bg-green-500/[0.06] border border-green-500/20 rounded-xl p-5 text-left">
                  <p className="text-xs text-green-400 font-semibold mb-2 flex items-center gap-2">
                    <span>🧠</span> Coach
                  </p>
                  <p className="text-sm text-neutral-300 leading-relaxed">
                    {consolidationResult.coaching_message}
                  </p>
                </div>
              )}

              {/* Self-reported difficulty + notes */}
              <div className="mb-8 text-left max-w-md mx-auto space-y-4">
                <div>
                  <label className="block text-xs text-neutral-500 uppercase tracking-wider mb-2">
                    ¿Qué estrategia usaste en general?
                  </label>
                  <select
                    value={sessionMeta.strategy_type}
                    onChange={(e) => updateSessionMeta({ strategy_type: e.target.value })}
                    className="w-full bg-white/[0.04] border border-white/[0.1] rounded-lg px-3 py-2 text-white"
                  >
                    {STRATEGY_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value} className="bg-neutral-900">
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs text-neutral-500 uppercase tracking-wider mb-2">
                    ¿Qué tan difícil te resultó? (1 = fácil, 5 = difícil)
                  </label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((n) => (
                      <button
                        key={n}
                        type="button"
                        onClick={() => updateSessionMeta({ self_reported_difficulty: n })}
                        className={`flex-1 py-2 rounded-lg border text-sm font-bold ${
                          sessionMeta.self_reported_difficulty === n
                            ? "bg-green-500/15 border-green-500/50 text-green-300"
                            : "bg-white/[0.03] border-white/[0.06] text-neutral-300"
                        }`}
                      >
                        {n}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs text-neutral-500 uppercase tracking-wider mb-2">
                    Notas (opcional)
                  </label>
                  <textarea
                    value={sessionMeta.notes}
                    onChange={(e) => updateSessionMeta({ notes: e.target.value })}
                    rows={3}
                    maxLength={500}
                    placeholder="Algo que quieras recordar sobre esta sesión..."
                    className="w-full bg-white/[0.04] border border-white/[0.1] rounded-lg px-3 py-2 text-white text-sm resize-none"
                  />
                </div>

                {!metaSaved && (
                  <button
                    onClick={() => saveSessionMeta(gameSession.id, sessionMeta)}
                    disabled={sessionMeta.self_reported_difficulty == null}
                    className="btn btn-ghost text-sm px-6 w-full"
                  >
                    Guardar feedback
                  </button>
                )}
                {metaSaved && (
                  <p className="text-xs text-green-500 text-center">✓ Feedback guardado</p>
                )}
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

export default MemoryGame