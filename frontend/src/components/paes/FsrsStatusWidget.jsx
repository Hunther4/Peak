import React from "react"

export function FsrsStatusWidget({ fsrsStatus, onReviewDueClick }) {
  if (!fsrsStatus) return null

  const dueCount = fsrsStatus.due_for_review_count || 0
  const cappedCount = fsrsStatus.capped_review_queue?.length || 0

  return (
    <div className="bg-neutral-900/60 border border-white/[0.08] rounded-2xl p-5 backdrop-blur-xl mb-6 shadow-xl">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
              Motor FSRS v4.5
            </span>
            <span className="text-xs text-neutral-400">
              Amortiguación cognitiva activa (Máx 5/día)
            </span>
          </div>
          <h3 className="text-lg font-bold text-white">
            Estado de Memoria & Retención Espaciada
          </h3>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-neutral-800/80 border border-white/[0.06] px-4 py-2 rounded-xl text-center">
            <div className="text-2xl font-black text-amber-400">{dueCount}</div>
            <div className="text-[11px] font-medium text-neutral-400">Repasos pendientes</div>
          </div>
          <div className="bg-neutral-800/80 border border-white/[0.06] px-4 py-2 rounded-xl text-center">
            <div className="text-2xl font-black text-emerald-400">{cappedCount}</div>
            <div className="text-[11px] font-medium text-neutral-400">Objetivo hoy</div>
          </div>
        </div>
      </div>

      {cappedCount > 0 && (
        <div className="mt-4 pt-4 border-t border-white/[0.06] flex items-center justify-between">
          <span className="text-sm text-neutral-300">
            Tenés subtemas en tu cola prioritaria listos para reforzar estabilidad de memoria.
          </span>
          {onReviewDueClick && (
            <button
              onClick={onReviewDueClick}
              className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-black font-bold text-xs rounded-xl shadow-lg shadow-emerald-500/20 transition-all duration-150"
            >
              Iniciar Repasos FSRS
            </button>
          )}
        </div>
      )}
    </div>
  )
}
