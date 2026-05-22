const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api"

// Read API key from Vite env var (VITE_PEAK_API_KEY) or localStorage
const API_KEY = import.meta.env.VITE_PEAK_API_KEY || localStorage.getItem("peak_api_key")

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`
  const headers = {
    "Content-Type": "application/json",
    ...(API_KEY ? { "X-API-Key": API_KEY } : {}),
    ...options.headers,
  }
  const res = await fetch(url, {
    headers,
    ...options,
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `Error ${res.status}`)
  }

  return res.json()
}

export const api = {
  request,

  skills: {
    getAll: () => request("/skills/"),
    getById: (id) => request(`/skills/${id}`),
    getBySlug: (slug) => request(`/skills/by-slug/${slug}`),
  },

  sessions: {
    getAll: (skillId = null) => {
      const query = skillId ? `?skill_id=${skillId}` : ""
      return request(`/sessions/${query}`)
    },
    getById: (id) => request(`/sessions/${id}`),
    create: (data) =>
      request("/sessions/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    getCount: (skillId) => request(`/sessions/skill/${skillId}/count`),
  },

  assessments: {
    getAll: (skillId = null) => {
      const query = skillId ? `?skill_id=${skillId}` : ""
      return request(`/assessments/${query}`)
    },
    getById: (id) => request(`/assessments/${id}`),
    create: (data) =>
      request("/assessments/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },

  dashboard: {
    getSummary: () => request("/dashboard/summary"),
    getTimeline: (skillId = null) => {
      const query = skillId ? `?skill_id=${skillId}` : ""
      return request(`/dashboard/timeline${query}`)
    },
  },

  books: {
    getStatus: () => request("/books/status"),
    index: (force = false) =>
      request("/books/index", {
        method: "POST",
        body: JSON.stringify({ force }),
      }),
    search: (q, top_k = 3) =>
      request(`/books/search?q=${encodeURIComponent(q)}&top_k=${top_k}`),
  },

  mental: {
    getReps: (skillId = null) => {
      const query = skillId ? `?skill_id=${skillId}` : ""
      return request(`/mental/reps${query}`)
    },
    generateRep: (skillId) =>
      request("/mental/reps/generate", {
        method: "POST",
        body: JSON.stringify({ skill_id: skillId }),
      }),
    acceptRep: (repId, description, skillId) =>
      request(`/mental/reps/${repId}/accept`, {
        method: "POST",
        body: JSON.stringify({ description, skill_id: skillId }),
      }),

    getChallenges: (skillId = null, completed = null) => {
      let query = "?"
      if (skillId) query += `skill_id=${skillId}`
      if (completed !== null) query += `${skillId ? "&" : ""}completed=${completed}`
      return request(`/mental/challenges${query === "?" ? "" : query}`)
    },
    generateChallenge: (skillId, difficultyOverride = null) => {
      const body = { skill_id: skillId }
      if (difficultyOverride) body.difficulty_override = difficultyOverride
      return request("/mental/challenges/generate", {
        method: "POST",
        body: JSON.stringify(body),
      })
    },
    completeChallenge: (challengeId, completed = true) =>
      request(`/mental/challenges/${challengeId}/complete`, {
        method: "PATCH",
        body: JSON.stringify({ completed }),
      }),
    getNext: (skillId) => request(`/mental/challenges/next/${skillId}`),
  },

  models: {
    getStatus: () => request("/models/status"),
    getMode: () => request("/models/status"),
    setMode: (mode) =>
      request("/models/mode", {
        method: "PUT",
        body: JSON.stringify({ mode }),
      }),
    getBest: (task) => request(`/models/best?task=${task}`),
    getAvailable: (task) => request(`/models/available?task=${task}`),
    getSelection: () => request("/models/selection"),
    select: (modelName, provider, modelId) =>
      request("/models/select", {
        method: "POST",
        body: JSON.stringify({
          model_name: modelName,
          provider,
          model_id: modelId,
        }),
      }),
    selectAuto: () =>
      request("/models/select", {
        method: "POST",
        body: JSON.stringify({ auto: true }),
      }),
  },

  profile: {
    get: () => request("/profile"),
    save: (data) =>
      request("/profile", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    uploadAvatar: async (file) => {
      const url = `${BASE_URL}/profile/avatar`
      const formData = new FormData()
      formData.append("file", file)
      const headers = {
        ...(API_KEY ? { "X-API-Key": API_KEY } : {}),
      }
      const res = await fetch(url, {
        method: "POST",
        headers,
        body: formData,
      })
      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(error.detail || `Error ${res.status}`)
      }
      return res.json()
    },
  },

  memoryGame: {
    createSession: (skillId) => request(`/memory-game/sessions?skill_id=${skillId}`, { method: "POST" }),
    createRound: (sessionId) =>
      request(`/memory-game/sessions/${sessionId}/rounds`, { method: "POST" }),
    submitAttempt: (roundId, submittedNumbers) =>
      request(`/memory-game/rounds/${roundId}/attempts`, {
        method: "POST",
        body: JSON.stringify({ submitted_numbers: submittedNumbers }),
      }),
    consolidate: (sessionId) =>
      request(`/memory-game/sessions/${sessionId}/consolidate`, { method: "POST" }),
    getState: (sessionId) => request(`/memory-game/sessions/${sessionId}/state`),
    getHistory: (sessionId) => request(`/memory-game/sessions/${sessionId}/history`),
  },
}

export default api
