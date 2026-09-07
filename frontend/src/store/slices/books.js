import { api } from "../../api/client"

export const createBooksSlice = (set, get) => ({
  // State
  books: [],
  booksLoading: false,
  isIndexing: false,
  indexingProgress: 0,
  _indexPollCleanup: null,

  // Actions
  fetchBooksStatus: async () => {
    set({ booksLoading: true })
    try {
      const data = await api.books.getStatus()
      set({
        books: data.books ?? [],
        isIndexing: data.is_indexing ?? false,
        indexingProgress: data.progress ?? 0,
        booksLoading: false,
      })
    } catch (e) {
      console.warn("[store] fetchBooksStatus error:", e.message)
      set({ booksLoading: false })
    }
  },

  indexBooks: async (force = false) => {
    // Cleanup any existing poll
    const prev = get()._indexPollCleanup
    if (prev) prev()

    set({ isIndexing: true, indexingProgress: 0 })
    try {
      await api.books.index(force)
      // Poll liviano: refrescamos status cada 3s hasta que termine (max 60 = 3 min)
      let retries = 0
      const MAX_RETRIES = 60
      const poll = setInterval(async () => {
        retries++
        try {
          const data = await api.books.getStatus()
          set({
            books: data.books ?? [],
            isIndexing: data.is_indexing ?? false,
            indexingProgress: data.progress ?? 0,
          })
          if (!data.is_indexing || retries >= MAX_RETRIES) clearInterval(poll)
        } catch {
          clearInterval(poll)
          set({ isIndexing: false })
        }
      }, 3000)
      const cleanup = () => clearInterval(poll)
      set({ _indexPollCleanup: cleanup })
    } catch (e) {
      set({ isIndexing: false })
      throw e
    }
  }
})