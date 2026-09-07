import { useState } from "react"
import { useStore } from "../store/store"
import { useToast } from "./ui"

const PROVIDER_LABELS = {
  groq: "Groq",
  openrouter: "OpenRouter",
  lm_studio: "LM Studio",
}

const PROVIDER_ICONS = {
  groq: "⚡",
  openrouter: "🌐",
  lm_studio: "🖥",
}

function groupByProvider(models) {
  const groups = {}
  for (const m of models) {
    if (!groups[m.provider]) groups[m.provider] = []
    groups[m.provider].push(m)
  }
  return groups
}

export default function ModelInfo() {
  const { ai_mode, best_model, available_models, selectedModel, selectModel, selectModelAuto, fetchAiStatus } = useStore()
  const toast = useToast()
  const [modalOpen, setModalOpen] = useState(false)
  const [selected, setSelected] = useState(null)

  const openModal = () => {
    setSelected(selectedModel?.auto ? "auto" : `${selectedModel.provider}|${selectedModel.model_id}`)
    setModalOpen(true)
  }

  const closeModal = () => setModalOpen(false)

  const handleSave = async () => {
    try {
      if (selected === "auto") {
        await selectModelAuto()
        toast?.success("Selección automática activada")
      } else {
        const [provider, modelId] = selected.split("|")
        const model = available_models.find((m) => m.model_id === modelId && m.provider === provider)
        if (model) {
          await selectModel(model.name, model.provider, model.model_id)
          toast?.success(`Modelo cambiado a ${model.name}`)
        }
      }
      fetchAiStatus()
      closeModal()
    } catch (e) {
      toast?.error(e.message)
    }
  }

  const groups = groupByProvider(available_models)
  const providerOrder = ["groq", "openrouter", "lm_studio"]

  return (
    <>
      <div className="card space-y-4 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent rounded-full" />
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

        {/* Current selection indicator */}
        <div className="bg-white/[0.02] border border-white/[0.04] rounded-xl p-3 relative z-10">
          {selectedModel?.auto ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs text-green-400 font-bold">✦</span>
                <div>
                  <p className="text-xs font-semibold text-neutral-300">Recomendada (automática)</p>
                  {best_model && (
                    <p className="text-[10px] text-neutral-600 mt-0.5">
                      {best_model.name} · {best_model.provider}
                    </p>
                  )}
                </div>
              </div>
              {best_model?.score && (
                <div className="text-right">
                  <p className="text-sm font-black text-green-400">{best_model.score}</p>
                  <p className="text-[8px] text-neutral-700 uppercase">score</p>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs text-cyan-400 font-bold">◈</span>
                <div>
                  <p className="text-xs font-semibold text-neutral-300">{selectedModel.model_name}</p>
                  <p className="text-[10px] text-neutral-600 mt-0.5">
                    {PROVIDER_LABELS[selectedModel.provider] || selectedModel.provider} · Manual
                  </p>
                </div>
              </div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-500/70 border border-cyan-500/20 bg-cyan-500/10 px-2 py-0.5 rounded-full">
                Manual
              </span>
            </div>
          )}
        </div>

        <button
          onClick={openModal}
          className="relative z-10 w-full btn btn-ghost text-[11px] font-bold uppercase tracking-wider py-2"
        >
          Seleccionar modelo
        </button>
      </div>

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center p-4" onClick={closeModal}>
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" aria-hidden="true" style={{ animation: "fadeIn 0.2s ease-out" }} />
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="model-modal-title"
            className="relative bg-neutral-900/95 border border-white/[0.08] rounded-2xl p-6 max-w-lg w-full shadow-2xl max-h-[80vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
            onKeyDown={(e) => { if (e.key === "Escape") closeModal() }}
            style={{ animation: "fadeInUp 0.3s cubic-bezier(0.4, 0, 0.2, 1)" }}
          >
            <h3 id="model-modal-title" className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500" />
              Seleccionar modelo
            </h3>
            <p className="text-[11px] text-neutral-500 mb-4">
              Elegí manualmente o dejá la selección inteligente
            </p>

            <div className="overflow-y-auto flex-1 -mx-6 px-6 space-y-2">
              {/* Auto option */}
              <label
                className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all duration-200 ${
                  selected === "auto"
                    ? "border-green-500/40 bg-green-500/10"
                    : "border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04] hover:border-white/[0.1]"
                }`}
                onClick={() => setSelected("auto")}
              >
                <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors ${
                  selected === "auto" ? "border-green-400" : "border-neutral-600"
                }`}>
                  {selected === "auto" && <div className="w-2.5 h-2.5 rounded-full bg-green-400" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-lg bg-green-500/15 flex items-center justify-center text-[10px]">✦</span>
                    <p className="text-sm font-semibold text-white">Recomendada (automática)</p>
                    <span className="text-[9px] font-bold uppercase tracking-wider text-green-400/70 border border-green-500/20 bg-green-500/10 px-1.5 py-0.5 rounded-full">
                      Default
                    </span>
                  </div>
                  {best_model && (
                    <p className="text-[11px] text-neutral-500 mt-1 ml-7">
                      Mejor opción según la tarea · Actual: {best_model.name} ({best_model.score})
                    </p>
                  )}
                </div>
              </label>

              <div className="h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent my-3" />

              {/* Providers */}
              {providerOrder.map((provider) => {
                const models = groups[provider]
                if (!models || models.length === 0) return null
                return (
                  <div key={provider} className="space-y-1">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-neutral-600 px-1 py-1.5 flex items-center gap-1.5">
                      <span>{PROVIDER_ICONS[provider]}</span>
                      {PROVIDER_LABELS[provider] || provider}
                    </p>
                    {models.map((m) => (
                      <label
                        key={`${m.provider}|${m.model_id}`}
                        className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all duration-200 ${
                          selected === `${m.provider}|${m.model_id}`
                            ? "border-cyan-500/40 bg-cyan-500/10"
                            : "border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04] hover:border-white/[0.1]"
                        }`}
                        onClick={() => setSelected(`${m.provider}|${m.model_id}`)}
                      >
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors ${
                          selected === `${m.provider}|${m.model_id}` ? "border-cyan-400" : "border-neutral-600"
                        }`}>
                          {selected === `${m.provider}|${m.model_id}` && <div className="w-2.5 h-2.5 rounded-full bg-cyan-400" />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-white truncate">{m.name}</p>
                          <p className="text-[10px] text-neutral-500 mt-0.5">
                            {m.context_window ? `${(m.context_window / 1024).toFixed(0)}K contexto` : ""}
                            {m.capabilities ? ` · ${m.capabilities.split("|").join(", ")}` : ""}
                          </p>
                        </div>
                        {m.score && (
                          <div className="text-right shrink-0">
                            <p className="text-sm font-black text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-500">{m.score}</p>
                            <p className="text-[8px] text-neutral-700 uppercase">score</p>
                          </div>
                        )}
                      </label>
                    ))}
                  </div>
                )
              })}
            </div>

            <div className="flex items-center justify-end gap-3 mt-4 pt-4 border-t border-white/[0.06]">
              <button onClick={closeModal} className="btn btn-ghost text-xs">
                Cancelar
              </button>
              <button onClick={handleSave} className="btn btn-primary text-xs">
                Guardar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}