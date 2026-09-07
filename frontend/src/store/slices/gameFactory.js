/**
 * Game slice factory — generates common Zustand game slices to eliminate
 * duplication across memory, math, and IQ game stores.
 *
 * Each game has identical patterns for session management, round creation,
 * attempt submission, consolidation, state fetching, and history.
 *
 * Usage:
 *
 *   import { createGameSlice } from "./gameFactory"
 *
 *   export const createMemoryGameSlice = (set, get) =>
 *     createGameSlice({
 *       apiModule: api.memoryGame,
 *       stateKeys: {
 *         session: "gameSession",
 *         round: "currentRound",
 *         attempt: "lastAttempt",
 *         phase: "gamePhase",
 *         history: "gameHistory",
 *         error: "gameError",
 *       },
 *       actionNames: {
 *         start: "startMemoryGame",
 *         createRound: "createMemoryRound",
 *         submitAttempt: "submitMemoryAttempt",
 *         consolidate: "consolidateMemoryGame",
 *         fetchState: "fetchMemoryState",
 *         fetchHistory: "fetchMemoryHistory",
 *         reset: "resetMemoryGame",
 *       },
 *       startPhase: "presenting",
 *       extraState: { ... },
 *       extraActions: { ... },
 *       afterSubmitAttempt: (set, get, result) => ({ ... }),
 *     })(set, get)
 */

export const createGameSlice = (config) => (set, get) => {
  const {
    apiModule,
    stateKeys = {},
    actionNames = {},
    startPhase = "ready",
    extraState = {},
    extraActions = {},
    afterStartSession = null,
    afterSubmitAttempt = null,
    afterConsolidate = null,
  } = config

  const keyPrefix = stateKeys.session
    ? stateKeys.session.replace(/Session$/, "")
    : ""

  const keys = {
    session: stateKeys.session || `${keyPrefix}Session`,
    round:
      stateKeys.round ||
      (keyPrefix === "game"
        ? "currentRound"
        : `${keyPrefix}CurrentRound`),
    attempt:
      stateKeys.attempt ||
      (keyPrefix === "game"
        ? "lastAttempt"
        : `${keyPrefix}LastAttempt`),
    phase: stateKeys.phase || `${keyPrefix}Phase`,
    history: stateKeys.history || `${keyPrefix}History`,
    error: stateKeys.error || `${keyPrefix}Error`,
  }

  // Infer action name defaults from keyPrefix
  const defaultActionName = (suffix) => {
    if (keyPrefix === "game") {
      const map = {
        start: "startMemoryGame",
        createRound: "createMemoryRound",
        submitAttempt: "submitMemoryAttempt",
        consolidate: "consolidateMemoryGame",
        fetchState: "fetchMemoryState",
        fetchHistory: "fetchMemoryHistory",
        reset: "resetMemoryGame",
      }
      return map[suffix]
    }
    const ucFirst = keyPrefix.charAt(0).toUpperCase() + keyPrefix.slice(1)
    const suffixMap = {
      start: `start${ucFirst}`,
      createRound: `create${ucFirst}Round`,
      submitAttempt: `submit${ucFirst}Attempt`,
      consolidate: `consolidate${ucFirst}`,
      fetchState: `fetch${ucFirst}State`,
      fetchHistory: `fetch${ucFirst}History`,
      reset: `reset${ucFirst}`,
    }
    return suffixMap[suffix]
  }

  const actions = {
    start: actionNames.start || defaultActionName("start"),
    createRound: actionNames.createRound || defaultActionName("createRound"),
    submitAttempt:
      actionNames.submitAttempt || defaultActionName("submitAttempt"),
    consolidate: actionNames.consolidate || defaultActionName("consolidate"),
    fetchState: actionNames.fetchState || defaultActionName("fetchState"),
    fetchHistory:
      actionNames.fetchHistory || defaultActionName("fetchHistory"),
    reset: actionNames.reset || defaultActionName("reset"),
  }

  // Snapshot initial extra state for reset
  const initialExtraValues = { ...extraState }

  return {
    /* ── State ────────────────────────────────── */
    [keys.session]: null,
    [keys.round]: null,
    [keys.attempt]: null,
    [keys.phase]: "idle",
    [keys.history]: [],
    [keys.error]: null,
    ...extraState,

    /* ── Actions ──────────────────────────────── */

    [actions.start]: async (skillId) => {
      const session = await apiModule.createSession(skillId)
      set({ [keys.session]: session, [keys.phase]: startPhase, [keys.error]: null })
      if (afterStartSession) afterStartSession(set, get, session)
      return session
    },

    [actions.createRound]: async () => {
      const s = get()[keys.session]
      const round = await apiModule.createRound(s.id)
      set({ [keys.round]: round, [keys.attempt]: null, [keys.phase]: "answering" })
      return round
    },

    [actions.submitAttempt]: async (roundId, ...args) => {
      const result = await apiModule.submitAttempt(roundId, ...args)
      const updates = { [keys.attempt]: result, [keys.phase]: "feedback" }
      if (afterSubmitAttempt) {
        Object.assign(updates, afterSubmitAttempt(set, get, result))
      }
      set(updates)
      return result
    },

    [actions.consolidate]: async (elapsedSeconds) => {
      const s = get()[keys.session]
      const body = elapsedSeconds != null ? { elapsed_seconds: elapsedSeconds } : undefined
      const result = await apiModule.consolidate(s.id, body)
      const updates = { [keys.phase]: "done", [keys.attempt]: null, [keys.round]: null }
      if (afterConsolidate) {
        Object.assign(updates, afterConsolidate(set, get, result))
      }
      set(updates)
      return result
    },

    [actions.fetchState]: async () => {
      const s = get()[keys.session]
      return await apiModule.getState(s.id)
    },

    [actions.fetchHistory]: async () => {
      const s = get()[keys.session]
      const data = await apiModule.getHistory(s.id)
      set({ [keys.history]: data.rounds })
      return data
    },

    [actions.reset]: () => {
      set({
        [keys.session]: null,
        [keys.round]: null,
        [keys.attempt]: null,
        [keys.phase]: "idle",
        [keys.history]: [],
        [keys.error]: null,
        ...initialExtraValues,
      })
    },

    /* ── Extra actions ────────────────────────── */
    ...extraActions,
  }
}
