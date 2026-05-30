import { api } from "../../api/client"

/**
 * IQ Practice slice — flat keys for backward compatibility.
 * Keys: iqSession, iqCurrentRound, iqLastAttempt, iqPhase, iqHistory, iqError
 */
export const createIQGameSlice = (set, get) => ({
  // State
  iqSession: null,
  iqCurrentRound: null,
  iqLastAttempt: null,
  iqPhase: "idle",
  iqHistory: [],
  iqError: null,

  // Actions
  startIQPractice: async (skillId) => {
    const session = await api.iqPractice.createSession(skillId)
    set({ iqSession: session, iqPhase: "answering", iqError: null })
    return session
  },

  createIQRound: async () => {
    const { iqSession } = get()
    const round = await api.iqPractice.createRound(iqSession.id)
    set({ iqCurrentRound: round, iqLastAttempt: null, iqPhase: "answering" })
    return round
  },

  submitIQAttempt: async (roundId, userAnswer) => {
    const result = await api.iqPractice.submitAttempt(roundId, userAnswer)
    set({ iqLastAttempt: result, iqPhase: "feedback" })
    return result
  },

  consolidateIQPractice: async () => {
    const { iqSession } = get()
    const result = await api.iqPractice.consolidate(iqSession.id)
    set({ iqPhase: "done", iqLastAttempt: null, iqCurrentRound: null })
    return result
  },

  fetchIQState: async () => {
    const { iqSession } = get()
    return await api.iqPractice.getState(iqSession.id)
  },

  fetchIQHistory: async () => {
    const { iqSession } = get()
    const data = await api.iqPractice.getHistory(iqSession.id)
    set({ iqHistory: data.rounds })
    return data
  },

  resetIQPractice: () => {
    set({
      iqSession: null,
      iqCurrentRound: null,
      iqLastAttempt: null,
      iqPhase: "idle",
      iqHistory: [],
      iqError: null,
    })
  },
})
