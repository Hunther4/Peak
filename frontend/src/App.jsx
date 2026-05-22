import { useEffect, useState, useCallback } from "react"
import { useStore } from "./store/store"
import SkillCard from "./components/SkillCard"
import Timeline from "./components/Timeline"
import SessionForm from "./components/SessionForm"
import BooksPanel from "./components/BooksPanel"
import AiModeToggle from "./components/AiModeToggle"
import ModelInfo from "./components/ModelInfo"
import MentalRepTimeline from "./components/MentalRepTimeline"
import ChallengeList from "./components/ChallengeList"
import { StatusIndicator } from "./components/StatusIndicator"
import AmbientParticles from "./components/AmbientParticles"
import Spotlight from "./components/Spotlight"
import { ToastProvider } from "./components/ui"

function App() {
  const { summary, loading, error, clearError, fetchSkills, fetchSummary, fetchMentalReps, fetchChallenges, fetchBooksStatus, fetchAiStatus } = useStore()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    fetchSkills()
    fetchSummary()
    fetchMentalReps()
    fetchChallenges()
    fetchBooksStatus()
    fetchAiStatus()
    setMounted(true)
  }, [])

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

  return (
    <ToastProvider>
      <div className="min-h-screen relative">
        {/* Ambient Background Effects */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden">
          <div className="absolute -top-[40%] -left-[20%] w-[60%] h-[60%] bg-green-500/[0.03] rounded-full blur-[120px]" style={{ animation: 'mesh-shift 15s ease-in-out infinite' }} />
          <div className="absolute -bottom-[30%] -right-[15%] w-[50%] h-[50%] bg-emerald-600/[0.02] rounded-full blur-[100px]" style={{ animation: 'mesh-shift 20s ease-in-out infinite reverse' }} />
          <div className="absolute top-[20%] right-[10%] w-[30%] h-[30%] bg-blue-500/[0.02] rounded-full blur-[80px]" style={{ animation: 'mesh-shift 18s ease-in-out infinite' }} />
          <div className="absolute bottom-[10%] left-[5%] w-[25%] h-[25%] bg-purple-500/[0.015] rounded-full blur-[90px]" style={{ animation: 'mesh-shift 22s ease-in-out infinite reverse' }} />
        </div>

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
                <p className="text-sm text-red-400">Error de conexión: {error}</p>
              </div>
              <button onClick={clearError} className="text-xs text-red-500/60 hover:text-red-400 transition-colors">
                Cerrar
              </button>
            </div>
          )}

          {/* Session Form - Full Width */}
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-9 h-9 rounded-xl bg-green-500/10 border border-green-500/20 flex items-center justify-center text-lg">
                ⚡
              </div>
              <h2 className="text-lg font-bold text-white">Nueva Sesión</h2>
              <div className="flex-1 h-px bg-gradient-to-r from-white/[0.06] to-transparent ml-4" />
            </div>
            <SessionForm />
          </section>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Left Column */}
            <div className="lg:col-span-5 space-y-8 stagger">
              {/* Skills */}
              <section>
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
                      <SkillCard key={s.skill.id} summary={s} />
                    ))}
                  </div>
                )}
              </section>

              {/* Challenges */}
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

              {/* Mental Reps */}
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

              {/* Books */}
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

              {/* Model Info */}
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
            </div>

            {/* Right Column: Timeline */}
            <div className="lg:col-span-7">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-9 h-9 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-lg">
                  📝
                </div>
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
