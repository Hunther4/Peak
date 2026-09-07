const BASE_URL = import.meta.env.VITE_API_URL || "/api"

// API key is held in memory only, not localStorage
let API_KEY = import.meta.env.VITE_PEAK_API_KEY || null

export const setClientApiKey = (key) => {
  API_KEY = key
}

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
    clearAll: () =>
      request("/sessions/clear-all", { method: "POST" }),
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
    createSession: (skillId) =>
      request("/memory-game/sessions", {
        method: "POST",
        body: JSON.stringify({ skill_id: skillId }),
      }),
    createRound: (sessionId) =>
      request(`/memory-game/sessions/${sessionId}/rounds`, { method: "POST" }),
    submitAttempt: (roundId, submittedNumbers) =>
      request(`/memory-game/rounds/${roundId}/attempts`, {
        method: "POST",
        body: JSON.stringify({ submitted_numbers: submittedNumbers }),
      }),
    consolidate: (sessionId, body) => {
      const opts = { method: "POST" }
      if (body !== undefined) opts.body = JSON.stringify(body)
      return request(`/memory-game/sessions/${sessionId}/consolidate`, opts)
    },
    getState: (sessionId) => request(`/memory-game/sessions/${sessionId}/state`),
    getHistory: (sessionId) => request(`/memory-game/sessions/${sessionId}/history`),
    logStrategy: (roundId, strategyUsed) =>
      request(`/memory-game/rounds/${roundId}/strategy-log`, {
        method: "POST",
        body: JSON.stringify({ strategy_used: strategyUsed }),
      }),
    saveMeta: (sessionId, meta) =>
      request(`/memory-game/sessions/${sessionId}/meta`, {
        method: "POST",
        body: JSON.stringify({
          strategy_type: meta.strategy_type,
          self_reported_difficulty: meta.self_reported_difficulty,
          notes: meta.notes,
        }),
      }),
  },

  mathThinking: {
    createSession: (skillId) =>
      request("/math-thinking/sessions", {
        method: "POST",
        body: JSON.stringify({ skill_id: skillId }),
      }),
    createRound: (sessionId) =>
      request(`/math-thinking/sessions/${sessionId}/rounds`, { method: "POST" }),
    submitAttempt: (roundId, userAnswer) =>
      request(`/math-thinking/rounds/${roundId}/attempts`, {
        method: "POST",
        body: JSON.stringify({ user_answer: userAnswer }),
      }),
    consolidate: (sessionId, body) => {
      const opts = { method: "POST" }
      if (body !== undefined) opts.body = JSON.stringify(body)
      return request(`/math-thinking/sessions/${sessionId}/consolidate`, opts)
    },
    getState: (sessionId) => request(`/math-thinking/sessions/${sessionId}/state`),
    getHistory: (sessionId) => request(`/math-thinking/sessions/${sessionId}/history`),
    getHint: (roundId) => request(`/math-thinking/rounds/${roundId}/hint`),
  },

  // --- IQ Practice ---
  iqPractice: {
    createSession: (skillId) =>
      request("/iq-practice/sessions", {
        method: "POST",
        body: JSON.stringify({ skill_id: skillId }),
      }),
    createRound: (sessionId) =>
      request(`/iq-practice/sessions/${sessionId}/rounds`, { method: "POST" }),
    submitAttempt: (roundId, userAnswer) =>
      request(`/iq-practice/rounds/${roundId}/attempts`, {
        method: "POST",
        body: JSON.stringify({ user_answer: userAnswer }),
      }),
    consolidate: (sessionId, body) => {
      const opts = { method: "POST" }
      if (body !== undefined) opts.body = JSON.stringify(body)
      return request(`/iq-practice/sessions/${sessionId}/consolidate`, opts)
    },
    getState: (sessionId) => request(`/iq-practice/sessions/${sessionId}/state`),
    getHistory: (sessionId) => request(`/iq-practice/sessions/${sessionId}/history`),
  },

  // --- Cognitive Telemetry (Dual N-Back) ---
  cognitive: {
    getSkills: () => request("/cognitive/skills/"),
    createSkill: (nombre, descripcion, faseIqBase = 100) =>
      request("/cognitive/skills/", {
        method: "POST",
        body: JSON.stringify({ nombre, descripcion, fase_iq_base: faseIqBase }),
      }),
    createSession: (cognitiveSkillId) =>
      request("/cognitive/sessions/", {
        method: "POST",
        body: JSON.stringify({ cognitive_skill_id: cognitiveSkillId }),
      }),
    uploadTrials: (sessionId, trials) =>
      request("/cognitive/trials/", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, trials }),
      }),
    finalizeSession: (sessionId, body) => {
      const opts = { method: "POST" }
      if (body !== undefined) opts.body = JSON.stringify(body)
      return request(`/cognitive/sessions/${sessionId}/finalize/`, opts)
    },
    consolidate: (sessionId, body) => {
      const opts = { method: "POST" }
      if (body !== undefined) opts.body = JSON.stringify(body)
      return request(`/cognitive/sessions/${sessionId}/consolidate`, opts)
    },
  },

  // --- PAES M1 Adaptive Learning Engine ---
  paes: {
    getFsrsStatus: (userId = 1) => request(`/paes/fsrs/status?user_id=${userId}`),
    getCurriculumSubtopics: (userId = 1) => request(`/paes/curriculum/subtopics?user_id=${userId}`),
    startStudySession: (sessionMode = "PRACTICE", subtopicSlug = null, questionCount = null) =>
      request("/paes/study/session/start", {
        method: "POST",
        body: JSON.stringify({
          session_mode: sessionMode,
          subtopic_slug: subtopicSlug,
          question_count: questionCount,
        }),
      }),
    finalizeExam: (sessionId, answers) =>
      request(`/paes/study/session/${sessionId}/finalize_exam`, {
        method: "POST",
        body: JSON.stringify({ answers }),
      }),
    submitAttempt: (data) =>
      request("/paes/study/session/submit", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    getParametricQuestion: (templateCode, seed = null) =>
      request("/paes/questions/generate_parametric", {
        method: "POST",
        body: JSON.stringify({ template_code: templateCode, seed }),
      }),
    getSocraticHint: (sessionId, questionId, requestedLevel = 1, studentMessage = null) =>
      request("/paes/tutor/step", {
        method: "POST",
        body: JSON.stringify({
          session_id: sessionId,
          question_id: questionId,
          requested_level: requestedLevel,
          student_message: studentMessage,
        }),
      }),
    generateStudyPlan: (studyHoursWeekly = 10, targetScore = 750) =>
      request("/paes/study/plan/generate", {
        method: "POST",
        body: JSON.stringify({ study_hours_weekly: studyHoursWeekly, target_score: targetScore }),
      }),
    searchDemre: (query, topK = 3) =>
      request(`/paes/rag/search?query=${encodeURIComponent(query)}&top_k=${topK}`),
    convertScore: (rawScore) =>
      request(`/paes/score/convert?raw_score=${rawScore}`),
  },
}

export default api
