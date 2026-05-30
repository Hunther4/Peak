import { api } from "../../api/client"

/**
 * Memory Game slice — flat keys for backward compatibility.
 * Keys: gameSession, currentRound, lastAttempt, gamePhase, gameHistory, gameError
 */
export const createMemoryGameSlice = (set, get) => ({
  // State
  gameSession: null,
  currentRound: null,
  lastAttempt: null,
  gamePhase: "idle",
  gameHistory: [],
  gameError: null,

  // Actions
  startMemoryGame: async (skillId) => {
    const session = await api.memoryGame.createSession(skillId)
    set({ gameSession: session, gamePhase: "presenting", gameError: null })
    return session
  },

  createMemoryRound: async () => {
    const { gameSession } = get()
    const round = await api.memoryGame.createRound(gameSession.id)
    set({ currentRound: round, lastAttempt: null, gamePhase: "presenting" })
    return round
  },

  submitMemoryAttempt: async (roundId, submittedNumbers) => {
    const result = await api.memoryGame.submitAttempt(roundId, submittedNumbers)
    set({ lastAttempt: result, gamePhase: "feedback" })
    return result
  },

  consolidateMemoryGame: async () => {
    const { gameSession } = get()
    const result = await api.memoryGame.consolidate(gameSession.id)
    set({ gamePhase: "done", lastAttempt: null, currentRound: null })
    return result
  },

  fetchMemoryState: async () => {
    const { gameSession } = get()
    return await api.memoryGame.getState(gameSession.id)
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
      gamePhase: "idle",
      gameHistory: [],
      gameError: null,
    })
  },
})
