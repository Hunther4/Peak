import { useEffect, useState, useCallback } from "react"
import { useNavigate } from "react-router"
import { useStore } from "../store/store"
import HeroStats from "../components/HeroStats"
import QuickActions from "../components/QuickActions"
import SkillGroup from "../components/SkillGroup"
import SessionForm from "../components/SessionForm"
import Timeline from "../components/Timeline"
import ChallengeList from "../components/ChallengeList"
import MentalRepTimeline from "../components/MentalRepTimeline"
import BooksPanel from "../components/BooksPanel"
import ModelInfo from "../components/ModelInfo"
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
    fetchMentalReps,
    fetchChallenges,
    fetchBooksStatus,
    fetchAiStatus,
  } = useStore()
  const [showSessionForm, setShowSessionForm] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetchSkills()
    fetchSummary()
    fetchTimeline()
    fetchMentalReps()
    fetchChallenges()
    fetchBooksStatus()
    fetchAiStatus()
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
      {/* Hero Stats — skeleton while loading */}
      {isLoading ? <SkeletonHero /> : <HeroStats />}

      {/* Quick Actions */}
      <QuickActions />

      {/* Error Banner */}
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

      {/* Skills Section */}
      <section className="mb-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-lg">
            🎯
          </div>
          <h2 className="text-lg font-bold text-white">Tus Skills</h2>
          {loading && (
            <div className="flex items-center gap-2 ml-auto">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-ping" />
              <span className="text-[10px] text-green-500/70 uppercase tracking-wider">Sync</span>
            </div>
          )}
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
            <p className="text-xs text-neutral-600">
              Ejecutá{" "}
              <code className="text-green-400 bg-green-500/10 px-2 py-1 rounded">
                python seed.py
              </code>{" "}
              para empezar
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 stagger">
            {groupedSummary?.map((group) => (
              <SkillGroup key={group.skill.id} group={group} onPractice={handlePractice} />
            ))}
          </div>
        )}
      </section>

      {/* Session Form — collapsed by default */}
      <section className="mb-8">
        {showSessionForm ? (
          <div className="relative">
            <SessionForm />
            <button
              onClick={() => setShowSessionForm(false)}
              className="mt-2 w-full py-2 text-[11px] text-neutral-500 hover:text-neutral-300 transition-colors uppercase tracking-wider"
            >
              ▴ Ocultar formulario
            </button>
          </div>
        ) : (
          <button
            onClick={() => setShowSessionForm(true)}
            className="card w-full py-4 px-5 flex items-center justify-between hover:border-green-500/20 transition-all duration-200 group"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center justify-center text-sm">
                +
              </div>
              <span className="text-sm font-medium text-neutral-400 group-hover:text-white transition-colors">
                Registro manual
              </span>
            </div>
            <span className="text-neutral-600 group-hover:text-neutral-400 transition-colors">
              ▾
            </span>
          </button>
        )}
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column — each section wrapped in ErrorBoundary */}
        <div className="lg:col-span-5 space-y-8 stagger">
          <ErrorBoundary fallbackMessage="Los desafíos no pudieron cargarse.">
            <section>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-lg">
                  🧩
                </div>
                <h2 className="text-lg font-bold text-white">Desafíos</h2>
                <div className="flex-1 h-px bg-gradient-to-r from-white/[0.06] to-transparent ml-4" />
              </div>
              <ChallengeList />
            </section>
          </ErrorBoundary>

          <ErrorBoundary fallbackMessage="Las representaciones mentales no pudieron cargarse.">
            <section>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-lg">
                  🧠
                </div>
                <h2 className="text-lg font-bold text-white">Representaciones Mentales</h2>
                <div className="flex-1 h-px bg-gradient-to-r from-white/[0.06] to-transparent ml-4" />
              </div>
              <MentalRepTimeline />
            </section>
          </ErrorBoundary>

          <ErrorBoundary fallbackMessage="La biblioteca RAG no pudo cargarse.">
            <section>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-lg">
                  📚
                </div>
                <h2 className="text-lg font-bold text-white">Biblioteca RAG</h2>
                <div className="flex-1 h-px bg-gradient-to-r from-white/[0.06] to-transparent ml-4" />
              </div>
              <BooksPanel />
            </section>
          </ErrorBoundary>

          <ErrorBoundary fallbackMessage="El motor de IA no pudo cargarse.">
            <section>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-lg">
                  🤖
                </div>
                <h2 className="text-lg font-bold text-white">Motor de IA</h2>
                <div className="flex-1 h-px bg-gradient-to-r from-white/[0.06] to-transparent ml-4" />
              </div>
              <ModelInfo />
            </section>
          </ErrorBoundary>
        </div>

        {/* Right Column: Timeline — with skeleton and error boundary */}
        <div className="lg:col-span-7">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-9 h-9 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-lg">
              📝
            </div>
            <h2 className="text-lg font-bold text-white">Registro de Auditoría</h2>
            <div className="flex-1 h-px bg-gradient-to-r from-white/[0.06] to-transparent ml-4" />
          </div>
          <ErrorBoundary fallbackMessage="El registro de auditoría no pudo cargarse.">
            <Timeline />
          </ErrorBoundary>
        </div>
      </div>
    </PageTransition>
  )
}
