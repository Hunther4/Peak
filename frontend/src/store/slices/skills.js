import { api } from "../../api/client"

/** Group flat skill summaries into root → children hierarchy. */
function groupSkillsByParent(skills) {
  const roots = []
  const byId = new Map()

  // Index all skills
  for (const s of skills) {
    byId.set(s.skill.id, { ...s, children: [] })
  }

  // Build tree
  for (const s of skills) {
    const node = byId.get(s.skill.id)
    if (s.skill.parent_id) {
      const parent = byId.get(s.skill.parent_id)
      if (parent) {
        parent.children.push(node)
      } else {
        roots.push(node) // orphan → treat as root
      }
    } else {
      roots.push(node)
    }
  }

  return roots
}

export const createSkillsSlice = (set, get) => ({
  // State
  skills: [],
  sessions: [],
  summary: null,
  groupedSummary: [],  // roots with nested children
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
      const groupedSummary = groupSkillsByParent(summary.skills || [])
      set({ summary, groupedSummary })
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

  /** Poll timeline until no entries are pending (or timeout). */
  pollPendingAudits: (maxMs = 30000, intervalMs = 2000) => {
    const start = Date.now()
    const tick = () => {
      const { timeline } = get()
      const hasPending = timeline?.some(e => e.ai_fields_status === 'pending')
      if (!hasPending || Date.now() - start > maxMs) return
      get().fetchTimeline()
      setTimeout(tick, intervalMs)
    }
    // First tick after a short delay to let background processing start
    setTimeout(tick, intervalMs)
  },

  createSession: async (sessionData) => {
    set({ loading: true, error: null })
    try {
      const session = await api.sessions.create(sessionData)
      set({ loading: false })
      // Refrescar inmediato
      get().fetchSummary()
      get().fetchTimeline()
      // Poll hasta que la auditoría background termine (máx 30s)
      get().pollPendingAudits()
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