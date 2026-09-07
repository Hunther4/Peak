import { describe, it, expect, vi, beforeEach } from "vitest"
import { create } from "zustand"
import { createMemoryGameSlice } from "../memoryGame"

// The real slice uses api.memoryGame — we mock api before importing the slice
vi.mock("../../../api/client", () => ({
  api: {
    memoryGame: {
      createSession: vi.fn(),
      createRound: vi.fn(),
      submitAttempt: vi.fn(),
      consolidate: vi.fn(),
      getState: vi.fn(),
      getHistory: vi.fn(),
      logStrategy: vi.fn(),
      saveMeta: vi.fn(),
    },
  },
}))

import { api } from "../../../api/client"

beforeEach(() => {
  vi.clearAllMocks()
})

describe("memoryGame slice - initial state", () => {
  it("has correct initial state with memory-specific extras", () => {
    const useTestStore = create((set, get) => createMemoryGameSlice(set, get))

    const state = useTestStore.getState()
    // Base game state with custom keys
    expect(state.gameSession).toBeNull()
    expect(state.currentRound).toBeNull()
    expect(state.lastAttempt).toBeNull()
    expect(state.gamePhase).toBe("idle")
    expect(state.gameHistory).toEqual([])
    expect(state.gameError).toBeNull()

    // Memory-specific extra state
    expect(state.consolidationResult).toBeNull()
    expect(state.roundStrategies).toEqual({})
    expect(state.sessionMeta).toEqual({
      strategy_type: "none",
      self_reported_difficulty: null,
      notes: "",
    })
    expect(state.metaSaved).toBe(false)
  })

  it("has all required action keys", () => {
    const useTestStore = create((set, get) => createMemoryGameSlice(set, get))

    const state = useTestStore.getState()
    const expectedActions = [
      "startMemoryGame",
      "createMemoryRound",
      "submitMemoryAttempt",
      "consolidateMemoryGame",
      "fetchMemoryState",
      "fetchMemoryHistory",
      "resetMemoryGame",
      "logRoundStrategy",
      "saveSessionMeta",
      "updateSessionMeta",
    ]
    expectedActions.forEach((key) => {
      expect(state).toHaveProperty(key)
      expect(state[key]).toBeInstanceOf(Function)
    })
  })
})

describe("memoryGame slice - game lifecycle", () => {
  it("startMemoryGame calls api and sets gamePhase=presenting", async () => {
    const session = { id: "mem1", rounds_completed: 0 }
    api.memoryGame.createSession.mockResolvedValue(session)

    const useTestStore = create((set, get) => createMemoryGameSlice(set, get))

    const result = await useTestStore.getState().startMemoryGame(1)

    expect(api.memoryGame.createSession).toHaveBeenCalledWith(1)
    expect(result).toEqual(session)
    const state = useTestStore.getState()
    expect(state.gameSession).toEqual(session)
    // startPhase for memory game is "presenting"
    expect(state.gamePhase).toBe("presenting")
  })

  it("createMemoryRound sets currentRound and gamePhase=answering", async () => {
    const session = { id: "mem1" }
    const round = { id: "r1", numbers: [3, 7, 1] }
    api.memoryGame.createSession.mockResolvedValue(session)
    api.memoryGame.createRound.mockResolvedValue(round)

    const useTestStore = create((set, get) => createMemoryGameSlice(set, get))

    await useTestStore.getState().startMemoryGame(1)
    const result = await useTestStore.getState().createMemoryRound()

    expect(api.memoryGame.createRound).toHaveBeenCalledWith("mem1")
    expect(result).toEqual(round)
    const state = useTestStore.getState()
    expect(state.currentRound).toEqual(round)
    expect(state.gamePhase).toBe("answering")
  })

  it("submitMemoryAttempt sets lastAttempt, bumps rounds_completed, sets phase=feedback", async () => {
    const session = { id: "mem1", rounds_completed: 0 }
    const round = { id: "r1" }
    const attempt = { id: "a1", correct: true }
    api.memoryGame.createSession.mockResolvedValue(session)
    api.memoryGame.createRound.mockResolvedValue(round)
    api.memoryGame.submitAttempt.mockResolvedValue(attempt)

    const useTestStore = create((set, get) => createMemoryGameSlice(set, get))

    await useTestStore.getState().startMemoryGame(1)
    await useTestStore.getState().createMemoryRound()
    const result = await useTestStore.getState().submitMemoryAttempt("r1", [3, 7, 1])

    expect(api.memoryGame.submitAttempt).toHaveBeenCalledWith("r1", [3, 7, 1])
    expect(result).toEqual(attempt)
    const state = useTestStore.getState()
    expect(state.lastAttempt).toEqual(attempt)
    expect(state.gamePhase).toBe("feedback")
    // afterSubmitAttempt bumps rounds_completed
    expect(state.gameSession.rounds_completed).toBe(1)
  })

  it("consolidateMemoryGame sets phase=done and stores consolidationResult", async () => {
    const session = { id: "mem1" }
    const consolidation = { score: 85, level: 4 }
    api.memoryGame.createSession.mockResolvedValue(session)
    api.memoryGame.consolidate.mockResolvedValue(consolidation)

    const useTestStore = create((set, get) => createMemoryGameSlice(set, get))

    await useTestStore.getState().startMemoryGame(1)
    await useTestStore.getState().consolidateMemoryGame()

    expect(api.memoryGame.consolidate).toHaveBeenCalledWith("mem1", undefined)
    const state = useTestStore.getState()
    expect(state.gamePhase).toBe("done")
    expect(state.consolidationResult).toEqual(consolidation)
  })

  it("resetMemoryGame resets all state to idle defaults", async () => {
    const session = { id: "mem1" }
    api.memoryGame.createSession.mockResolvedValue(session)

    const useTestStore = create((set, get) => createMemoryGameSlice(set, get))

    await useTestStore.getState().startMemoryGame(1)
    let state = useTestStore.getState()
    expect(state.gameSession).toEqual(session)

    useTestStore.getState().resetMemoryGame()

    state = useTestStore.getState()
    expect(state.gameSession).toBeNull()
    expect(state.currentRound).toBeNull()
    expect(state.lastAttempt).toBeNull()
    expect(state.gamePhase).toBe("idle")
    expect(state.gameHistory).toEqual([])
    expect(state.gameError).toBeNull()
    // Extra state is also reset
    expect(state.consolidationResult).toBeNull()
    expect(state.roundStrategies).toEqual({})
    expect(state.metaSaved).toBe(false)
  })
})

describe("memoryGame slice - memory-specific actions", () => {
  it("logRoundStrategy calls api and records strategy locally", async () => {
    const apiResult = { id: "log1", strategy_used: "chunking" }
    api.memoryGame.logStrategy.mockResolvedValue(apiResult)

    const useTestStore = create((set, get) => createMemoryGameSlice(set, get))

    const result = await useTestStore.getState().logRoundStrategy("r1", "chunking")

    expect(api.memoryGame.logStrategy).toHaveBeenCalledWith("r1", "chunking")
    expect(result).toEqual(apiResult)
    const state = useTestStore.getState()
    expect(state.roundStrategies).toEqual({ r1: "chunking" })
  })

  it("saveSessionMeta calls api and sets meta + metaSaved flag", async () => {
    const apiResult = { status: "saved" }
    api.memoryGame.saveMeta.mockResolvedValue(apiResult)

    const meta = {
      strategy_type: "visualization",
      self_reported_difficulty: 3,
      notes: "Used visualization technique",
    }

    const useTestStore = create((set, get) => createMemoryGameSlice(set, get))

    const result = await useTestStore.getState().saveSessionMeta("mem1", meta)

    expect(api.memoryGame.saveMeta).toHaveBeenCalledWith("mem1", meta)
    expect(result).toEqual(apiResult)
    const state = useTestStore.getState()
    expect(state.sessionMeta).toEqual(meta)
    expect(state.metaSaved).toBe(true)
  })

  it("updateSessionMeta patches sessionMeta without calling api", () => {
    const useTestStore = create((set, get) => createMemoryGameSlice(set, get))

    useTestStore.getState().updateSessionMeta({ self_reported_difficulty: 4 })

    const state = useTestStore.getState()
    expect(state.sessionMeta.self_reported_difficulty).toBe(4)
    // Other fields preserved
    expect(state.sessionMeta.strategy_type).toBe("none")
    expect(state.sessionMeta.notes).toBe("")
  })
})
