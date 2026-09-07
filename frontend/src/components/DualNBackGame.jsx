import { useState, useEffect, useRef, useCallback } from "react"
import { useStore } from "../store/store"
import { useSessionTimer } from "../hooks"
import { GameShell } from "./layout/GameShell"
import api from "../api/client"

const GRID_SIZE = 3
const TOTAL_POSITIONS = GRID_SIZE * GRID_SIZE
const LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H"]
const STIMULUS_MS = 800
const ISI_MS = 2200
const TRIALS_PER_BLOCK = 20
const TOTAL_BLOCKS = 3

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
  const [isPreview, setIsPreview] = useState(false)
  const [lastKeyPress, setLastKeyPress] = useState(null)
  const [trialVisPressed, setTrialVisPressed] = useState(false)
  const [trialAudPressed, setTrialAudPressed] = useState(false)
  const [currentBlock, setCurrentBlock] = useState(1)
  const [blockStats, setBlockStats] = useState([])

  const sessionTimer = useSessionTimer()

  const trialTimer = useRef(null)
  const stimulusTimer = useRef(null)
  const synthRef = useRef(null)
  const responseWindowStart = useRef(0)
  const responsesRef = useRef([])
  const runTrialRef = useRef(null)
  const isMountedRef = useRef(true)
  const currentBlockRef = useRef(1)
  const blockStatsRef = useRef([])
  const trialVisPressedRef = useRef(false)
  const trialAudPressedRef = useRef(false)
  const trialRtRef = useRef(null)
  const trialIndexRef = useRef(-1)
  const sequenceRef = useRef(null)

  // Load user's current N level from backend on mount
  useEffect(() => {
    let mounted = true
    api.cognitive.getSkills()
      .then(skills => {
        if (mounted && skills && skills.length > 0) {
          const current = skills[0]
          if (current.nivel_n_actual && current.nivel_n_actual > 1) {
            setN(current.nivel_n_actual)
          }
        }
      })
      .catch(() => {})
    return () => { mounted = false }
  }, [])

  // Cleanup
  useEffect(() => {
    isMountedRef.current = true
    synthRef.current = window.speechSynthesis
    return () => {
      isMountedRef.current = false
      if (trialTimer.current) clearTimeout(trialTimer.current)
      if (stimulusTimer.current) clearTimeout(stimulusTimer.current)
      synthRef.current?.cancel()
    }
  }, [])

  // Keep responsesRef in sync
  useEffect(() => {
    responsesRef.current = responses
  }, [responses])

  // Keep currentBlockRef and blockStatsRef in sync
  useEffect(() => {
    currentBlockRef.current = currentBlock
  }, [currentBlock])
  useEffect(() => {
    blockStatsRef.current = blockStats
  }, [blockStats])

  // Start game
  const handleStart = useCallback(() => {
    sessionTimer.reset()
    const seq = generateSequence(n, TRIALS_PER_BLOCK + n)
    seq.n = n
    sequenceRef.current = seq
    setSequence(seq)
    setTrialIndex(-1)
    trialIndexRef.current = -1
    setResponses([])
    responsesRef.current = []
    setResults(null)
    setConsolidated(false)
    setMessage("")
    setCurrentBlock(1)
    currentBlockRef.current = 1
    setBlockStats([])
    blockStatsRef.current = []
    setPhase("playing")
  }, [n, sessionTimer])

  // Run trial
  const runTrial = useCallback((index, seq) => {
    const currentN = seq.n ?? n
    trialIndexRef.current = index
    sequenceRef.current = seq

    if (index >= TRIALS_PER_BLOCK + currentN) {
      // Calculate block results
      const block = currentBlockRef.current
      const blockResponses = responsesRef.current.filter(r => r.block === block)
      const validResponses = blockResponses
      const correct = validResponses.filter(r => r.correct).length
      const visCorrect = validResponses.filter(r => r.visCorrect).length
      const audCorrect = validResponses.filter(r => r.audCorrect).length
      const visTargets = validResponses.filter(r => r.visTarget).length
      const audTargets = validResponses.filter(r => r.audTarget).length

      const accuracy = validResponses.length > 0 ? Math.round((correct / validResponses.length) * 100) : 0
      const visAccuracy = validResponses.length > 0 ? Math.round((visCorrect / validResponses.length) * 100) : 0
      const audAccuracy = validResponses.length > 0 ? Math.round((audCorrect / validResponses.length) * 100) : 0
      const activeRTs = validResponses.filter(r => r.reactionTime > 0)
      const avgRT = activeRTs.length > 0
        ? Math.round(activeRTs.reduce((sum, r) => sum + r.reactionTime, 0) / activeRTs.length)
        : 0

      const stats = { accuracy, visAccuracy, audAccuracy, avgReactionTime: avgRT, total: validResponses.length, correct, n: currentN, block }
      const newBlockStats = [...blockStatsRef.current, stats]
      setBlockStats(newBlockStats)

      // More blocks?
      if (block < TOTAL_BLOCKS) {
        setResults(stats)
        setPhase("coaching")
        return
      }

      // Final results across all completed blocks
      const allValid = responsesRef.current
      const totalCorrect = allValid.filter(r => r.correct).length
      const globalAccuracy = allValid.length > 0 ? Math.round((totalCorrect / allValid.length) * 100) : 0
      const globalVisCorrect = allValid.filter(r => r.visCorrect).length
      const globalAudCorrect = allValid.filter(r => r.audCorrect).length
      const globalVisAccuracy = allValid.length > 0 ? Math.round((globalVisCorrect / allValid.length) * 100) : 0
      const globalAudAccuracy = allValid.length > 0 ? Math.round((globalAudCorrect / allValid.length) * 100) : 0
      const allRTs = allValid.filter(r => r.reactionTime > 0)
      const globalAvgRT = allRTs.length > 0
        ? Math.round(allRTs.reduce((sum, r) => sum + r.reactionTime, 0) / allRTs.length)
        : 0

      let nextN = currentN
      if (globalAccuracy >= 80) nextN = Math.min(currentN + 1, 5)
      else if (globalAccuracy < 60) nextN = Math.max(currentN - 1, 1)

      setResults({
        accuracy: globalAccuracy,
        visAccuracy: globalVisAccuracy,
        audAccuracy: globalAudAccuracy,
        avgReactionTime: globalAvgRT,
        total: allValid.length,
        correct: totalCorrect,
        n: currentN,
        nextN,
      })
      setPhase("results")
      return
    }

    // Reset trial input tracking for this new trial
    trialVisPressedRef.current = false
    trialAudPressedRef.current = false
    trialRtRef.current = null
    setTrialVisPressed(false)
    setTrialAudPressed(false)
    setLastKeyPress(null)

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
      synthRef.current.cancel()
      const utterance = new SpeechSynthesisUtterance(letter)
      utterance.rate = 1.2
      synthRef.current.speak(utterance)
    }

    // Preview phase: first N trials show position longer (3s) so user can memorize
    const isPreviewTrial = index < currentN
    setIsPreview(isPreviewTrial)
    const stimulusDuration = isPreviewTrial ? 3000 : STIMULUS_MS
    const isiDuration = isPreviewTrial ? 1000 : ISI_MS - STIMULUS_MS

    // Hide stimulus after duration
    stimulusTimer.current = setTimeout(() => {
      if (!isMountedRef.current) return
      setShowingStimulus(false)
      setActivePosition(null)
      setActiveLetter(null)

      // Wait then evaluate trial and run next
      trialTimer.current = setTimeout(() => {
        if (!isMountedRef.current) return

        // Evaluate trial if index >= currentN
        if (index >= currentN) {
          const isVisMatch = seq.visualTargets.has(index)
          const isAudMatch = seq.audioTargets.has(index)
          const visPressed = trialVisPressedRef.current
          const audPressed = trialAudPressedRef.current
          const visCorrect = visPressed === isVisMatch
          const audCorrect = audPressed === isAudMatch
          const correct = visCorrect && audCorrect
          const rt = trialRtRef.current ?? 0

          let keyLabel = "None"
          if (visPressed && audPressed) keyLabel = "D"
          else if (visPressed) keyLabel = "A"
          else if (audPressed) keyLabel = "W"

          const evaluatedTrial = {
            block: currentBlockRef.current,
            trial: index,
            position: seq.positions[index],
            letter: LETTERS[seq.letters[index]],
            visTarget: isVisMatch,
            audTarget: isAudMatch,
            visPressed,
            audPressed,
            visCorrect,
            audCorrect,
            correct,
            key: keyLabel,
            reactionTime: rt,
          }

          responsesRef.current = [...responsesRef.current, evaluatedTrial]
          setResponses([...responsesRef.current])
        }

        runTrialRef.current(index + 1, seq)
      }, isiDuration)
    }, stimulusDuration)
  }, [n])

  // Keep runTrialRef in sync
  useEffect(() => {
    runTrialRef.current = runTrial
  }, [runTrial])

  // Start game loop
  useEffect(() => {
    if (phase === "playing" && sequence && trialIndex === -1) {
      const startDelay = setTimeout(() => {
        runTrial(0, sequence)
      }, 1500)
      return () => clearTimeout(startDelay)
    }
  }, [phase, sequence, trialIndex, runTrial])

  // Unified input handler for both keydown and button clicks
  const handleInput = useCallback((inputKey) => {
    if (phase !== "playing" || trialIndexRef.current < 0 || !sequenceRef.current) return
    if (submitting) return
    const currentN = sequenceRef.current?.n ?? n
    if (trialIndexRef.current < currentN) return // Preview phase: inputs ignored

    const key = inputKey.toLowerCase()
    if (key !== "a" && key !== "w" && key !== "l" && key !== "d" && key !== " ") return

    const rt = Math.round(performance.now() - responseWindowStart.current)
    if (trialRtRef.current === null) {
      trialRtRef.current = rt
    }

    if (key === "a") {
      trialVisPressedRef.current = true
      setTrialVisPressed(true)
      setLastKeyPress("a")
    } else if (key === "w" || key === "l") {
      trialAudPressedRef.current = true
      setTrialAudPressed(true)
      setLastKeyPress("w")
    } else if (key === "d" || key === " ") {
      trialVisPressedRef.current = true
      trialAudPressedRef.current = true
      setTrialVisPressed(true)
      setTrialAudPressed(true)
      setLastKeyPress("d")
    }

    setTimeout(() => setLastKeyPress(null), 300)
  }, [phase, submitting, n])

  // Key handler
  const handleKeyDown = useCallback((e) => {
    if (e.repeat) return
    const key = e.key.toLowerCase()
    if (key === "a" || key === "w" || key === "l" || key === "d" || key === " ") {
      e.preventDefault()
      handleInput(key)
    }
  }, [handleInput])

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [handleKeyDown])

  // Submit to backend
  const handleSubmitResults = useCallback(async () => {
    if (submitting || !results) return
    setSubmitting(true)
    const elapsed = sessionTimer.elapsedSeconds
    const timerBody = { elapsed_seconds: elapsed }
    try {
      const session = await api.cognitive.createSession(1)

      const trials = responsesRef.current.map(r => ({
        estimulo: `V:${r.position} A:${r.letter}`,
        respuesta_esperada: (r.visTarget && r.audTarget) ? "Ambos" : r.visTarget ? "Visual" : r.audTarget ? "Audio" : "Ninguno",
        respuesta_usuario: (r.visPressed && r.audPressed) ? "Ambos" : r.visPressed ? "Visual" : r.audPressed ? "Audio" : "Ninguno",
        es_correcto: r.correct,
        tiempo_reaccion_ms: r.reactionTime || 0,
      }))

      if (trials.length === 0) {
        setError("No se registraron trials — jugá al menos 1 ronda")
        setSubmitting(false)
        return
      }

      await api.cognitive.uploadTrials(session.id, trials)
      await api.cognitive.finalizeSession(session.id, timerBody)
      await consolidateDualNBack(session.id)
      setConsolidated(true)
      setError(null)
    } catch (e) {
      setError(`Error guardando sesión: ${e.message}`)
    } finally {
      setSubmitting(false)
    }
  }, [consolidateDualNBack, results, sessionTimer, submitting])

  // Auto-submit results to backend when entering results phase
  useEffect(() => {
    if (phase === "results" && results && !consolidated && !submitting) {
      handleSubmitResults() // eslint-disable-line react-hooks/set-state-in-effect
    }
  }, [phase, results, consolidated, submitting, handleSubmitResults])

  const handleContinue = useCallback(() => {
    setN(results.nextN)
    setPhase("setup")
    setResults(null)
    setResponses([])
    responsesRef.current = []
    setMessage("")
  }, [results])

  const handleNextBlock = useCallback(() => {
    const nextBlock = currentBlock + 1
    setCurrentBlock(nextBlock)
    currentBlockRef.current = nextBlock
    setResults(null)
    // Generate new sequence for next block
    const seq = generateSequence(n, TRIALS_PER_BLOCK + n)
    seq.n = n
    sequenceRef.current = seq
    setSequence(seq)
    setTrialIndex(-1)
    trialIndexRef.current = -1
    setMessage("")
    setPhase("playing")
  }, [currentBlock, n])

  const handleFinishEarly = useCallback(() => {
    const allValid = responsesRef.current
    if (allValid.length === 0) {
      setPhase("setup")
      return
    }
    const currentN = sequenceRef.current?.n ?? n
    const totalCorrect = allValid.filter(r => r.correct).length
    const globalAccuracy = Math.round((totalCorrect / allValid.length) * 100)
    const globalVisCorrect = allValid.filter(r => r.visCorrect).length
    const globalAudCorrect = allValid.filter(r => r.audCorrect).length
    const globalVisAccuracy = Math.round((globalVisCorrect / allValid.length) * 100)
    const globalAudAccuracy = Math.round((globalAudCorrect / allValid.length) * 100)
    const allRTs = allValid.filter(r => r.reactionTime > 0)
    const globalAvgRT = allRTs.length > 0
      ? Math.round(allRTs.reduce((sum, r) => sum + r.reactionTime, 0) / allRTs.length)
      : 0

    let nextN = currentN
    if (globalAccuracy >= 80) nextN = Math.min(currentN + 1, 5)
    else if (globalAccuracy < 60) nextN = Math.max(currentN - 1, 1)

    setResults({
      accuracy: globalAccuracy,
      visAccuracy: globalVisAccuracy,
      audAccuracy: globalAudAccuracy,
      avgReactionTime: globalAvgRT,
      total: allValid.length,
      correct: totalCorrect,
      n: currentN,
      nextN,
    })
    setPhase("results")
  }, [n])

  const handleBack = useCallback(() => {
    if (trialTimer.current) clearTimeout(trialTimer.current)
    if (stimulusTimer.current) clearTimeout(stimulusTimer.current)
    synthRef.current?.cancel()
    onClose?.()
  }, [onClose])

  // Grid cells
  const gridCells = Array.from({ length: TOTAL_POSITIONS }, (_, i) => i)
  const currentBlockResponses = responses.filter(r => r.block === currentBlock)
  const attemptedCount = currentBlockResponses.length
  const correctCount = currentBlockResponses.filter(r => r.correct).length
  const visTargetCount = sequence ? [...sequence.visualTargets].filter(i => i >= n && i <= trialIndex).length : 0
  const audTargetCount = sequence ? [...sequence.audioTargets].filter(i => i >= n && i <= trialIndex).length : 0
  const visHitCount = currentBlockResponses.filter(r => r.visTarget && r.visPressed).length
  const audHitCount = currentBlockResponses.filter(r => r.audTarget && r.audPressed).length

  return (
    <GameShell
      title="Dual N-Back"
      subtitle="Memoria de trabajo — Jaeggi et al. 2008"
      icon="🧠"
      accentColor="green"
      sessionTimer={phase !== "setup" ? sessionTimer.formatTime() : null}
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
          <div className="space-y-6">
            <div className="card p-8 text-center">
              <div className="w-16 h-16 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center text-2xl mx-auto mb-6">
                🧠
              </div>
              <h2 className="text-2xl font-black text-white mb-2">Dual N-Back</h2>
              <p className="text-sm text-neutral-400 mb-6 max-w-md mx-auto leading-relaxed">
                Entrenamiento de memoria de trabajo. Mirá la grilla — una celda se ilumina y suena una letra.
                Recordá si la <strong className="text-white">posición</strong> o la <strong className="text-white">letra</strong> son iguales a las de hace N intentos atrás.
              </p>

              {/* Ejemplo visual paso a paso */}
              <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-5 mb-6 max-w-lg mx-auto text-left">
                <p className="text-xs text-green-400 font-semibold uppercase tracking-wider mb-3">Cómo funciona — Ejemplo N=1</p>
                <div className="space-y-3 text-sm text-neutral-300">
                  <div className="flex items-start gap-3">
                    <span className="text-green-400 font-mono font-bold text-xs mt-0.5">T1</span>
                    <span>Se ilumina la celda <strong className="text-white">arriba-izquierda</strong> y suena la letra <strong className="text-white">"R"</strong></span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-green-400 font-mono font-bold text-xs mt-0.5">T2</span>
                    <span>Se ilumina la celda <strong className="text-white">centro</strong> y suena la letra <strong className="text-white">"K"</strong></span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-yellow-400 font-mono font-bold text-xs mt-0.5">T2</span>
                    <span>Ahora preguntás: ¿La posición o letra de T2 es igual a T1? → No. No presionás nada.</span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-green-400 font-mono font-bold text-xs mt-0.5">T3</span>
                    <span>Se ilumina <strong className="text-white">arriba-izquierda</strong> otra vez y suena <strong className="text-white">"R"</strong></span>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-yellow-400 font-mono font-bold text-xs mt-0.5">T3</span>
                    <span>¿T3 = T2? → No. ¿T3 = T1? → <strong className="text-green-400">¡Sí! Misma posición Y misma letra.</strong> → Presionás <kbd className="text-green-400 bg-green-500/10 px-1.5 py-0.5 rounded font-mono font-bold">D</kbd></span>
                  </div>
                </div>
                <p className="text-xs text-neutral-500 mt-3 italic">Con N=2, comparás con hace 2 intentos. Con N=3, con hace 3. Eso es lo que hace difícil.</p>
              </div>

              <div className="flex items-center justify-center gap-6 mb-8 text-sm">
                <div className="flex items-center gap-2">
                  <kbd className="text-green-400 bg-green-500/10 px-3 py-1 rounded font-mono font-bold">A</kbd>
                  <span className="text-neutral-400">Posición igual</span>
                </div>
                <div className="flex items-center gap-2">
                  <kbd className="text-green-400 bg-green-500/10 px-3 py-1 rounded font-mono font-bold">W</kbd>
                  <span className="text-neutral-400">Letra igual</span>
                </div>
                <div className="flex items-center gap-2">
                  <kbd className="text-green-400 bg-green-500/10 px-3 py-1 rounded font-mono font-bold">D</kbd>
                  <span className="text-neutral-400">Posición + Letra</span>
                </div>
              </div>

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
                <span className="text-3xl font-black text-green-400">{currentBlock}/{TOTAL_BLOCKS}</span>
                <p className="text-[10px] text-neutral-500 uppercase tracking-wider mt-1">Bloque</p>
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

            {/* Preview indicator */}
            {isPreview && (
              <div className="text-center">
                <span className="text-sm text-yellow-400 font-semibold bg-yellow-500/10 px-4 py-2 rounded-full">
                  👀 Memorizá esta posición — el juego empieza después
                </span>
              </div>
            )}

            {/* 3x3 Grid */}
            <div className="flex justify-center">
              <div className="grid grid-cols-3 gap-3 w-[360px] h-[360px]">
                {gridCells.map(i => (
                  <div
                    key={i}
                    className={`rounded-2xl border-2 transition-all duration-100 flex items-center justify-center text-4xl font-black ${
                      showingStimulus && activePosition === i
                        ? "bg-green-500 border-green-400 shadow-[0_0_40px_rgba(34,197,94,0.6)] scale-110 text-black"
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
              <span className={`text-9xl font-black transition-all duration-100 ${
                showingStimulus ? "text-white scale-100 opacity-100" : "text-neutral-800 scale-75 opacity-0"
              }`}>
                {showingStimulus ? activeLetter : "—"}
              </span>
            </div>

            {/* Interactive Input Buttons (Keyboard & Touch) */}
            <div className="grid grid-cols-3 gap-3 max-w-md mx-auto">
              <button
                type="button"
                onClick={() => handleInput("a")}
                disabled={phase !== "playing" || isPreview}
                className={`p-4 rounded-xl border flex flex-col items-center justify-center transition-all duration-150 cursor-pointer select-none active:scale-95 ${
                  lastKeyPress === "a" || trialVisPressed
                    ? "bg-green-500 text-black border-green-400 shadow-lg shadow-green-500/30 scale-105"
                    : "bg-neutral-900/80 hover:bg-neutral-800/80 border-white/[0.08] text-white"
                }`}
              >
                <kbd className={`px-2 py-0.5 rounded text-xs font-mono font-bold mb-1.5 transition-colors ${
                  lastKeyPress === "a" || trialVisPressed
                    ? "bg-black/20 text-black"
                    : "bg-green-500/10 text-green-400"
                }`}>A</kbd>
                <span className="font-bold text-xs sm:text-sm">🎯 Posición</span>
              </button>

              <button
                type="button"
                onClick={() => handleInput("w")}
                disabled={phase !== "playing" || isPreview}
                className={`p-4 rounded-xl border flex flex-col items-center justify-center transition-all duration-150 cursor-pointer select-none active:scale-95 ${
                  lastKeyPress === "w" || trialAudPressed
                    ? "bg-green-500 text-black border-green-400 shadow-lg shadow-green-500/30 scale-105"
                    : "bg-neutral-900/80 hover:bg-neutral-800/80 border-white/[0.08] text-white"
                }`}
              >
                <kbd className={`px-2 py-0.5 rounded text-xs font-mono font-bold mb-1.5 transition-colors ${
                  lastKeyPress === "w" || trialAudPressed
                    ? "bg-black/20 text-black"
                    : "bg-green-500/10 text-green-400"
                }`}>W / L</kbd>
                <span className="font-bold text-xs sm:text-sm">🔊 Letra</span>
              </button>

              <button
                type="button"
                onClick={() => handleInput("d")}
                disabled={phase !== "playing" || isPreview}
                className={`p-4 rounded-xl border flex flex-col items-center justify-center transition-all duration-150 cursor-pointer select-none active:scale-95 ${
                  lastKeyPress === "d" || (trialVisPressed && trialAudPressed)
                    ? "bg-green-500 text-black border-green-400 shadow-lg shadow-green-500/30 scale-105"
                    : "bg-neutral-900/80 hover:bg-neutral-800/80 border-white/[0.08] text-white"
                }`}
              >
                <kbd className={`px-2 py-0.5 rounded text-xs font-mono font-bold mb-1.5 transition-colors ${
                  lastKeyPress === "d" || (trialVisPressed && trialAudPressed)
                    ? "bg-black/20 text-black"
                    : "bg-green-500/10 text-green-400"
                }`}>D / Espacio</kbd>
                <span className="font-bold text-xs sm:text-sm">⚡ Ambos</span>
              </button>
            </div>

            {/* Trial log — trials in this block */}
            {currentBlockResponses.length > 0 && (
              <div className="card p-4">
                <p className="text-[10px] text-neutral-500 uppercase tracking-wider mb-3 text-center">
                  Últimos {Math.min(currentBlockResponses.length, 10)} trials del bloque {currentBlock}
                </p>
                <div className="flex justify-center gap-1.5 flex-wrap">
                  {currentBlockResponses.slice(-10).map((r) => (
                    <div
                      key={r.trial}
                      className={`flex flex-col items-center gap-0.5 px-2.5 py-1.5 rounded-lg text-[10px] border ${
                        r.correct
                          ? "bg-green-500/[0.06] border-green-500/20"
                          : "bg-red-500/[0.06] border-red-500/20"
                      }`}
                    >
                      <span className="text-neutral-500 font-mono">T{r.trial}</span>
                      <span className={`font-bold ${r.correct ? "text-green-400" : "text-red-400"}`}>
                        {r.correct ? "✓" : "✗"} {r.key !== "None" ? r.key : "—"}
                      </span>
                      <span className="text-neutral-600">
                        {r.visTarget ? "V" : "·"}{r.audTarget ? "A" : "·"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

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

        {/* COACHING PHASE — between blocks */}
        {phase === "coaching" && results && (
          <div className="space-y-6" style={{ animation: "fadeInUp 0.4s ease-out both" }}>
            <div className="card p-8 text-center">
              <div className="text-6xl font-black text-green-400 mb-2">
                Bloque {currentBlock} completado
              </div>
              <p className="text-sm text-neutral-500">
                {currentBlock < TOTAL_BLOCKS ? `Quedan ${TOTAL_BLOCKS - currentBlock} bloques` : "¡Último bloque!"}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="card p-5 text-center">
                <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Precisión</p>
                <p className={`text-3xl font-black ${results.accuracy >= 80 ? "text-green-400" : results.accuracy >= 70 ? "text-yellow-400" : "text-red-400"}`}>
                  {results.accuracy}%
                </p>
              </div>
              <div className="card p-5 text-center">
                <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Tiempo de Reacción</p>
                <p className="text-3xl font-black text-white">{results.avgReactionTime} <span className="text-sm text-neutral-500 font-normal">ms</span></p>
              </div>
              <div className="card p-5 text-center">
                <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">🎯 Visual</p>
                <p className={`text-3xl font-black ${results.visAccuracy >= 80 ? "text-green-400" : "text-yellow-400"}`}>
                  {results.visAccuracy}%
                </p>
              </div>
              <div className="card p-5 text-center">
                <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">🔊 Auditivo</p>
                <p className={`text-3xl font-black ${results.audAccuracy >= 80 ? "text-green-400" : "text-yellow-400"}`}>
                  {results.audAccuracy}%
                </p>
              </div>
            </div>

            {/* Comparison with previous block */}
            {blockStats.length > 0 && (
              <div className="card p-5">
                <p className="text-xs text-neutral-500 uppercase tracking-wider mb-3">Comparación con bloque anterior</p>
                {(() => {
                  const prev = blockStats[blockStats.length - 1]
                  const diff = results.accuracy - prev.accuracy
                  return (
                    <div className="flex items-center gap-3">
                      <span className={`text-lg font-bold ${diff > 0 ? "text-green-400" : diff < 0 ? "text-red-400" : "text-neutral-400"}`}>
                        {diff > 0 ? `↑ +${diff}%` : diff < 0 ? `↓ ${diff}%` : "— sin cambio"}
                      </span>
                      <span className="text-sm text-neutral-500">
                        ({prev.accuracy}% → {results.accuracy}%)
                      </span>
                    </div>
                  )
                })()}
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button onClick={handleNextBlock} className="btn btn-primary px-8 py-3 text-base">
                Siguiente bloque →
              </button>
              <button onClick={handleFinishEarly} className="btn btn-secondary px-6 py-3 text-base">
                Finalizar sesión ahora
              </button>
            </div>
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