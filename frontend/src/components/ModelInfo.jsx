import { useStore } from "../store/store"

export default function ModelInfo() {
  const { ai_mode, best_model } = useStore()

  return (
    <div className="card space-y-4 relative overflow-hidden">
      {/* Top accent line */}
      <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent rounded-full" />
      
      {/* Ambient background glow */}
      <div className="absolute -right-20 -bottom-20 w-64 h-64 bg-cyan-500/[0.03] rounded-full blur-3xl pointer-events-none" />
      
      <h3 className="section-title !mb-0 relative z-10">Motor de IA</h3>

      <div className="flex items-center gap-3 relative z-10">
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center text-sm transition-all duration-300 hover:scale-105 ${
          ai_mode === "api"
            ? "bg-green-500/10 text-green-400 border border-green-500/20 hover:border-green-500/30 hover:shadow-glow-green"
            : "bg-blue-500/10 text-blue-400 border border-blue-500/20 hover:border-blue-500/30 hover:shadow-glow-blue"
        }`}>
          {ai_mode === "api" ? "☁" : "🖥"}
        </div>
        <div>
          <p className="text-sm font-semibold text-white">
            {ai_mode === "api" ? "Cloud Router" : "LM Studio Local"}
          </p>
          <p className="text-[10px] text-neutral-600 uppercase tracking-wider">
            {ai_mode === "api" ? "Groq → OpenRouter → Fallback" : "GPU · Sin límites"}
          </p>
        </div>
      </div>

      {best_model && (
        <div className="bg-white/[0.02] border border-white/[0.04] rounded-xl p-3 flex items-center justify-between relative z-10 transition-all duration-300 hover:border-cyan-500/20 hover:bg-white/[0.03] group/model">
          <div>
            <p className="text-xs font-semibold text-neutral-300 group-hover/model:text-white transition-colors duration-300">{best_model.name}</p>
            <p className="text-[10px] text-neutral-600 mt-0.5">{best_model.provider} · Auditoría</p>
          </div>
          {best_model.score && (
            <div className="text-right">
              <p className="text-lg font-black text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-500">{best_model.score}</p>
              <p className="text-[8px] text-neutral-700 uppercase">score</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
