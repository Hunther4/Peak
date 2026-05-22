import { useState, memo } from 'react';

const SkillCard = memo(function SkillCard({ summary }) {
  const { skill, total_sessions, sessions_this_week, streak_days, last_assessment } = summary;
  const [isHovered, setIsHovered] = useState(false);

  // Calculate level percentage for the ring
  const levelPercent = Math.min((skill.current_level / 100) * 100, 100);
  const circumference = 2 * Math.PI * 40;
  const strokeDashoffset = circumference - (levelPercent / 100) * circumference;

  return (
    <div
      className="card group relative overflow-hidden hover:border-green-500/30 transition-all duration-500 hover:-translate-y-2"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Ambient glow layers */}
      <div className="absolute -right-16 -top-16 w-48 h-48 bg-green-500/[0.04] rounded-full blur-3xl group-hover:bg-green-500/[0.08] transition-all duration-700" style={{ animation: isHovered ? 'mesh-shift 10s ease-in-out infinite' : 'none' }} />
      <div className="absolute -left-8 -bottom-8 w-32 h-32 bg-emerald-500/[0.03] rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-all duration-700" />
      <div className="absolute inset-0 bg-gradient-to-br from-green-500/[0.02] via-transparent to-emerald-500/[0.02] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <div className="relative flex items-start gap-6">
        {/* Level Ring */}
        <div className="relative shrink-0 group/ring">
          {/* Outer pulse ring */}
          {isHovered && (
            <div className="absolute inset-0 rounded-full border-2 border-green-500/20" style={{ animation: 'pulse-ring 2s ease-out infinite' }} />
          )}
          
          <svg width="96" height="96" viewBox="0 0 96 96" className="transform -rotate-90 transition-transform duration-500 group-hover/ring:scale-110 group-hover/ring:rotate-0" role="img" aria-label={`Nivel ${Math.round(skill.current_level)} de 100`}>
            {/* Track */}
            <circle cx="48" cy="48" r="40" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="5" />
            {/* Progress */}
            <circle
              cx="48" cy="48" r="40" fill="none"
              stroke="url(#levelGradient)"
              strokeWidth="5"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className="transition-all duration-1000 ease-out"
              style={{ filter: isHovered ? 'drop-shadow(0 0 4px rgba(34, 197, 94, 0.5))' : 'none' }}
            />
            <defs>
              <linearGradient id="levelGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#4ade80" />
                <stop offset="50%" stopColor="#22c55e" />
                <stop offset="100%" stopColor="#059669" />
              </linearGradient>
            </defs>
          </svg>
          {/* Level Number */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-black text-white leading-none" style={{ textShadow: isHovered ? '0 0 12px rgba(34, 197, 94, 0.4)' : 'none' }}>
              {Math.round(skill.current_level)}
            </span>
            <span className="text-[9px] text-neutral-500 uppercase tracking-widest mt-1">nivel</span>
          </div>
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0 pt-1">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-bold text-xl text-white truncate" style={{ textShadow: isHovered ? '0 0 8px rgba(255,255,255,0.1)' : 'none' }}>
              {skill.name}
            </h3>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-neutral-500 bg-white/[0.04] px-3 py-1.5 rounded-lg border border-white/[0.08] shrink-0 ml-3 transition-all duration-300 group-hover:border-green-500/20 group-hover:text-green-400/70">
              {skill.domain}
            </span>
          </div>

          {/* Stats Row */}
          <div className="flex items-center gap-5 mt-4">
            <div className="flex items-center gap-2 group/stat">
              <span className="text-xl font-bold text-neutral-200 group-hover/stat:text-white transition-colors">{total_sessions}</span>
              <span className="text-[11px] text-neutral-500 uppercase">sesiones</span>
            </div>
            <div className="w-px h-5 bg-white/[0.08]" />
            <div className="flex items-center gap-2 group/stat">
              <span className="text-xl font-bold text-neutral-200 group-hover/stat:text-white transition-colors">{sessions_this_week}</span>
              <span className="text-[11px] text-neutral-500 uppercase">esta sem</span>
            </div>
            <div className="w-px h-5 bg-white/[0.08]" />
            <div className="flex items-center gap-2 group/stat">
              <span className="text-xl font-bold text-orange-400 group-hover/stat:text-orange-300 transition-colors" style={{ textShadow: isHovered ? '0 0 8px rgba(251, 146, 60, 0.4)' : 'none' }}>{streak_days}</span>
              <span className="text-[11px] text-orange-400/60 uppercase">🔥 racha</span>
            </div>
          </div>

          {/* Last Assessment */}
          {last_assessment && (
            <div className="mt-4 flex items-center justify-between bg-white/[0.03] rounded-xl px-4 py-3 border border-white/[0.06] transition-all duration-300 hover:border-green-500/20 hover:bg-white/[0.04] group-hover:border-green-500/10">
              <span className="text-[11px] text-neutral-500 uppercase tracking-wider">Última evaluación</span>
              <span className="text-lg font-bold text-white">{last_assessment.score} <span className="text-neutral-500 font-normal text-sm">pts</span></span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

export default SkillCard;
