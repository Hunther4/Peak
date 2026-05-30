import { useState, useCallback } from "react"

/**
 * Wraps loading/error state for API calls.
 * Eliminates repetitive useState pairs across components.
 *
 * @returns {object} Loading state, error state, and control actions
 */
export function useApiState() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const clearError = useCallback(() => setError(null), [])

  const withLoading = useCallback(async (asyncFn) => {
    setLoading(true)
    setError(null)
    try {
      const result = await asyncFn()
      return result
    } catch (e) {
      setError(e.message || "Error desconocido")
      throw e
    } finally {
      setLoading(false)
    }
  }, [])

  return { loading, error, setLoading, setError, clearError, withLoading }
}
