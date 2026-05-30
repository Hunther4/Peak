import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useStore } from '../store'

vi.mock('../../api/client', () => ({
  api: {
    iqPractice: {
      createSession: vi.fn(),
      createRound: vi.fn(),
      submitAttempt: vi.fn(),
      consolidate: vi.fn(),
    },
  },
  default: {
    iqPractice: {
      createSession: vi.fn(),
      createRound: vi.fn(),
      submitAttempt: vi.fn(),
      consolidate: vi.fn(),
    },
  },
}))

import { api } from '../../api/client'

describe('IQ Practice store transitions', () => {
  beforeEach(() => {
    useStore.getState().resetIQPractice()
    vi.clearAllMocks()
  })

  it('has correct initial state', () => {
    const state = useStore.getState()
    expect(state.iqPhase).toBe('idle')
    expect(state.iqSession).toBeNull()
    expect(state.iqCurrentRound).toBeNull()
    expect(state.iqLastAttempt).toBeNull()
  })

  it('startIQPractice sets iqPhase=answering and iqSession', async () => {
    const session = { id: 's1', skill_id: 'sk1' }
    api.iqPractice.createSession.mockResolvedValue(session)

    const result = await useStore.getState().startIQPractice('sk1')

    expect(api.iqPractice.createSession).toHaveBeenCalledWith('sk1')
    expect(result).toEqual(session)
    const state = useStore.getState()
    expect(state.iqPhase).toBe('answering')
    expect(state.iqSession).toEqual(session)
  })

  it('createIQRound sets iqCurrentRound and iqPhase=answering', async () => {
    const session = { id: 's1' }
    const round = { id: 'r1', pattern: [1, 2, 3] }
    api.iqPractice.createSession.mockResolvedValue(session)
    api.iqPractice.createRound.mockResolvedValue(round)

    await useStore.getState().startIQPractice('sk1')
    const result = await useStore.getState().createIQRound()

    expect(api.iqPractice.createRound).toHaveBeenCalledWith('s1')
    expect(result).toEqual(round)
    const state = useStore.getState()
    expect(state.iqCurrentRound).toEqual(round)
    expect(state.iqPhase).toBe('answering')
    expect(state.iqLastAttempt).toBeNull()
  })

  it('submitIQAttempt sets iqLastAttempt and iqPhase=feedback', async () => {
    const session = { id: 's1' }
    const round = { id: 'r1' }
    const attempt = { id: 'a1', correct: true }
    api.iqPractice.createSession.mockResolvedValue(session)
    api.iqPractice.createRound.mockResolvedValue(round)
    api.iqPractice.submitAttempt.mockResolvedValue(attempt)

    await useStore.getState().startIQPractice('sk1')
    await useStore.getState().createIQRound()
    const result = await useStore.getState().submitIQAttempt('r1', 42)

    expect(api.iqPractice.submitAttempt).toHaveBeenCalledWith('r1', 42)
    expect(result).toEqual(attempt)
    const state = useStore.getState()
    expect(state.iqLastAttempt).toEqual(attempt)
    expect(state.iqPhase).toBe('feedback')
  })

  it('consolidateIQPractice sets iqPhase=done, clears iqLastAttempt and iqCurrentRound', async () => {
    const session = { id: 's1' }
    const round = { id: 'r1' }
    const consolidation = { score: 100 }
    api.iqPractice.createSession.mockResolvedValue(session)
    api.iqPractice.createRound.mockResolvedValue(round)
    api.iqPractice.consolidate.mockResolvedValue(consolidation)

    await useStore.getState().startIQPractice('sk1')
    await useStore.getState().createIQRound()
    const result = await useStore.getState().consolidateIQPractice()

    expect(api.iqPractice.consolidate).toHaveBeenCalledWith('s1')
    expect(result).toEqual(consolidation)
    const state = useStore.getState()
    expect(state.iqPhase).toBe('done')
    expect(state.iqLastAttempt).toBeNull()
    expect(state.iqCurrentRound).toBeNull()
  })

  it('resetIQPractice resets all IQ state back to idle defaults', async () => {
    const session = { id: 's1' }
    const round = { id: 'r1' }
    const consolidation = { score: 100 }
    api.iqPractice.createSession.mockResolvedValue(session)
    api.iqPractice.createRound.mockResolvedValue(round)
    api.iqPractice.consolidate.mockResolvedValue(consolidation)

    await useStore.getState().startIQPractice('sk1')
    await useStore.getState().createIQRound()
    await useStore.getState().consolidateIQPractice()

    // Verify state is set
    let state = useStore.getState()
    expect(state.iqPhase).toBe('done')

    // Reset
    useStore.getState().resetIQPractice()

    state = useStore.getState()
    expect(state.iqPhase).toBe('idle')
    expect(state.iqSession).toBeNull()
    expect(state.iqCurrentRound).toBeNull()
    expect(state.iqLastAttempt).toBeNull()
    expect(state.iqHistory).toEqual([])
    expect(state.iqError).toBeNull()
  })
})