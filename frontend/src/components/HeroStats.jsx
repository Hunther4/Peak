import { useStore } from "../store/store"

// Compute aggregate stats from per-skill summary data
function computeStats(summary) {
  if (!summary?.skills?.length) {
    return { totalSessions: 0, weeklySessions: 0, streak: 0, avgLevel: 0 }
  }

  const skills = summary.skills
  const totalSessions = skills.reduce((sum, s) => sum + s.total_sessions, 0)
  const weeklySessions = skills.reduce((sum, s) => sum + s.sessions_this_week, 0)
  const streak = Math.max(...skills.map((s) => s.streak_days), 0)
  const levels = skills.map((s) => s.skill.current_level).filter(Boolean)
  const avgLevel = levels.length ? levels.reduce((a, b) => a + b, 0) / levels.length : 0

  return { totalSessions, weeklySessions, streak, avgLevel }
}

const STATS = [
  {
    key: "totalSessions",
    label: "Sesiones",
    icon: "📊",
    color: "from-blue-500/15 to-blue-600/5",
    border: "border-blue-500/20",
    text: "text-blue-400",
  },
  {
    key: "weeklySessions",
    label: "Esta semana",
    icon: "🔥",
    color: "from-orange-500/15 to-orange-600/5",
    border: "border-orange-500/20",
    text: "text-orange-400",
  },
  {
    key: "streak",
    label: "Racha",
    icon: "⚡",
    color: "from-green-500/15 to-green-600/5",
    border: "border-green-500/20",
    text: "text-green-400",
  },
  {
    key: "avgLevel",
    label: "Nivel promedio",
    icon: "🎯",
    color: "from-purple-500/15 to-purple-600/5",
    border: "border-purple-500/20",
    text: "text-purple-400",
  },
]

export default function HeroStats() {
  const { summary } = useStore()
  const stats = computeStats(summary)

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {STATS.map((s) => (
        <div
          key={s.key}
          className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${s.color} border ${s.border} p-5 group hover:scale-[1.02] transition-transform duration-200`}
        >
          <div className="flex items-start justify-between mb-3">
            <span className="text-2xl">{s.icon}</span>
          </div>
          <p className={`text-3xl font-black ${s.text} tracking-tight`}>
            {s.key === "avgLevel" ? stats[s.key].toFixed(1) : stats[s.key]}
          </p>
          <p className="text-[11px] uppercase tracking-wider text-neutral-500 font-medium mt-1">
            {s.label}
          </p>
        </div>
      ))}
    </div>
  )
}
