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
    paesSubjects,
    paesActiveSubject,
    fetchPaesSubjects,
    setPaesActiveSubject,
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
  const [parametricTemplate, setParametricTemplate] = useState("PARAM-M1-ALG-01")
  const [parametricSelected, setParametricSelected] = useState(null)
  const [parametricEvaluated, setParametricEvaluated] = useState(false)

  useEffect(() => {
    if (fetchPaesSubjects) fetchPaesSubjects()
    fetchPaesFsrsStatus()
    fetchPaesSubtopics(1, paesActiveSubject || "M1")
  }, [paesActiveSubject])

  const handleStartSubtopic = (slug) => {
    startPaesSession("PRACTICE", slug)
  }

  const handleStartGeneral = () => {
    startPaesSession("PRACTICE", null)
  }

  const handleGenerateParametric = async (templateCode = parametricTemplate) => {
    setParametricLoading(true)
    setParametricRevealed(false)
    setParametricSelected(null)
    setParametricEvaluated(false)
    try {
      const q = await api.paes.getParametricQuestion(templateCode)
      setParametricQuestion(q)
    } catch (e) {
      console.error(e)
    } finally {
      setParametricLoading(false)
    }
  }

const SUBJECTS_LIST = [
  { code: "M1", name: "Matemática 1", icon: "📐", badge: "Obligatoria", timePerQ: "2 min 09 seg / preg" },
  { code: "LECTURA", name: "Competencia Lectora", icon: "📖", badge: "Obligatoria", timePerQ: "2 min 18 seg / preg" },
  { code: "M2", name: "Matemática 2", icon: "📊", badge: "Específica", timePerQ: "2 min 32 seg / preg" },
  { code: "CIENCIAS", name: "Ciencias", icon: "🧪", badge: "Electiva", timePerQ: "2 min 00 seg / preg" },
  { code: "HISTORIA", name: "Historia y Cs. Sociales", icon: "🏛️", badge: "Electiva", timePerQ: "1 min 50 seg / preg" },
]

const SUBJECT_EXAMS_CONFIG = {
  M1: {
    mini: { count: 15, time: 32, label: "15 Preguntas balanceadas en los 4 ejes DEMRE M1." },
    mid: { count: 30, time: 65, label: "30 Preguntas para medir ritmo y resistencia." },
    full: { count: 65, time: 140, label: "Simulacro Oficial Completo M1 (60 evaluadas + 5 piloto)." },
  },
  LECTURA: {
    mini: { count: 15, time: 35, label: "15 Preguntas con textos continuos y discontinuos." },
    mid: { count: 30, time: 70, label: "30 Preguntas con las 3 habilidades oficiales DEMRE." },
    full: { count: 65, time: 150, label: "Simulacro Oficial Completo de Comprensión Lectora (150 min)." },
  },
  M2: {
    mini: { count: 15, time: 35, label: "15 Preguntas de trigonometría, logaritmos y funciones." },
    mid: { count: 30, time: 75, label: "30 Preguntas de nivel 3° y 4° Medio avanzado." },
    full: { count: 55, time: 140, label: "Simulacro Oficial Completo Matemática 2 (55 preguntas)." },
  },
  CIENCIAS: {
    mini: { count: 20, time: 40, label: "20 Preguntas de Biología, Física y Química." },
    mid: { count: 40, time: 80, label: "40 Preguntas de módulo común y electivo." },
    full: { count: 80, time: 160, label: "Simulacro Oficial Completo de Ciencias (80 preguntas)." },
  },
  HISTORIA: {
    mini: { count: 15, time: 30, label: "15 Preguntas de análisis de fuentes y ciudadanía." },
    mid: { count: 30, time: 60, label: "30 Preguntas de Historia de Chile, economía y territorio." },
    full: { count: 65, time: 120, label: "Simulacro Oficial Completo de Historia (65 preguntas)." },
  },
}

  // Group subtopics dynamically by Ejes
  const subtopicsByEje = useMemo(() => {
    const list = paesSubtopicsList || []
    const groups = {}
    list.forEach((sub) => {
      const eje = sub.eje_name || "General"
      if (!groups[eje]) groups[eje] = []
      groups[eje].push(sub)
    })
    return groups
  }, [paesSubtopicsList])

  // 1. If currently in EXAM MODE: show PaesExamRunner
  if (paesExamActive) {
    return <PaesExamRunner />
  }

  const currentSubject = SUBJECTS_LIST.find((s) => s.code === (paesActiveSubject || "M1")) || SUBJECTS_LIST[0]
  const currentExamConfig = SUBJECT_EXAMS_CONFIG[currentSubject.code] || SUBJECT_EXAMS_CONFIG["M1"]

  // 2. If viewing EXAM RESULTS: show PaesExamResults
  if (paesExamResults) {
    return (
      <PaesExamResults
        onNewExam={() => startPaesExam(currentExamConfig.mini.count, currentSubject.code)}
        onBackToStudy={() => exitPaesExam()}
      />
    )
  }

  return (
    <div className="max-w-5xl mx-auto py-4 animate-fade-in pb-16">
      {/* 5 Official PAES Subjects Switcher Pills */}
      <div className="flex items-center gap-2 mb-6 p-1.5 rounded-2xl bg-neutral-900/60 border border-white/[0.06] overflow-x-auto">
        {SUBJECTS_LIST.map((subj) => {
          const isActive = (paesActiveSubject || "M1") === subj.code
          return (
            <button
              key={subj.code}
              onClick={() => setPaesActiveSubject(subj.code)}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap cursor-pointer ${
                isActive
                  ? "bg-sky-500 text-neutral-950 shadow-md shadow-sky-500/20 font-black"
                  : "text-neutral-400 hover:text-white hover:bg-white/[0.04]"
              }`}
            >
              <span>{subj.icon}</span>
              <span>{subj.name}</span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded-md font-mono ${
                  isActive ? "bg-black/20 text-neutral-900" : "bg-white/[0.06] text-neutral-400"
                }`}
              >
                {subj.badge}
              </span>
            </button>
          )
        })}
      </div>

      {/* Top Main Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">{currentSubject.icon}</span>
            <h1 className="text-2xl font-black text-white tracking-tight">
              Academia PAES {currentSubject.name}
            </h1>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-sky-500/10 border border-sky-500/20 text-sky-400 font-bold">
              {currentSubject.code}
            </span>
          </div>
          <p className="text-xs md:text-sm text-neutral-400">
            Ecosistema de preparación oficial DEMRE 2026 con Ensayos Concretos, Algoritmo FSRS y Práctica Deliberada.
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
                    Ambiente Oficial DEMRE {currentSubject.code}
                  </span>
                  <h3 className="text-xl font-bold text-white">
                    Simulacros Oficiales de {currentSubject.name}
                  </h3>
                  <p className="text-xs text-neutral-400 max-w-xl">
                    Practicá bajo presión real de tiempo ({currentSubject.timePerQ}). Al finalizar, obtenés tu puntaje en escala oficial DEMRE 100–1000 y el solucionario analítico.
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="px-4 py-3 rounded-2xl bg-neutral-950/80 border border-white/[0.06] text-center font-mono">
                    <span className="text-[10px] text-neutral-400 block uppercase">Ritmo Oficial</span>
                    <span className="text-sm font-bold text-sky-400">{currentSubject.timePerQ}</span>
                  </div>
                </div>
              </div>

              {/* 3 Exam Tier Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {/* Mini-Ensayo */}
                <div className="p-6 rounded-3xl bg-neutral-900/60 border border-white/[0.08] hover:border-sky-500/50 transition-all flex flex-col justify-between group">
                  <div className="space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="p-3 rounded-2xl bg-sky-500/10 text-sky-400 text-xl font-bold">
                        ⚡
                      </span>
                      <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-sky-500/10 border border-sky-500/20 text-sky-400">
                        {currentExamConfig.mini.time} MIN
                      </span>
                    </div>
                    <div>
                      <h4 className="text-base font-bold text-white">Mini-Ensayo Focalizado</h4>
                      <p className="text-xs text-neutral-400 mt-1">{currentExamConfig.mini.label}</p>
                    </div>
                    <div className="pt-3 border-t border-white/[0.06] text-[11px] text-neutral-400 font-mono">
                      • {currentExamConfig.mini.count} Preguntas seleccionadas
                    </div>
                  </div>

                  <button
                    onClick={() => startPaesExam(currentExamConfig.mini.count, currentSubject.code)}
                    className="w-full mt-6 py-3 rounded-xl bg-sky-500 hover:bg-sky-400 text-neutral-950 font-bold text-xs transition-all shadow-lg shadow-sky-500/20 cursor-pointer"
                  >
                    Iniciar Mini-Ensayo ({currentExamConfig.mini.count}) ➔
                  </button>
                </div>

                {/* Medio Ensayo */}
                <div className="p-6 rounded-3xl bg-neutral-900/60 border border-white/[0.08] hover:border-purple-500/50 transition-all flex flex-col justify-between group">
                  <div className="space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="p-3 rounded-2xl bg-purple-500/10 text-purple-400 text-xl font-bold">
                        📝
                      </span>
                      <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-purple-500/10 border border-purple-500/20 text-purple-400">
                        {currentExamConfig.mid.time} MIN
                      </span>
                    </div>
                    <div>
                      <h4 className="text-base font-bold text-white">Medio Ensayo Calibrado</h4>
                      <p className="text-xs text-neutral-400 mt-1">{currentExamConfig.mid.label}</p>
                    </div>
                    <div className="pt-3 border-t border-white/[0.06] text-[11px] text-neutral-400 font-mono">
                      • {currentExamConfig.mid.count} Preguntas para medir resistencia
                    </div>
                  </div>

                  <button
                    onClick={() => startPaesExam(currentExamConfig.mid.count, currentSubject.code)}
                    className="w-full mt-6 py-3 rounded-xl bg-purple-500 hover:bg-purple-400 text-white font-bold text-xs transition-all shadow-lg shadow-purple-500/20 cursor-pointer"
                  >
                    Iniciar Medio Ensayo ({currentExamConfig.mid.count}) ➔
                  </button>
                </div>

                {/* Ensayo Completo DEMRE */}
                <div className="p-6 rounded-3xl bg-neutral-900/60 border border-white/[0.08] hover:border-emerald-500/50 transition-all flex flex-col justify-between group relative overflow-hidden">
                  <div className="space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="p-3 rounded-2xl bg-emerald-500/10 text-emerald-400 text-xl font-bold">
                        🎓
                      </span>
                      <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                        {currentExamConfig.full.time} MIN
                      </span>
                    </div>
                    <div>
                      <h4 className="text-base font-bold text-white">Simulacro Oficial Completo</h4>
                      <p className="text-xs text-neutral-400 mt-1">
                        {currentExamConfig.full.label}
                      </p>
                    </div>
                    <div className="pt-3 border-t border-white/[0.06] text-[11px] text-neutral-400 font-mono">
                      • {currentExamConfig.full.count} Preguntas oficiales DEMRE 2026
                    </div>
                  </div>

                  <button
                    onClick={() => startPaesExam(currentExamConfig.full.count, currentSubject.code)}
                    className="w-full mt-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-neutral-950 font-black text-xs transition-all shadow-lg shadow-emerald-500/25 cursor-pointer"
                  >
                    Iniciar Simulacro ({currentExamConfig.full.count} Preguntas) ➔
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

                <div className="flex items-center gap-3 flex-wrap">
                  <select
                    value={parametricTemplate}
                    onChange={(e) => {
                      setParametricTemplate(e.target.value)
                      handleGenerateParametric(e.target.value)
                    }}
                    className="bg-neutral-800 border border-white/[0.1] text-neutral-200 text-xs font-bold rounded-xl px-3 py-2.5 focus:outline-none focus:border-purple-500 cursor-pointer"
                  >
                    <option value="PARAM-M1-ALG-01">📐 Ecuación Lineal 1° Grado</option>
                    <option value="PARAM-M1-ALG-02">🔀 Sistema de Ecuaciones 2×2</option>
                    <option value="PARAM-M1-GEO-01">🔺 Teorema de Pitágoras</option>
                  </select>

                  <button
                    onClick={() => handleGenerateParametric()}
                    disabled={parametricLoading}
                    className="px-5 py-2.5 bg-purple-500 hover:bg-purple-400 text-white font-bold text-xs rounded-xl shadow-lg shadow-purple-500/20 transition-all cursor-pointer disabled:opacity-50"
                  >
                    {parametricLoading ? "Generando..." : "🎲 Nueva Instancia"}
                  </button>
                </div>
              </div>

              {parametricQuestion ? (
                <div className="space-y-6">
                  {/* Stem */}
                  <div className="p-5 rounded-2xl bg-neutral-950/80 border border-white/[0.06] text-sm md:text-base text-neutral-100 leading-relaxed font-medium">
                    <MathRenderer text={parametricQuestion.stem} />
                  </div>

                  {/* Options */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {parametricQuestion.options.map((opt) => {
                      const optKey = opt.id || opt.key
                      const isSelected = parametricSelected === optKey
                      const isCorrect = opt.is_correct

                      let borderBgClass = "bg-neutral-950/60 border-white/[0.08] hover:border-white/[0.2] text-neutral-200"
                      if (parametricEvaluated || parametricRevealed) {
                        if (isCorrect) {
                          borderBgClass = "bg-emerald-500/15 border-emerald-500 text-emerald-300 shadow-sm shadow-emerald-500/20"
                        } else if (isSelected) {
                          borderBgClass = "bg-rose-500/15 border-rose-500 text-rose-300"
                        } else {
                          borderBgClass = "bg-neutral-950/40 border-white/[0.04] text-neutral-400 opacity-60"
                        }
                      } else if (isSelected) {
                        borderBgClass = "bg-purple-500/15 border-purple-500 text-purple-200 ring-2 ring-purple-500/30"
                      }

                      return (
                        <button
                          key={optKey}
                          type="button"
                          disabled={parametricEvaluated || parametricRevealed}
                          onClick={() => setParametricSelected(optKey)}
                          className={`p-4 rounded-2xl border transition-all text-left flex items-center gap-3.5 cursor-pointer disabled:cursor-default ${borderBgClass}`}
                        >
                          <span className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs font-mono shrink-0 transition-colors ${
                            (parametricEvaluated || parametricRevealed) && isCorrect
                              ? "bg-emerald-500 text-neutral-950"
                              : (parametricEvaluated || parametricRevealed) && isSelected
                                ? "bg-rose-500 text-white"
                                : isSelected
                                  ? "bg-purple-500 text-white"
                                  : "bg-neutral-800 text-neutral-400"
                          }`}>
                            {optKey}
                          </span>
                          <div className="flex-1 min-w-0">
                            <MathRenderer text={opt.content || opt.text} />
                          </div>
                          {(parametricEvaluated || parametricRevealed) && isCorrect && (
                            <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
                              ✓ Correcta
                            </span>
                          )}
                          {(parametricEvaluated || parametricRevealed) && isSelected && !isCorrect && (
                            <span className="text-xs font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-md border border-rose-500/20">
                              ✗ Tu elección
                            </span>
                          )}
                          {(parametricEvaluated || parametricRevealed) && opt.distractor_type && (
                            <span className="text-[10px] font-mono text-neutral-400 bg-neutral-800/80 px-1.5 py-0.5 rounded border border-white/[0.06]">
                              {opt.distractor_type}
                            </span>
                          )}
                        </button>
                      )
                    })}
                  </div>

                  {/* Actions bar */}
                  <div className="flex items-center justify-between pt-2 border-t border-white/[0.06] flex-wrap gap-3">
                    <div className="flex items-center gap-3">
                      {!parametricEvaluated && !parametricRevealed ? (
                        <button
                          type="button"
                          disabled={!parametricSelected}
                          onClick={() => {
                            setParametricEvaluated(true)
                            setParametricRevealed(true)
                          }}
                          className="px-6 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-neutral-950 font-bold text-xs rounded-xl shadow-lg shadow-emerald-500/20 transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                        >
                          Comprobar Respuesta
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={() => handleGenerateParametric()}
                          className="px-6 py-2.5 bg-purple-500 hover:bg-purple-400 text-white font-bold text-xs rounded-xl shadow-lg shadow-purple-500/20 transition-all cursor-pointer"
                        >
                          Siguiente Ejercicio SymPy ➔
                        </button>
                      )}

                      <button
                        type="button"
                        onClick={() => setParametricRevealed(!parametricRevealed)}
                        className="text-xs font-bold text-neutral-400 hover:text-white underline cursor-pointer"
                      >
                        {parametricRevealed ? "Ocultar Solución" : "Revelar Explicación Directa"}
                      </button>
                    </div>

                    {parametricEvaluated && (
                      <div className="text-xs font-mono font-bold">
                        {parametricQuestion.options.find(o => (o.id || o.key) === parametricSelected)?.is_correct ? (
                          <span className="text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-xl border border-emerald-500/20">
                            🎉 ¡Respuesta Correcta!
                          </span>
                        ) : (
                          <span className="text-rose-400 bg-rose-500/10 px-3 py-1.5 rounded-xl border border-rose-500/20">
                            💡 Respuesta Incorrecta — Revisa el paso a paso abajo
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Complete, Unambiguous Step-by-Step Explanation */}
                  {parametricRevealed && parametricQuestion.explanation && (
                    <div className="p-6 rounded-2xl bg-neutral-950/80 border border-purple-500/30 text-xs text-neutral-300 leading-relaxed space-y-4 animate-fade-in shadow-xl shadow-purple-950/20">
                      <div className="flex items-center gap-2 text-purple-400 font-bold text-sm border-b border-white/[0.06] pb-2">
                        <span>📝</span>
                        <span>Solucionario Oficial y Desglose Paso a Paso</span>
                      </div>

                      {/* Step by step */}
                      {parametricQuestion.explanation.step_by_step && (
                        <div className="space-y-1.5">
                          <strong className="text-white block font-bold text-xs">
                            Paso a paso analítico:
                          </strong>
                          <div className="p-3.5 bg-neutral-900/90 rounded-xl border border-white/[0.06] text-neutral-200">
                            <MathRenderer text={parametricQuestion.explanation.step_by_step} />
                          </div>
                        </div>
                      )}

                      {/* Key concept */}
                      {parametricQuestion.explanation.key_concept && (
                        <div className="space-y-1">
                          <strong className="text-sky-400 block font-bold text-xs">
                            🎯 Concepto Clave DEMRE:
                          </strong>
                          <p className="text-neutral-300 pl-1">
                            {parametricQuestion.explanation.key_concept}
                          </p>
                        </div>
                      )}

                      {/* Frequent mistake */}
                      {parametricQuestion.explanation.frequent_mistake && (
                        <div className="space-y-1">
                          <strong className="text-amber-400 block font-bold text-xs">
                            ⚠️ Distractor y Error Frecuente:
                          </strong>
                          <p className="text-neutral-400 pl-1">
                            {parametricQuestion.explanation.frequent_mistake}
                          </p>
                        </div>
                      )}

                      {/* Short summary */}
                      {parametricQuestion.explanation.short_summary && (
                        <div className="pt-2 border-t border-white/[0.04] text-[11px] text-neutral-400 font-mono">
                          Conclusión: <span className="text-white">{parametricQuestion.explanation.short_summary}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-neutral-500 text-xs">
                  Hacé clic en &quot;Nueva Instancia&quot; para probar el motor algebraico SymPy.
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
