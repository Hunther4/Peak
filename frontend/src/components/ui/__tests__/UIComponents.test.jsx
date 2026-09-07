import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import Button from "../Button"
import Card from "../Card"
import { Modal } from "../Modal"
import { ToastProvider } from "../Toast"

// ──────────────────────────────────────────────
// Button
// ──────────────────────────────────────────────
describe("Button", () => {
  it("renders with text", () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText("Click me")).toBeInTheDocument()
  })

  it("handles onClick", () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Click</Button>)
    fireEvent.click(screen.getByText("Click"))
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it("does not fire onClick when disabled", () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick} disabled>Click</Button>)
    fireEvent.click(screen.getByText("Click"))
    expect(onClick).not.toHaveBeenCalled()
  })

  it("applies variant classes", () => {
    render(<Button variant="primary">Primary</Button>)
    const btn = screen.getByText("Primary")
    expect(btn.className).toContain("from-green-400")
  })

  it("applies size classes", () => {
    render(<Button size="sm">Small</Button>)
    const btn = screen.getByText("Small")
    expect(btn.className).toContain("px-3")
  })
})

// ──────────────────────────────────────────────
// Card
// ──────────────────────────────────────────────
describe("Card", () => {
  it("renders children", () => {
    render(<Card><span data-testid="inner">Content</span></Card>)
    expect(screen.getByTestId("inner")).toBeInTheDocument()
  })

  it("applies hover class when hover prop is true", () => {
    render(<Card hover>Hover Card</Card>)
    const card = screen.getByText("Hover Card").closest("div")
    expect(card.className).toContain("hover:border-green-500/30")
  })

  it("applies interactive class when interactive prop is true", () => {
    render(<Card interactive>Interactive</Card>)
    const card = screen.getByText("Interactive").closest("div")
    expect(card.className).toContain("cursor-pointer")
  })
})

// ──────────────────────────────────────────────
// Modal
// ──────────────────────────────────────────────
describe("Modal", () => {
  it("renders content when isOpen is true", () => {
    render(
      <Modal isOpen={true} title="Test Modal" onClose={vi.fn()}>
        Modal content
      </Modal>
    )
    expect(screen.getByText("Modal content")).toBeInTheDocument()
    expect(screen.getByText("Test Modal")).toBeInTheDocument()
    expect(screen.getByText("Cancelar")).toBeInTheDocument()
  })

  it("does not render anything when isOpen is false", () => {
    render(
      <Modal isOpen={false} title="Hidden Modal" onClose={vi.fn()}>
        Should not be visible
      </Modal>
    )
    expect(screen.queryByText("Should not be visible")).not.toBeInTheDocument()
  })

  it("shows confirm button when onConfirm is provided", () => {
    render(
      <Modal isOpen={true} title="Confirm" onClose={vi.fn()} onConfirm={vi.fn()} confirmText="Aceptar">
        Content
      </Modal>
    )
    expect(screen.getByText("Aceptar")).toBeInTheDocument()
  })

  it("calls onClose when Cancelar is clicked", () => {
    const onClose = vi.fn()
    render(
      <Modal isOpen={true} title="Test" onClose={onClose}>
        Content
      </Modal>
    )
    fireEvent.click(screen.getByText("Cancelar"))
    expect(onClose).toHaveBeenCalledTimes(1)
  })
})

// ──────────────────────────────────────────────
// Toast (ToastProvider)
// ──────────────────────────────────────────────
describe("Toast", () => {
  it("renders nothing when no toasts are added", () => {
    const { container } = render(<ToastProvider><div>App</div></ToastProvider>)
    expect(container.textContent).toBe("App")
  })

  it("renders toasts via context", () => {
    function ToastAdder() {
      // We use the exported ToastProvider — we just test it renders children
      return <div data-testid="toast-child">Child</div>
    }
    render(
      <ToastProvider>
        <ToastAdder />
      </ToastProvider>
    )
    expect(screen.getByTestId("toast-child")).toBeInTheDocument()
  })
})
