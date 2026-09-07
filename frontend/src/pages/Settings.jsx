import { useState, useCallback } from "react"
import { Link } from "react-router"
import { useStore } from "../store/store"
import { useToast } from "../components/ui/Toast"
import AiModeToggle from "../components/AiModeToggle"
import ModelInfo from "../components/ModelInfo"
import ProfileAvatar from "../components/ProfileAvatar"
import { PageTransition } from "../components/ui/PageTransition"

export default function Settings() {
  const { fetchSkills, fetchSummary, fetchTimeline, fetchMentalReps, fetchChallenges } = useStore()
  const toast = useToast()
  const [clearing, setClearing] = useState(false)
  const [showClearConfirm, setShowClearConfirm] = useState(false)
  const [showClearFinal, setShowClearFinal] = useState(false)

  const handleClearData = useCallback(async () => {
    setShowClearConfirm(false)
    setShowClearFinal(false)
    setClearing(true)
    try {
      const { default: api } = await import("../api/client")
      await api.sessions.clearAll()
      fetchSkills()
      fetchSummary()
      fetchTimeline()
      fetchMentalReps()
      fetchChallenges()
      toast.success("Datos limpiados correctamente.")
    } catch (e) {
      console.error("Error al limpiar:", e)
      toast.error("Error al limpiar datos.")
    } finally {
      setClearing(false)
    }
  }, [fetchSkills, fetchSummary, fetchTimeline, fetchMentalReps, fetchChallenges, toast])

  return (
    <PageTransition>
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-white">Ajustes</h1>
        <p className="text-sm text-neutral-500 mt-1">Configuración de tu cuenta y preferencias</p>
      </div>

      {/* Profile */}
      <section className="card space-y-4">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Perfil</h2>
        <ProfileAvatar />
      </section>

      {/* AI Mode */}
      <section className="card space-y-4">
        <h2 className="text-sm font-bold text-white uppercase tracking-wider">Motor de IA</h2>
        <p className="text-xs text-neutral-500">Elegí entre procesamiento local o en la nube.</p>
        <AiModeToggle />
        <div className="pt-2">
          <ModelInfo />
        </div>
      </section>

      {/* Danger Zone */}
      <section className="card space-y-4 border-red-500/20">
        <h2 className="text-sm font-bold text-red-400 uppercase tracking-wider">Zona de peligro</h2>
        <p className="text-xs text-neutral-500">
          Borrar todos los registros de práctica. Las skills, el perfil y la configuración se mantienen.
        </p>
        <button
          onClick={() => setShowClearConfirm(true)}
          disabled={clearing}
          className="px-4 py-2 rounded-xl text-xs font-bold text-red-400 bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 hover:border-red-500/30 transition-all duration-200 disabled:opacity-40"
        >
          {clearing ? "Borrando..." : "Borrar todos los datos de práctica"}
        </button>
      </section>

      {/* Clear confirm modal — step 1 */}
      {showClearConfirm && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center p-4" onClick={() => setShowClearConfirm(false)}>
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
          <div
            role="dialog"
            aria-modal="true"
            className="relative bg-neutral-900/95 border border-white/[0.08] rounded-2xl p-6 max-w-sm w-full shadow-2xl"
            onClick={(e) => e.stopPropagation()}
            style={{ animation: "fadeInUp 0.3s cubic-bezier(0.4, 0, 0.2, 1)" }}
          >
            <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500" />
              ¿Eliminar datos?
            </h3>
            <p className="text-sm text-neutral-400 mb-6">
              Se borrarán todas las sesiones, juegos y evaluaciones. No se puede deshacer.
            </p>
            <div className="flex items-center justify-end gap-3">
              <button onClick={() => setShowClearConfirm(false)} className="btn btn-ghost text-xs">
                Cancelar
              </button>
              <button onClick={() => { setShowClearConfirm(false); setShowClearFinal(true) }} className="btn btn-ghost text-xs text-red-400 border-red-500/30 hover:bg-red-500/20">
                Continuar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Clear confirm modal — step 2 (final) */}
      {showClearFinal && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center p-4" onClick={() => setShowClearFinal(false)}>
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
          <div
            role="dialog"
            aria-modal="true"
            className="relative bg-neutral-900/95 border border-white/[0.08] rounded-2xl p-6 max-w-sm w-full shadow-2xl"
            onClick={(e) => e.stopPropagation()}
            style={{ animation: "fadeInUp 0.3s cubic-bezier(0.4, 0, 0.2, 1)" }}
          >
            <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500" />
              ¿Estás seguro?
            </h3>
            <p className="text-sm text-neutral-400 mb-6">
              Esta acción es <span className="text-red-400 font-bold">irreversible</span>. Todos los datos de práctica se perderán.
            </p>
            <div className="flex items-center justify-end gap-3">
              <button onClick={() => setShowClearFinal(false)} className="btn btn-ghost text-xs">
                Cancelar
              </button>
              <button onClick={handleClearData} className="btn text-xs text-red-400 bg-red-500/20 border border-red-500/30 hover:bg-red-500/30">
                Sí, borrar todo
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Back */}
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-sm text-neutral-500 hover:text-white transition-colors"
      >
        ← Volver al panel
      </Link>
    </div>
    </PageTransition>
  )
}
