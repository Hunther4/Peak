import { useState, useEffect, useRef, useCallback } from "react"
import { useStore } from "../store/store"
import { GameShell } from "./layout/GameShell"

function formatTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`
}

export default function GuidedPractice({ skillId, onClose }) {
  const { summary, createSession } = useStore()

  const [phase, setPhase] = useState("idle")
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [description, setDescription] = useState("")
  const [difficulty, setDifficulty] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [error, setError] = useState(null)

  const timerRef = useRef(null)
  const textareaRef = useRef(null)
  const phaseRef = useRef(phase)
  const isPausedRef = useRef(isPaused)
  phaseRef.current = phase
  isPausedRef.current = isPaused

  // Get skill name from summary
  const skill = summary?.skills?.find(s => s.skill.id === skillId)
  const skillName = skill?.skill?.name || "Práctica"

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [])

  // --- Start practicing ---
  const handleStart = useCallback(() => {
    setError(null)
    setPhase("practicing")
    setElapsedSeconds(0)
    setIsPaused(false)

    timerRef.current = setInterval(() => {
      if (!isPausedRef.current) {
        setElapsedSeconds(prev => prev + 1)
      }
    }, 1000)
  }, [])

  // --- Toggle pause ---
  const togglePause = useCallback(() => {
    setIsPaused(p => !p)
  }, [])

  // --- Finish and save ---
  const handleFinish = useCallback(async () => {
    if (isSubmitting) return

    // Confirm if less than 60 seconds
    if (elapsedSeconds < 60) {
      if (!window.confirm("¿Seguro? Menos de 1 minuto — el registro podría no ser útil.")) {
        return
      }
    }

    setIsSubmitting(true)
    if (timerRef.current) clearInterval(timerRef.current)

    const durationMinutes = Math.max(10, Math.ceil(elapsedSeconds / 60))

    try {
      await createSession({
        skill_id: skillId,
        duration_minutes: durationMinutes,
        what_i_practiced: description.trim() || `Práctica guiada de ${skillName}`,
        difficulty: difficulty,
        entry_mode: "quick",
        timer_elapsed_sec: elapsedSeconds,
        session_data: {
          type: "guided_practice",
          elapsed_seconds: elapsedSeconds,
        },
      })
      setPhase("finished")
    } catch (e) {
      setError(e.message || "Error al guardar la sesión")
    } finally {
      setIsSubmitting(false)
    }
  }, [elapsedSeconds, description, difficulty, skillId, skillName, createSession])

  const finishRef = useRef(handleFinish)
  finishRef.current = handleFinish

  // Keyboard shortcuts
  useEffect(() => {
    const onKeyDown = (e) => {
      if (phaseRef.current !== "practicing") return

      if (e.key === " ") {
        e.preventDefault()
        setIsPaused((p) => !p)
        return
      }

      if (e.key === "Escape") {
        e.preventDefault()
        if (window.confirm("¿Finalizar la práctica? El tiempo se guardará.")) {
          finishRef.current()
        }
      }
    }

    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [])

  return (
    <GameShell
      title="Práctica guiada"
      subtitle={skillName}
      icon="🧠"
      accentColor="green"
      onBack={onClose}
      error={error}
      onClearError={() => setError(null)}
    >
      <main className="flex items-center justify-center min-h-[calc(100vh-200px)] px-6 py-12">
        <div className="w-full max-w-md" style={{ animation: "fadeInUp 0.5s ease-out both" }}>
          {/* IDLE */}
          {phase === "idle" && (
            <div className="card p-8 md:p-10">
              <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center text-2xl mx-auto mb-6">
                🧠
              </div>

              <h2 className="text-2xl font-black text-white text-center mb-1">
                Práctica guiada
              </h2>
              <p className="text-sm text-neutral-400 text-center mb-8">
                {skillName}
              </p>

              {/* Description input */}
              <div className="mb-6">
                <label className="block text-xs text-neutral-500 uppercase tracking-wider mb-2">
                  ¿Qué vas a practicar?
                </label>
                <textarea
                  ref={textareaRef}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Ej: cifrado de Vigenère, algoritmo de Dijkstra..."
                  maxLength={500}
                  className="w-full h-24 px-4 py-3 bg-white/[0.04] border border-white/[0.1] rounded-xl text-white text-sm focus:outline-none focus:border-green-500/50 focus:bg-white/[0.06] transition-all duration-300 resize-none"
                />
              </div>

              {/* Difficulty selector */}
              <div className="mb-6">
                <label className="block text-xs text-neutral-500 uppercase tracking-wider mb-3">
                  Dificultad: {difficulty}/5
                </label>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((n) => (
                    <button
                      key={n}
                      type="button"
                      onClick={() => setDifficulty(n)}
                      className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all border ${
                        n <= difficulty
                          ? "bg-green-500/20 border-green-500/40 text-green-400"
                          : "bg-white/[0.04] border-white/[0.08] text-neutral-500 hover:border-white/[0.2]"
                      }`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>

              <p className="text-xs text-neutral-600 text-center mb-8 leading-relaxed">
                Sin límite — practicá hasta que sientas que aprendiste algo
              </p>

              <button onClick={handleStart} className="btn btn-primary text-base w-full py-3">
                Comenzar práctica
              </button>
            </div>
          )}

          {/* PRACTICING */}
          {phase === "practicing" && (
            <div className="card p-8 md:p-10 text-center">
              <div className="w-full h-1 bg-white/[0.06] rounded-full mb-8 overflow-hidden">
                <div
                  className="h-full bg-green-500 rounded-full transition-all duration-1000 ease-linear"
                  style={{ width: `${Math.min(100, (elapsedSeconds / 1800) * 100)}%` }}
                />
              </div>

              <div
                className={`text-6xl md:text-7xl font-black font-mono tracking-wider mb-4 transition-opacity duration-300 ${
                  isPaused ? "opacity-40" : "text-white"
                }`}
              >
                {formatTime(elapsedSeconds)}
              </div>

              {description && (
                <p className="text-sm text-neutral-400 mb-6 max-w-sm mx-auto line-clamp-2">
                  {description}
                </p>
              )}

              {isPaused && (
                <p className="text-xs text-amber-400/70 mb-6">⏸ Pausado</p>
              )}

              <p className="text-xs text-neutral-600 mb-8">
                Concentrate en lo que estás haciendo
              </p>

              <div className="flex gap-3">
                <button onClick={togglePause} className="btn btn-ghost text-sm flex-1">
                  {isPaused ? "▶ Reanudar" : "⏸ Pausa"}
                </button>
                <button
                  onClick={handleFinish}
                  disabled={isSubmitting}
                  className="btn btn-primary text-sm flex-1"
                >
                  {isSubmitting ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="w-4 h-4 border-2 border-black/30 border-t-black/80 rounded-full animate-spin" />
                      Guardando...
                    </span>
                  ) : (
                    "Finalizar sesión"
                  )}
                </button>
              </div>
            </div>
          )}

          {/* FINISHED */}
          {phase === "finished" && (
            <div className="card p-8 md:p-10 text-center">
              <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center text-2xl mx-auto mb-6">
                🏆
              </div>

              <h2 className="text-2xl font-black text-white mb-8">
                ¡Sesión completada!
              </h2>

              <div className="space-y-3 mb-8 text-left">
                <div className="flex items-center justify-between bg-white/[0.03] rounded-xl px-5 py-3 border border-white/[0.06]">
                  <span className="text-xs text-neutral-500">Duración</span>
                  <span className="text-sm font-bold text-white font-mono">{formatTime(elapsedSeconds)}</span>
                </div>
                <div className="flex items-center justify-between bg-white/[0.03] rounded-xl px-5 py-3 border border-white/[0.06]">
                  <span className="text-xs text-neutral-500">Skill</span>
                  <span className="text-sm font-bold text-white">{skillName}</span>
                </div>
                <div className="flex items-center justify-between bg-white/[0.03] rounded-xl px-5 py-3 border border-white/[0.06]">
                  <span className="text-xs text-neutral-500">¿Qué practicaste?</span>
                  <span className="text-sm font-bold text-white text-right max-w-[200px] truncate" title={description}>
                    {description}
                  </span>
                </div>
                <div className="flex items-center justify-between bg-white/[0.03] rounded-xl px-5 py-3 border border-white/[0.06]">
                  <span className="text-xs text-neutral-500">Dificultad</span>
                  <span className="text-sm font-bold text-white">{difficulty}/5</span>
                </div>
              </div>

              <button onClick={onClose} className="btn btn-primary text-base w-full py-3">
                Volver al panel
              </button>
            </div>
          )}
        </div>
      </main>
    </GameShell>
  )
}