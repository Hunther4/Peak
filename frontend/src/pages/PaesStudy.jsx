import React, { useEffect, useState, useMemo } from "react"
import { useStore } from "../store/store"
import { FsrsStatusWidget } from "../components/paes/FsrsStatusWidget"
import { PaesQuestionCard } from "../components/paes/PaesQuestionCard"
import { SocraticTutorDrawer } from "../components/paes/SocraticTutorDrawer"
import { PaesExamRunner } from "../components/paes/PaesExamRunner"
import { PaesExamResults } from "../components/paes/PaesExamResults"
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
    paesExamActive,
    paesExamResults,
    fetchPaesFsrsStatus,
    fetchPaesSubtopics,
    startPaesSession,
    startPaesExam,
    selectPaesOption,
    setPaesConfidence,
    submitPaesAttempt,
    nextPaesQuestion,
    requestSocraticHint,
    resetPaesSession,
    exitPaesExam,
  } = useStore()

  // Tab: "exams" | "curriculum" | "parametric" | "fsrs"
  const [activeTab, setActiveTab] = useState("exams")
  const [parametricQuestion, setParametricQuestion] = useState(null)
  const [parametricLoading, setParametricLoading] = useState(false)
  const [parametricRevealed, setParametricRevealed] = useState(false)

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

  const handleGenerateParametric = async (templateCode = "PARAM-M1-ALG-01") => {
    setParametricLoading(true)
    setParametricRevealed(false)
    try {
      const q = await api.paes.getParametricQuestion(templateCode)
      setParametricQuestion(q)
    } catch (e) {
      console.error(e)
    } finally {
      setParametricLoading(false)
    }
  }

  // Group the 13 subtopics by Ejes
  const subtopicsByEje = useMemo(() => {
    const list = paesSubtopicsList || []
    const groups = {
      "Números": [],
      "Álgebra y Funciones": [],
      "Geometría": [],
      "Probabilidad y Estadística": [],
    }

    list.forEach((sub) => {
      const s = (sub.slug || "").toLowerCase()
      if (s.includes("numero") || s.includes("entero") || s.includes("porcentaje") || s.includes("potencia")) {
        groups["Números"].push(sub)
      } else if (s.includes("algebra") || s.includes("ecuacion") || s.includes("funcion") || s.includes("sistema")) {
        groups["Álgebra y Funciones"].push(sub)
      } else if (s.includes("geometria") || s.includes("perimetro") || s.includes("transformacion") || s.includes("pitagoras")) {
        groups["Geometría"].push(sub)
      } else {
        groups["Probabilidad y Estadística"].push(sub)
      }
    })

    return groups
  }, [paesSubtopicsList])

  // 1. If currently in EXAM MODE: show PaesExamRunner
  if (paesExamActive) {
    return <PaesExamRunner />
  }

  // 2. If viewing EXAM RESULTS: show PaesExamResults
  if (paesExamResults) {
    return (
      <PaesExamResults
        onNewExam={() => startPaesExam(15)}
        onBackToStudy={() => exitPaesExam()}
      />
    )
  }

  return (
    <div className="max-w-5xl mx-auto py-4 animate-fade-in pb-16">
      {/* Top Main Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">📐</span>
            <h1 className="text-2xl font-black text-white tracking-tight">
              Academia PAES Competencia Matemática 1 (M1)
            </h1>
          </div>
          <p className="text-xs md:text-sm text-neutral-400">
            Ecosistema especializado con Ensayos Oficiales DEMRE, FSRS v4.5 y Generador Paramétrico SymPy.
          </p>
        </div>

        {paesSessionId && !paesExamActive && (
          <button
            onClick={resetPaesSession}
            className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-xs font-bold rounded-xl border border-white/[0.08] transition-all self-start md:self-auto cursor-pointer"
          >
            ← Salir de Práctica
          </button>
        )}
      </div>

      {/* Error Alert */}
      {paesError && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs mb-6 flex items-center justify-between">
          <span>{paesError}</span>
          <button
            onClick={() => {
              fetchPaesFsrsStatus()
              fetchPaesSubtopics()
            }}
            className="text-xs underline font-semibold text-rose-400 cursor-pointer"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* REGULAR PRACTICE SESSION IN PROGRESS */}
      {paesSessionId && paesActiveQuestion ? (
        <div className="space-y-6">
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
        /* REGULAR BLOCK COMPLETE */
        <div className="bg-neutral-900/80 border border-white/[0.08] rounded-3xl p-8 backdrop-blur-xl text-center max-w-xl mx-auto my-8 space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 text-emerald-400 text-3xl flex items-center justify-center mx-auto border border-emerald-500/30">
            🏆
          </div>
          <h2 className="text-xl font-black text-white">¡Bloque de Práctica Completado!</h2>
          <p className="text-xs text-neutral-400 leading-relaxed">
            Tus respuestas fueron integradas al modelo FSRS. La estabilidad de memoria y tus errores cognitivos ya están sincronizados.
          </p>
          <button
            onClick={() => {
              resetPaesSession()
              fetchPaesFsrsStatus()
            }}
            className="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-neutral-950 font-bold text-xs rounded-xl shadow-lg shadow-emerald-500/20 transition-all cursor-pointer"
          >
            Volver al Ecosistema PAES
          </button>
        </div>
      ) : (
        /* SPECIALIZED HUB TABS */
        <div className="space-y-6">
          {/* Main Tab Navigation */}
          <div className="flex items-center gap-2 p-1.5 bg-neutral-900/80 border border-white/[0.08] rounded-2xl backdrop-blur-md overflow-x-auto">
            {[
              { id: "exams", label: "🎯 Ensayos Concretos (Simulacros)", icon: "🎯" },
              { id: "curriculum", label: "📚 Temario 2026 (13 Subtemas)", icon: "📚" },
              { id: "parametric", label: "🎲 Generador SymPy", icon: "🎲" },
              { id: "fsrs", label: "🧠 Memoria FSRS v4.5", icon: "🧠" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer flex items-center gap-2 ${
                  activeTab === tab.id
                    ? "bg-white text-neutral-950 shadow-md"
                    : "text-neutral-400 hover:text-white"
                }`}
              >
                <span>{tab.label}</span>
              </button>
            ))}
          </div>

          {/* TAB 1: CONCRETE EXAMS (SIMULACROS FORMALES) */}
          {activeTab === "exams" && (
            <div className="space-y-6 animate-fade-in">
              {/* Hero Banner */}
              <div className="p-6 rounded-3xl bg-neutral-900/40 border border-white/[0.06] flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="space-y-1 text-center md:text-left">
                  <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-sky-400">
                    Ambiente Oficial DEMRE
                  </span>
                  <h3 className="text-xl font-bold text-white">
                    Simulacros Oficiales con Temporizador & Escala DEMRE
                  </h3>
                  <p className="text-xs text-neutral-400 max-w-xl">
                    Practicá bajo presión real de tiempo (2:09 min por pregunta). Al finalizar, obtenés tu puntaje en escala oficial 100–1000 y el solucionario detallado.
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="px-4 py-3 rounded-2xl bg-neutral-950/80 border border-white/[0.06] text-center font-mono">
                    <span className="text-[10px] text-neutral-400 block uppercase">Tiempo Oficial</span>
                    <span className="text-sm font-bold text-sky-400">2 min 09 seg / preg</span>
                  </div>
                </div>
              </div>

              {/* 3 Exam Tier Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {/* Mini-Ensayo (15 Preguntas) */}
                <div className="p-6 rounded-3xl bg-neutral-900/60 border border-white/[0.08] hover:border-sky-500/50 transition-all flex flex-col justify-between group">
                  <div className="space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="p-3 rounded-2xl bg-sky-500/10 text-sky-400 text-xl font-bold">
                        ⚡
                      </span>
                      <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-sky-500/10 border border-sky-500/20 text-sky-400">
                        32 MIN
                      </span>
                    </div>
                    <div>
                      <h4 className="text-base font-bold text-white">Mini-Ensayo Focalizado</h4>
                      <p className="text-xs text-neutral-400 mt-1">15 Preguntas balanceadas en los 4 ejes DEMRE.</p>
                    </div>
                    <div className="pt-3 border-t border-white/[0.06] space-y-1 text-[11px] text-neutral-400 font-mono">
                      <div>• 4 Números • 5 Álgebra</div>
                      <div>• 3 Geometría • 3 Probabilidades</div>
                    </div>
                  </div>

                  <button
                    onClick={() => startPaesExam(15)}
                    className="w-full mt-6 py-3 rounded-xl bg-sky-500 hover:bg-sky-400 text-neutral-950 font-bold text-xs transition-all shadow-lg shadow-sky-500/20 cursor-pointer"
                  >
                    Iniciar Mini-Ensayo (15) ➔
                  </button>
                </div>

                {/* Medio Ensayo (30 Preguntas) */}
                <div className="p-6 rounded-3xl bg-neutral-900/60 border border-white/[0.08] hover:border-purple-500/50 transition-all flex flex-col justify-between group">
                  <div className="space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="p-3 rounded-2xl bg-purple-500/10 text-purple-400 text-xl font-bold">
                        📝
                      </span>
                      <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-purple-500/10 border border-purple-500/20 text-purple-400">
                        65 MIN
                      </span>
                    </div>
                    <div>
                      <h4 className="text-base font-bold text-white">Medio Ensayo Calibrado</h4>
                      <p className="text-xs text-neutral-400 mt-1">30 Preguntas para medir resistencia y precisión.</p>
                    </div>
                    <div className="pt-3 border-t border-white/[0.06] space-y-1 text-[11px] text-neutral-400 font-mono">
                      <div>• 7 Números • 10 Álgebra</div>
                      <div>• 7 Geometría • 6 Probabilidades</div>
                    </div>
                  </div>

                  <button
                    onClick={() => startPaesExam(30)}
                    className="w-full mt-6 py-3 rounded-xl bg-purple-500 hover:bg-purple-400 text-white font-bold text-xs transition-all shadow-lg shadow-purple-500/20 cursor-pointer"
                  >
                    Iniciar Medio Ensayo (30) ➔
                  </button>
                </div>

                {/* Ensayo Completo DEMRE (65 Preguntas) */}
                <div className="p-6 rounded-3xl bg-neutral-900/60 border border-white/[0.08] hover:border-emerald-500/50 transition-all flex flex-col justify-between group relative overflow-hidden">
                  <div className="space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="p-3 rounded-2xl bg-emerald-500/10 text-emerald-400 text-xl font-bold">
                        🎓
                      </span>
                      <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                        140 MIN
                      </span>
                    </div>
                    <div>
                      <h4 className="text-base font-bold text-white">Simulacro Oficial Completo</h4>
                      <p className="text-xs text-neutral-400 mt-1">
                        65 Preguntas oficiales (60 puntuables + 5 piloto).
                      </p>
                    </div>
                    <div className="pt-3 border-t border-white/[0.06] space-y-1 text-[11px] text-neutral-400 font-mono">
                      <div>• 15 Números • 20 Álgebra</div>
                      <div>• 15 Geometría • 15 Probabilidades</div>
                    </div>
                  </div>

                  <button
                    onClick={() => startPaesExam(65)}
                    className="w-full mt-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-neutral-950 font-bold text-xs transition-all shadow-lg shadow-emerald-500/20 cursor-pointer"
                  >
                    Iniciar Ensayo Completo (65) ➔
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: TEMARIO OFICIAL (13 SUBTEMAS POR EJE) */}
          {activeTab === "curriculum" && (
            <div className="space-y-6 animate-fade-in">
              {Object.entries(subtopicsByEje).map(([ejeName, subtopics]) => (
                <div
                  key={ejeName}
                  className="p-6 rounded-3xl bg-neutral-900/60 border border-white/[0.06] space-y-4"
                >
                  <div className="flex items-center justify-between pb-3 border-b border-white/[0.04]">
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-sky-400" />
                      <span>{ejeName}</span>
                    </h3>
                    <span className="text-xs text-neutral-400 font-mono">
                      {subtopics.length} subtemas
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {subtopics.map((st) => (
                      <div
                        key={st.id}
                        className="p-4 rounded-2xl bg-neutral-950/60 border border-white/[0.04] hover:border-white/[0.1] transition-all flex items-center justify-between gap-3"
                      >
                        <div className="flex-1 min-w-0">
                          <h4 className="text-xs font-bold text-white truncate">{st.name}</h4>
                          <div className="flex items-center gap-3 mt-1.5 text-[11px] text-neutral-400">
                            <span>
                              Dominio: <strong className="text-sky-400">{Math.round(st.mastery * 100)}%</strong>
                            </span>
                            <span>
                              Caja: <strong className="text-amber-400">{st.leitner_box}</strong>
                            </span>
                          </div>
                          <div className="w-full bg-neutral-800 h-1.5 rounded-full overflow-hidden mt-2">
                            <div
                              className="bg-sky-500 h-full rounded-full transition-all duration-500"
                              style={{ width: `${Math.round(st.mastery * 100)}%` }}
                            />
                          </div>
                        </div>

                        <button
                          onClick={() => handleStartSubtopic(st.slug)}
                          className="px-3.5 py-2 bg-neutral-800 hover:bg-sky-500 hover:text-neutral-950 text-neutral-200 text-xs font-bold rounded-xl border border-white/[0.08] transition-all shrink-0 cursor-pointer"
                        >
                          Entrenar
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 3: GENERADOR PARAMETRICO SYMPY */}
          {activeTab === "parametric" && (
            <div className="p-6 md:p-8 rounded-3xl bg-neutral-900/60 border border-white/[0.08] space-y-6 animate-fade-in">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-6 border-b border-white/[0.06]">
                <div>
                  <span className="text-[10px] font-mono uppercase font-bold text-purple-400 tracking-wider">
                    Motor Matemático Formal
                  </span>
                  <h3 className="text-lg font-bold text-white">
                    Generador Paramétrico SymPy
                  </h3>
                  <p className="text-xs text-neutral-400 mt-0.5">
                    Generá infinitas instancias algebraicas con distractores matemáticos controlados.
                  </p>
                </div>

                <button
                  onClick={() => handleGenerateParametric()}
                  disabled={parametricLoading}
                  className="px-5 py-2.5 bg-purple-500 hover:bg-purple-400 text-white font-bold text-xs rounded-xl shadow-lg shadow-purple-500/20 transition-all cursor-pointer"
                >
                  {parametricLoading ? "Generando..." : "🎲 Generar Nueva Instancia"}
                </button>
              </div>

              {parametricQuestion ? (
                <div className="space-y-6">
                  {/* Stem */}
                  <div className="p-5 rounded-2xl bg-neutral-950/80 border border-white/[0.06] text-sm md:text-base text-neutral-100 leading-relaxed">
                    <MathRenderer text={parametricQuestion.stem} />
                  </div>

                  {/* Options */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {parametricQuestion.options.map((opt) => (
                      <div
                        key={opt.key}
                        className={`p-4 rounded-xl border transition-all flex items-center gap-3 ${
                          parametricRevealed && opt.is_correct
                            ? "bg-emerald-500/20 border-emerald-500 text-emerald-200 font-bold"
                            : "bg-neutral-850 border-white/[0.06] text-neutral-200"
                        }`}
                      >
                        <span className="w-7 h-7 rounded-lg bg-neutral-800 flex items-center justify-center font-bold text-xs font-mono">
                          {opt.key}
                        </span>
                        <div className="flex-1">
                          <MathRenderer text={opt.content || opt.text} />
                        </div>
                        {parametricRevealed && opt.is_correct && (
                          <span className="text-xs text-emerald-400 font-mono font-bold">✓</span>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Reveal Solution */}
                  <div className="flex items-center justify-between pt-4">
                    <button
                      onClick={() => setParametricRevealed(!parametricRevealed)}
                      className="text-xs font-bold text-purple-400 hover:text-purple-300 underline cursor-pointer"
                    >
                      {parametricRevealed ? "Ocultar Solución" : "Revelar Solución y Distractores"}
                    </button>
                  </div>

                  {parametricRevealed && parametricQuestion.explanation && (
                    <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/20 text-xs text-neutral-300 leading-relaxed animate-fade-in">
                      <strong className="text-purple-400 block mb-1">Explicación Paso a Paso:</strong>
                      <MathRenderer
                        text={
                          parametricQuestion.explanation.correct_solution ||
                          parametricQuestion.explanation.short_summary ||
                          ""
                        }
                      />
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-neutral-500 text-xs">
                  Hacé clic en &quot;Generar Nueva Instancia&quot; para probar el motor algebraico SymPy.
                </div>
              )}
            </div>
          )}

          {/* TAB 4: FSRS RETENTION WIDGET */}
          {activeTab === "fsrs" && (
            <div className="space-y-6 animate-fade-in">
              <FsrsStatusWidget
                fsrsStatus={paesFsrsStatus}
                onReviewDueClick={handleStartGeneral}
              />
            </div>
          )}
        </div>
      )}
    </div>
  )
}
