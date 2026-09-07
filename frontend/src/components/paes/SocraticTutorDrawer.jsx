import React, { useState } from "react"
import { MathRenderer } from "./MathRenderer"

export function SocraticTutorDrawer({ hints = [], onRequestHint, loading = false }) {
  const [studentInput, setStudentInput] = useState("")

  const handleAsk = (e) => {
    e.preventDefault()
    onRequestHint(studentInput.trim() || null)
    setStudentInput("")
  }

  return (
    <div className="bg-neutral-900/80 border border-white/[0.08] rounded-2xl p-5 backdrop-blur-xl mt-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-sm">
            💡
          </div>
          <h4 className="text-sm font-bold text-white uppercase tracking-wider">
            Tutor Socrático Adaptativo
          </h4>
        </div>
        <span className="text-xs text-neutral-400">
          Nivel de andamiaje: {hints.length} / 6
        </span>
      </div>

      {hints.length === 0 ? (
        <div className="p-4 rounded-xl bg-neutral-800/40 border border-white/[0.04] text-center">
          <p className="text-xs text-neutral-400 mb-3">
            ¿Trancado o con dudas de cómo plantear el ejercicio? Pedile una pista orientadora al tutor sin quemar la solución.
          </p>
          <button
            onClick={() => onRequestHint(null)}
            disabled={loading}
            className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-semibold rounded-xl border border-white/[0.08] transition-all"
          >
            {loading ? "Generando pista..." : "Pedir Pista Nivel 1"}
          </button>
        </div>
      ) : (
        <div className="space-y-3 mb-4">
          {hints.map((h, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-xl bg-neutral-800/60 border border-emerald-500/20 text-xs"
            >
              <div className="flex items-center gap-2 mb-1 text-emerald-400 font-bold uppercase text-[10px]">
                <span>Pista {h.tutor_level}</span>
              </div>
              <MathRenderer text={h.hint} className="text-neutral-300" />
            </div>
          ))}

          {hints.length < 6 && (
            <form onSubmit={handleAsk} className="flex gap-2 pt-2">
              <input
                type="text"
                value={studentInput}
                onChange={(e) => setStudentInput(e.target.value)}
                placeholder="Escribe tu duda o avance (opcional)..."
                className="flex-1 bg-neutral-800/60 border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500/50"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-3 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/30 rounded-xl text-xs font-bold transition-all"
              >
                {loading ? "..." : `Pista ${hints.length + 1}`}
              </button>
            </form>
          )}
        </div>
      )}
    </div>
  )
}
