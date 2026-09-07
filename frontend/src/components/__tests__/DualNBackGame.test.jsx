import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"

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
    cognitive: {
      getSkills: vi.fn().mockResolvedValue([]),
      createSession: vi.fn(),
      uploadTrials: vi.fn(),
      finalizeSession: vi.fn(),
      consolidate: vi.fn(),
    },
  },
  api: {
    cognitive: {
      getSkills: vi.fn().mockResolvedValue([]),
      createSession: vi.fn(),
      uploadTrials: vi.fn(),
      finalizeSession: vi.fn(),
      consolidate: vi.fn(),
    },
  },
}))

const speechSynthesisMock = {
  speak: vi.fn(),
  cancel: vi.fn(),
  getVoices: vi.fn().mockReturnValue([]),
}

import { useStore } from "../../store/store"
import DualNBackGame from "../DualNBackGame"

function createMockState(overrides = {}) {
  return {
    consolidateDualNBack: vi.fn(),
    ...overrides,
  }
}

describe("DualNBackGame", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.defineProperty(window, "speechSynthesis", {
      value: speechSynthesisMock,
      writable: true,
      configurable: true,
    })
  })

  it("renders setup phase without crashing", () => {
    useStore.mockReturnValue(createMockState())
    useStore.getState.mockReturnValue(createMockState())
    render(<DualNBackGame />)
    // Title appears in GameShell header and possibly elsewhere
    expect(screen.getAllByText(/Dual N-Back/).length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText("Iniciar Entrenamiento")).toBeInTheDocument()
  })

  it("shows N-level selection in setup phase", () => {
    useStore.mockReturnValue(createMockState())
    useStore.getState.mockReturnValue(createMockState())
    render(<DualNBackGame />)
    // Level buttons
    for (let i = 1; i <= 5; i++) {
      expect(screen.getByText(i.toString())).toBeInTheDocument()
    }
  })

  it("shows key legend (A, W, D)", () => {
    useStore.mockReturnValue(createMockState())
    useStore.getState.mockReturnValue(createMockState())
    render(<DualNBackGame />)
    // The key legend kbd elements show A, W, D — multiple matches in playing phase
    expect(screen.getAllByText("A").length).toBeGreaterThan(0)
    expect(screen.getAllByText("W").length).toBeGreaterThan(0)
    expect(screen.getAllByText("D").length).toBeGreaterThan(0)
  })

  it("renders setup instructions for N=1 example", () => {
    useStore.mockReturnValue(createMockState())
    useStore.getState.mockReturnValue(createMockState())
    render(<DualNBackGame />)
    expect(screen.getByText(/Cómo funciona/)).toBeInTheDocument()
  })

  it("transitions to playing phase and displays interactive buttons on start", () => {
    useStore.mockReturnValue(createMockState())
    useStore.getState.mockReturnValue(createMockState())
    render(<DualNBackGame />)

    const startBtn = screen.getByText("Iniciar Entrenamiento")
    fireEvent.click(startBtn)

    expect(screen.getByText(/Bloque/)).toBeInTheDocument()
    expect(screen.getByText(/Posición/)).toBeInTheDocument()
    expect(screen.getByText(/Letra/)).toBeInTheDocument()
    expect(screen.getByText(/Ambos/)).toBeInTheDocument()
  })
})
