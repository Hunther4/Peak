import { describe, it, expect, vi } from "vitest"
import { render, screen } from "@testing-library/react"

// Mock store with minimal state
vi.mock("../store/store", () => ({
  useStore: () => ({
    mathSession: null,
    mathCurrentRound: null,
    mathLastAttempt: null,
    mathPhase: "idle",
    mathHistory: [],
    mathError: null,
    mathStats: null,
    startMathThinking: vi.fn(),
    createMathRound: vi.fn(),
    submitMathAttempt: vi.fn(),
    consolidateMathThinking: vi.fn(),
    resetMathThinking: vi.fn(),
    fetchMathState: vi.fn(),
    fetchMathHistory: vi.fn(),
  }),
}))

vi.mock("../hooks", () => ({
  useSessionTimer: () => ({ elapsedSeconds: 0, formatTime: () => "00:00", reset: vi.fn() }),
}))

import MathThinkingGame from "../MathThinkingGame"

describe("MathThinkingGame", () => {
  it("renders idle phase with title and start button", () => {
    render(<MathThinkingGame skillId={1} />)
    expect(screen.getAllByText("Pensamiento Matemático").length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText("Comenzar")).toBeInTheDocument()
  })

  it("shows feature descriptions in idle phase", () => {
    render(<MathThinkingGame skillId={1} />)
    expect(screen.getByText(/Problemas según tu nivel/)).toBeInTheDocument()
    expect(screen.getByText(/Dificultad adaptativa/)).toBeInTheDocument()
    expect(screen.getByText(/Pistas y solución paso a paso/)).toBeInTheDocument()
  })
})
