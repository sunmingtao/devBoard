import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App.jsx'

const events = [
  {
    id: 1,
    topic: 'devboard.tasks',
    partitionId: 0,
    messageOffset: 3,
    messageKey: '9',
    eventType: 'TASK_CREATED',
    taskId: 9,
    eventTimestamp: '2026-05-04T20:26:29.879Z',
    userId: 3,
    payload: '{"eventType":"TASK_CREATED"}',
    receivedAt: '2026-05-04T20:26:30.000Z'
  }
]

describe('App', () => {
  beforeEach(() => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => events
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders persisted events loaded from the API', async () => {
    render(<App />)

    expect(await screen.findByText('TASK_CREATED')).toBeInTheDocument()
    expect(screen.getByText('devboard.tasks')).toBeInTheDocument()
    expect(screen.getByText('Stored events')).toBeInTheDocument()
    expect(screen.getAllByText('1')).not.toHaveLength(0)
  })

  it('reloads when the row limit changes', async () => {
    const user = userEvent.setup()
    render(<App />)

    await screen.findByText('TASK_CREATED')
    await user.selectOptions(screen.getByLabelText(/rows/i), '25')

    await waitFor(() => {
      expect(fetch).toHaveBeenLastCalledWith('/api/events?limit=25', expect.any(Object))
    })
  })
})
