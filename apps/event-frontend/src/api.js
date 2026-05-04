const EVENTS_API_URL = import.meta.env.VITE_EVENTS_API_URL || '/api/events'

export async function fetchEvents(limit = 100) {
  const response = await fetch(`${EVENTS_API_URL}?limit=${encodeURIComponent(limit)}`, {
    headers: {
      Accept: 'application/json'
    }
  })

  if (!response.ok) {
    throw new Error(`Event API returned ${response.status}`)
  }

  return response.json()
}
