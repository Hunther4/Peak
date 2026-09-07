import { api } from "../../api/client"
import { createGameSlice } from "./gameFactory"

/**
 * IQ Practice slice — flat keys for backward compatibility.
 * Keys: iqSession, iqCurrentRound, iqLastAttempt, iqPhase, iqHistory, iqError
 */
export const createIQGameSlice = (set, get) =>
  createGameSlice({
    apiModule: api.iqPractice,
    stateKeys: {
      session: "iqSession",
      round: "iqCurrentRound",
      attempt: "iqLastAttempt",
      phase: "iqPhase",
      history: "iqHistory",
      error: "iqError",
    },
    actionNames: {
      start: "startIQPractice",
      createRound: "createIQRound",
      submitAttempt: "submitIQAttempt",
      consolidate: "consolidateIQPractice",
      fetchState: "fetchIQState",
      fetchHistory: "fetchIQHistory",
      reset: "resetIQPractice",
    },
    startPhase: "loading",
  })(set, get)
