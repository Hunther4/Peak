import { useEffect, useRef, useState } from "react"

/**
 * PageTransition — wraps page content with a fade-in animation.
 * Use at the top of each page component.
 */
export function PageTransition({ children, className = "" }) {
  const [visible, setVisible] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    // Trigger fade-in on next frame
    requestAnimationFrame(() => setVisible(true))
  }, [])

  return (
    <div
      ref={ref}
      className={`transition-all duration-300 ease-out ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"
      } ${className}`}
    >
      {children}
    </div>
  )
}
