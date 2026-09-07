import { useEffect, useCallback, useState } from "react"
import { useBlocker } from "react-router"

/**
 * Blocks navigation during active game phases.
 * Combines react-router's useBlocker with beforeunload for refresh protection.
 *
 * @param {boolean} shouldBlock - Whether navigation should be blocked
 * @returns {{ showPrompt: boolean, confirmNavigation: () => void, cancelNavigation: () => void }}
 */
export function useGameBlocker(shouldBlock) {
  const [showPrompt, setShowPrompt] = useState(false)
  const [pendingNavigation, setPendingNavigation] = useState(null)

  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      shouldBlock && currentLocation.pathname !== nextLocation.pathname
  )

  // When blocker blocks a navigation, show our custom prompt
  useEffect(() => {
    if (blocker.state === "blocked") {
      setShowPrompt(true)
      setPendingNavigation(blocker)
    }
  }, [blocker.state])

  // beforeunload handler for browser refresh / tab close
  useEffect(() => {
    if (!shouldBlock) return

    const handler = (e) => {
      e.preventDefault()
      e.returnValue = ""
    }

    window.addEventListener("beforeunload", handler)
    return () => window.removeEventListener("beforeunload", handler)
  }, [shouldBlock])

  const confirmNavigation = useCallback(() => {
    if (pendingNavigation) {
      pendingNavigation.proceed()
    }
    setShowPrompt(false)
    setPendingNavigation(null)
  }, [pendingNavigation])

  const cancelNavigation = useCallback(() => {
    if (pendingNavigation) {
      pendingNavigation.reset()
    }
    setShowPrompt(false)
    setPendingNavigation(null)
  }, [pendingNavigation])

  return { showPrompt, confirmNavigation, cancelNavigation }
}

/**
 * Exit confirmation dialog component.
 * Renders a modal when navigation is blocked.
 */
export function ExitGamePrompt({ show, onConfirm, onCancel }) {
  if (!show) return null

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={onCancel}>
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="exit-dialog-title"
        className="relative bg-neutral-900/95 border border-white/[0.08] rounded-2xl p-6 max-w-sm w-full shadow-2xl"
        onClick={(e) => e.stopPropagation()}
        style={{ animation: 'fadeInUp 0.3s cubic-bezier(0.4, 0, 0.2, 1)' }}
      >
        <h3 id="exit-dialog-title" className="text-lg font-bold text-white mb-2 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-orange-500" />
          ¿Salir del juego?
        </h3>
        <p className="text-sm text-neutral-400 mb-6">
          Si salís ahora, perderás el progreso de esta sesión.
        </p>
        <div className="flex items-center justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-xl text-xs font-bold text-neutral-300 bg-white/[0.04] border border-white/[0.08] hover:bg-white/[0.08] transition-all"
          >
            Quedarme
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-red-500/20 border border-red-500/30 hover:bg-red-500/30 transition-all"
          >
            Salir
          </button>
        </div>
      </div>
    </div>
  )
}
