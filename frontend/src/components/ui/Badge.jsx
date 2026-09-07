import { memo } from "react"

const VARIANTS = {
  deliberate: "bg-green-500/20 text-green-400",
  purposeful: "bg-yellow-500/20 text-yellow-400",
  naive: "bg-neutral-500/20 text-neutral-400",
  plateau: "bg-orange-500/20 text-orange-400",
  info: "bg-blue-500/20 text-blue-400",
  success: "bg-green-500/20 text-green-400",
  warning: "bg-yellow-500/20 text-yellow-400",
  danger: "bg-red-500/20 text-red-400",
}

const LABELS = {
  deliberate: "🎯 Deliberada",
  purposeful: "📋 Con propósito",
  naive: "🔄 Naive",
  plateau: "⚠ Estancado",
}

const Badge = memo(function Badge({ variant = "info", label, children, className = "" }) {
  const text = label || LABELS[variant] || children
  return (
    <span
      className={`inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider px-2 py-1 rounded-md ${VARIANTS[variant] || VARIANTS.info} ${className}`}
    >
      {text}
    </span>
  )
})

export default Badge
