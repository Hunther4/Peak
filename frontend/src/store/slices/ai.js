import { api } from "../../api/client"

export const createAISlice = (set, get) => ({
  // State
  ai_mode: "local",
  available_models: [],
  best_model: null,
  selectedModel: { auto: true },

  // Actions
  fetchAiStatus: async () => {
    try {
      const statusRes = await api.models.getStatus()
      set({ ai_mode: statusRes.mode })

      const modelsRes = await api.models.getAvailable()
      set({ available_models: modelsRes })

      const bestRes = await api.models.getBest("audit")
      set({ best_model: bestRes })

      const selRes = await api.models.getSelection()
      set({ selectedModel: selRes.selection })
    } catch (e) {
      console.warn("[store] fetchAiStatus error:", e.message)
    }
  },

  setAiMode: async (mode) => {
    try {
      await api.models.setMode(mode)
      set({ ai_mode: mode })
      get().fetchAiStatus()
    } catch (e) {
      console.warn("[store] setAiMode error:", e.message)
    }
  },

  selectModel: async (modelName, provider, modelId) => {
    try {
      await api.models.select(modelName, provider, modelId)
      set({
        selectedModel: {
          auto: false,
          model_name: modelName,
          provider,
          model_id: modelId,
        },
      })
    } catch (e) {
      console.warn("[store] selectModel error:", e.message)
      throw e
    }
  },

  selectModelAuto: async () => {
    try {
      await api.models.selectAuto()
      set({ selectedModel: { auto: true } })
    } catch (e) {
      console.warn("[store] selectModelAuto error:", e.message)
      throw e
    }
  }
})