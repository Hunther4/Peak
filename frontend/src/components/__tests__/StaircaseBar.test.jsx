import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { StaircaseBar } from "../StaircaseBar"

describe("StaircaseBar", () => {
  it("renders correct/5 and incorrect/3 at level 1", () => {
    render(<StaircaseBar correct={2} incorrect={1} level={1} />)
    expect(screen.getByText("2/5")).toBeInTheDocument()
    expect(screen.getByText("1/3")).toBeInTheDocument()
  })

  it("renders correct/5 and incorrect/3 at level 3", () => {
    render(<StaircaseBar correct={1} incorrect={0} level={3} />)
    expect(screen.getByText("1/5")).toBeInTheDocument()
    expect(screen.getByText("0/3")).toBeInTheDocument()
  })

  it("renders correct/5 and incorrect/3 at level 5", () => {
    render(<StaircaseBar correct={0} incorrect={0} level={5} />)
    expect(screen.getByText("0/5")).toBeInTheDocument()
    expect(screen.getByText("0/3")).toBeInTheDocument()
  })

  it("renders correct/5 and incorrect/3 at level 8", () => {
    render(<StaircaseBar correct={4} incorrect={2} level={8} />)
    expect(screen.getByText("4/5")).toBeInTheDocument()
    expect(screen.getByText("2/3")).toBeInTheDocument()
  })

  it("defaults to level 1 when level is omitted", () => {
    render(<StaircaseBar correct={3} incorrect={0} />)
    expect(screen.getByText("3/5")).toBeInTheDocument()
    expect(screen.getByText("0/3")).toBeInTheDocument()
  })

  it("exposes aria labels for accessibility", () => {
    render(<StaircaseBar correct={2} incorrect={1} level={3} />)
    expect(screen.getByLabelText("Aciertos consecutivos: 2 de 5")).toBeInTheDocument()
    expect(screen.getByLabelText("Errores consecutivos: 1 de 3")).toBeInTheDocument()
  })
})
