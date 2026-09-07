import React, { useState } from "react"

export function PaesReadingStimulus({ title, text, defaultExpanded = false }) {
  const [fontSize, setFontSize] = useState("text-base") // text-sm, text-base, text-lg, text-xl
  const [fontFamily, setFontFamily] = useState("serif") // serif, sans
  const [lineHeight, setLineHeight] = useState("leading-relaxed") // leading-normal, leading-relaxed, leading-loose
  const [concentrationMode, setConcentrationMode] = useState(false)
  const [columnWidth, setColumnWidth] = useState("max-w-prose") // max-w-prose, max-w-2xl, max-w-none

  if (!text) return null

  // Split into paragraphs and render with DEMRE-style paragraph numbers
  const paragraphs = text
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean)

  return (
    <div
      className={`rounded-3xl border transition-all ${
        concentrationMode
          ? "fixed inset-4 z-50 bg-neutral-950/95 border-sky-500/40 shadow-2xl p-6 lg:p-10 overflow-y-auto backdrop-blur-2xl"
          : "p-6 rounded-2xl bg-white/[0.02] border-white/[0.08] mb-6"
      }`}
    >
      {/* Header & Controls Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 mb-4 border-b border-white/[0.08]">
        <div className="flex items-center gap-2">
          <span className="p-1.5 rounded-lg bg-sky-500/10 text-sky-400 text-sm">📖</span>
          <div>
            <span className="text-[10px] font-mono uppercase font-bold tracking-wider text-sky-400 block">
              Texto de Lectura / Estímulo Oficial
            </span>
            <h4 className="text-sm font-bold text-white tracking-tight">
              {title || "Lectura Comprensiva DEMRE"}
            </h4>
          </div>
        </div>

        {/* Reader Customization Toolbar */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-neutral-900 border border-white/[0.06] text-xs">
          {/* Font Serif / Sans */}
          <button
            onClick={() => setFontFamily(fontFamily === "serif" ? "sans" : "serif")}
            className={`px-2 py-1 rounded-lg font-medium transition-all ${
              fontFamily === "serif" ? "bg-sky-500/20 text-sky-300 font-serif" : "text-neutral-400 hover:text-white"
            }`}
            title="Cambiar tipografía (Serif / Sans)"
          >
            {fontFamily === "serif" ? "Serif" : "Sans"}
          </button>

          <span className="w-px h-3.5 bg-white/10 mx-0.5" />

          {/* Font Sizes A- / A+ */}
          <button
            onClick={() => {
              if (fontSize === "text-xl") setFontSize("text-lg")
              else if (fontSize === "text-lg") setFontSize("text-base")
              else if (fontSize === "text-base") setFontSize("text-sm")
            }}
            className="px-2 py-1 rounded-lg text-neutral-400 hover:text-white transition-all font-mono"
            title="Reducir tamaño de letra"
          >
            A-
          </button>
          <button
            onClick={() => {
              if (fontSize === "text-sm") setFontSize("text-base")
              else if (fontSize === "text-base") setFontSize("text-lg")
              else if (fontSize === "text-lg") setFontSize("text-xl")
            }}
            className="px-2 py-1 rounded-lg text-neutral-400 hover:text-white transition-all font-mono font-bold"
            title="Aumentar tamaño de letra"
          >
            A+
          </button>

          <span className="w-px h-3.5 bg-white/10 mx-0.5" />

          {/* Line Spacing */}
          <button
            onClick={() => {
              if (lineHeight === "leading-normal") setLineHeight("leading-relaxed")
              else if (lineHeight === "leading-relaxed") setLineHeight("leading-loose")
              else setLineHeight("leading-normal")
            }}
            className="px-2 py-1 rounded-lg text-neutral-400 hover:text-white transition-all font-mono"
            title="Cambiar espaciado de línea"
          >
            ↕
          </button>

          <span className="w-px h-3.5 bg-white/10 mx-0.5" />

          {/* Concentration Mode */}
          <button
            onClick={() => setConcentrationMode(!concentrationMode)}
            className={`px-2.5 py-1 rounded-lg font-medium transition-all flex items-center gap-1 ${
              concentrationMode
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold"
                : "text-neutral-400 hover:text-white"
            }`}
            title="Modo Concentración (Pantalla Completa de Lectura)"
          >
            <span>{concentrationMode ? "✕ Salir" : "🔍 Foco"}</span>
          </button>
        </div>
      </div>

      {/* Reading Text Container */}
      <div
        className={`mx-auto ${columnWidth} ${
          fontFamily === "serif" ? "font-serif text-neutral-200" : "font-sans text-neutral-300"
        } ${fontSize} ${lineHeight} transition-all space-y-4 select-text`}
      >
        {paragraphs.map((p, idx) => (
          <div key={idx} className="flex gap-3 group">
            <span className="text-[11px] font-mono text-neutral-500 font-bold select-none pt-1 shrink-0 opacity-40 group-hover:opacity-100 transition-opacity">
              [{idx + 1}]
            </span>
            <p className="leading-relaxed text-justify">{p}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
