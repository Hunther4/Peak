import { useEffect, useState, useCallback } from "react"
import { useNavigate } from "react-router"
import { useStore } from "../store/store"
import DeliberatePracticeHero from "../components/dashboard/DeliberatePracticeHero"
import OptimalDailyAction from "../components/dashboard/OptimalDailyAction"
import DualProgressRadar from "../components/dashboard/DualProgressRadar"
import SkillGroup from "../components/SkillGroup"
import SessionForm from "../components/SessionForm"
import Timeline from "../components/Timeline"
import ChallengeList from "../components/ChallengeList"
import { SkeletonHero, SkeletonCard } from "../components/ui/Skeleton"
import { ErrorBoundary } from "../components/ui/ErrorBoundary"
import { PageTransition } from "../components/ui/PageTransition"

export default function Dashboard() {
  const {
    groupedSummary,
    loading,
    error,
    clearError,
    fetchSkills,
    fetchSummary,
    fetchTimeline,
    fetchChallenges,
    fetchPaesSubtopics,
  } = useStore()
  const [showSessionForm, setShowSessionForm] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetchSkills()
    fetchSummary()
    fetchTimeline()
    fetchChallenges()
    if (fetchPaesSubtopics) {
      fetchPaesSubtopics()
    }
  }, [])

  const handlePractice = useCallback(
    (skillId, skillType) => {
      navigate(`/practice/${skillType}?skillId=${skillId}`)
    },
    [navigate]
  )

  const isLoading = loading && !groupedSummary?.length

  return (
    <PageTransition>
      {/* 1. Deliberate Practice Hero & Plateau Alert */}
      {isLoading ? <SkeletonHero /> : <DeliberatePracticeHero />}

      {/* 2. Optimal Daily Action (Algorithmic ZDP + FSRS Recommendation) */}
      <OptimalDailyAction />

      {/* 3. Dual Progress Radar: PAES 100-1000 DEMRE vs Cognitive Foundations */}
      <DualProgressRadar />

      {/* Error Banner if any */}
      {error && (
        <div
          className="mb-8 p-4 bg-red-500/[0.08] border border-red-500/20 rounded-2xl flex items-center justify-between"
          style={{ animation: "fadeInUp 0.3s ease-out" }}
        >
          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center text-red-400 text-sm">
              ✕
            </span>
            <p className="text-sm text-red-400">
              Error de conexión: {typeof error === "string" ? error : JSON.stringify(error)}
            </p>
          </div>
          <button
            onClick={clearError}
            className="text-xs text-red-500/60 hover:text-red-400 transition-colors"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* 4. Active Skills Section */}
      <section className="mb-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-lg">
            🎯
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">Tus Skills</h2>
            <p className="text-xs text-neutral-400">Progreso individual y subhabilidades activas</p>
          </div>
        </div>

        {isLoading ? (
          <div className="space-y-6">
            <SkeletonCard />
            <SkeletonCard />
          </div>
        ) : groupedSummary?.length === 0 ? (
          <div className="card text-center py-12">
            <div className="w-16 h-16 rounded-2xl bg-neutral-800/50 flex items-center justify-center text-2xl mx-auto mb-4">
              🎯
            </div>
            <p className="text-sm text-neutral-400 mb-2">No hay skills todavía</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 stagger">
            {groupedSummary?.map((group) => (
              <SkillGroup key={group.skill.id} group={group} onPractice={handlePractice} />
            ))}
          </div>
        )}
      </section>

      {/* Manual Session Section */}
      <section className="mb-8">
        {showSessionForm ? (
          <div className="p-4 rounded-3xl bg-neutral-900/60 border border-white/[0.08] backdrop-blur-xl">
            <SessionForm onSaved={() => setShowSessionForm(false)} />
            <button
              onClick={() => setShowSessionForm(false)}
              className="mt-2 w-full py-2 text-[11px] text-neutral-500 hover:text-neutral-300 transition-colors uppercase tracking-wider cursor-pointer"
            >
              ▴ Ocultar formulario
            </button>
          </div>
        ) : (
          <button
            onClick={() => setShowSessionForm(true)}
            className="w-full py-3.5 px-4 rounded-2xl border border-dashed border-white/[0.08] hover:border-white/[0.2] bg-white/[0.01] hover:bg-white/[0.03] text-neutral-400 hover:text-white transition-all flex items-center justify-center gap-2 text-xs font-semibold cursor-pointer"
          >
            <span>+</span>
            <span>Registro manual</span>
          </button>
        )}
      </section>

      {/* 5. Two-column layout: Desafíos Activos & Auditoría Ericsson */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Active AI Challenges */}
        <div className="lg:col-span-5 space-y-6">
          <ErrorBoundary fallbackMessage="Los desafíos no pudieron cargarse.">
            <div className="p-6 rounded-3xl bg-white/[0.02] border border-white/[0.06]">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-lg">
                  🧩
                </div>
                <div>
                  <h3 className="text-base font-bold text-white tracking-tight">Desafíos Deliberados</h3>
                  <p className="text-xs text-neutral-400">Micro-metas generadas por IA</p>
                </div>
              </div>
              <ChallengeList />
            </div>
          </ErrorBoundary>
        </div>

        {/* Right Column: Deliberate Practice Audit Timeline */}
        <div className="lg:col-span-7">
          <ErrorBoundary fallbackMessage="El registro de auditoría no pudo cargarse.">
            <div className="p-6 rounded-3xl bg-white/[0.02] border border-white/[0.06]">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-lg">
                  📋
                </div>
                <div>
                  <h3 className="text-base font-bold text-white tracking-tight">Registro de Auditoría</h3>
                  <p className="text-xs text-neutral-400">Veredictos de Anders Ericsson & detección de errores</p>
                </div>
              </div>
              <Timeline />
            </div>
          </ErrorBoundary>
        </div>
      </div>
    </PageTransition>
  )
}
