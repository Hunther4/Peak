import { useState } from 'react';
import { useStore } from '../store/store';
import { useToast, Modal, Spinner } from './ui';

export default function MentalRepTimeline() {
  const { mentalReps, summary, generateRep, generatingRep, acceptRep } = useStore()
  const toast = useToast()

  const selectedSkill = summary?.skills?.[0]
  const skillId = selectedSkill?.skill?.id

  const [pendingRep, setPendingRep] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleGenerate = async () => {
    if (!skillId) {
      toast.warning('Seleccioná una skill primero.');
      return;
    }
    try {
      const result = await generateRep(skillId)
      if (result?.generated) {
        setPendingRep(result)
        setIsModalOpen(true)
      } else {
        toast.warning(result?.message || 'No se pudo generar la representación.')
      }
    } catch (e) {
      toast.error("Error generando MentalRep: " + e.message)
    }
  }

  const handleAccept = async () => {
    if (!pendingRep || !skillId) return
    try {
      await acceptRep(pendingRep.prev_rep_id || 0, pendingRep.description, skillId)
      toast.success('Representación mental guardada.')
      setIsModalOpen(false)
      setPendingRep(null)
    } catch (e) {
      toast.error("Error guardando: " + e.message)
    }
  }

  return (
    <>
      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="section-title !mb-0">Representaciones Mentales</h3>
          <button
            onClick={handleGenerate}
            disabled={generatingRep || !skillId}
            className="btn btn-ghost text-[10px] px-3 py-1.5 flex items-center gap-2"
          >
            {generatingRep ? (
              <>
                <Spinner size="sm" />
                Generando...
              </>
            ) : (
              <>🧠 Nueva</>
            )}
          </button>
        </div>

        {mentalReps.length === 0 ? (
          <div className="text-center py-6">
            <div className="w-12 h-12 rounded-xl bg-neutral-800/50 flex items-center justify-center text-xl mx-auto mb-3">🧠</div>
            <p className="text-xs text-neutral-500 leading-relaxed">
              Acumulá sesiones para que la IA detecte cambios en tu comprensión.
            </p>
          </div>
        ) : (
          <div className="space-y-4 relative">
            {/* Vertical timeline line with gradient */}
            <div className="absolute left-[7px] top-2 bottom-2 w-px bg-gradient-to-b from-green-500/40 via-amber-500/20 to-transparent" />

            {mentalReps.map((rep, index) => (
              <div key={rep.id} className="relative pl-7 group/rep" style={{ animation: `fadeInUp 0.5s ease-out ${index * 0.1}s both` }}>
                {/* Timeline dot with pulse effect */}
                <div className={`absolute left-0 top-1.5 w-[15px] h-[15px] rounded-full border-2 transition-all duration-300 ${
                  index === 0 
                    ? 'border-green-500 bg-green-500/20 shadow-glow-green' 
                    : 'border-neutral-700 bg-neutral-900 group-hover/rep:border-amber-500/30'
                }`}>
                  {index === 0 && (
                    <div className="absolute inset-0 rounded-full bg-green-500/20 animate-ping" style={{ animationDuration: '2s' }} />
                  )}
                </div>

                <div className="pb-1 bg-white/[0.02] rounded-xl p-4 border border-white/[0.06] transition-all duration-300 hover:border-green-500/20 hover:bg-white/[0.03] hover:translate-x-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-[10px] font-bold text-green-500/70 bg-green-500/[0.06] px-2 py-0.5 rounded-md border border-green-500/10">
                      v{rep.version}
                    </span>
                    <span className="text-[10px] text-neutral-600 font-mono">
                      {new Date(rep.created_at).toLocaleDateString()}
                    </span>
                    <span className="text-[10px] text-neutral-700">· {rep.trigger}</span>
                  </div>
                  <p className="text-sm text-neutral-300 leading-relaxed">{rep.description}</p>
                  {rep.previous_summary && rep.version > 1 && (
                    <details className="mt-3 group/details">
                      <summary className="text-[10px] text-neutral-600 cursor-pointer hover:text-neutral-400 transition-colors uppercase tracking-wider font-bold">
                        Ver v{rep.version - 1}
                      </summary>
                      <p className="text-xs text-neutral-600 mt-2 italic pl-3 border-l-2 border-white/[0.06] leading-relaxed">
                        {rep.previous_summary}
                      </p>
                    </details>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal for accepting a new Mental Rep */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => { setIsModalOpen(false); setPendingRep(null); }}
        title="Nueva Representación Mental"
        onConfirm={handleAccept}
        confirmText="Aceptar y guardar"
      >
        {pendingRep && (
          <div className="space-y-4">
            <p className="text-neutral-200 leading-relaxed text-base">{pendingRep.description}</p>
            
            <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-4 space-y-2">
              <p className="text-sm text-neutral-500 leading-relaxed">{pendingRep.reasoning}</p>
            </div>

            <div className="flex items-center gap-2">
              {pendingRep.is_real_shift ? (
                <span className="badge badge-deliberate">✅ Cambio real detectado</span>
              ) : (
                <span className="badge bg-yellow-500/10 text-yellow-400 border-yellow-500/20">⚠ Cambio menor</span>
              )}
            </div>

            {pendingRep.key_insight && (
              <div className="border-l-2 border-green-500/30 pl-3">
                <p className="text-[10px] text-neutral-600 uppercase tracking-wider mb-1">Insight clave</p>
                <p className="text-sm text-green-400/80 leading-relaxed">{pendingRep.key_insight}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </>
  )
}
