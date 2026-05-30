import { useState, useEffect, useCallback } from "react"
import { useStore } from "../store/store"
import { GameShell } from "./layout/GameShell"

const OPTION_LABELS = ["A", "B", "C", "D"]

const PUZZLE_TYPE_ICONS = {
  number_sequence: "🔢",
  verbal_analogy: "💬",
  logical: "🧩",
  pattern: "🔮",
}

const PUZZLE_TYPE_LABELS = {
  number_sequence: "Secuencia Numérica",
  verbal_analogy: "Analogía Verbal",
  logical: "Razonamiento Lógico",
  pattern: "Reconocimiento de Patrones",
}

export default function IQPracticeGame({ skillId, onClose }) {
  const {
    iqSession,
    iqCurrentRound,
    iqLastAttempt,
    iqPhase,
    iqError,
    startIQPractice,
    createIQRound,
    submitIQAttempt,
    consolidateIQPractice,
    resetIQPractice,
    fetchSummary,
    fetchTimeline,
  } = useStore()

  const [level, setLevel] = useState(1)
  const [bestLevel, setBestLevel] = useState(1)
  const [puzzlesCompleted, setPuzzlesCompleted] = useState(0)
  const [selectedOption, setSelectedOption] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [consolidating, setConsolidating] = useState(false)
  const [error, setError] = useState(null)
  const [staircaseMsg, setStaircaseMsg] = useState("")

  // Key handler
  const handleKeyDown = useCallback((e) => {
    if (iqPhase !== "answering" || !iqCurrentRound || submitting) return
    const key = e.key.toLowerCase()
    if (key === "a" || key === "b" || key === "c" || key === "d") {
      e.preventDefault()
      const idx = key.charCodeAt(0) - 97
      if (idx < iqCurrentRound.options.length) {
        setSelectedOption(idx)
      }
    }
    if (key === "enter" && selectedOption !== null) {
      e.preventDefault()
      handleSubmit()
    }
  }, [iqPhase, iqCurrentRound, submitting, selectedOption])

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [handleKeyDown])

  // --- Start ---
  const handleStart = useCallback(async () => {
    setError(null)
    try {
      const session = await startIQPractice(skillId)
      setLevel(session.level)
      setBestLevel(session.best_level)
      setPuzzlesCompleted(0)
      await createIQRound()
    } catch (e) {
      setError(e.message)
    }
  }, [skillId, startIQPractice, createIQRound])

  // --- Submit answer ---
  const handleSubmit = useCallback(async () => {
    if (!iqCurrentRound || submitting || selectedOption === null) return
    setSubmitting(true)
    setError(null)
    try {
      const answer = iqCurrentRound.options[selectedOption]
      const result = await submitIQAttempt(iqCurrentRound.id, answer)
      setLevel(result.staircase_result.new_level)
      setStaircaseMsg(result.staircase_result.message)
      if (result.staircase_result.new_level > bestLevel) {
        setBestLevel(result.staircase_result.new_level)
      }
      setPuzzlesCompleted(prev => prev + 1)
    } catch (e) {
      setError(e.message)
    } finally {
      setSubmitting(false)
    }
  }, [iqCurrentRound, submitting, selectedOption, bestLevel, submitIQAttempt])

  // --- Next puzzle ---
  const handleNext = useCallback(async () => {
    setError(null)
    try {
      await createIQRound()
      setSelectedOption(null)
      setStaircaseMsg("")
    } catch (e) {
      setError(e.message)
    }
  }, [createIQRound])

  // --- Consolidate ---
  const handleConsolidate = useCallback(async () => {
    if (!iqSession || consolidating) return
    setConsolidating(true)
    setError(null)
    try {
      await consolidateIQPractice()
      fetchSummary()
      fetchTimeline()
    } catch (e) {
      setError(e.message)
    } finally {
      setConsolidating(false)
    }
  }, [iqSession, consolidating, consolidateIQPractice, fetchSummary, fetchTimeline])

  // --- Back ---
  const handleBack = useCallback(() => {
    resetIQPractice()
    onClose?.()
  }, [resetIQPractice, onClose])

  // Staircase indicator component
  const StaircaseBar = ({ cc, ci }) => (
    <div className="flex items-center gap-3 text-xs">
      <div className="flex items-center gap-1.5">
        <span className="text-green-400/70">✓</span>
        <div className="flex gap-0.5">
          {[0, 1, 2].map(i => (
            <div key={i} className={`w-2 h-2 rounded-full transition-all duration-300 ${i < cc ? "bg-green-400 shadow-sm shadow-green-400/50" : "bg-neutral-800"}`} />
          ))}
        </div>
        <span className="text-neutral-600">{cc}/3</span>
      </div>
      <span className="text-neutral-700">|</span>
      <div className="flex items-center gap-1.5">
        <span className="text-red-400/70">✕</span>
        <div className="flex gap-0.5">
          {[0, 1, 2].map(i => (
            <div key={i} className={`w-2 h-2 rounded-full transition-all duration-300 ${i < ci ? "bg-red-400 shadow-sm shadow-red-400/50" : "bg-neutral-800"}`} />
          ))}
        </div>
        <span className="text-neutral-600">{ci}/3</span>
      </div>
    </div>
  )

  return (
    <GameShell
      title="Práctica de IQ"
      subtitle="Razonamiento e inteligencia general"
      icon="IQ"
      accentColor="purple"
      level={level}
      phase={iqPhase}
      onBack={handleBack}
      error={error || iqError}
      onClearError={() => setError(null)}
    >
      <main className="max-w-[700px] mx-auto px-6 py-12">
        {/* IDLE PHASE — Welcome */}
        {iqPhase === "idle" && (
          <div className="space-y-8">
            <div className="card p-10 text-center">
              <div className="w-20 h-20 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-4xl mx-auto mb-6">
                🧠
              </div>
              <h2 className="text-3xl font-black text-white mb-3">Práctica de IQ</h2>
              <p className="text-neutral-400 mb-8 max-w-lg mx-auto leading-relaxed">
                Ejercicios de inteligencia general generados por IA: secuencias numéricas,
                analogías verbales, puzzles lógicos y reconocimiento de patrones.
                Cada 3 correctos <span className="text-green-400">subís de nivel</span>.
              </p>

              <div className="grid grid-cols-2 gap-4 max-w-md mx-auto mb-8">
                {Object.entries(PUZZLE_TYPE_ICONS).map(([type, icon]) => (
                  <div key={type} className="card p-4 text-center">
                    <span className="text-2xl mb-1">{icon}</span>
                    <p className="text-[11px] text-neutral-500 uppercase tracking-wider">{PUZZLE_TYPE_LABELS[type]}</p>
                  </div>
                ))}
              </div>

              <button onClick={handleStart} className="btn btn-primary px-10 py-4 text-lg">
                Comenzar Práctica
              </button>
            </div>
          </div>
        )}

        {/* ANSWERING PHASE */}
        {iqPhase === "answering" && iqCurrentRound && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-sm text-neutral-500">Nivel <span className="text-white font-bold">{level}</span></span>
                <span className="text-sm text-neutral-600">|</span>
                <span className="text-sm text-neutral-500">{puzzlesCompleted} puzzles</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-lg">{PUZZLE_TYPE_ICONS[iqCurrentRound.puzzle_type] || "🧩"}</span>
              <span className="text-xs text-purple-400/80 bg-purple-500/10 px-3 py-1 rounded-full font-mono uppercase tracking-wider">
                {PUZZLE_TYPE_LABELS[iqCurrentRound.puzzle_type] || iqCurrentRound.puzzle_type}
              </span>
            </div>

            <div className="card p-8">
              <p className="text-xl text-white leading-relaxed font-medium">
                {iqCurrentRound.question}
              </p>
            </div>

            <div className="grid grid-cols-1 gap-3">
              {iqCurrentRound.options.map((option, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setSelectedOption(idx)
                    setError(null)
                  }}
                  disabled={submitting}
                  className={`card p-5 text-left transition-all duration-200 cursor-pointer ${
                    selectedOption === idx
                      ? "border-purple-500/50 bg-purple-500/10 ring-1 ring-purple-500/30"
                      : "hover:border-purple-500/20 hover:bg-white/[0.03]"
                  } ${submitting ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                  <div className="flex items-center gap-4">
                    <span className={`w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold transition-all ${
                      selectedOption === idx
                        ? "bg-purple-500 text-white shadow-lg shadow-purple-500/30"
                        : "bg-neutral-800 text-neutral-400"
                    }`}>
                      {OPTION_LABELS[idx]}
                    </span>
                    <span className="text-base text-white">{option}</span>
                  </div>
                </button>
              ))}
            </div>

            <div className="flex justify-center">
              <button
                onClick={handleSubmit}
                disabled={selectedOption === null || submitting}
                className={`btn px-10 py-4 text-lg ${
                  selectedOption !== null && !submitting
                    ? "btn-primary"
                    : "bg-neutral-800 text-neutral-500 cursor-not-allowed"
                }`}
              >
                {submitting ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                    Evaluando...
                  </span>
                ) : (
                  "Confirmar respuesta"
                )}
              </button>
            </div>

            <p className="text-center text-xs text-neutral-600">
              Teclas: <kbd className="text-neutral-400 bg-neutral-800 px-2 py-0.5 rounded font-mono">A</kbd>
              <kbd className="text-neutral-400 bg-neutral-800 px-2 py-0.5 rounded font-mono ml-1">B</kbd>
              <kbd className="text-neutral-400 bg-neutral-800 px-2 py-0.5 rounded font-mono ml-1">C</kbd>
              <kbd className="text-neutral-400 bg-neutral-800 px-2 py-0.5 rounded font-mono ml-1">D</kbd>
              {" "}para elegir, <kbd className="text-neutral-400 bg-neutral-800 px-2 py-0.5 rounded font-mono">Enter</kbd> para enviar
            </p>
          </div>
        )}

        {/* FEEDBACK PHASE */}
        {iqPhase === "feedback" && iqLastAttempt && (
          <div className="space-y-6">
            <div className={`card p-8 text-center border-2 ${
              iqLastAttempt.correct
                ? "border-green-500/30 bg-green-500/[0.04]"
                : "border-red-500/30 bg-red-500/[0.04]"
            }`}>
              <div className="text-6xl mb-4">
                {iqLastAttempt.correct ? "✅" : "❌"}
              </div>
              <h2 className={`text-2xl font-black mb-2 ${iqLastAttempt.correct ? "text-green-400" : "text-red-400"}`}>
                {iqLastAttempt.correct ? "¡Correcto!" : "Incorrecto"}
              </h2>
              <p className="text-neutral-400 text-sm">{staircaseMsg}</p>
            </div>

            <div className="card p-6">
              <p className="text-xs text-neutral-500 uppercase tracking-wider mb-2">Explicación</p>
              <p className="text-sm text-neutral-300 leading-relaxed">
                {iqLastAttempt.explanation || iqLastAttempt.correct_answer}
              </p>
              {!iqLastAttempt.correct && iqLastAttempt.correct_answer && (
                <div className="mt-4 p-3 bg-green-500/[0.06] border border-green-500/20 rounded-xl">
                  <p className="text-xs text-green-400/80 uppercase tracking-wider mb-1">Respuesta correcta</p>
                  <p className="text-base text-white font-medium">{iqLastAttempt.correct_answer}</p>
                </div>
              )}
            </div>

            <div className="card p-5">
              <p className="text-xs text-neutral-500 uppercase tracking-wider mb-3">Progreso de escalera</p>
            </div>

            <div className="flex gap-4 justify-center">
              <button onClick={handleNext} className="btn btn-primary px-8">
                Siguiente puzzle
              </button>
              {puzzlesCompleted >= 3 && (
                <button
                  onClick={handleConsolidate}
                  disabled={consolidating}
                  className="btn btn-secondary px-6"
                >
                  {consolidating ? "Finalizando..." : "Finalizar sesión"}
                </button>
              )}
            </div>

            <p className="text-center text-xs text-neutral-600">
              {puzzlesCompleted < 3
                ? `Completá al menos ${3 - puzzlesCompleted} puzzle${3 - puzzlesCompleted !== 1 ? "s" : ""} más para finalizar`
                : "Podés seguir practicando o finalizar la sesión"}
            </p>
          </div>
        )}

        {/* DONE PHASE */}
        {iqPhase === "done" && (
          <div className="space-y-8">
            <div className="card p-12 text-center">
              <div className="text-6xl mb-4">🎉</div>
              <h2 className="text-3xl font-black text-white mb-2">¡Sesión completada!</h2>
              <p className="text-neutral-400 mb-8">
                Completaste {puzzlesCompleted} puzzles de IQ · Mejor nivel: {bestLevel}
              </p>
              <button onClick={handleBack} className="btn btn-primary px-10 py-4 text-lg">
                Volver al inicio
              </button>
            </div>
          </div>
        )}
      </main>
    </GameShell>
  )
}