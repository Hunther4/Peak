import { api } from "../../api/client"

export const createPaesSlice = (set, get) => ({
  paesSessionId: null,
  paesSubtopic: null,
  paesQuestions: [],
  paesCurrentIndex: 0,
  paesActiveQuestion: null,
  paesSelectedOption: null,
  paesConfidence: 3,
  paesLastResult: null,
  paesFsrsStatus: null,
  paesSubtopicsList: [],
  paesSocraticHints: [],
  paesLoading: false,
  paesError: null,

  // --- Multidisciplinary PAES Subjects ---
  paesSubjects: [],
  paesActiveSubject: "M1",

  // --- Exam Simulation State ---
  paesExamActive: false,
  paesExamTimeLimitMinutes: 32,
  paesExamAnswers: {}, // { [qId]: { selectedOption, timeSpentSeconds } }
  paesExamFlags: [], // [qId]
  paesExamResults: null,

  fetchPaesSubjects: async () => {
    try {
      set({ paesLoading: true, paesError: null })
      const data = await api.paes.getSubjects()
      set({ paesSubjects: data.subjects || [], paesLoading: false })
      return data.subjects
    } catch (err) {
      set({ paesError: err.message, paesLoading: false })
    }
  },

  setPaesActiveSubject: async (code) => {
    set({ paesActiveSubject: code })
    await get().fetchPaesSubtopics(1, code)
  },

  fetchPaesFsrsStatus: async (userId = 1) => {
    try {
      set({ paesLoading: true, paesError: null })
      const data = await api.paes.getFsrsStatus(userId)
      set({ paesFsrsStatus: data, paesLoading: false })
      return data
    } catch (err) {
      set({ paesError: err.message, paesLoading: false })
    }
  },

  fetchPaesSubtopics: async (userId = 1, subjectCode = null) => {
    try {
      set({ paesLoading: true, paesError: null })
      const targetSubject = subjectCode || get().paesActiveSubject || "M1"
      const data = await api.paes.getCurriculumSubtopics(userId, targetSubject)
      set({ paesSubtopicsList: data.subtopics, paesLoading: false })
      return data.subtopics
    } catch (err) {
      set({ paesError: err.message, paesLoading: false })
    }
  },

  startPaesSession: async (sessionMode = "PRACTICE", subtopicSlug = null, questionCount = null, subjectCode = null) => {
    try {
      set({ paesLoading: true, paesError: null, paesSocraticHints: [], paesLastResult: null, paesExamActive: false })
      const targetSubject = subjectCode || get().paesActiveSubject || "M1"
      const data = await api.paes.startStudySession(sessionMode, subtopicSlug, questionCount, targetSubject)
      set({
        paesSessionId: data.session_id,
        paesSubtopic: data.subtopic,
        paesQuestions: data.questions,
        paesCurrentIndex: 0,
        paesActiveQuestion: data.questions[0] || null,
        paesSelectedOption: null,
        paesLoading: false,
      })
      return data
    } catch (err) {
      set({ paesError: err.message, paesLoading: false })
    }
  },

  // Start an official DEMRE mock test
  startPaesExam: async (questionCount = 15, subjectCode = null) => {
    try {
      set({
        paesLoading: true,
        paesError: null,
        paesExamActive: true,
        paesExamResults: null,
        paesExamAnswers: {},
        paesExamFlags: [],
        paesSocraticHints: [],
        paesLastResult: null,
      })
      const targetSubject = subjectCode || get().paesActiveSubject || "M1"
      const data = await api.paes.startStudySession("EXAM", null, questionCount, targetSubject)
      set({
        paesSessionId: data.session_id,
        paesSubtopic: `Simulacro Oficial (${data.subject_name || targetSubject} - ${questionCount} Preguntas)`,
        paesQuestions: data.questions,
        paesCurrentIndex: 0,
        paesActiveQuestion: data.questions[0] || null,
        paesExamTimeLimitMinutes: data.time_limit_minutes || (questionCount >= 60 ? 140 : questionCount >= 30 ? 65 : 32),
        paesLoading: false,
      })
      return data
    } catch (err) {
      set({ paesError: err.message, paesLoading: false, paesExamActive: false })
    }
  },

  setExamAnswer: (questionId, selectedOption, timeSpentSeconds = 0) => {
    const { paesExamAnswers } = get()
    const current = paesExamAnswers[questionId] || {}
    set({
      paesExamAnswers: {
        ...paesExamAnswers,
        [questionId]: {
          selectedOption,
          timeSpentSeconds: (current.timeSpentSeconds || 0) + timeSpentSeconds,
        },
      },
    })
  },

  toggleExamFlag: (questionId) => {
    const { paesExamFlags } = get()
    const exists = paesExamFlags.includes(questionId)
    set({
      paesExamFlags: exists
        ? paesExamFlags.filter((id) => id !== questionId)
        : [...paesExamFlags, questionId],
    })
  },

  jumpToPaesQuestion: (idx) => {
    const { paesQuestions } = get()
    if (idx >= 0 && idx < paesQuestions.length) {
      set({
        paesCurrentIndex: idx,
        paesActiveQuestion: paesQuestions[idx],
        paesSelectedOption: null,
      })
    }
  },

  finalizePaesExam: async () => {
    const { paesSessionId, paesQuestions, paesExamAnswers, paesActiveSubject } = get()
    if (!paesSessionId) return

    try {
      set({ paesLoading: true, paesError: null })
      const answersList = paesQuestions.map((q) => {
        const recorded = paesExamAnswers[q.id]
        return {
          question_id: q.id,
          selected_option: recorded ? recorded.selectedOption : null,
          time_spent_seconds: recorded ? recorded.timeSpentSeconds : 0,
        }
      })

      const results = await api.paes.finalizeExam(paesSessionId, answersList, paesActiveSubject || "M1")
      set({
        paesExamResults: results,
        paesExamActive: false,
        paesLoading: false,
      })
      return results
    } catch (err) {
      set({ paesError: err.message, paesLoading: false })
    }
  },

  exitPaesExam: () =>
    set({
      paesExamActive: false,
      paesExamResults: null,
      paesSessionId: null,
      paesQuestions: [],
      paesActiveQuestion: null,
    }),

  selectPaesOption: (optKey) => set({ paesSelectedOption: optKey }),
  setPaesConfidence: (val) => set({ paesConfidence: val }),

  submitPaesAttempt: async (timeSpentSeconds = 30) => {
    const { paesSessionId, paesActiveQuestion, paesSelectedOption, paesConfidence } = get()
    if (!paesSessionId || !paesActiveQuestion || !paesSelectedOption) return

    try {
      set({ paesLoading: true, paesError: null })
      const res = await api.paes.submitAttempt({
        session_id: paesSessionId,
        question_id: paesActiveQuestion.id,
        selected_option: paesSelectedOption,
        time_spent_seconds: timeSpentSeconds,
        perceived_confidence: paesConfidence,
      })
      set({
        paesLastResult: res,
        paesLoading: false,
      })
      return res
    } catch (err) {
      set({ paesError: err.message, paesLoading: false })
    }
  },

  nextPaesQuestion: () => {
    const { paesQuestions, paesCurrentIndex } = get()
    const nextIdx = paesCurrentIndex + 1
    if (nextIdx < paesQuestions.length) {
      set({
        paesCurrentIndex: nextIdx,
        paesActiveQuestion: paesQuestions[nextIdx],
        paesSelectedOption: null,
        paesLastResult: null,
        paesSocraticHints: [],
      })
    } else {
      set({
        paesActiveQuestion: null,
        paesLastResult: null,
      })
    }
  },

  requestSocraticHint: async (studentMessage = null) => {
    const { paesSessionId, paesActiveQuestion, paesSocraticHints } = get()
    if (!paesSessionId || !paesActiveQuestion) return

    const nextLevel = paesSocraticHints.length + 1
    try {
      const data = await api.paes.getSocraticHint(
        paesSessionId,
        paesActiveQuestion.id,
        nextLevel,
        studentMessage
      )
      set({
        paesSocraticHints: [...paesSocraticHints, data],
      })
      return data
    } catch (err) {
      set({ paesError: err.message })
    }
  },

  resetPaesSession: () =>
    set({
      paesSessionId: null,
      paesSubtopic: null,
      paesQuestions: [],
      paesCurrentIndex: 0,
      paesActiveQuestion: null,
      paesSelectedOption: null,
      paesLastResult: null,
      paesSocraticHints: [],
      paesError: null,
      paesExamActive: false,
      paesExamResults: null,
    }),
})
