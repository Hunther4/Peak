import { Outlet, NavLink } from "react-router"
import { StatusIndicator } from "../StatusIndicator"

const NAV_ITEMS = [
  { to: "/", icon: "🏠", label: "Panel", end: true },
  { to: "/paes", icon: "📐", label: "PAES M1" },
  { to: "/settings", icon: "⚙️", label: "Ajustes" },
]

export default function AppShell() {
  return (
    <div className="min-h-screen bg-neutral-950 relative">
      {/* Sidebar — desktop only */}
      <aside className="hidden lg:flex fixed left-0 top-0 h-full w-16 flex-col items-center py-6 gap-2 border-r border-white/[0.06] bg-neutral-950/80 backdrop-blur-xl z-40">
        {/* Logo */}
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-black font-black text-lg mb-6 shadow-lg shadow-green-500/25">
          P
        </div>

        {/* Nav items */}
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              `w-10 h-10 rounded-xl flex items-center justify-center text-lg transition-all duration-200 ${
                isActive
                  ? "bg-green-500/15 border border-green-500/20 shadow-sm"
                  : "hover:bg-white/[0.04] border border-transparent"
              }`
            }
            title={item.label}
          >
            {item.icon}
          </NavLink>
        ))}

        {/* Status at bottom */}
        <div className="mt-auto pb-2">
          <StatusIndicator compact />
        </div>
      </aside>

      {/* Main content — offset by sidebar on desktop */}
      <div className="lg:ml-16">
        {/* Mobile header */}
        <header className="lg:hidden sticky top-0 z-50 border-b border-white/[0.06] glass-panel" style={{ backdropFilter: 'blur(24px) saturate(1.8)' }}>
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-black font-black text-sm">
                P
              </div>
              <span className="text-sm font-bold text-white">Peak</span>
            </div>
            <StatusIndicator />
          </div>
        </header>

        {/* Page content */}
        <main className="max-w-[1400px] mx-auto px-4 lg:px-8 py-6 relative z-10">
          <Outlet />
        </main>
      </div>

      {/* Bottom nav — mobile only */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-50 border-t border-white/[0.06] bg-neutral-950/90 backdrop-blur-xl" style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}>
        <div className="flex items-center justify-around py-2">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex flex-col items-center gap-1 px-4 py-2 rounded-xl transition-all duration-200 ${
                  isActive
                    ? "text-green-400"
                    : "text-neutral-500 hover:text-neutral-300"
                }`
              }
            >
              <span className="text-lg">{item.icon}</span>
              <span className="text-[9px] font-bold uppercase tracking-wider">{item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
