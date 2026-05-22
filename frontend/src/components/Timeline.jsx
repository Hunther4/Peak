import { useEffect, useState, useRef, memo } from 'react';
import { useStore } from '../store/store';

function parseAuditLog(entry) {
  if (!entry.ai_audit_log) return null;
  try {
    return JSON.parse(entry.ai_audit_log);
  } catch {
    return null;
  }
}

const ScoreRing = memo(function ScoreRing({ score, size = 40 }) {
  const radius = (size / 2) - 3;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 70 ? '#22c55e' : score >= 40 ? '#f59e0b' : '#ef4444';
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setTimeout(() => setIsVisible(true), 200);
        }
      },
      { threshold: 0.5 }
    );

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="transform -rotate-90">
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="3" />
        <circle
          cx={size/2} cy={size/2} r={radius} fill="none"
          stroke={color} strokeWidth="3" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={isVisible ? offset : circumference}
          className="transition-all duration-1000 ease-out"
          style={{ filter: `drop-shadow(0 0 4px ${color}40)` }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-[11px] font-bold text-neutral-300">{score}</span>
      </div>
    </div>
  );
});

export default function Timeline() {
  const { timeline, fetchTimeline } = useStore();
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchTimeline();
  }, []);

  if (!timeline || timeline.length === 0) {
    return (
      <div className="card text-center py-20">
        <div className="w-20 h-20 rounded-2xl bg-neutral-800/50 flex items-center justify-center text-3xl mx-auto mb-4">📝</div>
        <p className="text-neutral-400 text-sm font-medium">No hay sesiones todavía</p>
        <p className="text-neutral-600 text-xs mt-2">Creá tu primera sesión en el panel de arriba</p>
      </div>
    );
  }

  const filteredTimeline = filter === 'all' ? timeline :
    filter === 'deliberate' ? timeline.filter(e => e.was_deliberate === true) :
    filter === 'not-deliberate' ? timeline.filter(e => e.was_deliberate === false) :
    timeline.filter(e => e.ai_fields_status === 'pending');

  return (
    <div className="space-y-4">
      {/* Filter Tabs */}
      <div className="flex items-center gap-1 p-1.5 bg-white/[0.03] rounded-xl border border-white/[0.06] backdrop-blur-sm">
        {[
          { key: 'all', label: 'Todas', count: timeline.length },
          { key: 'deliberate', label: 'Deliberadas', count: timeline.filter(e => e.was_deliberate === true).length },
          { key: 'not-deliberate', label: 'No delib.', count: timeline.filter(e => e.was_deliberate === false).length },
          { key: 'pending', label: 'Pendientes', count: timeline.filter(e => e.ai_fields_status === 'pending').length },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            aria-pressed={filter === tab.key}
            className={`flex-1 px-3 py-2.5 text-[10px] font-bold uppercase tracking-wider rounded-lg transition-all duration-300 relative overflow-hidden ${
              filter === tab.key
                ? 'bg-white/[0.1] text-white shadow-sm'
                : 'text-neutral-500 hover:text-neutral-300 hover:bg-white/[0.04]'
            }`}
          >
            {filter === tab.key && (
              <div className="absolute inset-0 bg-gradient-to-r from-green-500/10 to-transparent" />
            )}
            <span className="relative">
              {tab.label} <span className="opacity-40 ml-1">{tab.count}</span>
            </span>
          </button>
        ))}
      </div>

      {/* Entries */}
      <div className="space-y-3 stagger custom-scrollbar" style={{ maxHeight: '75vh', overflowY: 'auto', paddingRight: '4px' }}>
        {filteredTimeline.map((entry, index) => {
          const auditLog = parseAuditLog(entry);
          const isPending = entry.ai_fields_status === 'pending';
          const isDeliberate = entry.was_deliberate === true;
          const isNotDeliberate = entry.was_deliberate === false;
          const isOnboarding = entry.onboarding_mode === true;

          return (
            <div
              key={entry.id}
              className="card !p-0 relative overflow-hidden group/entry transition-all duration-500 hover:border-white/[0.1] hover:-translate-y-0.5 hover:shadow-2xl hover:shadow-black/30"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              {/* Animated status bar */}
              <div className={`absolute top-0 left-0 w-1 h-full rounded-l-2xl ${
                isPending ? 'bg-yellow-500' :
                isDeliberate ? 'bg-green-500' :
                isNotDeliberate ? 'bg-red-500' : 'bg-neutral-700'
              }`} />
              
              {isPending && (
                <div className="absolute top-0 left-0 w-full h-full">
                  <div className="absolute top-0 left-0 w-1 h-full bg-yellow-500 shimmer" style={{ animation: 'shimmer 1.5s infinite' }} />
                </div>
              )}

              {/* Hover gradient overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-green-500/[0.02] via-transparent to-transparent opacity-0 group-hover/entry:opacity-100 transition-opacity duration-500" />

              <div className="pl-5 pr-5 py-5 relative">
                {/* Header */}
                <div className="flex items-center justify-between gap-3 mb-4">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <span className="font-bold text-base text-white truncate">{entry.skill_name}</span>
                    {isPending && <span className="badge badge-pending text-[9px]">IA procesando</span>}
                    {isOnboarding && !isPending && <span className="badge badge-onboarding text-[9px]">Onboarding</span>}
                    {!isPending && isDeliberate && <span className="badge badge-deliberate text-[9px]">Deliberada</span>}
                    {!isPending && isNotDeliberate && <span className="badge badge-not-deliberate text-[9px]">No deliberada</span>}
                  </div>
                  <span className="text-[10px] text-neutral-600 whitespace-nowrap font-mono">
                    {new Date(entry.date).toLocaleString('es-AR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

                {/* Details */}
                <div className="bg-white/[0.02] rounded-xl p-4 text-sm space-y-2 border border-white/[0.04] transition-all duration-300 group-hover/entry:border-green-500/10">
                  <p className="text-neutral-300"><span className="text-neutral-500 text-[10px] uppercase tracking-wider mr-2 font-semibold">Práctica</span>{entry.what_i_practiced}</p>
                  <p className="text-neutral-300"><span className="text-neutral-500 text-[10px] uppercase tracking-wider mr-2 font-semibold">Error</span>{entry.micro_error_found}</p>
                  <div className="flex items-center gap-3 pt-2 text-[10px] text-neutral-500 uppercase tracking-wider">
                    <span className="flex items-center gap-1">⏱ {entry.duration_minutes} min</span>
                    <span className="w-px h-3 bg-white/[0.06]" />
                    <span>📊 Dif {entry.difficulty}/5</span>
                    <span className="w-px h-3 bg-white/[0.06]" />
                    <span>{entry.entry_mode === 'quick' ? '⚡ Rápido' : '📋 Completo'}</span>
                  </div>
                </div>

                {/* Audit Verdict */}
                {auditLog && !isPending && (
                  <div className="mt-4 pt-4 border-t border-white/[0.06]">
                    <div className="flex items-start gap-3">
                      <ScoreRing score={auditLog.score} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="text-[10px] font-bold uppercase tracking-[0.15em] text-neutral-500">Auditoría</h4>
                          <span className="text-[10px] text-neutral-600 font-mono">
                            Confianza: {(auditLog.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <p className="text-sm text-neutral-200 font-medium mb-1">{auditLog.verdict}</p>
                        <p className="text-xs text-neutral-500 leading-relaxed">{auditLog.reasoning}</p>
                        {auditLog.domain_specific_notes && (
                          <p className="text-xs text-neutral-600 mt-2 italic border-l-2 border-white/[0.08] pl-3">{auditLog.domain_specific_notes}</p>
                        )}
                        {auditLog.book_citations?.length > 0 && (
                          <div className="mt-3 space-y-2">
                            {auditLog.book_citations.map((cite, i) => (
                              <p key={i} className="text-[10px] text-green-400/80 bg-green-500/[0.06] rounded-lg px-3 py-2 border border-green-500/10 leading-relaxed hover:border-green-500/20 hover:bg-green-500/[0.08] transition-all duration-200 cursor-default">
                                📖 {cite}
                              </p>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Loading shimmer for pending */}
                {isPending && (
                  <div className="mt-4 space-y-2">
                    <div className="h-3 w-3/4 rounded-full bg-neutral-800 shimmer" />
                    <div className="h-3 w-1/2 rounded-full bg-neutral-800 shimmer" />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
