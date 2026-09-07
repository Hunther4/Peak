import { describe, it, expect, vi, beforeEach } from "vitest"
import { create } from "zustand"
import { createGameSlice } from "../gameFactory"

/** Minimal API module that returns mockable functions. */
function createMockApi() {
  return {
    createSession: vi.fn(),
    createRound: vi.fn(),
    submitAttempt: vi.fn(),
    consolidate: vi.fn(),
    getState: vi.fn(),
    getHistory: vi.fn(),
  }
}

let mockApi

beforeEach(() => {
  mockApi = createMockApi()
})

/**
 * Helper: create a store using createGameSlice with the given config.
 */
function buildStore(cfg = {}) {
  return create((set, get) =>
    createGameSlice({
      apiModule: mockApi,
      ...cfg,
    })(set, get),
  )
}

/*
 * The factory infers keys/actions from keyPrefix (derived from stateKeys.session).
 * When no stateKeys: keyPrefix = "" → uppercase state keys (Session, CurrentRound...)
 * but bare action names (start, createRound, submitAttempt, consolidate, etc.)
 *
 * When stateKeys.session = "gameSession": keyPrefix = "game" → hardcoded memory
 * game names (startMemoryGame, createMemoryRound, etc.)
 */

describe("createGameSlice - initial state", () => {
  it("creates default state keys when no stateKeys provided", () => {
    const useTestStore = buildStore()

    const state = useTestStore.getState()
    // With empty keyPrefix, inferred keys are capitalized: Session, CurrentRound...
    expect(state.Session).toBeNull()
    expect(state.CurrentRound).toBeNull()
    expect(state.LastAttempt).toBeNull()
    expect(state.Phase).toBe("idle")
    expect(state.History).toEqual([])
    expect(state.Error).toBeNull()
  })

  it("uses custom stateKeys when provided", () => {
    const useTestStore = buildStore({
      stateKeys: {
        session: "gameSession",
        round: "currentRound",
        attempt: "lastAttempt",
        phase: "gamePhase",
        history: "gameHistory",
        error: "gameError",
      },
    })

    const state = useTestStore.getState()
    expect(state.gameSession).toBeNull()
    expect(state.currentRound).toBeNull()
    expect(state.lastAttempt).toBeNull()
    expect(state.gamePhase).toBe("idle")
    expect(state.gameHistory).toEqual([])
    expect(state.gameError).toBeNull()
  })

  it("includes extraState in initial state", () => {
    const useTestStore = buildStore({
      extraState: {
        mathStats: null,
        customFlag: true,
      },
    })

    const state = useTestStore.getState()
    expect(state.mathStats).toBeNull()
    expect(state.customFlag).toBe(true)
  })

  it("infers action names from keyPrefix when not provided", () => {
    // stateKeys.session = "mySession" → keyPrefix = "my" → action prefix "My"
    const useTestStore = buildStore({
      stateKeys: { session: "mySession" },
    })

    const state = useTestStore.getState()
    expect(state.startMy).toBeInstanceOf(Function)
    expect(state.createMyRound).toBeInstanceOf(Function)
    expect(state.submitMyAttempt).toBeInstanceOf(Function)
    expect(state.consolidateMy).toBeInstanceOf(Function)
    expect(state.resetMy).toBeInstanceOf(Function)
  })
})

describe("createGameSlice - actions (default config, no stateKeys)", () => {
  /*
   * With the default config (no stateKeys), keyPrefix = "" so actions
   * get bare names: start, createRound, submitAttempt, consolidate, etc.
   * This is the simplest config to test action behavior.
   */

  it("start calls apiModule.createSession and sets state", async () => {
    const session = { id: "sess1", rounds_completed: 0 }
    mockApi.createSession.mockResolvedValue(session)

    const useTestStore = buildStore({ startPhase: "ready" })

    const result = await useTestStore.getState().start(1)

    expect(mockApi.createSession).toHaveBeenCalledWith(1)
    expect(result).toEqual(session)
    const state = useTestStore.getState()
    expect(state.Session).toEqual(session)
    expect(state.Phase).toBe("ready")
    expect(state.Error).toBeNull()
  })

  it("createRound calls apiModule and sets round + answering phase", async () => {
    const session = { id: "sess1" }
    const round = { id: "round1", problem: "2 + 2" }
    mockApi.createSession.mockResolvedValue(session)
    mockApi.createRound.mockResolvedValue(round)

    const useTestStore = buildStore()

    await useTestStore.getState().start(1)
    const result = await useTestStore.getState().createRound()

    expect(mockApi.createRound).toHaveBeenCalledWith("sess1")
    expect(result).toEqual(round)
    const state = useTestStore.getState()
    expect(state.CurrentRound).toEqual(round)
    expect(state.Phase).toBe("answering")
    expect(state.LastAttempt).toBeNull()
  })

  it("submitAttempt calls apiModule and sets attempt + feedback phase", async () => {
    const session = { id: "sess1" }
    const round = { id: "round1" }
    const attempt = { id: "a1", correct: true }
    mockApi.createSession.mockResolvedValue(session)
    mockApi.createRound.mockResolvedValue(round)
    mockApi.submitAttempt.mockResolvedValue(attempt)

    const useTestStore = buildStore()

    await useTestStore.getState().start(1)
    await useTestStore.getState().createRound()
    const result = await useTestStore.getState().submitAttempt("round1", "42")

    expect(mockApi.submitAttempt).toHaveBeenCalledWith("round1", "42")
    expect(result).toEqual(attempt)
    const state = useTestStore.getState()
    expect(state.LastAttempt).toEqual(attempt)
    expect(state.Phase).toBe("feedback")
  })

  it("consolidate calls apiModule and sets phase to done", async () => {
    const session = { id: "sess1" }
    const round = { id: "round1" }
    const consolidation = { score: 100 }
    mockApi.createSession.mockResolvedValue(session)
    mockApi.createRound.mockResolvedValue(round)
    mockApi.consolidate.mockResolvedValue(consolidation)

    const useTestStore = buildStore()

    await useTestStore.getState().start(1)
    await useTestStore.getState().createRound()
    const result = await useTestStore.getState().consolidate()

    expect(mockApi.consolidate).toHaveBeenCalledWith("sess1", undefined)
    expect(result).toEqual(consolidation)
    const state = useTestStore.getState()
    expect(state.Phase).toBe("done")
    expect(state.LastAttempt).toBeNull()
    expect(state.CurrentRound).toBeNull()
  })

  it("consolidate forwards elapsed_seconds when provided", async () => {
    const session = { id: "sess1" }
    mockApi.createSession.mockResolvedValue(session)
    mockApi.consolidate.mockResolvedValue({ status: "ok" })

    const useTestStore = buildStore()

    await useTestStore.getState().start(1)
    await useTestStore.getState().consolidate(42)

    expect(mockApi.consolidate).toHaveBeenCalledWith("sess1", { elapsed_seconds: 42 })
  })

  it("reset clears all state to idle defaults", async () => {
    const session = { id: "sess1" }
    mockApi.createSession.mockResolvedValue(session)

    const useTestStore = buildStore({
      extraState: { extraField: "preserve-me" },
    })

    await useTestStore.getState().start(1)
    let state = useTestStore.getState()
    expect(state.Session).toEqual(session)

    useTestStore.getState().reset()

    state = useTestStore.getState()
    expect(state.Session).toBeNull()
    expect(state.CurrentRound).toBeNull()
    expect(state.LastAttempt).toBeNull()
    expect(state.Phase).toBe("idle")
    expect(state.History).toEqual([])
    expect(state.Error).toBeNull()
    // extraState keys are restored to initial values
    expect(state.extraField).toBe("preserve-me")
  })

  it("fetchState calls apiModule.getState", async () => {
    const session = { id: "sess1" }
    const stateData = { level: 3, score: 50 }
    mockApi.createSession.mockResolvedValue(session)
    mockApi.getState.mockResolvedValue(stateData)

    const useTestStore = buildStore()

    await useTestStore.getState().start(1)
    const result = await useTestStore.getState().fetchState()

    expect(mockApi.getState).toHaveBeenCalledWith("sess1")
    expect(result).toEqual(stateData)
  })

  it("fetchHistory calls apiModule and sets history", async () => {
    const session = { id: "sess1" }
    const historyData = { rounds: [{ id: "r1", correct: true }] }
    mockApi.createSession.mockResolvedValue(session)
    mockApi.getHistory.mockResolvedValue(historyData)

    const useTestStore = buildStore()

    await useTestStore.getState().start(1)
    const result = await useTestStore.getState().fetchHistory()

    expect(mockApi.getHistory).toHaveBeenCalledWith("sess1")
    expect(result).toEqual(historyData)
    const state = useTestStore.getState()
    expect(state.History).toEqual(historyData.rounds)
  })

  it("supports afterSubmitAttempt callback to merge extra updates", async () => {
    const session = { id: "sess1" }
    const round = { id: "r1" }
    const attempt = { correct: true }
    mockApi.createSession.mockResolvedValue(session)
    mockApi.createRound.mockResolvedValue(round)
    mockApi.submitAttempt.mockResolvedValue(attempt)

    const useTestStore = buildStore({
      afterSubmitAttempt: () => ({ extraCounter: 42 }),
    })

    await useTestStore.getState().start(1)
    await useTestStore.getState().createRound()
    await useTestStore.getState().submitAttempt("r1", "42")

    const state = useTestStore.getState()
    expect(state.extraCounter).toBe(42)
  })

  it("supports afterConsolidate callback to merge extra updates", async () => {
    const session = { id: "sess1" }
    mockApi.createSession.mockResolvedValue(session)
    mockApi.consolidate.mockResolvedValue({ score: 100 })

    const useTestStore = buildStore({
      afterConsolidate: (set, get, result) => ({
        consolidationResult: result,
      }),
    })

    await useTestStore.getState().start(1)
    await useTestStore.getState().consolidate()

    const state = useTestStore.getState()
    expect(state.consolidationResult).toEqual({ score: 100 })
  })

  it("includes extraActions in the slice", () => {
    const useTestStore = buildStore({
      extraActions: {
        doCustomThing: vi.fn(),
        anotherAction: () => "result",
      },
    })

    const state = useTestStore.getState()
    expect(state.doCustomThing).toBeInstanceOf(Function)
    expect(state.anotherAction).toBeInstanceOf(Function)
  })
})

describe("createGameSlice - action keys present", () => {
  it("exposes all standard action keys with default config", () => {
    const useTestStore = buildStore()

    const state = useTestStore.getState()
    // With no stateKeys, keyPrefix = "" → bare action names
    expect(state.start).toBeInstanceOf(Function)
    expect(state.createRound).toBeInstanceOf(Function)
    expect(state.submitAttempt).toBeInstanceOf(Function)
    expect(state.consolidate).toBeInstanceOf(Function)
    expect(state.fetchState).toBeInstanceOf(Function)
    expect(state.fetchHistory).toBeInstanceOf(Function)
    expect(state.reset).toBeInstanceOf(Function)
  })

  it("uses custom actionNames when provided", () => {
    const useTestStore = buildStore({
      stateKeys: { session: "s", round: "r", attempt: "a", phase: "p", history: "h", error: "e" },
      actionNames: {
        start: "myStart",
        reset: "myReset",
      },
    })

    const state = useTestStore.getState()
    expect(state.myStart).toBeInstanceOf(Function)
    expect(state.myReset).toBeInstanceOf(Function)
    // Inferred from keyPrefix = "s" → ucFirst = "S"
    // createRound → createSRound
    expect(state.createSRound).toBeInstanceOf(Function)
    expect(state.submitSAttempt).toBeInstanceOf(Function)
  })
})
