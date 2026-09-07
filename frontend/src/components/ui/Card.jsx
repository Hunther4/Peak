import { memo } from "react"

const Card = memo(function Card({
  children,
  className = "",
  hover = false,
  interactive = false,
  ...props
}) {
  return (
    <div
      className={`card relative overflow-hidden ${hover ? "hover:border-green-500/30 hover:-translate-y-2" : ""} ${interactive ? "cursor-pointer" : ""} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
})

export default Card
