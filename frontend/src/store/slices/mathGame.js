import { api } from "../../api/client"
import { createGameSlice } from "./gameFactory"

/**
 * Math Thinking slice — flat keys for backward compatibility.
 * Keys: mathSession, mathCurrentRound, mathLastAttempt, mathPhase, mathHistory,
 *        mathError, mathStats
 */
export const createMathGameSlice = (set, get) =>
  createGameSlice({
    apiModule: api.mathThinking,
    stateKeys: {
      session: "mathSession",
      round: "mathCurrentRound",
      attempt: "mathLastAttempt",
      phase: "mathPhase",
      history: "mathHistory",
      error: "mathError",
    },
    actionNames: {
      start: "startMathThinking",
      createRound: "createMathRound",
      submitAttempt: "submitMathAttempt",
      consolidate: "consolidateMathThinking",
      fetchState: "fetchMathState",
      fetchHistory: "fetchMathHistory",
      reset: "resetMathThinking",
    },
    startPhase: "ready",
    extraState: {
      mathStats: null,
    },
  })(set, get)
