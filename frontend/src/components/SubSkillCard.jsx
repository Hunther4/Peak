import { memo, useState, useEffect } from "react"
import { MiniLevelRing } from "./ui/ProgressBar"
import Badge from "./ui/Badge"

// Simple trend indicator based on sessions_this_week
function TrendArrow({ sessionsThisWeek }) {
  if (sessionsThisWeek >= 5) return <span className="text-green-400 text-[10px]" title="Activo">↑</span>
  if (sessionsThisWeek >= 2) return <span className="text-yellow-400 text-[10px]" title="Regular">→</span>
  if (sessionsThisWeek >= 1) return <span className="text-orange-400 text-[10px]" title="Poco">↓</span>
  return <span className="text-neutral-600 text-[10px]" title="Sin actividad">·</span>
}

// Time since last practice
function TimeSince({ iso }) {
  const [text, setText] = useState(null)

  useEffect(() => {
    if (!iso) return
    const diff = Date.now() - new Date(iso).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) setText("ahora")
    else if (mins < 60) setText(`${mins}m`)
    else {
      const hours = Math.floor(mins / 60)
      if (hours < 24) setText(`${hours}h`)
      else {
        const days = Math.floor(hours / 24)
        if (days < 7) setText(`${days}d`)
        else {
          const weeks = Math.floor(days / 7)
          setText(`${weeks}sem`)
        }
      }
    }
  }, [iso])

  if (!text) return null
  return (
    <span className="text-[10px] text-neutral-600" title={new Date(iso).toLocaleString()}>
      {text}
    </span>
  )
}

const SubSkillCard = memo(function SubSkillCard({ summary, onPractice }) {
  const { skill, total_sessions, sessions_this_week, streak_days, last_session } =
    summary

  const isGameSkill = ["memory_number", "problem_set", "dual_n_back", "iq_practice"].includes(
    skill.skill_type
  )

  const handleClick = () => {
    if (onPractice && isGameSkill) {
      onPractice(skill.id, skill.skill_type)
    }
  }

  return (
    <div
      className={`flex items-center gap-4 p-3 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:border-green-500/20 hover:bg-white/[0.04] transition-all duration-200 ${isGameSkill ? "cursor-pointer" : ""}`}
      onClick={handleClick}
      role={isGameSkill ? "button" : undefined}
      tabIndex={isGameSkill ? 0 : undefined}
      onKeyDown={
        isGameSkill
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") handleClick()
            }
          : undefined
      }
    >
      {/* Mini level ring */}
      <MiniLevelRing level={skill.current_level} />

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-white truncate">{skill.name}</span>
          {skill.practice_level && (
            <Badge variant={skill.practice_level} className="!text-[9px] !px-1.5 !py-0.5" />
          )}
          {skill.is_plateaued && <span className="text-[9px] text-orange-400" title="Estancado">⚠</span>}
          <TrendArrow sessionsThisWeek={sessions_this_week} />
        </div>
        <div className="flex items-center gap-3 mt-1">
          <span className="text-[10px] text-neutral-500">{total_sessions} sesiones</span>
          {sessions_this_week > 0 && (
            <span className="text-[10px] text-green-500/70">{sessions_this_week} esta sem</span>
          )}
          {streak_days > 0 && (
            <span className="text-[10px] text-orange-400/70">🔥 {streak_days}</span>
          )}
          <TimeSince iso={last_session} />
        </div>
      </div>

      {/* Play button for game skills */}
      {isGameSkill && onPractice && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onPractice(skill.id, skill.skill_type)
          }}
          className="shrink-0 w-8 h-8 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center justify-center text-green-400 hover:bg-green-500/20 hover:border-green-500/30 transition-all duration-200"
          title="Practicar"
        >
          ▶
        </button>
      )}
    </div>
  )
})

export default SubSkillCard
