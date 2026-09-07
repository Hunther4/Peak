import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { MemoryTips } from "../MemoryTips"

const ALL_TIP_IDS = [
  "chunking",
  "visualization",
  "pattern",
  "rehearsal",
  "semantic",
  "interference",
]

function countRenderedTips() {
  return ALL_TIP_IDS.filter((id) =>
    screen.queryByTestId(`memory-tip-${id}`),
  ).length
}

describe("MemoryTips", () => {
  it("renders nothing when phase is presenting", () => {
    const { container } = render(<MemoryTips phase="presenting" />)
    expect(container.firstChild).toBeNull()
  })

  it("renders nothing when phase is done", () => {
    const { container } = render(<MemoryTips phase="done" />)
    expect(container.firstChild).toBeNull()
  })

  it("renders all 6 tips in a grid when phase is idle and not compact", () => {
    render(<MemoryTips phase="idle" compact={false} />)
    expect(countRenderedTips()).toBe(6)
    ALL_TIP_IDS.forEach((id) => {
      expect(screen.getByTestId(`memory-tip-${id}`)).toBeInTheDocument()
    })
  })

  it("renders 1 tip when phase is feedback and no currentTipId is set", () => {
    render(<MemoryTips phase="feedback" />)
    expect(countRenderedTips()).toBe(1)
  })

  it("renders the specific tip when currentTipId is set on feedback", () => {
    render(<MemoryTips phase="feedback" currentTipId="rehearsal" />)
    expect(screen.getByTestId("memory-tip-rehearsal")).toBeInTheDocument()
    expect(countRenderedTips()).toBe(1)
  })

  it("calls onDismiss when 'Ver todos los consejos' is clicked", () => {
    const onDismiss = vi.fn()
    render(<MemoryTips phase="feedback" onDismiss={onDismiss} />)
    fireEvent.click(screen.getByRole("button", { name: "Ver todos los consejos" }))
    expect(onDismiss).toHaveBeenCalledTimes(1)
  })

  it("does not show the dismiss button when onDismiss is not provided", () => {
    render(<MemoryTips phase="feedback" />)
    expect(
      screen.queryByRole("button", { name: "Ver todos los consejos" }),
    ).not.toBeInTheDocument()
  })

  it("renders 1 tip when compact=true and phase is idle (regression: compact applies outside feedback too)", () => {
    render(<MemoryTips phase="idle" compact={true} />)
    expect(countRenderedTips()).toBe(1)
  })

  it("renders title, body, and technique badge for each tip on idle", () => {
    render(<MemoryTips phase="idle" />)
    expect(screen.getByText("Agrupá en bloques")).toBeInTheDocument()
    expect(screen.getByText("Repaso")).toBeInTheDocument()
    expect(screen.getAllByText("Atención").length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText("Codificación").length).toBeGreaterThanOrEqual(1)
  })

  it("applies data-testid='memory-tips' to the root container on idle", () => {
    render(<MemoryTips phase="idle" />)
    expect(screen.getByTestId("memory-tips")).toBeInTheDocument()
  })

  it("applies data-testid='memory-tips' to the root container on feedback too", () => {
    render(<MemoryTips phase="feedback" onDismiss={() => {}} />)
    expect(screen.getByTestId("memory-tips")).toBeInTheDocument()
  })

  it("applies data-testid='memory-tip-{id}' to each tip card", () => {
    render(<MemoryTips phase="idle" />)
    ALL_TIP_IDS.forEach((id) => {
      expect(screen.getByTestId(`memory-tip-${id}`)).toBeInTheDocument()
    })
  })
})
