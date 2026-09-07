import { api } from "../../api/client"

export const createMentalSlice = (set, get) => ({
  // State
  mentalReps: [],
  challenges: [],
  pendingChallenges: 0,
  generatingRep: false,
  generatingChallenge: false,

  // Actions
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
  }
})