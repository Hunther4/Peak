import { useState } from 'react';
import { useStore } from '../store/store';
import { Spinner, useToast } from './ui';

export default function ChallengeList() {
  const {
    challenges, summary,
    generateChallenge, generatingChallenge,
    completeChallenge, fetchChallenges,
  } = useStore()
  const toast = useToast()

  const selectedSkill = summary?.skills?.[0]
  const skillId = selectedSkill?.skill?.id
  const activeChallenges = challenges.filter((c) => !c.completed)
  const completedChallenges = challenges.filter((c) => c.completed)
  const [hoveredId, setHoveredId] = useState(null)

  const handleGenerate = async () => {
    if (!skillId) {
      toast.warning('Seleccioná una skill primero.');
      return;
    }
    try {
      const result = await generateChallenge(skillId)
      if (result?.generated) {
        fetchChallenges(skillId)
      }
    } catch (e) {
      console.error("Error generando challenge:", e.message)
    }
  }

  const handleComplete = async (id) => {
    try {
      await completeChallenge(id, true)
    } catch (e) {
      console.error("Error completando challenge:", e.message)
    }
  }

  return (
    <div className="card space-y-4">
      {/* Top accent line */}
      <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-amber-500/30 to-transparent rounded-full" />
      
      <div className="flex items-center justify-between">
        <h3 className="section-title !mb-0">Desafíos</h3>
        <button
          onClick={handleGenerate}
          disabled={generatingChallenge || !skillId}
          className="btn btn-ghost text-[10px] px-3 py-1.5 flex items-center gap-2 relative overflow-hidden group"
        >
          {generatingChallenge ? (
            <>
              <Spinner size="sm" />
              Generando...
            </>
          ) : (
            <>🎯 Nuevo</>
          )}
          {/* Hover glow effect */}
          <div className="absolute inset-0 bg-amber-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </button>
      </div>

      {challenges.length === 0 ? (
        <div className="text-center py-6">
          <div className="w-12 h-12 rounded-xl bg-neutral-800/50 flex items-center justify-center text-xl mx-auto mb-3">🎯</div>
          <p className="text-xs text-neutral-500 leading-relaxed">
            La IA genera desafíos concretos después de cada sesión deliberada.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {activeChallenges.map((c, index) => (
            <div
              key={c.id}
              className="group relative flex items-start gap-3 p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-amber-500/20 hover:bg-white/[0.03] transition-all duration-300 cursor-pointer overflow-hidden"
              onMouseEnter={() => setHoveredId(c.id)}
              onMouseLeave={() => setHoveredId(null)}
              style={{ 
                animation: `fadeInUp 0.4s ease-out ${index * 0.1}s both`,
                transform: hoveredId === c.id ? 'translateX(2px)' : 'none'
              }}
            >
              {/* Hover gradient overlay */}
              {hoveredId === c.id && (
                <div className="absolute inset-0 bg-gradient-to-r from-amber-500/[0.03] to-transparent pointer-events-none" />
              )}
              
              <button
                onClick={() => handleComplete(c.id)}
                className="w-6 h-6 mt-0.5 rounded-lg border-2 border-neutral-700 hover:border-amber-500 hover:bg-amber-500/10 transition-all duration-300 shrink-0 flex items-center justify-center relative overflow-hidden group/checkbox z-10"
                title="Completar"
              >
                <div className="absolute inset-0 bg-amber-500/20 opacity-0 group-hover/checkbox:opacity-100 transition-opacity duration-300" />
              </button>
              
              <div className="flex-1 min-w-0 relative z-10">
                <p className="text-sm text-neutral-300 leading-relaxed group-hover:text-white transition-colors duration-300">
                  {c.description}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-[10px] text-neutral-600 font-mono">
                    {"●".repeat(c.difficulty_target)}{"○".repeat(5 - c.difficulty_target)}
                  </span>
                  <span className="text-[10px] text-neutral-700">
                    {new Date(c.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          ))}

          {completedChallenges.length > 0 && (
            <details className="mt-3 group/details">
              <summary className="text-[10px] text-neutral-600 cursor-pointer hover:text-neutral-400 transition-colors uppercase tracking-wider font-bold flex items-center gap-2">
                <span className="w-4 h-px bg-neutral-800" />
                Completados ({completedChallenges.length})
                <span className="flex-1 h-px bg-neutral-800" />
              </summary>
              <div className="mt-3 space-y-2">
                {completedChallenges.map((c) => (
                  <div key={c.id} className="flex items-start gap-3 p-3 rounded-lg bg-white/[0.01] border border-white/[0.03] hover:border-green-500/10 hover:bg-white/[0.02] transition-all duration-200">
                    <span className="w-6 h-6 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center justify-center text-green-500 text-[10px] shrink-0 mt-0.5">✓</span>
                    <div>
                      <p className="text-xs text-neutral-600 line-through">{c.description}</p>
                      <p className="text-[10px] text-neutral-800 mt-0.5 font-mono">
                        {c.completed_at ? new Date(c.completed_at).toLocaleDateString() : ""}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}
    </div>
  )
}
