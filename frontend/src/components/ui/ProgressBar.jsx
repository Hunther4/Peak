import { memo } from "react"

// Circular level ring — used by SkillCard, SubSkillCard
export const LevelRing = memo(function LevelRing({
  level,
  size = 96,
  strokeWidth = 5,
  className = "",
}) {
  const radius = (size / 2) - strokeWidth - 2
  const circumference = 2 * Math.PI * radius
  const percent = Math.min(Math.max(level / 100, 0), 1)
  const offset = circumference - percent * circumference

  return (
    <div className={`relative shrink-0 ${className}`}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="-rotate-90"
        role="img"
        aria-label={`Nivel ${Math.round(level)} de 100`}
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.04)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="url(#peakLevelGradient)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-1000 ease-out"
        />
        <defs>
          <linearGradient id="peakLevelGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4ade80" />
            <stop offset="50%" stopColor="#22c55e" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-black text-white leading-none">
          {Math.round(level)}
        </span>
        <span className="text-[9px] text-neutral-500 uppercase tracking-widest mt-1">nivel</span>
      </div>
    </div>
  )
})

// Mini level ring — for SubSkillCard
export const MiniLevelRing = memo(function MiniLevelRing({
  level,
  size = 40,
  strokeWidth = 3,
  className = "",
}) {
  const radius = (size / 2) - strokeWidth - 2
  const circumference = 2 * Math.PI * radius
  const percent = Math.min(Math.max(level / 100, 0), 1)
  const offset = circumference - percent * circumference

  return (
    <div className={`relative shrink-0 ${className}`}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="-rotate-90"
      >
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth={strokeWidth} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="url(#peakMiniLevelGradient)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-700"
        />
        <defs>
          <linearGradient id="peakMiniLevelGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4ade80" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>
        </defs>
      </svg>
      <span className="absolute inset-0 flex items-center justify-center text-[11px] font-bold text-white">
        {Math.round(level)}
      </span>
    </div>
  )
})

// Linear progress bar — for staircase, generic progress
export const ProgressBar = memo(function ProgressBar({
  value,
  max = 100,
  color = "green",
  size = "sm",
  label,
  className = "",
}) {
  const percent = Math.min(Math.max((value / max) * 100, 0), 100)
  const colors = {
    green: "bg-green-500",
    blue: "bg-blue-500",
    purple: "bg-purple-500",
    orange: "bg-orange-500",
    red: "bg-red-500",
  }
  const heights = { sm: "h-1.5", md: "h-2.5", lg: "h-4" }

  return (
    <div className={className}>
      {label && (
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[10px] uppercase tracking-wider text-neutral-500 font-medium">{label}</span>
          <span className="text-[10px] text-neutral-400 font-mono">{Math.round(percent)}%</span>
        </div>
      )}
      <div className={`w-full ${heights[size]} rounded-full bg-white/[0.06] overflow-hidden`}>
        <div
          className={`${heights[size]} rounded-full ${colors[color] || colors.green} transition-all duration-700 ease-out`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
})
