import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen } from "@testing-library/react"

vi.mock("../../store/store", () => ({
  useStore: Object.assign(vi.fn(), { getState: vi.fn(), setState: vi.fn() }),
}))

vi.mock("../../hooks", () => ({
  useSessionTimer: () => ({
    elapsedSeconds: 0,
    formatTime: () => "00:00",
    reset: vi.fn(),
    pause: vi.fn(),
    resume: vi.fn(),
  }),
}))

vi.mock("../../api/client", () => ({
  default: {
    iqPractice: {
      createRound: vi.fn(),
    },
    sessions: {
      getAll: vi.fn().mockResolvedValue([]),
    },
  },
}))

import { useStore } from "../../store/store"
import IQPracticeGame from "../IQPracticeGame"

function createMockState(overrides = {}) {
  return {
    iqSession: null,
    iqCurrentRound: null,
    iqLastAttempt: null,
    iqPhase: "idle",
    iqHistory: [],
    iqError: null,
    startIQPractice: vi.fn(),
    createIQRound: vi.fn(),
    submitIQAttempt: vi.fn(),
    consolidateIQPractice: vi.fn(),
    resetIQPractice: vi.fn(),
    fetchSummary: vi.fn(),
    fetchTimeline: vi.fn(),
    ...overrides,
  }
}

describe("IQPracticeGame", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders idle phase without crashing", () => {
    useStore.mockReturnValue(createMockState())
    useStore.getState.mockReturnValue(createMockState())
    render(<IQPracticeGame skillId={1} />)
    expect(screen.getAllByText("Práctica de IQ").length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText("Comenzar Práctica")).toBeInTheDocument()
  })

  it("shows puzzle type descriptions in idle phase", () => {
    useStore.mockReturnValue(createMockState())
    useStore.getState.mockReturnValue(createMockState())
    render(<IQPracticeGame skillId={1} />)
    expect(screen.getByText("Secuencia Numérica")).toBeInTheDocument()
    expect(screen.getByText("Analogía Verbal")).toBeInTheDocument()
    expect(screen.getByText("Razonamiento Lógico")).toBeInTheDocument()
    expect(screen.getByText("Reconocimiento de Patrones")).toBeInTheDocument()
  })

  it("renders loading phase", () => {
    useStore.mockReturnValue(createMockState({ iqPhase: "loading" }))
    useStore.getState.mockReturnValue(createMockState({ iqPhase: "loading" }))
    render(<IQPracticeGame skillId={1} />)
    expect(screen.getByText("Generando puzzle...")).toBeInTheDocument()
  })

  it("renders answering phase with question and options", () => {
    const round = {
      id: "r1",
      puzzle_type: "number_sequence",
      question: "What comes next: 1, 1, 2, 3, 5, ?",
      options: ["7", "8", "9", "10"],
      correct_answer: "8",
    }
    useStore.mockReturnValue(createMockState({
      iqPhase: "answering",
      iqCurrentRound: round,
    }))
    useStore.getState.mockReturnValue(createMockState({
      iqPhase: "answering",
      iqCurrentRound: round,
    }))
    render(<IQPracticeGame skillId={1} />)
    expect(screen.getByText(/What comes next/)).toBeInTheDocument()
    expect(screen.getByText("7")).toBeInTheDocument()
    expect(screen.getByText("8")).toBeInTheDocument()
    expect(screen.getByText("9")).toBeInTheDocument()
    expect(screen.getByText("10")).toBeInTheDocument()
    expect(screen.getByText("Confirmar respuesta")).toBeInTheDocument()
  })

  it("renders feedback phase with result", () => {
    const round = {
      id: "r1",
      puzzle_type: "number_sequence",
      question: "Test?",
      options: ["A", "B", "C", "D"],
      correct_answer: "B",
    }
    useStore.mockReturnValue(createMockState({
      iqPhase: "feedback",
      iqCurrentRound: round,
      iqLastAttempt: { correct: true, explanation: "Well done!", staircase_result: { new_consecutive_correct: 1, new_consecutive_incorrect: 0, new_level: 2, message: "Level up!" } },
    }))
    useStore.getState.mockReturnValue(createMockState({
      iqPhase: "feedback",
      iqCurrentRound: round,
      iqLastAttempt: { correct: true, explanation: "Well done!", staircase_result: { new_consecutive_correct: 1, new_consecutive_incorrect: 0, new_level: 2, message: "Level up!" } },
    }))
    render(<IQPracticeGame skillId={1} />)
    expect(screen.getByText("¡Correcto!")).toBeInTheDocument()
    expect(screen.getByText("Siguiente puzzle")).toBeInTheDocument()
  })

  it("renders done phase with completion message", () => {
    useStore.mockReturnValue(createMockState({
      iqPhase: "done",
      iqSession: { id: "s1" },
    }))
    useStore.getState.mockReturnValue(createMockState({
      iqPhase: "done",
      iqSession: { id: "s1" },
    }))
    render(<IQPracticeGame skillId={1} />)
    expect(screen.getByText("¡Sesión completada!")).toBeInTheDocument()
    expect(screen.getByText("Volver al inicio")).toBeInTheDocument()
  })
})
