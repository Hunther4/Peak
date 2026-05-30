import { api } from "../../api/client"

export const createProfileSlice = (set, get) => ({
  // State
  profile: null,
  profileLoading: true,

  // Actions
  fetchProfile: async () => {
    // Instant load from localStorage cache
    const cached = localStorage.getItem("peak_profile")
    if (cached) {
      try {
        const parsed = JSON.parse(cached)
        set({ profile: parsed, profileLoading: false })
        // Sync with backend in background (don't await)
        api.profile.get().then(profile => {
          if (profile) {
            set({ profile })
            localStorage.setItem("peak_profile", JSON.stringify(profile))
          } else {
            // Backend doesn't have a profile — clear stale cache
            localStorage.removeItem("peak_profile")
            set({ profile: null })
          }
        }).catch(() => {})
        return parsed
      } catch (_e) {}
    }
    // First time — fetch from API
    try {
      const profile = await api.profile.get()
      if (profile) {
        localStorage.setItem("peak_profile", JSON.stringify(profile))
      }
      set({ profile, profileLoading: false })
      return profile
    } catch (e) {
      set({ profileLoading: false })
      return null
    }
  },

  saveProfile: async (name, age) => {
    const profile = await api.profile.save({ name, age })
    set({ profile })
    localStorage.setItem("peak_profile", JSON.stringify(profile))
    return profile
  },

  uploadAvatar: async (file) => {
    const result = await api.profile.uploadAvatar(file)
    const updated = { ...get().profile, avatar_url: result.avatar_url }
    set({ profile: updated })
    localStorage.setItem("peak_profile", JSON.stringify(updated))
    return result
  }
})