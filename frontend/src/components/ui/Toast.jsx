import { useState, useCallback, createContext, useContext } from "react"

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = "info", duration = 4000) => {
    const id = Date.now() + Math.random()
    setToasts((prev) => [...prev, { id, message, type, duration, exiting: false }])
    setTimeout(() => {
      setToasts((prev) => prev.map((t) => (t.id === id ? { ...t, exiting: true } : t)))
      setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 300)
    }, duration)
  }, [])

  const toast = {
    success: (msg) => addToast(msg, "success"),
    error: (msg) => addToast(msg, "error"),
    warning: (msg) => addToast(msg, "warning"),
    info: (msg) => addToast(msg, "info"),
  }

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <ToastContainer toasts={toasts} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  return useContext(ToastContext)
}

function ToastContainer({ toasts }) {
  if (toasts.length === 0) return null

  const icons = { success: "✓", error: "✕", warning: "⚠", info: "ℹ" }
  const colors = {
    success: "border-green-500/30 bg-green-500/10",
    error: "border-red-500/30 bg-red-500/10",
    warning: "border-yellow-500/30 bg-yellow-500/10",
    info: "border-blue-500/30 bg-blue-500/10",
  }
  const iconColors = {
    success: "text-green-400 bg-green-500/20",
    error: "text-red-400 bg-red-500/20",
    warning: "text-yellow-400 bg-yellow-500/20",
    info: "text-blue-400 bg-blue-500/20",
  }

  return (
    <div className="fixed top-6 right-6 z-[100] flex flex-col gap-3 max-w-sm">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`${t.exiting ? "toast-exit" : "toast"} flex items-start gap-3 px-4 py-3 rounded-xl border backdrop-blur-xl ${colors[t.type]}`}
          role="alert"
        >
          <span
            className={`w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 ${iconColors[t.type]}`}
          >
            {icons[t.type]}
          </span>
          <p className="text-sm text-neutral-200 leading-relaxed">{t.message}</p>
        </div>
      ))}
    </div>
  )
}
