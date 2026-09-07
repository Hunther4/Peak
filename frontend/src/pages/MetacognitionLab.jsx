import { useState, useEffect } from "react"
import { useStore } from "../store/store"
import MentalRepTimeline from "../components/MentalRepTimeline"
import ChallengeList from "../components/ChallengeList"
import BooksPanel from "../components/BooksPanel"
import { ErrorBoundary } from "../components/ui/ErrorBoundary"
import { PageTransition } from "../components/ui/PageTransition"

export default function MetacognitionLab() {
  const {
    fetchMentalReps,
    fetchChallenges,
    fetchBooksStatus,
    timeline,
  } = useStore()

  const [activeTab, setActiveTab] = useState("mental") // mental | errors | rag

  useEffect(() => {
    fetchMentalReps()
    fetchChallenges()
    fetchBooksStatus()
  }, [])

  // Analyze micro-errors from recent timeline sessions
  const errorLogs = (timeline || [])
    .filter((s) => s.micro_error_found)
    .slice(0, 20)

  return (
    <PageTransition>
      <div className="space-y-8">
        {/* Header Hero */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 lg:p-8 rounded-3xl bg-white/[0.02] border border-white/[0.06] backdrop-blur-xl">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase font-bold px-2.5 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-400">
                Ericsson Deliberate Laboratory
              </span>
              <span className="text-xs text-neutral-400 font-medium">
                Metacognición & Base de Conocimiento
              </span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-black tracking-tight text-white">
              Laboratorio de Metacognición & RAG
            </h1>
            <p className="text-xs lg:text-sm text-neutral-400 leading-relaxed">
              La maestría no se logra acumulando horas vacías, sino refinando representaciones mentales cada vez más abstractas y analizando la anatomía exacta de cada fallo.
            </p>
          </div>

          {/* Navigation Pill Tabs */}
          <div className="flex items-center gap-1.5 p-1.5 rounded-2xl bg-neutral-900/80 border border-white/[0.08] shrink-0 self-start md:self-center">
            <button
              onClick={() => setActiveTab("mental")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                activeTab === "mental"
                  ? "bg-amber-500 text-black shadow-lg shadow-amber-500/20"
                  : "text-neutral-400 hover:text-white"
              }`}
            >
              🧠 Modelos Mentales
            </button>
            <button
              onClick={() => setActiveTab("errors")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                activeTab === "errors"
                  ? "bg-amber-500 text-black shadow-lg shadow-amber-500/20"
                  : "text-neutral-400 hover:text-white"
              }`}
            >
              🔍 Telemetría de Errores
            </button>
            <button
              onClick={() => setActiveTab("rag")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                activeTab === "rag"
                  ? "bg-amber-500 text-black shadow-lg shadow-amber-500/20"
                  : "text-neutral-400 hover:text-white"
              }`}
            >
              📚 Biblioteca Peak RAG
            </button>
          </div>
        </div>

        {/* Tab 1: Representaciones Mentales & Retos */}
        {activeTab === "mental" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div className="lg:col-span-7 space-y-6">
              <div className="p-6 rounded-3xl bg-white/[0.02] border border-white/[0.06]">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-xl">
                    🧠
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-white tracking-tight">
                      Evolución de Representaciones Mentales
                    </h2>
                    <p className="text-xs text-neutral-400">
                      Estructuras cognitivas internas auditadas (v1 $\to$ v2 $\to$ v3)
                    </p>
                  </div>
                </div>

                <ErrorBoundary fallbackMessage="Las representaciones mentales no pudieron cargarse.">
                  <MentalRepTimeline />
                </ErrorBoundary>
              </div>
            </div>

            <div className="lg:col-span-5 space-y-6">
              <div className="p-6 rounded-3xl bg-white/[0.02] border border-white/[0.06]">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-xl">
                    🧩
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-white tracking-tight">
                      Desafíos Deliberados Activos
                    </h2>
                    <p className="text-xs text-neutral-400">
                      Generados para someter tus modelos mentales a estrés
                    </p>
                  </div>
                </div>

                <ErrorBoundary fallbackMessage="Los desafíos no pudieron cargarse.">
                  <ChallengeList />
                </ErrorBoundary>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Telemetría de Errores & Micro-fallos */}
        {activeTab === "errors" && (
          <div className="space-y-6">
            <div className="p-6 lg:p-8 rounded-3xl bg-white/[0.02] border border-white/[0.06]">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-lg font-bold text-white tracking-tight">
                    Análisis de Micro-Errores (Ventana de Práctica)
                  </h2>
                  <p className="text-xs text-neutral-400 mt-1">
                    Clasificación inmediata: Aritmético vs Conceptual vs Descuido vs Timeout.
                  </p>
                </div>
                <span className="text-xs font-mono font-bold px-3 py-1 rounded-xl bg-white/[0.06] text-neutral-300">
                  {errorLogs.length} registros auditados
                </span>
              </div>

              {errorLogs.length === 0 ? (
                <div className="text-center py-12 text-neutral-500 text-sm">
                  No hay micro-errores registrados en tus últimas sesiones. ¡Excelente precisión!
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {errorLogs.map((s, idx) => (
                    <div
                      key={s.id || idx}
                      className="p-4 rounded-2xl bg-neutral-900/60 border border-white/[0.06] space-y-2 hover:border-amber-500/30 transition-all"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-mono text-neutral-400">
                          {s.created_at ? new Date(s.created_at).toLocaleDateString() : "Reciente"}
                        </span>
                        <span className="text-[10px] font-bold uppercase font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          {s.was_deliberate ? "Deliberada" : "Práctica"}
                        </span>
                      </div>

                      <p className="text-xs font-semibold text-white truncate">
                        {s.what_i_practiced}
                      </p>

                      <div className="p-2.5 rounded-xl bg-red-500/[0.08] border border-red-500/20 text-[11px] text-red-300 font-mono">
                        ⚠️ {s.micro_error_found}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 3: Biblioteca RAG Anders Ericsson */}
        {activeTab === "rag" && (
          <div className="space-y-6">
            <div className="p-6 lg:p-8 rounded-3xl bg-white/[0.02] border border-white/[0.06]">
              <div className="mb-6 space-y-1">
                <h2 className="text-lg font-bold text-white tracking-tight">
                  Biblioteca RAG: Libro Oficial "Peak"
                </h2>
                <p className="text-xs text-neutral-400">
                  Indexación semántica en ChromaDB del libro de Anders Ericsson & Robert Pool para sustentar las auditorías pedagógicas.
                </p>
              </div>

              <ErrorBoundary fallbackMessage="La biblioteca RAG no pudo cargarse.">
                <BooksPanel />
              </ErrorBoundary>
            </div>
          </div>
        )}
      </div>
    </PageTransition>
  )
}
