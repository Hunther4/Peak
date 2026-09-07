import React, { useMemo } from "react"

export function MathRenderer({ text = "", className = "" }) {
  const htmlContent = useMemo(() => {
    if (!text) return ""
    // Replace $math$ with rendered KaTeX or span
    return text.replace(/\$([^\$]+)\$/g, (_, expr) => {
      if (typeof window !== "undefined" && window.katex) {
        try {
          return window.katex.renderToString(expr, { throwOnError: false })
        } catch {
          return `<span class="font-mono text-emerald-400">${expr}</span>`
        }
      }
      return `<span class="font-mono text-emerald-400">${expr}</span>`
    })
  }, [text])

  return (
    <div
      className={`leading-relaxed text-neutral-200 ${className}`}
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  )
}
