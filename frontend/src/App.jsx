import { useEffect, useState, useCallback } from "react"
import { useStore } from "./store/store"
import api from "./api/client"
import SkillCard from "./components/SkillCard"
import Timeline from "./components/Timeline"
import SessionForm from "./components/SessionForm"
import BooksPanel from "./components/BooksPanel"
import AiModeToggle from "./components/AiModeToggle"
import ModelInfo from "./components/ModelInfo"
import MentalRepTimeline from "./components/MentalRepTimeline"
import ChallengeList from "./components/ChallengeList"
import { StatusIndicator } from "./components/StatusIndicator"
import ProfileAvatar from "./components/ProfileAvatar"
import AmbientParticles from "./components/AmbientParticles"
import Spotlight from "./components/Spotlight"
import { AmbientBackground } from "./components/layout/AmbientBackground"
import { ToastProvider } from "./components/ui"
import WelcomeScreen from './components/WelcomeScreen'
import MemoryGame from './components/MemoryGame'
import MathThinkingGame from './components/MathThinkingGame'
import DualNBackGame from './components/DualNBackGame'
import IQPracticeGame from './components/IQPracticeGame'
import GuidedPractice from './components/GuidedPractice'

// Game route map — adding a new game = 1 line here + 1 component file
const GAME_ROUTES = {
  memory_number: { Component: MemoryGame, needsSkillId: true },
  problem_set: { Component: MathThinkingGame, needsSkillId: true },
  dual_n_back: { Component: DualNBackGame, needsSkillId: false },
  iq_practice: { Component: IQPracticeGame, needsSkillId: true },
  _guided: { Component: GuidedPractice, needsSkillId: true },
}

function App() {
  const { summary, loading, error, clearError, fetchSkills, fetchSummary, fetchTimeline, fetchMentalReps, fetchChallenges, fetchBooksStatus, fetchAiStatus, profile, profileLoading, fetchProfile } = useStore()
  const [mounted, setMounted] = useState(false)
  const [activeGame, setActiveGame] = useState(null) // { type: string, skillId: number | null }
  const [showSessionForm, setShowSessionForm] = useState(false)

  useEffect(() => {
    fetchProfile()
    fetchSkills()
    fetchSummary()
    fetchMentalReps()
    fetchChallenges()
    fetchBooksStatus()
    fetchAiStatus()
    setMounted(true)
  }, [])

  // Clear all practice data
  const [clearing, setClearing] = useState(false)
  const handleClearData = useCallback(async () => {
    if (!window.confirm("¿Eliminar todos los registros de práctica? Esto incluye sesiones, juegos y evaluaciones. No se puede deshacer.")) return
    setClearing(true)
    try {
      await api.sessions.clearAll()
      fetchSkills()
      fetchSummary()
      fetchTimeline()
      fetchMentalReps()
      fetchChallenges()
    } catch (e) {
      console.error("Error al limpiar registros:", e)
    } finally {
      setClearing(false)
    }
  }, [fetchSkills, fetchSummary, fetchTimeline, fetchMentalReps, fetchChallenges])

  // Card spotlight effect
  const handleCardMouseMove = useCallback((e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width) * 100
    const y = ((e.clientY - rect.top) / rect.height) * 100
    e.currentTarget.style.setProperty('--mouse-x', `${x}%`)
    e.currentTarget.style.setProperty('--mouse-y', `${y}%`)
  }, [])

  useEffect(() => {
    const cards = document.querySelectorAll('.card')
    cards.forEach(card => {
      card.addEventListener('mousemove', handleCardMouseMove)
    })
    return () => {
      cards.forEach(card => {
        card.removeEventListener('mousemove', handleCardMouseMove)
      })
    }
  }, [mounted, handleCardMouseMove])

  // Unified practice routing
  const handlePractice = useCallback((skillId, skillType) => {
    const route = GAME_ROUTES[skillType]
    if (route) {
      setActiveGame({ type: skillType, skillId: route.needsSkillId ? skillId : null })
    } else {
      setActiveGame({ type: "_guided", skillId })
    }
  }, [])

  // Single close handler — replaces 5 identical callbacks
  const handleCloseGame = useCallback(() => {
    setActiveGame(null)
    fetchSummary()
    fetchTimeline()
  }, [fetchSummary, fetchTimeline])

  // Profile guard — show spinner while loading, welcome if no profile
  if (profileLoading) {
    return (
      <div className="min-h-screen bg-neutral-950 flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-neutral-700 border-t-green-500 rounded-full animate-spin" />
      </div>
    )
  }

  if (!profile) {
    return <WelcomeScreen />
  }

  // Game overlay — render active game via route map
  if (activeGame) {
    const route = GAME_ROUTES[activeGame.type]
    if (route) {
      const { Component } = route
      return (
        <Component
          skillId={activeGame.skillId}
          onClose={handleCloseGame}
        />
      )
    }
  }

  return (
    <ToastProvider>
      <div className="min-h-screen relative">
        {/* Ambient Background Effects */}
        <AmbientBackground />

        {/* Particles & Spotlight */}
        <AmbientParticles />
        <Spotlight />

        {/* Navbar */}
        <header className="sticky top-0 z-50 border-b border-white/[0.06] glass-panel" style={{ backdropFilter: 'blur(24px) saturate(1.8)' }}>
          <div className="max-w-[1400px] mx-auto flex items-center justify-between px-8 py-4">
            {/* Logo */}
            <div className="flex items-center gap-4">
              <div className="relative group cursor-pointer" role="button" tabIndex={0} aria-label="Peak inicio">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-black font-black text-lg shadow-lg shadow-green-500/25 group-hover:shadow-green-500/40 transition-all duration-300 group-hover:scale-105">
                  P
                </div>
                <div className="absolute -inset-1 rounded-xl bg-gradient-to-br from-green-400/20 to-emerald-600/20 blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </div>
              <div>
                <h1 className="text-xl font-black tracking-tight text-white leading-none">
                  Peak <span className="text-green-400/80 font-semibold">practice</span>
                </h1>
                <p className="text-[10px] uppercase tracking-[0.25em] text-neutral-500 font-medium mt-0.5">
                  Práctica deliberada 🎯
                </p>
              </div>
            </div>

            {/* Right Controls */}
            <div className="flex items-center gap-4">
              <StatusIndicator />
              <div className="w-px h-6 bg-white/[0.06]" />
              <AiModeToggle />
              <button
                onClick={handleClearData}
                disabled={clearing}
                className="text-[11px] text-neutral-600 hover:text-red-400 transition-colors uppercase tracking-wider font-medium disabled:opacity-40"
                title="Limpiar todos los registros de práctica"
              >
                {clearing ? "..." : "Limpiar"}
              </button>
              <ProfileAvatar />
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-[1400px] mx-auto px-6 lg:px-8 py-8 relative z-10">
          {/* Error Banner */}
          {error && (
            <div className="mb-8 p-4 bg-red-500/[0.08] border border-red-500/20 rounded-2xl flex items-center justify-between" style={{ animation: 'fadeInUp 0.3s ease-out' }}>
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center text-red-400 text-sm">✕</span>
                <p className="text-sm text-red-400">Error de conexión: {typeof error === 'string' ? error : JSON.stringify(error)}</p>
              </div>
              <button onClick={clearError} className="text-xs text-red-500/60 hover:text-red-400 transition-colors">
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
            
            {summary?.skills?.length === 0 ? (
              <div className="card text-center py-12">
                <div className="w-16 h-16 rounded-2xl bg-neutral-800/50 flex items-center justify-center text-2xl mx-auto mb-4">🎯</div>
                <p className="text-sm text-neutral-400 mb-2">No hay skills todavía</p>
                <p className="text-xs text-neutral-600">
                  Ejecutá <code className="text-green-400 bg-green-500/10 px-2 py-1 rounded">python seed.py</code> para empezar
                </p>
              </div>
            ) : (
              <div className="space-y-4 stagger">
                {summary?.skills?.map((s) => (
                  <SkillCard key={s.skill.id} summary={s} onPractice={handlePractice} />
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
                <span className="text-neutral-600 group-hover:text-neutral-400 transition-colors">▾</span>
              </button>
            )}
          </section>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Left Column */}
            <div className="lg:col-span-5 space-y-8 stagger">
              <section>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-lg">🧩</div>
                  <h2 className="text-lg font-bold text-white">Desafíos</h2>
                  <div className="flex-1 h-px bg-gradient-to-r from-white/[0.06] to-transparent ml-4" />
                </div>
                <ChallengeList />
              </section>

              <section>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-lg">🧠</div>
                  <h2 className="text-lg font-bold text-white">Representaciones Mentales</h2>
                  <div className="flex-1 h-px bg-gradient-to-r from-white/[0.06] to-transparent ml-4" />
                </div>
                <MentalRepTimeline />
              </section>

              <section>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-lg">📚</div>
                  <h2 className="text-lg font-bold text-white">Biblioteca RAG</h2>
                  <div className="flex-1 h-px bg-gradient-to-r from-white/[0.06] to-transparent ml-4" />
                </div>
                <BooksPanel />
              </section>

              <section>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-lg">🤖</div>
                  <h2 className="text-lg font-bold text-white">Motor de IA</h2>
                  <div className="flex-1 h-px bg-gradient-to-r from-white/[0.06] to-transparent ml-4" />
                </div>
                <ModelInfo />
              </section>
            </div>

            {/* Right Column: Timeline */}
            <div className="lg:col-span-7">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-9 h-9 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-lg">📝</div>
                <h2 className="text-lg font-bold text-white">Registro de Auditoría</h2>
                <div className="flex-1 h-px bg-gradient-to-r from-white/[0.06] to-transparent ml-4" />
              </div>
              <Timeline />
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t border-white/[0.06] mt-16">
          <div className="max-w-[1400px] mx-auto px-8 py-6 flex items-center justify-between">
            <p className="text-[10px] text-neutral-600 uppercase tracking-widest">
              Peak Practice · Práctica Deliberada 🚀
            </p>
            <p className="text-[10px] text-neutral-700 font-mono">
              v4.0
            </p>
          </div>
        </footer>
      </div>
    </ToastProvider>
  )
}

export default App