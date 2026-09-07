import { memo } from "react"

const SIZES = {
  sm: "w-4 h-4",
  md: "w-6 h-6",
  lg: "w-8 h-8",
}

const Spinner = memo(function Spinner({ size = "sm", className = "" }) {
  return (
    <div
      className={`${SIZES[size]} border-2 border-neutral-700 border-t-green-500 rounded-full animate-spin ${className}`}
      role="status"
      aria-label="Cargando"
    >
      <span className="sr-only">Cargando...</span>
    </div>
  )
})

export default Spinner
