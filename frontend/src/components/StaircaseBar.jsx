/**
 * StaircaseBar — visual indicator of the adaptive staircase progress.
 *
 * Shows consecutive correct / incorrect counts against the current level's
 * thresholds. Used in IQ Practice and Math Thinking to give the user
 * real-time feedback on how close they are to leveling up or down.
 *
 * Uniform thresholds (matches backend core/staircase.py):
 *   - 5 correct to level UP, 3 incorrect to level DOWN (all levels)
 */
export function StaircaseBar({ correct, incorrect }) {
  const correctThreshold = 5
  const incorrectThreshold = 3

  return (
    <div className="flex items-center justify-center gap-4 text-xs" data-testid="staircase-bar">
      <div className="flex items-center gap-1.5">
        <span className="text-green-400/70" aria-hidden="true">✓</span>
        <div className="flex gap-0.5" role="progressbar" aria-valuenow={correct} aria-valuemax={correctThreshold} aria-label={`Aciertos consecutivos: ${correct} de ${correctThreshold}`}>
          {Array.from({ length: correctThreshold }, (_, i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                i < correct
                  ? "bg-green-400 shadow-sm shadow-green-400/50"
                  : "bg-neutral-800"
              }`}
            />
          ))}
        </div>
        <span className="text-neutral-600 tabular-nums">
          {correct}/{correctThreshold}
        </span>
      </div>

      <span className="text-neutral-700" aria-hidden="true">|</span>

      <div className="flex items-center gap-1.5">
        <span className="text-red-400/70" aria-hidden="true">✕</span>
        <div className="flex gap-0.5" role="progressbar" aria-valuenow={incorrect} aria-valuemax={incorrectThreshold} aria-label={`Errores consecutivos: ${incorrect} de ${incorrectThreshold}`}>
          {Array.from({ length: incorrectThreshold }, (_, i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                i < incorrect
                  ? "bg-red-400 shadow-sm shadow-red-400/50"
                  : "bg-neutral-800"
              }`}
            />
          ))}
        </div>
        <span className="text-neutral-600 tabular-nums">
          {incorrect}/{incorrectThreshold}
        </span>
      </div>
    </div>
  )
}
