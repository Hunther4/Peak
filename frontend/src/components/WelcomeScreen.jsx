import { useState } from "react"
import { useStore } from "../store/store"
import AmbientParticles from "./AmbientParticles"

function WelcomeScreen() {
  const { saveProfile } = useStore()
  const [name, setName] = useState("")
  const [age, setAge] = useState("")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!name.trim() || !age) return

    setSaving(true)
    setError(null)
    try {
      await saveProfile(name.trim(), parseInt(age, 10))
    } catch (err) {
      setError(err.message)
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-950 relative flex items-center justify-center overflow-hidden">
      {/* Ambient Background Effects — same mesh as main app */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-[40%] -left-[20%] w-[60%] h-[60%] bg-green-500/[0.03] rounded-full blur-[120px]" style={{ animation: 'mesh-shift 15s ease-in-out infinite' }} />
        <div className="absolute -bottom-[30%] -right-[15%] w-[50%] h-[50%] bg-emerald-600/[0.02] rounded-full blur-[100px]" style={{ animation: 'mesh-shift 20s ease-in-out infinite reverse' }} />
        <div className="absolute top-[20%] right-[10%] w-[30%] h-[30%] bg-blue-500/[0.02] rounded-full blur-[80px]" style={{ animation: 'mesh-shift 18s ease-in-out infinite' }} />
        <div className="absolute bottom-[10%] left-[5%] w-[25%] h-[25%] bg-purple-500/[0.015] rounded-full blur-[90px]" style={{ animation: 'mesh-shift 22s ease-in-out infinite reverse' }} />
      </div>

      <AmbientParticles />

      {/* Welcome Card */}
      <div
        className="relative z-10 w-full max-w-md mx-4"
        style={{ animation: 'fadeInUp 0.6s ease-out both' }}
      >
        <div className="card p-8 md:p-10 text-center">
          {/* Logo */}
          <div className="mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-black font-black text-2xl shadow-lg shadow-green-500/25 mx-auto mb-4">
              P
            </div>
            <h1 className="text-2xl md:text-3xl font-black tracking-tight text-white">
              Peak <span className="text-green-400/80 font-semibold">Practice</span>
            </h1>
            <p className="text-xs uppercase tracking-[0.25em] text-neutral-500 font-medium mt-1.5">
              Práctica Deliberada 🎯
            </p>
          </div>

          {/* Divider */}
          <div className="h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent mb-6" />

          {/* Greeting */}
          <p className="text-neutral-300 text-base mb-2">Bienvenido a Peak</p>
          <p className="text-neutral-500 text-xs mb-8">
            Contanos quién sos para empezar
          </p>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4 text-left">
            <div>
              <label className="block text-xs font-medium text-neutral-400 mb-1.5 uppercase tracking-wider">
                Nombre
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Tu nombre"
                required
                className="input"
                autoFocus
                disabled={saving}
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-neutral-400 mb-1.5 uppercase tracking-wider">
                Edad
              </label>
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="Tu edad"
                min={1}
                max={150}
                required
                className="input"
                disabled={saving}
              />
            </div>

            {error && (
              <p className="text-xs text-red-400 text-center">{error}</p>
            )}

            <button
              type="submit"
              disabled={saving || !name.trim() || !age}
              className="btn btn-primary w-full mt-2"
            >
              {saving ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-black/30 border-t-black/80 rounded-full animate-spin" />
                  Guardando...
                </span>
              ) : (
                "Comenzar 🚀"
              )}
            </button>
          </form>

          {/* Footer */}
          <p className="text-[10px] text-neutral-700 uppercase tracking-widest mt-8">
            Peak Practice · Práctica Deliberada
          </p>
        </div>
      </div>
    </div>
  )
}

export default WelcomeScreen
