import { useEffect } from "react"

/**
 * Registers keyboard shortcuts for a game and cleans up on unmount.
 *
 * @param {object} handlers - Map of key → callback (e.g., { a: () => select(0), Enter: submit })
 * @param {boolean} enabled - Whether shortcuts are active (default: true)
 */
export function useGameKeyboard(handlers, enabled = true) {
  useEffect(() => {
    if (!enabled) return

    const handleKeyDown = (e) => {
      const key = e.key.toLowerCase()
      const handler = handlers[key] || handlers[e.key]
      if (handler) {
        e.preventDefault()
        handler(e)
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [handlers, enabled])
}
