import { memo } from "react"

const SVG_ILLUSTRATIONS = {
  skills: (
    <svg viewBox="0 0 120 120" className="w-full h-full" fill="none">
      <circle cx="60" cy="60" r="50" stroke="rgba(255,255,255,0.06)" strokeWidth="2" strokeDasharray="4 4" />
      <circle cx="60" cy="60" r="30" stroke="rgba(255,255,255,0.04)" strokeWidth="1.5" strokeDasharray="3 3" />
      <circle cx="60" cy="60" r="8" fill="rgba(74,222,128,0.2)" />
      <circle cx="60" cy="60" r="3" fill="#4ade80" />
      <circle cx="35" cy="45" r="3" fill="rgba(255,255,255,0.1)" />
      <circle cx="85" cy="45" r="3" fill="rgba(255,255,255,0.1)" />
      <circle cx="60" cy="85" r="3" fill="rgba(255,255,255,0.1)" />
      <line x1="60" y1="60" x2="35" y2="45" stroke="rgba(255,255,255,0.06)" strokeWidth="1" />
      <line x1="60" y1="60" x2="85" y2="45" stroke="rgba(255,255,255,0.06)" strokeWidth="1" />
      <line x1="60" y1="60" x2="60" y2="85" stroke="rgba(255,255,255,0.06)" strokeWidth="1" />
    </svg>
  ),
  sessions: (
    <svg viewBox="0 0 120 120" className="w-full h-full" fill="none">
      <rect x="20" y="40" width="16" height="50" rx="4" fill="rgba(74,222,128,0.15)" />
      <rect x="42" y="30" width="16" height="60" rx="4" fill="rgba(74,222,128,0.2)" />
      <rect x="64" y="50" width="16" height="40" rx="4" fill="rgba(74,222,128,0.15)" />
      <rect x="86" y="20" width="16" height="70" rx="4" fill="rgba(74,222,128,0.25)" />
      <line x1="15" y1="95" x2="105" y2="95" stroke="rgba(255,255,255,0.08)" strokeWidth="1" />
    </svg>
  ),
  practice: (
    <svg viewBox="0 0 120 120" className="w-full h-full" fill="none">
      <circle cx="60" cy="60" r="45" stroke="rgba(255,255,255,0.06)" strokeWidth="2" />
      <path d="M50 45 L75 60 L50 75Z" fill="rgba(74,222,128,0.3)" stroke="#4ade80" strokeWidth="1.5" strokeLinejoin="round" />
    </svg>
  ),
}

const EmptyState = memo(function EmptyState({
  illustration = "skills",
  title,
  description,
  action,
  className = "",
}) {
  return (
    <div className={`text-center py-12 ${className}`}>
      <div className="w-24 h-24 mx-auto mb-4 opacity-60">
        {SVG_ILLUSTRATIONS[illustration] || SVG_ILLUSTRATIONS.skills}
      </div>
      <h3 className="text-sm font-bold text-white mb-1">{title}</h3>
      {description && (
        <p className="text-xs text-neutral-500 max-w-xs mx-auto mb-4">{description}</p>
      )}
      {action}
    </div>
  )
})

export default EmptyState
