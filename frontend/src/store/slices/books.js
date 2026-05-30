import { api } from "../../api/client"

export const createBooksSlice = (set) => ({
  // State
  books: [],
  booksLoading: false,
  isIndexing: false,
  indexingProgress: 0,

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
    set({ isIndexing: true, indexingProgress: 0 })
    try {
      await api.books.index(force)
      // Poll liviano: refrescamos status cada 3s hasta que termine
      const poll = setInterval(async () => {
        try {
          const data = await api.books.getStatus()
          set({
            books: data.books ?? [],
            isIndexing: data.is_indexing ?? false,
            indexingProgress: data.progress ?? 0,
          })
          if (!data.is_indexing) clearInterval(poll)
        } catch {
          clearInterval(poll)
          set({ isIndexing: false })
        }
      }, 3000)
    } catch (e) {
      set({ isIndexing: false })
      throw e
    }
  }
})