import React, { useEffect, useState } from "react"
import { useStore } from "../store/store"
import { FsrsStatusWidget } from "../components/paes/FsrsStatusWidget"
import { PaesQuestionCard } from "../components/paes/PaesQuestionCard"
import { SocraticTutorDrawer } from "../components/paes/SocraticTutorDrawer"
import { MathRenderer } from "../components/paes/MathRenderer"
import { api } from "../api/client"

export default function PaesStudy() {
  const {
    paesSessionId,
    paesSubtopic,
    paesQuestions,
    paesCurrentIndex,
    paesActiveQuestion,
    paesSelectedOption,
    paesConfidence,
    paesLastResult,
    paesFsrsStatus,
    paesSubtopicsList,
    paesSocraticHints,
    paesLoading,
    paesError,
    fetchPaesFsrsStatus,
    fetchPaesSubtopics,
    startPaesSession,
    selectPaesOption,
    setPaesConfidence,
    submitPaesAttempt,
    nextPaesQuestion,
    requestSocraticHint,
    resetPaesSession,
  } = useStore()

  const [scoreEstimate, setScoreEstimate] = useState(null)
  const [activeTab, setActiveTab] = useState("practice") // practice | curriculum | plan

  useEffect(() => {
    fetchPaesFsrsStatus()
    fetchPaesSubtopics()
  }, [])

  const handleStartSubtopic = (slug) => {
    startPaesSession("PRACTICE", slug)
  }

  const handleStartGeneral = () => {
    startPaesSession("PRACTICE", null)
  }

  const handleStartParametric = async () => {
    try {
      const q = await api.paes.getParametricQuestion("PARAM-M1-ALG-01")
      // Start session with parametric question
      await startPaesSession("PRACTICE", "m1-algebra-ecuaciones-lineales")
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div className="max-w-5xl mx-auto py-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xl">📐</span>
            <h1 className="text-2xl font-black text-white tracking-tight">
              PAES Competencia Matemática 1 (M1)
            </h1>
          </div>
          <p className="text-xs md:text-sm text-neutral-400">
            Ecosistema de práctica adaptativa con FSRS v4.5, generador paramétrico SymPy y telemetría cognitiva Peak.
          </p>
        </div>

        {paesSessionId && (
          <button
            onClick={resetPaesSession}
            className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-xs font-bold rounded-xl border border-white/[0.08] transition-all self-start md:self-auto"
          >
            ← Salir de Sesión
          </button>
        )}
      </div>

      {/* Error alert */}
      {paesError && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs mb-6">
          {paesError}
        </div>
      )}

      {/* SESSION IN PROGRESS */}
      {paesSessionId && paesActiveQuestion ? (
        <div className="space-y-6">
          {/* Progress bar */}
          <div className="flex items-center justify-between text-xs text-neutral-400 mb-2 font-mono">
            <span>
              Subtema: <strong className="text-white">{paesSubtopic || "General M1"}</strong>
            </span>
            <span>
              Pregunta {paesCurrentIndex + 1} de {paesQuestions.length}
            </span>
          </div>

          <PaesQuestionCard
            question={paesActiveQuestion}
            selectedOption={paesSelectedOption}
            onSelectOption={selectPaesOption}
            confidence={paesConfidence}
            onChangeConfidence={setPaesConfidence}
            onSubmit={() => submitPaesAttempt(25)}
            lastResult={paesLastResult}
            onNext={nextPaesQuestion}
            loading={paesLoading}
          />

          <SocraticTutorDrawer
            hints={paesSocraticHints}
            onRequestHint={requestSocraticHint}
            loading={paesLoading}
          />
        </div>
      ) : paesSessionId && !paesActiveQuestion ? (
        /* SESSION COMPLETE */
        <div className="bg-neutral-900/80 border border-white/[0.08] rounded-2xl p-8 backdrop-blur-xl text-center max-w-xl mx-auto my-8">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 text-emerald-400 text-3xl flex items-center justify-center mx-auto mb-4 border border-emerald-500/30">
            🏆
          </div>
          <h2 className="text-xl font-black text-white mb-2">¡Bloque de Estudio Completado!</h2>
          <p className="text-xs text-neutral-400 mb-6">
            Tus respuestas fueron integradas al modelo FSRS. La estabilidad de memoria y tus errores cognitivos ya están sincronizados con tu panel de Práctica Deliberada.
          </p>
          <button
            onClick={() => {
              resetPaesSession()
              fetchPaesFsrsStatus()
            }}
            className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-400 hover:to-green-500 text-black font-bold text-xs rounded-xl shadow-lg shadow-emerald-500/20 transition-all"
          >
            Volver al Temario M1
          </button>
        </div>
      ) : (
        /* OVERVIEW DASHBOARD */
        <div>
          <FsrsStatusWidget
            fsrsStatus={paesFsrsStatus}
            onReviewDueClick={handleStartGeneral}
          />

          {/* Action Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <div
              onClick={handleStartGeneral}
              className="p-5 rounded-2xl bg-neutral-900/60 border border-white/[0.08] hover:border-emerald-500/40 hover:bg-neutral-900/90 transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">⚡</span>
                <span className="text-xs text-emerald-400 font-bold group-hover:translate-x-1 transition-transform">
                  Comenzar →
                </span>
              </div>
              <h3 className="text-base font-bold text-white mb-1">Práctica Adaptativa ZDP</h3>
              <p className="text-xs text-neutral-400 leading-relaxed">
                El motor selecciona preguntas en tu Zona de Desarrollo Próximo optimizando la probabilidad de éxito y novedad.
              </p>
            </div>

            <div
              onClick={handleStartParametric}
              className="p-5 rounded-2xl bg-neutral-900/60 border border-white/[0.08] hover:border-purple-500/40 hover:bg-neutral-900/90 transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">🎲</span>
                <span className="text-xs text-purple-400 font-bold group-hover:translate-x-1 transition-transform">
                  Generar →
                </span>
              </div>
              <h3 className="text-base font-bold text-white mb-1">Generador Paramétrico SymPy</h3>
              <p className="text-xs text-neutral-400 leading-relaxed">
                Variantes algebraicas infinitas con distractores calculados matemáticamente sobre errores típicos de la PAES.
              </p>
            </div>
          </div>

          {/* Subtopics Official List */}
          <div className="bg-neutral-900/40 border border-white/[0.06] rounded-2xl p-6">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
              Temario Oficial DEMRE M1 2026 (13 Subtemas)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {paesSubtopicsList.map((st) => (
                <div
                  key={st.id}
                  className="p-4 rounded-xl bg-neutral-900/80 border border-white/[0.06] hover:border-white/[0.15] transition-all flex items-center justify-between gap-3"
                >
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-bold text-white truncate">{st.name}</h4>
                    <div className="flex items-center gap-3 mt-1.5 text-[11px] text-neutral-400">
                      <span>
                        Dominio: <strong className="text-emerald-400">{Math.round(st.mastery * 100)}%</strong>
                      </span>
                      <span>
                        Leitner: <strong className="text-amber-400">Caja {st.leitner_box}</strong>
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => handleStartSubtopic(st.slug)}
                    className="px-3 py-1.5 bg-neutral-800 hover:bg-emerald-500 hover:text-black text-neutral-200 text-xs font-bold rounded-lg border border-white/[0.08] transition-all shrink-0"
                  >
                    Entrenar
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
