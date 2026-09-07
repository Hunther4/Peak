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

import { useStore } from "../../store/store"
import MemoryGame from "../MemoryGame"

function createMockState(overrides = {}) {
  return {
    gameSession: null,
    currentRound: null,
    lastAttempt: null,
    gamePhase: "idle",
    gameHistory: [],
    gameError: null,
    consolidationResult: null,
    roundStrategies: {},
    sessionMeta: { strategy_type: "none", self_reported_difficulty: null, notes: "" },
    metaSaved: false,
    createMemoryRound: vi.fn(),
    submitMemoryAttempt: vi.fn(),
    consolidateMemoryGame: vi.fn(),
    logRoundStrategy: vi.fn(),
    saveSessionMeta: vi.fn(),
    updateSessionMeta: vi.fn(),
    resetMemoryGame: vi.fn(),
    startMemoryGame: vi.fn(),
    ...overrides,
  }
}

describe("MemoryGame", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders idle phase without crashing", () => {
    useStore.mockReturnValue(createMockState())
    useStore.getState.mockReturnValue(createMockState())
    render(<MemoryGame skillId={1} />)
    // Title appears in both GameShell header and idle phase — use getAllByText
    expect(screen.getAllByText("Memoria de Números").length).toBeGreaterThanOrEqual(1)
  })

  it("shows start button in idle phase", () => {
    useStore.mockReturnValue(createMockState())
    useStore.getState.mockReturnValue(createMockState())
    render(<MemoryGame skillId={1} />)
    expect(screen.getByText("Comenzar")).toBeInTheDocument()
  })

  it("shows feature cards in idle phase", () => {
    useStore.mockReturnValue(createMockState())
    useStore.getState.mockReturnValue(createMockState())
    render(<MemoryGame skillId={1} />)
    expect(screen.getByText(/Secuencias cada vez más largas/)).toBeInTheDocument()
    expect(screen.getByText(/Tiempo ajustado por dígito/)).toBeInTheDocument()
    expect(screen.getByText(/Seguimiento de progreso/)).toBeInTheDocument()
  })

  it("shows memory tips toggle in idle phase", () => {
    useStore.mockReturnValue(createMockState())
    useStore.getState.mockReturnValue(createMockState())
    render(<MemoryGame skillId={1} />)
    expect(screen.getByLabelText("Ver consejos de memoria")).toBeInTheDocument()
  })

  it("renders recalling phase with input fields", () => {
    const round = { id: "r1", numbers: [3, 7, 1], span: 3, phase: "acquisition", timing: { base_ms: 1000 } }
    useStore.mockReturnValue(createMockState({ gamePhase: "recalling", currentRound: round }))
    useStore.getState.mockReturnValue(createMockState({ gamePhase: "recalling", currentRound: round }))
    render(<MemoryGame skillId={1} />)
    // Span appears in multiple places — use getAllByText
    expect(screen.getAllByText(/Span 3/).length).toBeGreaterThanOrEqual(1)
    // Enviar button present
    expect(screen.getByText("Enviar")).toBeInTheDocument()
  })

  it("renders feedback phase with results", () => {
    const round = { id: "r1", numbers: [3, 7, 1], span: 3, phase: "acquisition", timing: { base_ms: 1000 } }
    const lastAttempt = { correct: true, staircase_result: { new_span: 3, new_phase: 1 }, numbers: [3, 7, 1] }
    useStore.mockReturnValue(createMockState({
      gamePhase: "feedback",
      currentRound: round,
      lastAttempt,
    }))
    useStore.getState.mockReturnValue(createMockState({
      gamePhase: "feedback",
      currentRound: round,
      lastAttempt,
    }))
    render(<MemoryGame skillId={1} />)
    expect(screen.getByText("Resultados")).toBeInTheDocument()
    expect(screen.getByText("Siguiente ronda")).toBeInTheDocument()
  })

  it("renders done phase with completion message", () => {
    useStore.mockReturnValue(createMockState({
      gamePhase: "done",
      gameSession: { id: "s1", rounds_completed: 5, best_span: 3, best_phase: 1 },
    }))
    useStore.getState.mockReturnValue(createMockState({
      gamePhase: "done",
      gameSession: { id: "s1", rounds_completed: 5, best_span: 3, best_phase: 1 },
    }))
    render(<MemoryGame skillId={1} />)
    expect(screen.getByText("¡Sesión completada!")).toBeInTheDocument()
    expect(screen.getByText("Volver al inicio")).toBeInTheDocument()
  })

  it("displays game error when gameError is set", () => {
    const errMsg = "Error de conexión"
    useStore.mockReturnValue(createMockState({ gameError: errMsg }))
    useStore.getState.mockReturnValue(createMockState({ gameError: errMsg }))
    render(<MemoryGame skillId={1} />)
    expect(screen.getByText(errMsg)).toBeInTheDocument()
  })
})
