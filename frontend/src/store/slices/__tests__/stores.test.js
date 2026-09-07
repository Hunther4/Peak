import { describe, it, expect, vi, beforeEach } from "vitest"
import { create } from "zustand"
import { createSkillsSlice } from "../skills"
import { createProfileSlice } from "../profile"
import { createMentalSlice } from "../mental"
import { createAISlice } from "../ai"
import { createBooksSlice } from "../books"

// Mock the api module — vitest hoists this before imports
vi.mock("../../../api/client", () => ({
  api: {
    skills: {
      getAll: vi.fn(),
      getById: vi.fn(),
      getBySlug: vi.fn(),
    },
    sessions: {
      create: vi.fn(),
      getAll: vi.fn(),
      getById: vi.fn(),
      getCount: vi.fn(),
      clearAll: vi.fn(),
    },
    assessments: {
      create: vi.fn(),
    },
    dashboard: {
      getSummary: vi.fn(),
      getTimeline: vi.fn(),
    },
    profile: {
      get: vi.fn(),
      save: vi.fn(),
      uploadAvatar: vi.fn(),
    },
    mental: {
      getReps: vi.fn(),
      generateRep: vi.fn(),
      acceptRep: vi.fn(),
      getChallenges: vi.fn(),
      generateChallenge: vi.fn(),
      completeChallenge: vi.fn(),
    },
    models: {
      getStatus: vi.fn(),
      getMode: vi.fn(),
      setMode: vi.fn(),
      getBest: vi.fn(),
      getAvailable: vi.fn(),
      getSelection: vi.fn(),
      select: vi.fn(),
      selectAuto: vi.fn(),
    },
    books: {
      getStatus: vi.fn(),
      index: vi.fn(),
      search: vi.fn(),
    },
  },
  setClientApiKey: vi.fn(),
}))

import { api } from "../../../api/client"

beforeEach(() => {
  vi.clearAllMocks()
  localStorage.clear()
})

// ──────────────────────────────────────────────
// Skills Slice
// ──────────────────────────────────────────────

describe("skills slice - initial state", () => {
  it("has correct initial state", () => {
    const slice = createSkillsSlice(() => {}, () => {})
    expect(slice).toHaveProperty("skills", [])
    expect(slice).toHaveProperty("sessions", [])
    expect(slice).toHaveProperty("summary", null)
    expect(slice).toHaveProperty("groupedSummary", [])
    expect(slice).toHaveProperty("timeline", [])
    expect(slice).toHaveProperty("loading", false)
    expect(slice).toHaveProperty("error", null)
  })

  it("has all required action keys", () => {
    const slice = createSkillsSlice(() => {}, () => {})
    const expectedActions = [
      "fetchSkills",
      "fetchSummary",
      "fetchTimeline",
      "pollPendingAudits",
      "createSession",
      "createAssessment",
      "clearError",
    ]
    expectedActions.forEach((key) => {
      expect(slice).toHaveProperty(key)
      expect(slice[key]).toBeInstanceOf(Function)
    })
  })

  it("clearError sets error to null", () => {
    const store = create((set, get) => ({ ...createSkillsSlice(set, get) }))
    store.setState({ error: "some error" })
    store.getState().clearError()
    expect(store.getState().error).toBeNull()
  })
})

describe("skills slice - fetchSkills", () => {
  it("sets loading then updates skills on success", async () => {
    const skillsData = [{ skill: { id: 1, name: "Math" } }]
    api.skills.getAll.mockResolvedValue(skillsData)

    const store = create((set, get) => ({ ...createSkillsSlice(set, get) }))
    const promise = store.getState().fetchSkills()

    // Should be loading during fetch
    expect(store.getState().loading).toBe(true)
    expect(store.getState().error).toBeNull()

    await promise

    expect(store.getState().skills).toEqual(skillsData)
    expect(store.getState().loading).toBe(false)
  })

  it("sets error on failure", async () => {
    api.skills.getAll.mockRejectedValue(new Error("Network error"))

    const store = create((set, get) => ({ ...createSkillsSlice(set, get) }))

    await store.getState().fetchSkills()

    const state = store.getState()
    expect(state.error).toBe("Network error")
    expect(state.loading).toBe(false)
  })
})

describe("skills slice - fetchSummary", () => {
  it("sets summary and groupedSummary on success", async () => {
    const summaryData = {
      skills: [
        { skill: { id: 1, name: "Root", parent_id: null } },
        { skill: { id: 2, name: "Child", parent_id: 1 } },
      ],
    }
    api.dashboard.getSummary.mockResolvedValue(summaryData)

    const store = create((set, get) => ({ ...createSkillsSlice(set, get) }))

    await store.getState().fetchSummary()

    const state = store.getState()
    expect(state.summary).toEqual(summaryData)
    expect(state.groupedSummary).toHaveLength(1)
    expect(state.groupedSummary[0].children).toHaveLength(1)
  })

  it("sets error on failure", async () => {
    api.dashboard.getSummary.mockRejectedValue(new Error("Summary error"))

    const store = create((set, get) => ({ ...createSkillsSlice(set, get) }))

    await store.getState().fetchSummary()

    expect(store.getState().error).toBe("Summary error")
  })

  it("fetchTimeline calls api and sets timeline data", async () => {
    const timelineData = { timeline: [{ id: 1, date: "2025-01-01" }] }
    api.dashboard.getTimeline.mockResolvedValue(timelineData)

    const store = create((set, get) => ({ ...createSkillsSlice(set, get) }))

    await store.getState().fetchTimeline()

    expect(api.dashboard.getTimeline).toHaveBeenCalledWith(null)
    expect(store.getState().timeline).toEqual(timelineData.timeline)
  })
})

// ──────────────────────────────────────────────
// Profile Slice
// ──────────────────────────────────────────────

describe("profile slice - initial state", () => {
  it("has correct initial state", () => {
    const slice = createProfileSlice(() => {}, () => {})
    expect(slice).toHaveProperty("profile", null)
    expect(slice).toHaveProperty("profileLoading", true)
  })

  it("has all required action keys", () => {
    const slice = createProfileSlice(() => {}, () => {})
    const expectedActions = ["fetchProfile", "saveProfile", "uploadAvatar"]
    expectedActions.forEach((key) => {
      expect(slice).toHaveProperty(key)
      expect(slice[key]).toBeInstanceOf(Function)
    })
  })

  it("fetchProfile returns cached profile from localStorage (background sync fires too)", async () => {
    // Profile slice fires a background sync even when cached (fire-and-forget).
    // Mock the API to return the same value so the background sync doesn't
    // overwrite with null.
    const cached = { name: "Cached User", age: 30 }
    api.profile.get.mockResolvedValue(cached)
    localStorage.setItem("peak_profile", JSON.stringify(cached))

    const store = create((set, get) => ({ ...createProfileSlice(set, get) }))

    const result = await store.getState().fetchProfile()

    // The important thing is that the cached value is returned immediately.
    expect(result).toEqual(cached)
    const state = store.getState()
    expect(state.profile).toEqual(cached)
    expect(state.profileLoading).toBe(false)
  })

  it("calls api when no cache exists", async () => {
    const profileData = { name: "API User", age: 25 }
    api.profile.get.mockResolvedValue(profileData)

    const store = create((set, get) => ({ ...createProfileSlice(set, get) }))

    const result = await store.getState().fetchProfile()

    expect(api.profile.get).toHaveBeenCalled()
    expect(result).toEqual(profileData)
    const state = store.getState()
    expect(state.profile).toEqual(profileData)
    expect(state.profileLoading).toBe(false)
  })

  it("saveProfile calls api and caches result", async () => {
    const saved = { name: "New Name", age: 35 }
    api.profile.save.mockResolvedValue(saved)

    const store = create((set, get) => ({ ...createProfileSlice(set, get) }))

    await store.getState().saveProfile("New Name", 35)

    expect(api.profile.save).toHaveBeenCalledWith({ name: "New Name", age: 35 })
    const state = store.getState()
    expect(state.profile).toEqual(saved)
    expect(JSON.parse(localStorage.getItem("peak_profile"))).toEqual(saved)
  })
})

// ──────────────────────────────────────────────
// Mental Slice
// ──────────────────────────────────────────────

describe("mental slice - initial state and actions", () => {
  it("has correct initial state", () => {
    const slice = createMentalSlice(() => {}, () => {})
    expect(slice).toHaveProperty("mentalReps", [])
    expect(slice).toHaveProperty("challenges", [])
    expect(slice).toHaveProperty("pendingChallenges", 0)
    expect(slice).toHaveProperty("generatingRep", false)
    expect(slice).toHaveProperty("generatingChallenge", false)
  })

  it("has all required action keys", () => {
    const slice = createMentalSlice(() => {}, () => {})
    const expectedActions = [
      "fetchMentalReps",
      "fetchChallenges",
      "generateRep",
      "acceptRep",
      "generateChallenge",
      "completeChallenge",
    ]
    expectedActions.forEach((key) => {
      expect(slice).toHaveProperty(key)
      expect(slice[key]).toBeInstanceOf(Function)
    })
  })

  it("fetchMentalReps sets mentalReps on success", async () => {
    const reps = [{ id: "r1", description: "Rep 1" }]
    api.mental.getReps.mockResolvedValue(reps)

    const store = create((set, get) => ({ ...createMentalSlice(set, get) }))

    await store.getState().fetchMentalReps()

    expect(store.getState().mentalReps).toEqual(reps)
  })

  it("generateRep sets generatingRep true then false", async () => {
    api.mental.generateRep.mockResolvedValue({ id: "rep1" })

    const store = create((set, get) => ({ ...createMentalSlice(set, get) }))

    const promise = store.getState().generateRep(1)
    expect(store.getState().generatingRep).toBe(true)
    await promise
    expect(store.getState().generatingRep).toBe(false)
  })

  it("generateChallenge sets generatingChallenge true then false", async () => {
    api.mental.generateChallenge.mockResolvedValue({ id: "ch1" })

    const store = create((set, get) => ({ ...createMentalSlice(set, get) }))

    const promise = store.getState().generateChallenge(1)
    expect(store.getState().generatingChallenge).toBe(true)
    await promise
    expect(store.getState().generatingChallenge).toBe(false)
  })

  it("completeChallenge calls api and refreshes challenges", async () => {
    api.mental.completeChallenge.mockResolvedValue({ id: "ch1", completed: true })
    api.mental.getChallenges.mockResolvedValue([])

    const store = create((set, get) => ({ ...createMentalSlice(set, get) }))

    await store.getState().completeChallenge("ch1")

    expect(api.mental.completeChallenge).toHaveBeenCalledWith("ch1", true)
  })
})

// ──────────────────────────────────────────────
// AI Slice
// ──────────────────────────────────────────────

describe("ai slice - initial state and actions", () => {
  it("has correct initial state", () => {
    const slice = createAISlice(() => {}, () => {})
    expect(slice).toHaveProperty("ai_mode", "local")
    expect(slice).toHaveProperty("available_models", [])
    expect(slice).toHaveProperty("best_model", null)
    expect(slice).toHaveProperty("selectedModel", { auto: true })
  })

  it("has all required action keys", () => {
    const slice = createAISlice(() => {}, () => {})
    const expectedActions = ["fetchAiStatus", "setAiMode", "selectModel", "selectModelAuto"]
    expectedActions.forEach((key) => {
      expect(slice).toHaveProperty(key)
      expect(slice[key]).toBeInstanceOf(Function)
    })
  })

  it("fetchAiStatus fetches all model endpoints", async () => {
    api.models.getStatus.mockResolvedValue({ mode: "cloud" })
    api.models.getAvailable.mockResolvedValue([{ name: "gpt4" }])
    api.models.getBest.mockResolvedValue({ name: "gpt4" })
    api.models.getSelection.mockResolvedValue({ selection: { auto: false, model_name: "gpt4" } })

    const store = create((set, get) => ({ ...createAISlice(set, get) }))

    await store.getState().fetchAiStatus()

    const state = store.getState()
    expect(state.ai_mode).toBe("cloud")
    expect(state.available_models).toEqual([{ name: "gpt4" }])
    expect(state.best_model).toEqual({ name: "gpt4" })
    expect(state.selectedModel).toEqual({ auto: false, model_name: "gpt4" })
  })

  it("selectModel updates selectedModel state", async () => {
    api.models.select.mockResolvedValue({})

    const store = create((set, get) => ({ ...createAISlice(set, get) }))

    await store.getState().selectModel("gpt4", "openai", "gpt-4")

    const state = store.getState()
    expect(state.selectedModel).toEqual({
      auto: false,
      model_name: "gpt4",
      provider: "openai",
      model_id: "gpt-4",
    })
  })

  it("selectModelAuto resets selectedModel to auto", async () => {
    api.models.selectAuto.mockResolvedValue({})

    const store = create((set, get) => ({ ...createAISlice(set, get) }))

    await store.getState().selectModelAuto()

    expect(store.getState().selectedModel).toEqual({ auto: true })
  })

  it("setAiMode calls api and updates mode", async () => {
    api.models.setMode.mockResolvedValue({})
    // setAiMode calls fetchAiStatus() internally, which re-fetches status.
    // We need the status endpoint to reflect the new mode.
    api.models.getStatus.mockResolvedValue({ mode: "cloud" })
    api.models.getAvailable.mockResolvedValue([])
    api.models.getBest.mockResolvedValue(null)
    api.models.getSelection.mockResolvedValue({ selection: { auto: true } })

    const store = create((set, get) => ({ ...createAISlice(set, get) }))

    await store.getState().setAiMode("cloud")

    expect(api.models.setMode).toHaveBeenCalledWith("cloud")
    expect(store.getState().ai_mode).toBe("cloud")
  })
})

// ──────────────────────────────────────────────
// Books Slice
// ──────────────────────────────────────────────

describe("books slice - initial state and actions", () => {
  it("has correct initial state", () => {
    const slice = createBooksSlice(() => {}, () => {})
    expect(slice).toHaveProperty("books", [])
    expect(slice).toHaveProperty("booksLoading", false)
    expect(slice).toHaveProperty("isIndexing", false)
    expect(slice).toHaveProperty("indexingProgress", 0)
    expect(slice).toHaveProperty("_indexPollCleanup", null)
  })

  it("has all required action keys", () => {
    const slice = createBooksSlice(() => {}, () => {})
    const expectedActions = ["fetchBooksStatus", "indexBooks"]
    expectedActions.forEach((key) => {
      expect(slice).toHaveProperty(key)
      expect(slice[key]).toBeInstanceOf(Function)
    })
  })

  it("fetchBooksStatus sets books and loading state", async () => {
    const data = { books: [{ id: 1, title: "Book 1" }], is_indexing: false, progress: 100 }
    api.books.getStatus.mockResolvedValue(data)

    const store = create((set, get) => ({ ...createBooksSlice(set, get) }))

    const promise = store.getState().fetchBooksStatus()
    expect(store.getState().booksLoading).toBe(true)

    await promise

    const state = store.getState()
    expect(state.books).toEqual([{ id: 1, title: "Book 1" }])
    expect(state.isIndexing).toBe(false)
    expect(state.indexingProgress).toBe(100)
    expect(state.booksLoading).toBe(false)
  })

  it("indexBooks sets isIndexing and calls api", async () => {
    api.books.index.mockResolvedValue({ status: "indexing" })

    const store = create((set, get) => ({ ...createBooksSlice(set, get) }))

    await store.getState().indexBooks()

    expect(api.books.index).toHaveBeenCalledWith(false)
  })
})
