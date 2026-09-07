import { Link } from "react-router"

export default function NotFound() {
  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center relative">
      {/* Ambient glow */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-green-500/[0.03] rounded-full blur-3xl" />
      </div>

      <div className="text-center relative z-10">
        <div className="text-8xl font-black text-white/10 mb-4">404</div>
        <h1 className="text-2xl font-bold text-white mb-2">Página no encontrada</h1>
        <p className="text-sm text-neutral-500 mb-8 max-w-md">
          La página que buscás no existe o fue movida.
        </p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold text-black bg-gradient-to-r from-green-400 to-emerald-500 hover:from-green-300 hover:to-emerald-400 transition-all duration-200 shadow-lg shadow-green-500/25 hover:shadow-green-500/40"
        >
          ← Volver al panel
        </Link>
      </div>
    </div>
  )
}
