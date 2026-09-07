import { useNavigate } from "react-router"
import { useStore } from "../store/store"

// Find the skill with the most sessions for "practice now" suggestion
function suggestSkill(groupedSummary) {
  if (!groupedSummary?.length) return null

  let best = null
  for (const group of groupedSummary) {
    // Check root skill
    if (!best || group.total_sessions > best.total_sessions) {
      best = { ...group.skill, total_sessions: group.total_sessions, last_session: group.last_session }
    }
    // Check children
    for (const child of group.children || []) {
      if (!best || child.total_sessions > best.total_sessions) {
        best = { ...child.skill, total_sessions: child.total_sessions, last_session: child.last_session }
      }
    }
  }
  return best
}

function formatRelativeTime(iso) {
  if (!iso) return null
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return "ahora"
  if (mins < 60) return `hace ${mins}m`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `hace ${hours}h`
  const days = Math.floor(hours / 24)
  return `hace ${days}d`
}

export default function QuickActions() {
  const navigate = useNavigate()
  const { groupedSummary } = useStore()
  const suggested = suggestSkill(groupedSummary)

  if (!suggested) return null

  const lastPractice = formatRelativeTime(suggested.last_session)

  return (
    <div className="mb-8">
      <button
        onClick={() => navigate(`/practice/${suggested.skill_type}?skillId=${suggested.id}`)}
        className="w-full card p-5 flex items-center justify-between hover:border-green-500/20 transition-all duration-200 group"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-black text-xl font-black shadow-lg shadow-green-500/25 group-hover:shadow-green-500/40 transition-all">
            ▶
          </div>
          <div className="text-left">
            <p className="text-sm font-bold text-white group-hover:text-green-400 transition-colors">
              Practicar ahora
            </p>
            <p className="text-xs text-neutral-500 mt-0.5">
              {suggested.name}
              {lastPractice && <span className="ml-2 text-neutral-600">· {lastPractice}</span>}
            </p>
          </div>
        </div>
        <span className="text-neutral-600 group-hover:text-green-400 transition-colors text-lg">
          →
        </span>
      </button>
    </div>
  )
}
