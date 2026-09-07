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

  fetchPaesSubtopics: async (userId = 1) => {
    try {
      set({ paesLoading: true, paesError: null })
      const data = await api.paes.getCurriculumSubtopics(userId)
      set({ paesSubtopicsList: data.subtopics, paesLoading: false })
      return data.subtopics
    } catch (err) {
      set({ paesError: err.message, paesLoading: false })
    }
  },

  startPaesSession: async (sessionMode = "PRACTICE", subtopicSlug = null) => {
    try {
      set({ paesLoading: true, paesError: null, paesSocraticHints: [], paesLastResult: null })
      const data = await api.paes.startStudySession(sessionMode, subtopicSlug)
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
    }),
})
