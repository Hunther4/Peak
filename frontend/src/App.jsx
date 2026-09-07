import { useEffect, useCallback } from "react"
import { createBrowserRouter, RouterProvider } from "react-router"
import { useStore } from "./store/store"
import { ToastProvider } from "./components/ui"
import AppShell from "./components/layout/AppShell"
import Dashboard from "./pages/Dashboard"
import Practice from "./pages/Practice"
import Settings from "./pages/Settings"
import PaesStudy from "./pages/PaesStudy"
import NotFound from "./pages/NotFound"
import WelcomeScreen from "./components/WelcomeScreen"

// Card spotlight effect — global, runs once
function useCardSpotlight() {
  const handleMouseMove = useCallback((e) => {
    const card = e.target.closest('.card')
    if (!card) return
    const rect = card.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width) * 100
    const y = ((e.clientY - rect.top) / rect.height) * 100
    card.style.setProperty('--mouse-x', `${x}%`)
    card.style.setProperty('--mouse-y', `${y}%`)
  }, [])

  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove)
    return () => document.removeEventListener('mousemove', handleMouseMove)
  }, [handleMouseMove])
}

// Profile guard wrapper — shows spinner while loading, welcome if no profile
function ProfileGuard({ children }) {
  const { profile, profileLoading, fetchProfile } = useStore()

  useEffect(() => {
    fetchProfile()
  }, [])

  if (profileLoading) {
    return (
      <div className="min-h-screen bg-neutral-950 flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-neutral-700 border-t-green-500 rounded-full animate-spin" />
      </div>
    )
  }

  if (!profile) {
    return <WelcomeScreen />
  }

  return children
}

// Router configuration
const router = createBrowserRouter(
  [
    {
      path: "/",
      element: (
        <ProfileGuard>
          <ToastProvider>
            <AppShell />
          </ToastProvider>
        </ProfileGuard>
      ),
      children: [
        { index: true, element: <Dashboard /> },
        { path: "practice/:gameType", element: <Practice /> },
        { path: "paes", element: <PaesStudy /> },
        { path: "settings", element: <Settings /> },
        { path: "*", element: <NotFound /> },
      ],
    },
  ],
  {
    future: {
      v7_relativeSplatPath: true,
    },
  }
)

function App() {
  useCardSpotlight()

  return <RouterProvider router={router} />
}

export default App
