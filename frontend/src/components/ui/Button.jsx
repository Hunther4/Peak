import { memo } from "react"

const VARIANTS = {
  primary:
    "bg-gradient-to-r from-green-400 to-emerald-500 text-black font-bold shadow-lg shadow-green-500/25 hover:shadow-green-500/40 hover:from-green-300 hover:to-emerald-400 active:scale-[0.98]",
  ghost:
    "bg-white/[0.04] text-neutral-300 border border-white/[0.08] hover:bg-white/[0.08] hover:text-white hover:border-white/[0.2]",
  danger:
    "bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 hover:text-red-300",
  subtle:
    "bg-transparent text-neutral-500 hover:text-neutral-300 hover:bg-white/[0.04]",
}

const SIZES = {
  sm: "px-3 py-1.5 text-[11px] rounded-lg",
  md: "px-4 py-2 text-xs rounded-xl",
  lg: "px-6 py-3 text-sm rounded-xl",
}

const Button = memo(function Button({
  children,
  variant = "primary",
  size = "md",
  className = "",
  disabled,
  ...props
}) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 font-semibold transition-all duration-200 disabled:opacity-40 disabled:pointer-events-none ${VARIANTS[variant]} ${SIZES[size]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
})

export default Button
