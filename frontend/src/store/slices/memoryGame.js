import { api } from "../../api/client"
import { createGameSlice } from "./gameFactory"

/**
 * Memory Game slice — flat keys for backward compatibility.
 * Keys: gameSession, currentRound, lastAttempt, gamePhase, gameHistory, gameError
 *
 * Memory-specific extras: logRoundStrategy, saveSessionMeta, updateSessionMeta,
 * roundStrategies, sessionMeta, metaSaved
 */
export const createMemoryGameSlice = (set, get) =>
  createGameSlice({
    apiModule: api.memoryGame,
    stateKeys: {
      session: "gameSession",
      round: "currentRound",
      attempt: "lastAttempt",
      phase: "gamePhase",
      history: "gameHistory",
      error: "gameError",
    },
    actionNames: {
      start: "startMemoryGame",
      createRound: "createMemoryRound",
      submitAttempt: "submitMemoryAttempt",
      consolidate: "consolidateMemoryGame",
      fetchState: "fetchMemoryState",
      fetchHistory: "fetchMemoryHistory",
      reset: "resetMemoryGame",
    },
    startPhase: "presenting",
    extraState: {
      consolidationResult: null,
      roundStrategies: {},
      sessionMeta: {
        strategy_type: "none",
        self_reported_difficulty: null,
        notes: "",
      },
      metaSaved: false,
    },
    afterSubmitAttempt: (set, get) => {
      const state = get()
      return {
        gameSession: state.gameSession
          ? { ...state.gameSession, rounds_completed: (state.gameSession.rounds_completed || 0) + 1 }
          : state.gameSession,
      }
    },
    afterConsolidate: (set, get, result) => ({
      consolidationResult: result,
    }),

    // Memory-specific actions
    extraActions: {
      logRoundStrategy: async (roundId, strategyUsed) => {
        const result = await api.memoryGame.logStrategy(roundId, strategyUsed)
        set((state) => ({
          roundStrategies: { ...state.roundStrategies, [roundId]: strategyUsed },
        }))
        return result
      },

      saveSessionMeta: async (sessionId, meta) => {
        const result = await api.memoryGame.saveMeta(sessionId, meta)
        set({ sessionMeta: meta, metaSaved: true })
        return result
      },

      updateSessionMeta: (patch) => {
        set((state) => ({ sessionMeta: { ...state.sessionMeta, ...patch } }))
      },
    },
  })(set, get)
