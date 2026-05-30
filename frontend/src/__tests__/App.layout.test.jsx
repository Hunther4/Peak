import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('../store/store', () => ({
  useStore: vi.fn(() => ({
    summary: { skills: [] },
    loading: false,
    error: null,
    clearError: vi.fn(),
    fetchSkills: vi.fn(),
    fetchSummary: vi.fn(),
    fetchTimeline: vi.fn(),
    fetchMentalReps: vi.fn(),
    fetchChallenges: vi.fn(),
    fetchBooksStatus: vi.fn(),
    fetchAiStatus: vi.fn(),
    profile: { name: 'Test', age: 25 },
    profileLoading: false,
    fetchProfile: vi.fn(),
  })),
}))

vi.mock('../api/client', () => ({
  default: { sessions: { clearAll: vi.fn() } },
  api: { sessions: { clearAll: vi.fn() } },
}))

vi.mock('../components/SkillCard', () => ({
  default: () => <div data-testid="skill-card" />,
}))

vi.mock('../components/Timeline', () => ({
  default: () => <div data-testid="timeline" />,
}))

vi.mock('../components/SessionForm', () => ({
  default: () => <div data-testid="session-form" />,
}))

vi.mock('../components/BooksPanel', () => ({
  default: () => <div data-testid="books-panel" />,
}))

vi.mock('../components/AiModeToggle', () => ({
  default: () => <div data-testid="ai-mode-toggle" />,
}))

vi.mock('../components/ModelInfo', () => ({
  default: () => <div data-testid="model-info" />,
}))

vi.mock('../components/MentalRepTimeline', () => ({
  default: () => <div data-testid="mental-reps" />,
}))

vi.mock('../components/ChallengeList', () => ({
  default: () => <div data-testid="challenge-list" />,
}))

vi.mock('../components/StatusIndicator', () => ({
  StatusIndicator: () => <div data-testid="status-indicator" />,
}))

vi.mock('../components/ProfileAvatar', () => ({
  default: () => <div data-testid="profile-avatar" />,
}))

vi.mock('../components/AmbientParticles', () => ({
  default: () => <div data-testid="ambient-particles" />,
}))

vi.mock('../components/Spotlight', () => ({
  default: () => <div data-testid="spotlight" />,
}))

vi.mock('../components/ui', () => ({
  ToastProvider: ({ children }) => <div>{children}</div>,
}))

vi.mock('../components/WelcomeScreen', () => ({
  default: () => <div data-testid="welcome-screen" />,
}))

vi.mock('../components/MemoryGame', () => ({
  default: () => <div data-testid="memory-game" />,
}))

vi.mock('../components/MathThinkingGame', () => ({
  default: () => <div data-testid="math-thinking-game" />,
}))

vi.mock('../components/DualNBackGame', () => ({
  default: () => <div data-testid="dual-nback-game" />,
}))

vi.mock('../components/IQPracticeGame', () => ({
  default: () => <div data-testid="iq-practice-game" />,
}))

vi.mock('../components/GuidedPractice', () => ({
  default: () => <div data-testid="guided-practice" />,
}))

import App from '../App'

describe('App dashboard layout', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders Skills section BEFORE SessionForm', () => {
    render(<App />)

    const skillsHeading = screen.getByText('Tus Skills')
    const registroButton = screen.getByText('Registro manual')

    const skillsSection = skillsHeading.closest('section')
    const sessionSection = registroButton.closest('section')

    expect(skillsSection).toBeTruthy()
    expect(sessionSection).toBeTruthy()

    const skillsIndex = Array.from(document.querySelectorAll('section')).indexOf(skillsSection)
    const sessionIndex = Array.from(document.querySelectorAll('section')).indexOf(sessionSection)

    expect(skillsIndex).toBeLessThan(sessionIndex)
  })

  it('SessionForm is collapsed by default', () => {
    render(<App />)

    const registroButton = screen.getByText('Registro manual')
    expect(registroButton).toBeInTheDocument()

    const sessionForm = screen.queryByTestId('session-form')
    expect(sessionForm).not.toBeInTheDocument()
  })
})
