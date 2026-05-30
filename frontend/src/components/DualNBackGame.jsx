import { useState, useEffect, useRef, useCallback } from "react"
import { useStore } from "../store/store"
import { GameShell } from "./layout/GameShell"
import api from "../api/client"

const GRID_SIZE = 3
const TOTAL_POSITIONS = GRID_SIZE * GRID_SIZE
const LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H"]
const STIMULUS_MS = 500
const ISI_MS = 2500
const TRIALS_PER_BLOCK = 20

function generateSequence(n, length) {
  const positions = Array.from({ length }, () => Math.floor(Math.random() * TOTAL_POSITIONS))
  const letters = Array.from({ length }, () => Math.floor(Math.random() * LETTERS.length))

  const visualTargets = new Set()
  const audioTargets = new Set()

  for (let i = n; i < length; i++) {
    if (Math.random() < 0.3) visualTargets.add(i)
    if (Math.random() < 0.3) audioTargets.add(i)
  }

  return { positions, letters, visualTargets, audioTargets }
}

function DualNBackGame({ onClose }) {
  const { consolidateDualNBack } = useStore()

  const [n, setN] = useState(1)
  const [phase, setPhase] = useState("setup")
  const [sequence, setSequence] = useState(null)
  const [trialIndex, setTrialIndex] = useState(-1)
  const [showingStimulus, setShowingStimulus] = useState(false)
  const [activePosition, setActivePosition] = useState(null)
  const [activeLetter, setActiveLetter] = useState(null)
  const [responses, setResponses] = useState([])
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [consolidated, setConsolidated] = useState(false)
  const [message, setMessage] = useState("")

  const trialTimer = useRef(null)
  const stimulusTimer = useRef(null)
  const synthRef = useRef(null)
  const responseWindowStart = useRef(0)

  // Cleanup
  useEffect(() => {
    synthRef.current = window.speechSynthesis
    return () => {
      if (trialTimer.current) clearTimeout(trialTimer.current)
      if (stimulusTimer.current) clearTimeout(stimulusTimer.current)
      synthRef.current?.cancel()
    }
  }, [])

  // Start game
  const handleStart = useCallback(() => {
    const seq = generateSequence(n, TRIALS_PER_BLOCK + n)
    setSequence(seq)
    setTrialIndex(-1)
    setResponses([])
    setResults(null)
    setConsolidated(false)
    setMessage("")
    setPhase("playing")
  }, [n])

  // Run trial
  const runTrial = useCallback((index, seq) => {
    if (index >= TRIALS_PER_BLOCK + n) {
      // Calculate results
      const validResponses = responses.filter(r => r.trial >= n)
      const correct = validResponses.filter(r => r.correct).length
      const visCorrect = validResponses.filter(r => r.visTarget === r.visPressed).length
      const audCorrect = validResponses.filter(r => r.audTarget === r.audPressed).length
      const visTargets = validResponses.filter(r => r.visTarget).length
      const audTargets = validResponses.filter(r => r.audTarget).length

      const accuracy = validResponses.length > 0 ? Math.round(correct / validResponses.length * 100) : 0
      const visAccuracy = visTargets > 0 ? Math.round(visCorrect / visTargets * 100) : 0
      const audAccuracy = audTargets > 0 ? Math.round(audCorrect / audTargets * 100) : 0
      const avgRT = validResponses.length > 0
        ? Math.round(validResponses.reduce((sum, r) => sum + r.reactionTime, 0) / validResponses.length)
        : 0

      let nextN = n
      if (accuracy >= 80) nextN = Math.min(n + 1, 5)
      else if (accuracy < 60) nextN = Math.max(n - 1, 1)

      setResults({ accuracy, visAccuracy, audAccuracy, avgReactionTime: avgRT, total: validResponses.length, correct, n, nextN })
      setPhase("results")
      return
    }

    // Show stimulus
    const pos = seq.positions[index]
    const letter = LETTERS[seq.letters[index]]

    setActivePosition(pos)
    setActiveLetter(letter)
    setShowingStimulus(true)
    setTrialIndex(index)
    responseWindowStart.current = performance.now()

    // Speak letter
    if (synthRef.current) {
      const utterance = new SpeechSynthesisUtterance(letter)
      utterance.rate = 1.2
      synthRef.current.speak(utterance)
    }

    // Hide stimulus after STIMULUS_MS
    stimulusTimer.current = setTimeout(() => {
      setShowingStimulus(false)
      setActivePosition(null)
      setActiveLetter(null)

      // Wait ISI_MS then next trial
      trialTimer.current = setTimeout(() => {
        runTrial(index + 1, seq)
      }, ISI_MS - STIMULUS_MS)
    }, STIMULUS_MS)
  }, [n, responses])

  // Start game loop
  useEffect(() => {
    if (phase === "playing" && sequence && trialIndex === 0) {
      const startDelay = setTimeout(() => {
        runTrial(0, sequence)
      }, 1500)
      return () => clearTimeout(startDelay)
    }
  }, [phase, sequence, trialIndex, runTrial])

  // Key handler
  const handleKeyDown = useCallback((e) => {
    if (phase !== "playing" || trialIndex < 0 || !sequence) return
    if (submitting) return

    const key = e.key.toLowerCase()
    if (key !== "v" && key !== "a" && key !== "b") return
    e.preventDefault()

    const reactionTime = Math.round(performance.now() - responseWindowStart.current)
    const isVisMatch = sequence.visualTargets.has(trialIndex)
    const isAudMatch = sequence.audioTargets.has(trialIndex)
    const visPressed = key === "v" || key === "b"
    const audPressed = key === "a" || key === "b"
    const visCorrect = visPressed === isVisMatch
    const audCorrect = audPressed === isAudMatch

    const response = {
      trial: trialIndex,
      position: sequence.positions[trialIndex],
      letter: LETTERS[sequence.letters[trialIndex]],
      visTarget: isVisMatch,
      audTarget: isAudMatch,
      visPressed,
      audPressed,
      visCorrect,
      audCorrect,
      correct: visCorrect && audCorrect,
      key,
      reactionTime,
    }

    setResponses(prev => [...prev, response])
  }, [phase, trialIndex, sequence, submitting])

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [handleKeyDown])

  // Submit to backend
  const handleSubmitResults = useCallback(async () => {
    if (submitting || !results) return
    setSubmitting(true)
    try {
      const session = await api.cognitive.createSession({
        skill_type: "dual_n_back",
        n_level: results.n,
      })

      const trials = responses.map(r => ({
        estimulo: `V:${r.position} A:${r.letter}`,
        respuesta_esperada: r.visTarget || r.audTarget ? "Match" : "NoMatch",
        respuesta_usuario: r.key.toUpperCase(),
        es_correcto: r.correct,
        tiempo_reaccion_ms: r.reactionTime,
      }))

      await api.cognitive.uploadTrials(session.id, trials)
      await api.cognitive.finalizeSession(session.id)
      await consolidateDualNBack(session.id)
      setConsolidated(true)
      setError(null)
    } catch (e) {
      console.warn("[DualNBack] Error submitting to backend:", e.message)
    } finally {
      setSubmitting(false)
    }
  }, [consolidateDualNBack])

  const handleContinue = useCallback(() => {
    setN(results.nextN)
    setPhase("setup")
    setResults(null)
    setResponses([])
    setMessage("")
  }, [results])

  const handleBack = useCallback(() => {
    if (trialTimer.current) clearTimeout(trialTimer.current)
    if (stimulusTimer.current) clearTimeout(stimulusTimer.current)
    synthRef.current?.cancel()
    onClose?.()
  }, [onClose])

  // Grid cells
  const gridCells = Array.from({ length: TOTAL_POSITIONS }, (_, i) => i)
  const attemptedCount = responses.filter(r => r.trial >= n).length
  const correctCount = responses.filter(r => r.trial >= n && r.correct).length
  const visTargetCount = sequence ? [...sequence.visualTargets].filter(i => i >= n && i <= trialIndex).length : 0
  const audTargetCount = sequence ? [...sequence.audioTargets].filter(i => i >= n && i <= trialIndex).length : 0
  const visHitCount = responses.filter(r => r.trial >= n && r.visTarget && r.visPressed).length
  const audHitCount = responses.filter(r => r.trial >= n && r.audTarget && r.audPressed).length

  return (
    <GameShell
      title="Dual N-Back"
      subtitle="Memoria de trabajo — Jaeggi et al. 2008"
      icon="🧠"
      accentColor="green"
      onBack={handleBack}
      error={error}
      onClearError={() => setError(null)}
    >
      <main className="max-w-[600px] mx-auto px-6 py-12">
        {/* Message */}
        {message && (
          <div className="mb-6 text-center">
            <p className="text-sm text-green-400/80 font-mono">{message}</p>
          </div>
        )}

        {/* SETUP PHASE */}
        {phase === "setup" && (
          <div className="space-y-8">
            <div className="card p-8 text-center">
              <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center text-2xl mx-auto mb-6">
                🧠
              </div>
              <h2 className="text-2xl font-black text-white mb-2">Dual N-Back</h2>
              <p className="text-sm text-neutral-400 mb-8 max-w-md mx-auto leading-relaxed">
                Entrenamiento científico de memoria de trabajo. Recordá la <strong className="text-white">posición visual</strong>
                {" "}y la <strong className="text-white">letra</strong> de hace N trials atrás.
                Presioná <kbd className="text-green-400 bg-green-500/10 px-2 py-0.5 rounded font-mono">V</kbd> si la posición coincide,
                {" "}<kbd className="text-green-400 bg-green-500/10 px-2 py-0.5 rounded font-mono">A</kbd> si la letra coincide,
                {" "}<kbd className="text-green-400 bg-green-500/10 px-2 py-0.5 rounded font-mono">B</kbd> si ambas.
              </p>

              <div className="flex items-center justify-center gap-4 mb-8">
                <span className="text-sm text-neutral-400 uppercase tracking-wider">Nivel N</span>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map(level => (
                    <button
                      key={level}
                      onClick={() => setN(level)}
                      className={`w-12 h-12 rounded-xl font-bold text-lg transition-all duration-200 ${
                        n === level
                          ? "bg-green-500 text-black shadow-lg shadow-green-500/30 scale-110"
                          : "bg-neutral-800 text-neutral-400 hover:bg-neutral-700 hover:text-white"
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              <button onClick={handleStart} className="btn btn-primary px-10 py-4 text-lg">
                Iniciar Entrenamiento
              </button>
            </div>
          </div>
        )}

        {/* PLAYING PHASE */}
        {phase === "playing" && (
          <div className="space-y-8">
            <div className="flex items-center justify-center gap-8 text-center">
              <div>
                <span className="text-3xl font-black text-white">N-{n}</span>
                <p className="text-[10px] text-neutral-500 uppercase tracking-wider mt-1">Nivel</p>
              </div>
              <div className="w-px h-10 bg-white/[0.08]" />
              <div>
                <span className="text-3xl font-black text-white">{trialIndex + 1}/{TRIALS_PER_BLOCK + n}</span>
                <p className="text-[10px] text-neutral-500 uppercase tracking-wider mt-1">Trial</p>
              </div>
              <div className="w-px h-10 bg-white/[0.08]" />
              <div>
                <span className="text-3xl font-black text-green-400">{attemptedCount > 0 ? Math.round(correctCount / attemptedCount * 100) : "—"}%</span>
                <p className="text-[10px] text-neutral-500 uppercase tracking-wider mt-1">Precisión</p>
              </div>
            </div>

            {/* 3x3 Grid */}
            <div className="flex justify-center">
              <div className="grid grid-cols-3 gap-3 w-[360px] h-[360px]">
                {gridCells.map(i => (
                  <div
                    key={i}
                    className={`rounded-2xl border-2 transition-all duration-150 flex items-center justify-center text-2xl font-black ${
                      showingStimulus && activePosition === i
                        ? "bg-green-500 border-green-400 shadow-[0_0_30px_rgba(34,197,94,0.5)] scale-105 text-black"
                        : "bg-neutral-900/50 border-white/[0.06] text-neutral-800"
                    }`}
                  >
                    {showingStimulus && activePosition === i ? "●" : ""}
                  </div>
                ))}
              </div>
            </div>

            {/* Current letter */}
            <div className="text-center">
              <span className={`text-8xl font-black transition-all duration-150 ${
                showingStimulus ? "text-white scale-100 opacity-100" : "text-neutral-800 scale-75 opacity-0"
              }`}>
                {showingStimulus ? activeLetter : "—"}
              </span>
            </div>

            {/* Key legend */}
            <div className="flex justify-center gap-4 text-xs text-neutral-500">
              <span><kbd className="text-green-400 bg-green-500/10 px-2 py-0.5 rounded font-mono">V</kbd> Visual match</span>
              <span><kbd className="text-green-400 bg-green-500/10 px-2 py-0.5 rounded font-mono">A</kbd> Audio match</span>
              <span><kbd className="text-green-400 bg-green-500/10 px-2 py-0.5 rounded font-mono">B</kbd> Ambos</span>
              <span className="text-neutral-600">(nada = ningún match)</span>
            </div>

            {/* Real-time hit counters */}
            <div className="grid grid-cols-2 gap-4">
              <div className="card p-4 text-center">
                <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">🎯 Visual</p>
                <p className="text-lg font-bold text-white">{visHitCount}/{visTargetCount} hits</p>
              </div>
              <div className="card p-4 text-center">
                <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">🔊 Auditivo</p>
                <p className="text-lg font-bold text-white">{audHitCount}/{audTargetCount} hits</p>
              </div>
            </div>
          </div>
        )}

        {/* FEEDBACK TRANSITION */}
        {phase === "feedback" && (
          <div className="card p-12 text-center">
            <div className="w-12 h-12 rounded-full border-2 border-green-500/30 border-t-green-500 animate-spin mx-auto mb-4" />
            <p className="text-sm text-neutral-400">Calculando resultados...</p>
          </div>
        )}

        {/* RESULTS PHASE */}
        {phase === "results" && results && (
          <div className="space-y-6">
            <div className="card p-8 text-center">
              <div className={`text-7xl font-black mb-2 ${results.nextN > results.n ? "text-green-400" : results.nextN < results.n ? "text-orange-400" : "text-white"}`}>
                N-{results.nextN}
              </div>
              <p className="text-sm text-neutral-500">
                {results.nextN > results.n
                  ? "↑ Subiste de nivel!"
                  : results.nextN < results.n
                    ? "↓ Bajaste de nivel — seguí practicando"
                    : "— Mantuviste el nivel"}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="card p-5 text-center">
                <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Precisión Global</p>
                <p className={`text-3xl font-black ${results.accuracy >= 80 ? "text-green-400" : results.accuracy >= 70 ? "text-yellow-400" : "text-red-400"}`}>
                  {results.accuracy}%
                </p>
              </div>
              <div className="card p-5 text-center">
                <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Tiempo de Reacción</p>
                <p className="text-3xl font-black text-white">{results.avgReactionTime} <span className="text-sm text-neutral-500 font-normal">ms</span></p>
              </div>
              <div className="card p-5 text-center">
                <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Visual</p>
                <p className={`text-3xl font-black ${results.visAccuracy >= 80 ? "text-green-400" : "text-yellow-400"}`}>
                  {results.visAccuracy}%
                </p>
              </div>
              <div className="card p-5 text-center">
                <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Auditivo</p>
                <p className={`text-3xl font-black ${results.audAccuracy >= 80 ? "text-green-400" : "text-yellow-400"}`}>
                  {results.audAccuracy}%
                </p>
              </div>
            </div>

            <div className="card p-5">
              <p className="text-xs text-neutral-500 uppercase tracking-wider mb-4">Detalle</p>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-neutral-400">Trials válidos</span>
                  <span className="text-white font-mono">{results.total}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-400">Correctos</span>
                  <span className="text-green-400 font-mono">{results.correct}/{results.total}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-400">N inicial</span>
                  <span className="text-white font-mono">N-{results.n}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-neutral-400">N siguiente</span>
                  <span className="text-green-400 font-mono">N-{results.nextN}</span>
                </div>
              </div>
            </div>

            {consolidated && (
              <div className="flex justify-center">
                <span className="text-xs text-green-500/70 bg-green-500/[0.06] border border-green-500/20 px-4 py-2 rounded-full flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                  Sesión registrada en el panel
                </span>
              </div>
            )}

            <div className="flex gap-4 justify-center">
              <button onClick={handleContinue} className="btn btn-primary px-8">
                Continuar en N-{results.nextN}
              </button>
              <button onClick={handleBack} className="btn btn-secondary px-6">
                Volver al inicio
              </button>
            </div>
          </div>
        )}
      </main>
    </GameShell>
  )
}

export default DualNBackGame