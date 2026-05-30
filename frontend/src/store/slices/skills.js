import { api } from "../../api/client"

export const createSkillsSlice = (set, get) => ({
  // State
  skills: [],
  sessions: [],
  summary: null,
  timeline: [],
  loading: false,
  error: null,

  // Actions
  fetchSkills: async () => {
    set({ loading: true, error: null })
    try {
      const skills = await api.skills.getAll()
      set({ skills, loading: false })
    } catch (e) {
      set({ error: e.message, loading: false })
    }
  },

  fetchSummary: async () => {
    try {
      const summary = await api.dashboard.getSummary()
      set({ summary })
    } catch (e) {
      set({ error: e.message })
    }
  },

  fetchTimeline: async (skillId = null) => {
    try {
      const data = await api.dashboard.getTimeline(skillId)
      set({ timeline: data.timeline })
    } catch (e) {
      set({ error: e.message })
    }
  },

  createSession: async (sessionData) => {
    set({ loading: true, error: null })
    try {
      const session = await api.sessions.create(sessionData)
      set({ loading: false })
      // Refrescar inmediato
      get().fetchSummary()
      get().fetchTimeline()
      // Y otro refresh a los 3s para capturar el resultado del background IA
      setTimeout(() => {
        get().fetchSummary()
        get().fetchTimeline()
      }, 3000)
      return session
    } catch (e) {
      set({ error: e.message, loading: false })
      throw e
    }
  },

  createAssessment: async (assessmentData) => {
    set({ loading: true, error: null })
    try {
      const assessment = await api.assessments.create(assessmentData)
      set({ loading: false })
      get().fetchSummary()
      return assessment
    } catch (e) {
      set({ error: e.message, loading: false })
      throw e
    }
  },

  clearError: () => set({ error: null })
})