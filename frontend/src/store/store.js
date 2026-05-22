import { create } from "zustand"
import { api } from "../api/client"

export const useStore = create((set, get) => ({
  // State
  skills: [],
  sessions: [],
  summary: null,
  timeline: [],
  loading: false,
  error: null,
  profile: null,
  profileLoading: true,

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

  // --- Books / RAG ---
  books: [],
  booksLoading: false,
  isIndexing: false,
  indexingProgress: 0,

  fetchBooksStatus: async () => {
    set({ booksLoading: true })
    try {
      const data = await api.books.getStatus()
      set({
        books: data.books ?? [],
        isIndexing: data.is_indexing ?? false,
        indexingProgress: data.progress ?? 0,
        booksLoading: false,
      })
    } catch (e) {
      console.warn("[store] fetchBooksStatus error:", e.message)
      set({ booksLoading: false })
    }
  },

  indexBooks: async (force = false) => {
   set({ isIndexing: true, indexingProgress: 0 })
    try {
      await api.books.index(force)
      // Poll liviano: refrescamos status cada 3s hasta que termine
      const poll = setInterval(async () => {
        try {
          const data = await api.books.getStatus()
          set({
            books: data.books ?? [],
            isIndexing: data.is_indexing ?? false,
            indexingProgress: data.progress ?? 0,
          })
          if (!data.is_indexing) clearInterval(poll)
        } catch {
          clearInterval(poll)
          set({ isIndexing: false })
        }
      }, 3000)
    } catch (e) {
      set({ isIndexing: false })
      throw e
    }
  },

  // --- Fase 5: MentalReps + Challenges ---
  mentalReps: [],
  challenges: [],
  pendingChallenges: 0,
  generatingRep: false,
  generatingChallenge: false,

  fetchMentalReps: async (skillId = null) => {
    try {
      const reps = await api.mental.getReps(skillId)
      set({ mentalReps: reps })
    } catch (e) {
      console.warn("[store] fetchMentalReps:", e.message)
    }
  },

  fetchChallenges: async (skillId = null) => {
    try {
      const challenges = await api.mental.getChallenges(skillId)
      set({ challenges })
    } catch (e) {
      console.warn("[store] fetchChallenges:", e.message)
    }
  },

  generateRep: async (skillId) => {
    set({ generatingRep: true })
    try {
      const result = await api.mental.generateRep(skillId)
      set({ generatingRep: false })
      return result
    } catch (e) {
      set({ generatingRep: false })
      throw e
    }
  },

  acceptRep: async (repId, description, skillId) => {
    try {
      const rep = await api.mental.acceptRep(repId, description, skillId)
      // Refrescar lista
      get().fetchMentalReps()
      return rep
    } catch (e) {
      console.warn("[store] acceptRep:", e.message)
      throw e
    }
  },

  generateChallenge: async (skillId, difficultyOverride = null) => {
    set({ generatingChallenge: true })
    try {
      const result = await api.mental.generateChallenge(skillId, difficultyOverride)
      set({ generatingChallenge: false })
      return result
    } catch (e) {
      set({ generatingChallenge: false })
      throw e
    }
  },

  completeChallenge: async (challengeId, completed = true) => {
    try {
      const result = await api.mental.completeChallenge(challengeId, completed)
      get().fetchChallenges()
      return result
    } catch (e) {
      console.warn("[store] completeChallenge:", e.message)
      throw e
    }
  },

  // --- Ai Router Mode ---
  ai_mode: "local",
  available_models: [],
  best_model: null,
  selectedModel: { auto: true },

  fetchAiStatus: async () => {
    try {
      const statusRes = await api.models.getStatus()
      set({ ai_mode: statusRes.mode })

      const modelsRes = await api.models.getAvailable()
      set({ available_models: modelsRes })

      const bestRes = await api.models.getBest("audit")
      set({ best_model: bestRes })

      const selRes = await api.models.getSelection()
      set({ selectedModel: selRes.selection })
    } catch (e) {
      console.warn("[store] fetchAiStatus error:", e.message)
    }
  },

  setAiMode: async (mode) => {
    try {
      await api.models.setMode(mode)
      set({ ai_mode: mode })
      get().fetchAiStatus()
    } catch (e) {
      console.warn("[store] setAiMode error:", e.message)
    }
  },

  selectModel: async (modelName, provider, modelId) => {
    try {
      await api.models.select(modelName, provider, modelId)
      set({
        selectedModel: {
          auto: false,
          model_name: modelName,
          provider,
          model_id: modelId,
        },
      })
    } catch (e) {
      console.warn("[store] selectModel error:", e.message)
      throw e
    }
  },

  selectModelAuto: async () => {
    try {
      await api.models.selectAuto()
      set({ selectedModel: { auto: true } })
    } catch (e) {
      console.warn("[store] selectModelAuto error:", e.message)
      throw e
    }
  },

  // --- Profile / Onboarding ---
  fetchProfile: async () => {
    // Instant load from localStorage cache
    const cached = localStorage.getItem("peak_profile")
    if (cached) {
      try {
        const parsed = JSON.parse(cached)
        set({ profile: parsed, profileLoading: false })
        // Sync with backend in background (don't await)
        api.profile.get().then(profile => {
          if (profile) {
            set({ profile })
            localStorage.setItem("peak_profile", JSON.stringify(profile))
          } else {
            // Backend doesn't have a profile — clear stale cache
            localStorage.removeItem("peak_profile")
            set({ profile: null })
          }
        }).catch(() => {})
        return parsed
      } catch {}
    }
    // First time — fetch from API
    try {
      const profile = await api.profile.get()
      if (profile) {
        localStorage.setItem("peak_profile", JSON.stringify(profile))
      }
      set({ profile, profileLoading: false })
      return profile
    } catch (e) {
      set({ profileLoading: false })
      return null
    }
  },

  saveProfile: async (name, age) => {
    const profile = await api.profile.save({ name, age })
    set({ profile })
    localStorage.setItem("peak_profile", JSON.stringify(profile))
    return profile
  },

  uploadAvatar: async (file) => {
    const result = await api.profile.uploadAvatar(file)
    const updated = { ...get().profile, avatar_url: result.avatar_url }
    set({ profile: updated })
    localStorage.setItem("peak_profile", JSON.stringify(updated))
    return result
  },

  // --- Memory Game ---
  gameSession: null,
  currentRound: null,
  lastAttempt: null,
  gamePhase: 'idle', // idle | presenting | recalling | feedback | consolidating | done
  gameHistory: [],
  gameError: null,

  startMemoryGame: async (skillId) => {
    const session = await api.memoryGame.createSession(skillId)
    set({ gameSession: session, gamePhase: 'presenting', gameError: null })
    return session
  },

  createMemoryRound: async () => {
    const { gameSession } = get()
    const round = await api.memoryGame.createRound(gameSession.id)
    set({ currentRound: round, lastAttempt: null, gamePhase: 'presenting' })
    return round
  },

  submitMemoryAttempt: async (roundId, submittedNumbers) => {
    const result = await api.memoryGame.submitAttempt(roundId, submittedNumbers)
    set({ lastAttempt: result, gamePhase: 'feedback' })
    return result
  },

  consolidateMemoryGame: async () => {
    const { gameSession } = get()
    const result = await api.memoryGame.consolidate(gameSession.id)
    set({ gamePhase: 'done', lastAttempt: null, currentRound: null })
    return result
  },

  fetchMemoryState: async () => {
    const { gameSession } = get()
    const state = await api.memoryGame.getState(gameSession.id)
    return state
  },

  fetchMemoryHistory: async () => {
    const { gameSession } = get()
    const data = await api.memoryGame.getHistory(gameSession.id)
    set({ gameHistory: data.rounds })
    return data
  },

  resetMemoryGame: () => {
    set({
      gameSession: null,
      currentRound: null,
      lastAttempt: null,
      gamePhase: 'idle',
      gameHistory: [],
      gameError: null,
    })
  },

  // --- Math Thinking Game ---
  mathSession: null,
  mathCurrentRound: null,
  mathLastAttempt: null,
  mathPhase: 'idle', // idle | ready | answering | feedback | done
  mathHistory: [],
  mathError: null,
  mathStats: null,

  startMathThinking: async (skillId) => {
    const session = await api.mathThinking.createSession(skillId)
    set({ mathSession: session, mathPhase: 'ready', mathError: null })
    return session
  },

  createMathRound: async () => {
    const { mathSession } = get()
    const round = await api.mathThinking.createRound(mathSession.id)
    set({ mathCurrentRound: round, mathLastAttempt: null, mathPhase: 'answering' })
    return round
  },

  submitMathAttempt: async (roundId, userAnswer) => {
    const result = await api.mathThinking.submitAttempt(roundId, userAnswer)
    set({ mathLastAttempt: result, mathPhase: 'feedback' })
    return result
  },

  consolidateMathThinking: async () => {
    const { mathSession } = get()
    const result = await api.mathThinking.consolidate(mathSession.id)
    set({ mathPhase: 'done', mathLastAttempt: null, mathCurrentRound: null })
    return result
  },

  fetchMathState: async () => {
    const { mathSession } = get()
    const state = await api.mathThinking.getState(mathSession.id)
    return state
  },

  fetchMathHistory: async () => {
    const { mathSession } = get()
    const data = await api.mathThinking.getHistory(mathSession.id)
    set({ mathHistory: data.rounds })
    return data
  },

  resetMathThinking: () => {
    set({
      mathSession: null,
      mathCurrentRound: null,
      mathLastAttempt: null,
      mathPhase: 'idle',
      mathHistory: [],
      mathError: null,
      mathStats: null,
    })
  },

  clearError: () => set({ error: null })
}))
