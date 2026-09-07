import { memo } from "react"
import { MiniLevelRing } from "./ui/ProgressBar"
import Badge from "./ui/Badge"

const SkillCard = memo(function SkillCard({ summary, onPractice, compact = false }) {
  const { skill, total_sessions, sessions_this_week, streak_days } = summary

  const isGameSkill = ["memory_number", "problem_set", "dual_n_back", "iq_practice"].includes(
    skill.skill_type
  )

  const handleClick = () => {
    if (onPractice && isGameSkill) {
      onPractice(skill.id, skill.skill_type)
    }
  }

  if (compact) {
    // Compact mode — 2 per row, like DualNBack grid
    return (
      <div
        className={`card group relative overflow-hidden hover:border-green-500/30 transition-all duration-300 p-4 ${isGameSkill ? "cursor-pointer" : ""}`}
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
        {/* Top row: ring + name */}
        <div className="flex items-center gap-3 mb-3">
          <MiniLevelRing level={skill.current_level} size={40} strokeWidth={3} />
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-bold text-white truncate">{skill.name}</h3>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-[9px] uppercase tracking-wider text-neutral-500">{skill.domain}</span>
              {skill.practice_level && (
                <Badge variant={skill.practice_level} className="!text-[8px] !px-1 !py-0" />
              )}
              {skill.is_plateaued && <span className="text-[9px] text-orange-400">⚠</span>}
            </div>
          </div>
        </div>

        {/* Stats row — compact */}
        <div className="flex items-center gap-3 text-[10px]">
          <span className="text-neutral-400">
            <span className="text-white font-bold">{total_sessions}</span> sesiones
          </span>
          {sessions_this_week > 0 && (
            <span className="text-green-500/70">
              <span className="font-bold">{sessions_this_week}</span> esta sem
            </span>
          )}
          {streak_days > 0 && (
            <span className="text-orange-400/70">🔥 {streak_days}</span>
          )}
        </div>

        {/* Play button — small, bottom right */}
        {isGameSkill && onPractice && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onPractice(skill.id, skill.skill_type)
            }}
            className="absolute bottom-3 right-3 w-8 h-8 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center justify-center text-green-400 hover:bg-green-500/20 hover:border-green-500/30 transition-all duration-200"
            title="Practicar"
          >
            ▶
          </button>
        )}
      </div>
    )
  }

  // Full mode — for root skills with children (used by SkillGroup)
  return (
    <div
      className={`card group relative overflow-hidden hover:border-green-500/30 transition-all duration-500 hover:-translate-y-2 ${isGameSkill ? "cursor-pointer" : ""}`}
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
      {/* Ambient glow */}
      <div className="absolute -right-16 -top-16 w-48 h-48 bg-green-500/[0.04] rounded-full blur-3xl group-hover:bg-green-500/[0.08] transition-all duration-700" />

      <div className="relative flex items-start gap-5">
        {/* Level Ring */}
        <div className="relative shrink-0">
          <MiniLevelRing level={skill.current_level} size={56} strokeWidth={4} />
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0 pt-0.5">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-bold text-lg text-white truncate">{skill.name}</h3>
            {skill.practice_level && <Badge variant={skill.practice_level} />}
            {skill.is_plateaued && (
              <span className="text-[10px] text-orange-400" title="Estancado">⚠</span>
            )}
          </div>

          {/* Stats Row */}
          <div className="flex items-center gap-4 mt-2">
            <span className="text-sm font-bold text-neutral-200">{total_sessions} <span className="text-[10px] font-normal text-neutral-500">sesiones</span></span>
            {sessions_this_week > 0 && (
              <span className="text-sm font-bold text-green-400">{sessions_this_week} <span className="text-[10px] font-normal text-neutral-500">esta sem</span></span>
            )}
            {streak_days > 0 && (
              <span className="text-sm font-bold text-orange-400">🔥 {streak_days}</span>
            )}
          </div>

          {/* Practice CTA */}
          {onPractice && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onPractice(skill.id, skill.skill_type)
              }}
              className="mt-3 py-2 px-4 rounded-lg text-xs font-bold text-black bg-gradient-to-r from-green-400 to-emerald-500 hover:from-green-300 hover:to-emerald-400 transition-all duration-200 shadow-md shadow-green-500/20 hover:shadow-green-500/30 active:scale-[0.98]"
            >
              Practicar
            </button>
          )}
        </div>
      </div>
    </div>
  )
})

export default SkillCard
