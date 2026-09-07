import { useEffect } from "react"
import { Outlet, NavLink, useNavigate } from "react-router"
import { StatusIndicator } from "../StatusIndicator"
import TopNavBar from "./TopNavBar"

const NAV_ITEMS = [
  { to: "/", icon: "🏠", label: "Centro de Mando", shortcut: "1", end: true },
  { to: "/gym", icon: "🧠", label: "Gimnasio Cognitivo", shortcut: "2" },
  { to: "/paes", icon: "📐", label: "Academia PAES M1", shortcut: "3" },
  { to: "/lab", icon: "🧪", label: "Laboratorio Metacognitivo", shortcut: "4" },
  { to: "/settings", icon: "⚙️", label: "Ajustes & Sistema", shortcut: "5" },
]

export default function AppShell() {
  const navigate = useNavigate()

  // Quick navigation shortcuts: keys 1 to 5 (when not inside an input)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (["INPUT", "TEXTAREA", "SELECT"].includes(e.target.tagName) || e.target.isContentEditable) {
        return
      }
      if (e.metaKey || e.ctrlKey || e.altKey) return

      const item = NAV_ITEMS.find((n) => n.shortcut === e.key)
      if (item) {
        navigate(item.to)
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [navigate])

  return (
    <div className="min-h-screen bg-neutral-950 relative text-neutral-100 selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* Sidebar — desktop only */}
      <aside className="hidden lg:flex fixed left-0 top-0 h-full w-18 flex-col items-center py-5 gap-3 border-r border-white/[0.06] bg-neutral-950/80 backdrop-blur-2xl z-40">
        {/* Brand Logo */}
        <NavLink
          to="/"
          className="w-11 h-11 rounded-2xl bg-gradient-to-br from-green-400 via-emerald-500 to-teal-600 flex items-center justify-center text-black font-black text-xl mb-4 shadow-xl shadow-green-500/20 hover:scale-105 transition-all group"
          title="Peak Practice · Inicio"
        >
          <span>P</span>
        </NavLink>

        {/* Nav items */}
        <nav className="flex flex-col items-center gap-2.5 w-full px-2">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `w-12 h-12 rounded-2xl flex flex-col items-center justify-center text-xl relative transition-all duration-200 group ${
                  isActive
                    ? "bg-green-500/15 border border-green-500/30 text-green-400 shadow-lg shadow-green-500/10"
                    : "hover:bg-white/[0.06] border border-transparent text-neutral-400 hover:text-white"
                }`
              }
              title={`${item.label} (Tecla ${item.shortcut})`}
            >
              <span>{item.icon}</span>
              <span className="text-[8px] font-mono text-neutral-500 group-hover:text-neutral-300 transition-colors">
                {item.shortcut}
              </span>
            </NavLink>
          ))}
        </nav>

        {/* Compact status at bottom */}
        <div className="mt-auto pb-3">
          <StatusIndicator compact />
        </div>
      </aside>

      {/* Main content area — offset by sidebar on desktop */}
      <div className="lg:ml-18 flex flex-col min-h-screen">
        {/* Universal Top Navigation Header */}
        <TopNavBar />

        {/* Page content */}
        <main className="flex-1 max-w-[1440px] w-full mx-auto px-4 lg:px-8 py-6 relative z-10 pb-24 lg:pb-8">
          <Outlet />
        </main>
      </div>

      {/* Bottom nav — mobile only */}
      <nav
        className="lg:hidden fixed bottom-0 left-0 right-0 z-50 border-t border-white/[0.08] bg-neutral-950/95 backdrop-blur-2xl"
        style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
      >
        <div className="flex items-center justify-around py-2 px-1">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 px-2.5 py-1.5 rounded-xl transition-all duration-200 ${
                  isActive
                    ? "text-green-400 font-bold"
                    : "text-neutral-500 hover:text-neutral-300 font-medium"
                }`
              }
            >
              <span className="text-base">{item.icon}</span>
              <span className="text-[8px] tracking-tight truncate max-w-[62px]">{item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
