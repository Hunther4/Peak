import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, act } from "@testing-library/react"
import { render, screen, fireEvent } from "@testing-library/react"
import { useGamePhase } from "../useGamePhase"
import { useApiState } from "../useApiState"
import { useGameKeyboard } from "../useGameKeyboard"

// ──────────────────────────────────────────────
// useGamePhase
// ──────────────────────────────────────────────
describe("useGamePhase", () => {
  it("returns idle phase by default", () => {
    const { result } = renderHook(() => useGamePhase())
    expect(result.current.phase).toBe("idle")
    expect(result.current.error).toBeNull()
  })

  it("accepts initial phase parameter", () => {
    const { result } = renderHook(() => useGamePhase("feedback"))
    expect(result.current.phase).toBe("feedback")
  })

  it("goToFeedback sets phase to feedback and clears error", () => {
    const { result } = renderHook(() => useGamePhase())
    act(() => result.current.setError("some error"))
    expect(result.current.error).toBe("some error")

    act(() => result.current.goToFeedback())
    expect(result.current.phase).toBe("feedback")
    expect(result.current.error).toBeNull()
  })

  it("goToDone sets phase to done and clears error", () => {
    const { result } = renderHook(() => useGamePhase())
    act(() => result.current.goToDone())
    expect(result.current.phase).toBe("done")
  })

  it("clearError sets error to null", () => {
    const { result } = renderHook(() => useGamePhase())
    act(() => result.current.setError("error"))
    expect(result.current.error).toBe("error")

    act(() => result.current.clearError())
    expect(result.current.error).toBeNull()
  })

  it("setPhase allows custom phase values", () => {
    const { result } = renderHook(() => useGamePhase())
    act(() => result.current.setPhase("presenting"))
    expect(result.current.phase).toBe("presenting")
  })

  it("goToIdle resets phase and error", () => {
    const { result } = renderHook(() => useGamePhase())
    act(() => {
      result.current.setPhase("done")
      result.current.setError("err")
    })
    act(() => result.current.goToIdle())
    expect(result.current.phase).toBe("idle")
    expect(result.current.error).toBeNull()
  })

  it("goToActive clears error but does not change phase directly", () => {
    const { result } = renderHook(() => useGamePhase())
    act(() => {
      result.current.setError("err")
      result.current.goToActive()
    })
    expect(result.current.error).toBeNull()
    expect(result.current.phase).toBe("idle")
  })
})

// ──────────────────────────────────────────────
// useApiState
// ──────────────────────────────────────────────
describe("useApiState", () => {
  it("initializes with loading=false and error=null", () => {
    const { result } = renderHook(() => useApiState())
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it("withLoading sets loading true during async call", async () => {
    const { result } = renderHook(() => useApiState())
    let resolvePromise
    const promise = new Promise((resolve) => { resolvePromise = resolve })
    const asyncCall = vi.fn().mockReturnValue(promise)

    let returnedPromise
    act(() => {
      returnedPromise = result.current.withLoading(asyncCall)
    })
    expect(result.current.loading).toBe(true)

    await act(async () => {
      resolvePromise("done")
      await returnedPromise
    })
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it("withLoading sets error on rejection", async () => {
    const { result } = renderHook(() => useApiState())
    const asyncCall = vi.fn().mockRejectedValue(new Error("Network error"))

    await act(async () => {
      try {
        await result.current.withLoading(asyncCall)
      } catch { /* expected */ }
    })

    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe("Network error")
  })

  it("clearError resets error to null", () => {
    const { result } = renderHook(() => useApiState())
    act(() => result.current.setError("err"))
    expect(result.current.error).toBe("err")

    act(() => result.current.clearError())
    expect(result.current.error).toBeNull()
  })

  it("setError and setLoading update state directly", () => {
    const { result } = renderHook(() => useApiState())
    act(() => {
      result.current.setLoading(true)
      result.current.setError("direct")
    })
    expect(result.current.loading).toBe(true)
    expect(result.current.error).toBe("direct")
  })
})

// ──────────────────────────────────────────────
// useGameKeyboard
// ──────────────────────────────────────────────
describe("useGameKeyboard", () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it("registers keydown listener on mount", () => {
    const addSpy = vi.spyOn(window, "addEventListener")
    renderHook(() => useGameKeyboard({ a: vi.fn() }))
    expect(addSpy).toHaveBeenCalledWith("keydown", expect.any(Function))
  })

  it("calls handler when matching key is pressed", () => {
    const handler = vi.fn()
    renderHook(() => useGameKeyboard({ a: handler }))
    fireEvent.keyDown(window, { key: "a" })
    expect(handler).toHaveBeenCalledTimes(1)
  })

  it("passes the event object to the handler", () => {
    const handler = vi.fn()
    renderHook(() => useGameKeyboard({ a: handler }))
    fireEvent.keyDown(window, { key: "a" })
    expect(handler).toHaveBeenCalledWith(expect.objectContaining({ key: "a" }))
  })

  it("calls handler by uppercase key name", () => {
    const handler = vi.fn()
    renderHook(() => useGameKeyboard({ Enter: handler }))
    fireEvent.keyDown(window, { key: "Enter" })
    expect(handler).toHaveBeenCalledTimes(1)
  })

  it("prevents default for matched keys", () => {
    const handler = vi.fn()
    renderHook(() => useGameKeyboard({ a: handler }))
    const event = new KeyboardEvent("keydown", { key: "a", cancelable: true })
    const preventDefaultSpy = vi.spyOn(event, "preventDefault")
    window.dispatchEvent(event)
    expect(preventDefaultSpy).toHaveBeenCalled()
  })

  it("does not call handler for non-mapped keys", () => {
    const handler = vi.fn()
    renderHook(() => useGameKeyboard({ a: handler }))
    fireEvent.keyDown(window, { key: "b" })
    expect(handler).not.toHaveBeenCalled()
  })

  it("does not register listener when enabled=false", () => {
    const addSpy = vi.spyOn(window, "addEventListener")
    renderHook(() => useGameKeyboard({ a: vi.fn() }, false))
    expect(addSpy).not.toHaveBeenCalledWith("keydown", expect.any(Function))
  })

  it("removes listener on unmount", () => {
    const removeSpy = vi.spyOn(window, "removeEventListener")
    const { unmount } = renderHook(() => useGameKeyboard({ a: vi.fn() }))
    unmount()
    expect(removeSpy).toHaveBeenCalledWith("keydown", expect.any(Function))
  })
})

// ──────────────────────────────────────────────
// useGameBlocker + ExitGamePrompt
//
// Note: useGameBlocker imports useBlocker from react-router.
// We mock the module globally so all imports use the mock.
// ──────────────────────────────────────────────

// Mock react-router for both useGameBlocker and any other module
vi.mock("react-router", () => ({
  useBlocker: vi.fn(() => ({ state: "unblocked", proceed: vi.fn(), reset: vi.fn() })),
}))

import { useGameBlocker, ExitGamePrompt } from "../useGameBlocker"

describe("useGameBlocker", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it("registers beforeunload when shouldBlock is true", () => {
    const addSpy = vi.spyOn(window, "addEventListener")
    const { result } = renderHook(() => useGameBlocker(true))

    expect(addSpy).toHaveBeenCalledWith("beforeunload", expect.any(Function))
    expect(result.current.showPrompt).toBe(false)
  })

  it("returns showPrompt=false and navigation controls", () => {
    const { result } = renderHook(() => useGameBlocker(true))

    expect(result.current).toHaveProperty("showPrompt")
    expect(result.current).toHaveProperty("confirmNavigation")
    expect(result.current).toHaveProperty("cancelNavigation")
    expect(result.current.showPrompt).toBe(false)
  })

  it("does not register beforeunload when shouldBlock is false", () => {
    const addSpy = vi.spyOn(window, "addEventListener")
    renderHook(() => useGameBlocker(false))

    const beforeUnloadCalls = addSpy.mock.calls.filter(c => c[0] === "beforeunload")
    expect(beforeUnloadCalls.length).toBe(0)
  })

  it("removes beforeunload listener on unmount", () => {
    const removeSpy = vi.spyOn(window, "removeEventListener")
    const { unmount } = renderHook(() => useGameBlocker(true))
    unmount()

    expect(removeSpy).toHaveBeenCalledWith("beforeunload", expect.any(Function))
  })
})

describe("ExitGamePrompt", () => {
  it("renders nothing when show is false", () => {
    render(<ExitGamePrompt show={false} onConfirm={vi.fn()} onCancel={vi.fn()} />)
    expect(screen.queryByText("¿Salir del juego?")).not.toBeInTheDocument()
  })

  it("renders dialog when show is true", () => {
    render(<ExitGamePrompt show={true} onConfirm={vi.fn()} onCancel={vi.fn()} />)
    expect(screen.getByText("¿Salir del juego?")).toBeInTheDocument()
    expect(screen.getByText("Quedarme")).toBeInTheDocument()
    expect(screen.getByText("Salir")).toBeInTheDocument()
  })

  it("calls onCancel when Quedarme is clicked", () => {
    const onCancel = vi.fn()
    render(<ExitGamePrompt show={true} onConfirm={vi.fn()} onCancel={onCancel} />)
    fireEvent.click(screen.getByText("Quedarme"))
    expect(onCancel).toHaveBeenCalledTimes(1)
  })

  it("calls onConfirm when Salir is clicked", () => {
    const onConfirm = vi.fn()
    render(<ExitGamePrompt show={true} onConfirm={onConfirm} onCancel={vi.fn()} />)
    fireEvent.click(screen.getByText("Salir"))
    expect(onConfirm).toHaveBeenCalledTimes(1)
  })
})
