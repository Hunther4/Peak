import { useEffect, useCallback, Suspense, lazy, useRef, useState } from "react"
import { useParams, useSearchParams, useNavigate } from "react-router"
import { useStore } from "../store/store"
import { useGameBlocker, ExitGamePrompt } from "../hooks/useGameBlocker.jsx"
import Spinner from "../components/ui/Spinner"

// Lazy-load game components — each becomes its own chunk
const MemoryGame = lazy(() => import("../components/MemoryGame"))
const MathThinkingGame = lazy(() => import("../components/MathThinkingGame"))
const DualNBackGame = lazy(() => import("../components/DualNBackGame"))
const IQPracticeGame = lazy(() => import("../components/IQPracticeGame"))

// Game route map — adding a new game = 1 line here + 1 component file
const GAME_COMPONENTS = {
  memory_number: { load: () => MemoryGame, needsSkillId: true },
  problem_set: { load: () => MathThinkingGame, needsSkillId: true },
  dual_n_back: { load: () => DualNBackGame, needsSkillId: false },
  iq_practice: { load: () => IQPracticeGame, needsSkillId: true },
}

function GameLoading() {
  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center">
      <div className="text-center">
        <Spinner size="lg" className="mx-auto mb-3" />
        <p className="text-xs text-neutral-500 uppercase tracking-wider">Cargando juego...</p>
      </div>
    </div>
  )
}

export default function Practice() {
  const { gameType } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { fetchSummary, fetchTimeline } = useStore()
  const gameAreaRef = useRef(null)
  const [hasInteracted, setHasInteracted] = useState(false)

  const skillId = searchParams.get("skillId")

  const route = GAME_COMPONENTS[gameType]

  // Invalid game type → redirect to dashboard
  useEffect(() => {
    if (!route) {
      navigate("/", { replace: true })
    }
  }, [route, navigate])

  // Track first interaction inside the game area (click/touch/keypress)
  useEffect(() => {
    if (hasInteracted) return
    const handler = (e) => {
      // Only activate after user interacts inside the game area
      if (gameAreaRef.current?.contains(e.target)) {
        setHasInteracted(true)
      }
    }
    document.addEventListener("click", handler, { capture: true })
    document.addEventListener("keydown", handler, { capture: true })
    return () => {
      document.removeEventListener("click", handler, { capture: true })
      document.removeEventListener("keydown", handler, { capture: true })
    }
  }, [hasInteracted])

  // Block navigation only after user has started interacting with the game
  const { showPrompt, confirmNavigation, cancelNavigation } = useGameBlocker(hasInteracted)

  const handleClose = useCallback(() => {
    fetchSummary()
    fetchTimeline()
    navigate("/")
  }, [fetchSummary, fetchTimeline, navigate])

  if (!route) return null

  const { needsSkillId } = route

  // If game needs skillId but none provided → redirect to dashboard
  if (needsSkillId && !skillId) {
    navigate("/", { replace: true })
    return null
  }

  const GameComponent = route.load()

  return (
    <div ref={gameAreaRef}>
      <Suspense fallback={<GameLoading />}>
        <GameComponent
          skillId={needsSkillId ? parseInt(skillId, 10) : null}
          onClose={handleClose}
        />
      </Suspense>

      {/* Exit confirmation — only shown when navigation is blocked */}
      <ExitGamePrompt
        show={showPrompt}
        onConfirm={confirmNavigation}
        onCancel={cancelNavigation}
      />
    </div>
  )
}
