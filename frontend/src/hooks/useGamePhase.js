import { useState, useCallback } from "react"

/**
 * Shared game phase machine.
 * Manages phase transitions for any game that follows:
 * idle → active → feedback → done
 *
 * @param {string} initialPhase - Starting phase (default: 'idle')
 * @returns {object} Phase state and transition actions
 */
export function useGamePhase(initialPhase = "idle") {
  const [phase, setPhase] = useState(initialPhase)
  const [error, setError] = useState(null)

  const goToIdle = useCallback(() => {
    setPhase("idle")
    setError(null)
  }, [])

  const goToActive = useCallback(() => {
    setError(null)
    // Each game sets its own active phase name via setPhase
  }, [])

  const goToFeedback = useCallback(() => {
    setPhase("feedback")
    setError(null)
  }, [])

  const goToDone = useCallback(() => {
    setPhase("done")
    setError(null)
  }, [])

  const clearError = useCallback(() => setError(null), [])

  return {
    phase,
    setPhase,
    error,
    setError,
    clearError,
    goToIdle,
    goToActive,
    goToFeedback,
    goToDone,
  }
}
