import { describe, it, expect, vi, beforeEach } from "vitest"
import { create } from "zustand"
import { createMathGameSlice } from "../mathGame"

vi.mock("../../../api/client", () => ({
  api: {
    mathThinking: {
      createSession: vi.fn(),
      createRound: vi.fn(),
      submitAttempt: vi.fn(),
      consolidate: vi.fn(),
      getState: vi.fn(),
      getHistory: vi.fn(),
      getHint: vi.fn(),
    },
  },
}))

import { api } from "../../../api/client"

beforeEach(() => {
  vi.clearAllMocks()
})

describe("mathGame slice - initial state", () => {
  it("has correct initial state with math-specific extras", () => {
    const useTestStore = create((set, get) => createMathGameSlice(set, get))

    const state = useTestStore.getState()
    // Base game state with custom keys
    expect(state.mathSession).toBeNull()
    expect(state.mathCurrentRound).toBeNull()
    expect(state.mathLastAttempt).toBeNull()
    expect(state.mathPhase).toBe("idle")
    expect(state.mathHistory).toEqual([])
    expect(state.mathError).toBeNull()

    // Math-specific extra state
    expect(state.mathStats).toBeNull()
  })

  it("has all required action keys", () => {
    const useTestStore = create((set, get) => createMathGameSlice(set, get))

    const state = useTestStore.getState()
    const expectedActions = [
      "startMathThinking",
      "createMathRound",
      "submitMathAttempt",
      "consolidateMathThinking",
      "fetchMathState",
      "fetchMathHistory",
      "resetMathThinking",
    ]
    expectedActions.forEach((key) => {
      expect(state).toHaveProperty(key)
      expect(state[key]).toBeInstanceOf(Function)
    })
  })
})

describe("mathGame slice - game lifecycle", () => {
  it("startMathThinking calls api and sets mathPhase=ready", async () => {
    const session = { id: "math1" }
    api.mathThinking.createSession.mockResolvedValue(session)

    const useTestStore = create((set, get) => createMathGameSlice(set, get))

    const result = await useTestStore.getState().startMathThinking(1)

    expect(api.mathThinking.createSession).toHaveBeenCalledWith(1)
    expect(result).toEqual(session)
    const state = useTestStore.getState()
    expect(state.mathSession).toEqual(session)
    // startPhase for math game is "ready"
    expect(state.mathPhase).toBe("ready")
    expect(state.mathError).toBeNull()
  })

  it("createMathRound sets mathCurrentRound and mathPhase=answering", async () => {
    const session = { id: "math1" }
    const round = { id: "r1", problem_text: "2 + 2 = ?" }
    api.mathThinking.createSession.mockResolvedValue(session)
    api.mathThinking.createRound.mockResolvedValue(round)

    const useTestStore = create((set, get) => createMathGameSlice(set, get))

    await useTestStore.getState().startMathThinking(1)
    const result = await useTestStore.getState().createMathRound()

    expect(api.mathThinking.createRound).toHaveBeenCalledWith("math1")
    expect(result).toEqual(round)
    const state = useTestStore.getState()
    expect(state.mathCurrentRound).toEqual(round)
    expect(state.mathPhase).toBe("answering")
    expect(state.mathLastAttempt).toBeNull()
  })

  it("submitMathAttempt sets mathLastAttempt and mathPhase=feedback", async () => {
    const session = { id: "math1" }
    const round = { id: "r1" }
    const attempt = { id: "a1", correct: true, solution_steps: ["Step 1..."] }
    api.mathThinking.createSession.mockResolvedValue(session)
    api.mathThinking.createRound.mockResolvedValue(round)
    api.mathThinking.submitAttempt.mockResolvedValue(attempt)

    const useTestStore = create((set, get) => createMathGameSlice(set, get))

    await useTestStore.getState().startMathThinking(1)
    await useTestStore.getState().createMathRound()
    const result = await useTestStore.getState().submitMathAttempt("r1", 4)

    expect(api.mathThinking.submitAttempt).toHaveBeenCalledWith("r1", 4)
    expect(result).toEqual(attempt)
    const state = useTestStore.getState()
    expect(state.mathLastAttempt).toEqual(attempt)
    expect(state.mathPhase).toBe("feedback")
  })

  it("consolidateMathThinking sets mathPhase=done and clears round/attempt", async () => {
    const session = { id: "math1" }
    const round = { id: "r1" }
    const consolidation = { score: 90 }
    api.mathThinking.createSession.mockResolvedValue(session)
    api.mathThinking.createRound.mockResolvedValue(round)
    api.mathThinking.consolidate.mockResolvedValue(consolidation)

    const useTestStore = create((set, get) => createMathGameSlice(set, get))

    await useTestStore.getState().startMathThinking(1)
    await useTestStore.getState().createMathRound()
    const result = await useTestStore.getState().consolidateMathThinking()

    expect(api.mathThinking.consolidate).toHaveBeenCalledWith("math1", undefined)
    expect(result).toEqual(consolidation)
    const state = useTestStore.getState()
    expect(state.mathPhase).toBe("done")
    expect(state.mathLastAttempt).toBeNull()
    expect(state.mathCurrentRound).toBeNull()
  })

  it("consolidateMathThinking forwards elapsed_seconds when provided", async () => {
    const session = { id: "math1" }
    api.mathThinking.createSession.mockResolvedValue(session)
    api.mathThinking.consolidate.mockResolvedValue({ status: "ok" })

    const useTestStore = create((set, get) => createMathGameSlice(set, get))

    await useTestStore.getState().startMathThinking(1)
    await useTestStore.getState().consolidateMathThinking(60)

    expect(api.mathThinking.consolidate).toHaveBeenCalledWith("math1", { elapsed_seconds: 60 })
  })

  it("resetMathThinking resets all state to idle defaults", async () => {
    const session = { id: "math1" }
    api.mathThinking.createSession.mockResolvedValue(session)

    const useTestStore = create((set, get) => createMathGameSlice(set, get))

    await useTestStore.getState().startMathThinking(1)
    let state = useTestStore.getState()
    expect(state.mathSession).toEqual(session)

    useTestStore.getState().resetMathThinking()

    state = useTestStore.getState()
    expect(state.mathSession).toBeNull()
    expect(state.mathCurrentRound).toBeNull()
    expect(state.mathLastAttempt).toBeNull()
    expect(state.mathPhase).toBe("idle")
    expect(state.mathHistory).toEqual([])
    expect(state.mathError).toBeNull()
    // Extra state also resets
    expect(state.mathStats).toBeNull()
  })

  it("fetchMathState calls api and returns state", async () => {
    const session = { id: "math1" }
    const stateData = { level: 5, score: 75 }
    api.mathThinking.createSession.mockResolvedValue(session)
    api.mathThinking.getState.mockResolvedValue(stateData)

    const useTestStore = create((set, get) => createMathGameSlice(set, get))

    await useTestStore.getState().startMathThinking(1)
    const result = await useTestStore.getState().fetchMathState()

    expect(api.mathThinking.getState).toHaveBeenCalledWith("math1")
    expect(result).toEqual(stateData)
  })

  it("fetchMathHistory calls api and sets mathHistory", async () => {
    const session = { id: "math1" }
    const historyData = { rounds: [{ id: "r1", correct: true }] }
    api.mathThinking.createSession.mockResolvedValue(session)
    api.mathThinking.getHistory.mockResolvedValue(historyData)

    const useTestStore = create((set, get) => createMathGameSlice(set, get))

    await useTestStore.getState().startMathThinking(1)
    const result = await useTestStore.getState().fetchMathHistory()

    expect(api.mathThinking.getHistory).toHaveBeenCalledWith("math1")
    expect(result).toEqual(historyData)
    const state = useTestStore.getState()
    expect(state.mathHistory).toEqual(historyData.rounds)
  })
})
