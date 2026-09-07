import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { ErrorBoundary } from "../ErrorBoundary"

// Suppress console.error from React when testing error boundaries
beforeEach(() => {
  vi.spyOn(console, "error").mockImplementation(() => {})
})

function GoodChild() {
  return <div data-testid="good-child">Hello World</div>
}

function BadChild() {
  throw new Error("Test error from BadChild")
}

describe("ErrorBoundary", () => {
  it("renders children normally when no error occurs", () => {
    render(
      <ErrorBoundary>
        <GoodChild />
      </ErrorBoundary>
    )
    expect(screen.getByTestId("good-child")).toBeInTheDocument()
    expect(screen.getByText("Hello World")).toBeInTheDocument()
  })

  it("catches errors and displays fallback UI", () => {
    render(
      <ErrorBoundary fallbackMessage="Custom error message">
        <BadChild />
      </ErrorBoundary>
    )
    expect(screen.getByText("Algo salió mal")).toBeInTheDocument()
    expect(screen.getByText("Custom error message")).toBeInTheDocument()
    expect(screen.getByText("Reintentar")).toBeInTheDocument()
  })

  it("displays default fallback message when none provided", () => {
    render(
      <ErrorBoundary>
        <BadChild />
      </ErrorBoundary>
    )
    expect(screen.getByText("Esta sección no pudo cargarse.")).toBeInTheDocument()
  })

  it("reset button clears error state and shows children again", () => {
    // We need to toggle between error and no-error states.
    // The ErrorBoundary catches the error and shows fallback.
    // Clicking "Reintentar" resets state and re-renders children.
    // If children still throw, it catches again.

    let shouldThrow = true
    function ConditionalChild() {
      if (shouldThrow) throw new Error("Conditional error")
      return <div data-testid="recovered">Recovered!</div>
    }

    render(
      <ErrorBoundary>
        <ConditionalChild />
      </ErrorBoundary>
    )

    // Error caught — fallback UI
    expect(screen.getByText("Algo salió mal")).toBeInTheDocument()

    // Stop the throw and click Reintentar
    shouldThrow = false
    fireEvent.click(screen.getByText("Reintentar"))

    // After reset, the child should render
    expect(screen.getByTestId("recovered")).toBeInTheDocument()
    expect(screen.getByText("Recovered!")).toBeInTheDocument()
  })
})
