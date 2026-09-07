import { describe, it, expect, vi, beforeEach } from "vitest"
import { api, setClientApiKey } from "../client"

// Save original fetch so we can restore between tests
const originalFetch = globalThis.fetch

beforeEach(() => {
  globalThis.fetch = vi.fn()
})

afterEach(() => {
  vi.restoreAllMocks()
  setClientApiKey(null)
})

describe("api client - request flow", () => {
  it("returns parsed JSON on successful response", async () => {
    const data = { id: 1, name: "test" }
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(data),
    })

    const result = await api.skills.getAll()
    expect(result).toEqual(data)
    expect(globalThis.fetch).toHaveBeenCalledTimes(1)
  })

  it("makes a GET request to the correct URL", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
    })

    await api.skills.getBySlug("math")
    const [url, opts] = globalThis.fetch.mock.calls[0]

    expect(url).toContain("/api/skills/by-slug/math")
    expect(opts.method).toBeUndefined() // GET by default
  })

  it("sends POST with JSON body for create endpoints", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: "s1" }),
    })

    const payload = { skill_id: 1 }
    await api.sessions.create(payload)

    const [, opts] = globalThis.fetch.mock.calls[0]
    expect(opts.method).toBe("POST")
    expect(opts.body).toBe(JSON.stringify(payload))
    expect(opts.headers["Content-Type"]).toBe("application/json")
  })

  it("throws an error with detail on 4xx response", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: false,
      status: 400,
      statusText: "Bad Request",
      json: () => Promise.resolve({ detail: "Invalid skill ID" }),
    })

    await expect(api.skills.getAll()).rejects.toThrow("Invalid skill ID")
  })

  it("throws an error with statusText when error JSON has no detail", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      json: () => Promise.resolve({}),
    })

    await expect(api.skills.getAll()).rejects.toThrow("Error 404")
  })

  it("falls back to statusText when error JSON parsing fails", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      json: () => Promise.reject(new Error("parse error")),
    })

    await expect(api.skills.getAll()).rejects.toThrow("Internal Server Error")
  })

  it("throws an error on 5xx response", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      json: () => Promise.resolve({ detail: "Server error" }),
    })

    await expect(api.skills.getAll()).rejects.toThrow("Server error")
  })

  it("throws an error when fetch rejects (network error)", async () => {
    globalThis.fetch.mockRejectedValue(new Error("Network failure"))

    await expect(api.skills.getAll()).rejects.toThrow("Network failure")
  })

  it("sets X-API-Key header when API key is configured", async () => {
    setClientApiKey("test-key-123")

    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
    })

    await api.skills.getAll()

    const [, opts] = globalThis.fetch.mock.calls[0]
    expect(opts.headers["X-API-Key"]).toBe("test-key-123")
  })

  it("does NOT include X-API-Key header when no API key is set", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
    })

    await api.skills.getAll()

    const [, opts] = globalThis.fetch.mock.calls[0]
    expect(opts.headers["X-API-Key"]).toBeUndefined()
  })

  it("handles query string parameters correctly", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    })

    await api.sessions.getAll(42)

    const [url] = globalThis.fetch.mock.calls[0]
    expect(url).toContain("?skill_id=42")
  })

  it("makes HEAD request when called via method override", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
    })

    // The api module exposes `request` directly for custom calls
    await api.request("/test", { method: "HEAD" })

    const [, opts] = globalThis.fetch.mock.calls[0]
    expect(opts.method).toBe("HEAD")
  })

  it("sends PATCH request for partial updates", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
    })

    await api.mental.completeChallenge("ch1", true)

    const [, opts] = globalThis.fetch.mock.calls[0]
    expect(opts.method).toBe("PATCH")
    expect(opts.body).toContain("true")
  })

  it("sends FormData for avatar upload (no Content-Type header)", async () => {
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ avatar_url: "https://example.com/av.jpg" }),
    })

    const file = new File(["fake"], "avatar.png", { type: "image/png" })
    await api.profile.uploadAvatar(file)

    const [, opts] = globalThis.fetch.mock.calls[0]
    // FormData must NOT have Content-Type set (browser sets it with boundary)
    expect(opts.body).toBeInstanceOf(FormData)
    expect(opts.headers["Content-Type"]).toBeUndefined()
  })

  it("sets X-API-Key on avatar upload when configured", async () => {
    setClientApiKey("key-for-upload")

    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ avatar_url: "x" }),
    })

    const file = new File(["fake"], "avatar.png", { type: "image/png" })
    await api.profile.uploadAvatar(file)

    const [, opts] = globalThis.fetch.mock.calls[0]
    expect(opts.headers["X-API-Key"]).toBe("key-for-upload")
  })
})

describe("api client - endpoint groups exist", () => {
  it("skills has required methods", () => {
    expect(api.skills.getAll).toBeInstanceOf(Function)
    expect(api.skills.getById).toBeInstanceOf(Function)
    expect(api.skills.getBySlug).toBeInstanceOf(Function)
  })

  it("sessions has required methods", () => {
    expect(api.sessions.getAll).toBeInstanceOf(Function)
    expect(api.sessions.getById).toBeInstanceOf(Function)
    expect(api.sessions.create).toBeInstanceOf(Function)
  })

  it("memoryGame has required methods", () => {
    expect(api.memoryGame.createSession).toBeInstanceOf(Function)
    expect(api.memoryGame.createRound).toBeInstanceOf(Function)
    expect(api.memoryGame.submitAttempt).toBeInstanceOf(Function)
    expect(api.memoryGame.consolidate).toBeInstanceOf(Function)
    expect(api.memoryGame.getState).toBeInstanceOf(Function)
    expect(api.memoryGame.getHistory).toBeInstanceOf(Function)
  })

  it("mathThinking has required methods", () => {
    expect(api.mathThinking.createSession).toBeInstanceOf(Function)
    expect(api.mathThinking.createRound).toBeInstanceOf(Function)
    expect(api.mathThinking.submitAttempt).toBeInstanceOf(Function)
    expect(api.mathThinking.getHint).toBeInstanceOf(Function)
  })
})
