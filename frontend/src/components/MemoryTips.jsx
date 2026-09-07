/**
 * MemoryTips — scientifically-grounded memory techniques shown during the
 * Memory Game. Renders nothing during 'presenting' and 'done' phases; a
 * full grid during 'idle'; a single rotating tip with a dismiss action
 * during 'feedback'.
 *
 * Tips cover four technique families: encoding (chunking, visualization,
 * semantic), rehearsal (active repetition), attention (pattern scan,
 * interference reduction).
 */
const TIPS = [
  {
    id: "chunking",
    title: "Agrupá en bloques",
    body: "Partí la secuencia en grupos de 3 o 4 dígitos (739-251 en vez de 7-3-9-2-5-1). La memoria de trabajo maneja mejor piezas con significado que piezas sueltas (Miller, 1956).",
    technique: "encoding",
  },
  {
    id: "visualization",
    title: "Asociá con imágenes",
    body: "Vinculá cada número con una imagen vívida o colocalo en un punto de un recorrido que conozcas bien (método de los loci). Cuanto más detallada la escena, más fácil de recuperar.",
    technique: "encoding",
  },
  {
    id: "pattern",
    title: "Buscá patrones",
    body: "Escaneá la secuencia antes de que aparezca: fechas (15-09), dobles (77, 33, 22), primos consecutivos. Tu cerebro reconoce configuraciones familiares más rápido que dígitos aislados.",
    technique: "attention",
  },
  {
    id: "rehearsal",
    title: "Repetí activamente",
    body: "Mientras llega el próximo dígito, repetí internamente el grupo anterior. No mires pasivamente: mantener los ítems activos en la memoria de trabajo es lo que evita que se borren.",
    technique: "rehearsal",
  },
  {
    id: "semantic",
    title: "Convertí en historia",
    body: "Transformá los números en algo con significado: 1945 → fin de la guerra, 911 → emergencias, 15-07 → Día del Amigo. Los datos con contexto se retienen mucho mejor que los abstractos.",
    technique: "encoding",
  },
  {
    id: "interference",
    title: "Anclá antes de avanzar",
    body: "Cuando aparece un dígito nuevo, «colocá» mentalmente el grupo anterior en un lugar fijo antes de prestarle atención. Así evitás que se superponga con lo que viene después.",
    technique: "attention",
  },
]

const TECHNIQUE_LABELS = {
  encoding: "Codificación",
  retrieval: "Recuperación",
  rehearsal: "Repaso",
  attention: "Atención",
}

function TipCard({ tip }) {
  return (
    <div className="card p-5" data-testid={`memory-tip-${tip.id}`}>
      <div className="flex items-start justify-between gap-3 mb-2">
        <h4 className="text-sm font-bold text-white leading-snug">{tip.title}</h4>
        <span className="shrink-0 text-[10px] text-neutral-500 uppercase tracking-wider px-2 py-0.5 rounded border border-white/[0.08]">
          {TECHNIQUE_LABELS[tip.technique]}
        </span>
      </div>
      <p className="text-xs text-neutral-400 leading-relaxed">{tip.body}</p>
    </div>
  )
}

function selectTip(currentTipId) {
  if (currentTipId) {
    const match = TIPS.find((t) => t.id === currentTipId)
    if (match) return match
  }
  return TIPS[Math.floor(Math.random() * TIPS.length)]
}

export function MemoryTips({
  phase = "idle",
  compact = false,
  currentTipId = null,
  onDismiss = null,
}) {
  if (phase === "presenting" || phase === "done") return null

  const showAll = phase === "idle" && !compact

  if (showAll) {
    return (
      <div
        className="grid grid-cols-1 md:grid-cols-2 gap-4"
        data-testid="memory-tips"
      >
        {TIPS.map((tip) => (
          <TipCard key={tip.id} tip={tip} />
        ))}
      </div>
    )
  }

  const tip = selectTip(currentTipId)
  const showDismiss = phase === "feedback" && typeof onDismiss === "function"

  return (
    <div className="space-y-3" data-testid="memory-tips">
      <TipCard tip={tip} />
      {showDismiss && (
        <div className="flex justify-end">
          <button
            type="button"
            onClick={onDismiss}
            className="text-[10px] text-neutral-500 uppercase tracking-wider hover:text-neutral-300 transition-colors"
            aria-label="Ver todos los consejos"
          >
            Ver todos los consejos
          </button>
        </div>
      )}
    </div>
  )
}
