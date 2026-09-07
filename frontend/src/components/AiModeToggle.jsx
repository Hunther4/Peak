import { useEffect } from "react"
import { useStore } from "../store/store"

export default function AiModeToggle() {
  const { ai_mode, setAiMode, fetchAiStatus } = useStore()

  useEffect(() => {
    fetchAiStatus()
  }, [])

  const handleToggle = (mode) => {
    if (ai_mode !== mode) {
      setAiMode(mode)
    }
  }

  return (
    <div className="flex bg-white/[0.03] rounded-xl p-1 border border-white/[0.06] transition-all duration-300 hover:border-white/[0.1]">
      <button
        onClick={() => handleToggle("local")}
        className={`px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded-lg transition-all duration-200 ${
          ai_mode === "local"
            ? "bg-blue-500/15 text-blue-400 border border-blue-500/20 shadow-sm"
            : "text-neutral-600 hover:text-neutral-400 border border-transparent"
        }`}
      >
        🖥 Local
      </button>
      <button
        onClick={() => handleToggle("api")}
        className={`px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded-lg transition-all duration-200 ${
          ai_mode === "api"
            ? "bg-green-500/15 text-green-400 border border-green-500/20 shadow-sm shadow-green-500/10"
            : "text-neutral-600 hover:text-neutral-400 border border-transparent"
        }`}
      >
        ☁ Cloud
      </button>
    </div>
  )
}
