import { api } from "../../api/client"

/**
 * Math Thinking slice — flat keys for backward compatibility.
 * Keys: mathSession, mathCurrentRound, mathLastAttempt, mathPhase, mathHistory, mathError, mathStats
 */
export const createMathGameSlice = (set, get) => ({
  // State
  mathSession: null,
  mathCurrentRound: null,
  mathLastAttempt: null,
  mathPhase: "idle",
  mathHistory: [],
  mathError: null,
  mathStats: null,

  // Actions
  startMathThinking: async (skillId) => {
    const session = await api.mathThinking.createSession(skillId)
    set({ mathSession: session, mathPhase: "ready", mathError: null })
    return session
  },

  createMathRound: async () => {
    const { mathSession } = get()
    const round = await api.mathThinking.createRound(mathSession.id)
    set({ mathCurrentRound: round, mathLastAttempt: null, mathPhase: "answering" })
    return round
  },

  submitMathAttempt: async (roundId, userAnswer) => {
    const result = await api.mathThinking.submitAttempt(roundId, userAnswer)
    set({ mathLastAttempt: result, mathPhase: "feedback" })
    return result
  },

  consolidateMathThinking: async () => {
    const { mathSession } = get()
    const result = await api.mathThinking.consolidate(mathSession.id)
    set({ mathPhase: "done", mathLastAttempt: null, mathCurrentRound: null })
    return result
  },

  fetchMathState: async () => {
    const { mathSession } = get()
    return await api.mathThinking.getState(mathSession.id)
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
      mathPhase: "idle",
      mathHistory: [],
      mathError: null,
      mathStats: null,
    })
  },
})
