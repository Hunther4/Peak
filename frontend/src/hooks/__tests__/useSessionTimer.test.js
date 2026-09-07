import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useSessionTimer } from '../useSessionTimer'

describe('useSessionTimer', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('starts at 0 and isRunning=true on mount', () => {
    const { result } = renderHook(() => useSessionTimer())
    expect(result.current.elapsedSeconds).toBe(0)
    expect(result.current.isRunning).toBe(true)
  })

  it('increments elapsedSeconds every 1000ms while running', () => {
    const { result } = renderHook(() => useSessionTimer())
    act(() => {
      vi.advanceTimersByTime(3000)
    })
    expect(result.current.elapsedSeconds).toBe(3)
  })

  it('formatTime returns MM:SS zero-padded', () => {
    const { result } = renderHook(() => useSessionTimer())
    expect(result.current.formatTime()).toBe('00:00')

    act(() => {
      vi.advanceTimersByTime(65 * 1000)
    })
    expect(result.current.formatTime()).toBe('01:05')
  })

  it('pause stops the count, resume continues from current value', () => {
    const { result } = renderHook(() => useSessionTimer())

    act(() => {
      vi.advanceTimersByTime(2000)
    })
    expect(result.current.elapsedSeconds).toBe(2)

    act(() => {
      result.current.pause()
    })
    expect(result.current.isRunning).toBe(false)

    act(() => {
      vi.advanceTimersByTime(5000)
    })
    expect(result.current.elapsedSeconds).toBe(2)

    act(() => {
      result.current.resume()
    })
    act(() => {
      vi.advanceTimersByTime(3000)
    })
    expect(result.current.elapsedSeconds).toBe(5)
  })

  it('reset zeros the counter and resumes', () => {
    const { result } = renderHook(() => useSessionTimer())

    act(() => {
      vi.advanceTimersByTime(5000)
    })
    expect(result.current.elapsedSeconds).toBe(5)

    act(() => {
      result.current.pause()
    })
    act(() => {
      result.current.reset()
    })
    expect(result.current.elapsedSeconds).toBe(0)
    expect(result.current.isRunning).toBe(true)

    act(() => {
      vi.advanceTimersByTime(2000)
    })
    expect(result.current.elapsedSeconds).toBe(2)
  })

  it('cleans up the interval on unmount', () => {
    const clearIntervalSpy = vi.spyOn(globalThis, 'clearInterval')
    const { unmount } = renderHook(() => useSessionTimer())
    unmount()
    expect(clearIntervalSpy).toHaveBeenCalled()
    clearIntervalSpy.mockRestore()
  })
})
