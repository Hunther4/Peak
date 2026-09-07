import { useState, useEffect, useCallback, useRef } from "react"

/**
 * Tracks session elapsed seconds with pause/resume/reset controls.
 * Auto-starts on mount, auto-cleans on unmount.
 *
 * @returns {object} Timer state and controls
 *   - elapsedSeconds: number of seconds since last reset (count-up)
 *   - isRunning: true while the timer is actively counting
 *   - pause: () => void — stop counting (keeps elapsedSeconds)
 *   - resume: () => void — resume counting from current elapsedSeconds
 *   - reset: () => void — zero the counter and resume counting
 *   - formatTime: () => string — "MM:SS" representation of elapsedSeconds
 */
export function useSessionTimer() {
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [isRunning, setIsRunning] = useState(true)
  const intervalRef = useRef(null)

  useEffect(() => {
    if (!isRunning) return
    intervalRef.current = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1)
    }, 1000)
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [isRunning])

  const pause = useCallback(() => setIsRunning(false), [])
  const resume = useCallback(() => setIsRunning(true), [])
  const reset = useCallback(() => {
    setElapsedSeconds(0)
    setIsRunning(true)
  }, [])

  const formatTime = useCallback(() => {
    const m = Math.floor(elapsedSeconds / 60)
    const s = elapsedSeconds % 60
    return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`
  }, [elapsedSeconds])

  return { elapsedSeconds, isRunning, pause, resume, reset, formatTime }
}
