import { Activity, AlertCircle, Clock, Database, RefreshCw } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { fetchEvents } from './api.js'

const LIMIT_OPTIONS = [25, 50, 100, 250]

function formatDate(value) {
  if (!value) {
    return 'Unknown'
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'medium'
  }).format(new Date(value))
}

function eventTone(eventType) {
  if (eventType === 'TASK_CREATED') {
    return 'created'
  }
  if (eventType === 'TASK_UPDATED') {
    return 'updated'
  }
  return 'neutral'
}

function App() {
  const [events, setEvents] = useState([])
  const [limit, setLimit] = useState(100)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadEvents = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await fetchEvents(limit)
      setEvents(data)
    } catch (err) {
      setError(err.message || 'Unable to load events')
    } finally {
      setLoading(false)
    }
  }, [limit])

  useEffect(() => {
    loadEvents()
  }, [loadEvents])

  const stats = useMemo(() => {
    const eventTypes = new Set(events.map((event) => event.eventType).filter(Boolean))
    const latestReceivedAt = events[0]?.receivedAt

    return {
      total: events.length,
      eventTypes: eventTypes.size,
      latestReceivedAt
    }
  }, [events])

  return (
    <main className="event-shell">
      <section className="toolbar" aria-label="Event controls">
        <div className="title-block">
          <div className="app-mark" aria-hidden="true">
            <Activity size={22} />
          </div>
          <div>
            <h1>DevBoard Events</h1>
            <p>Kafka task events persisted by event-service</p>
          </div>
        </div>

        <div className="controls">
          <label className="limit-control">
            <span>Rows</span>
            <select value={limit} onChange={(event) => setLimit(Number(event.target.value))}>
              {LIMIT_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>

          <button type="button" className="icon-button" onClick={loadEvents} disabled={loading} aria-label="Refresh events">
            <RefreshCw size={18} className={loading ? 'spin' : ''} />
          </button>
        </div>
      </section>

      <section className="summary-grid" aria-label="Event summary">
        <article className="summary-tile">
          <Database size={18} />
          <span>{stats.total}</span>
          <p>Stored events</p>
        </article>
        <article className="summary-tile">
          <Activity size={18} />
          <span>{stats.eventTypes}</span>
          <p>Event types</p>
        </article>
        <article className="summary-tile wide">
          <Clock size={18} />
          <span>{formatDate(stats.latestReceivedAt)}</span>
          <p>Latest received</p>
        </article>
      </section>

      {error && (
        <section className="error-banner" role="alert">
          <AlertCircle size={18} />
          <span>{error}</span>
        </section>
      )}

      <section className="event-table" aria-label="Persisted events">
        <div className="event-head">
          <span>Type</span>
          <span>Task</span>
          <span>Kafka position</span>
          <span>Received</span>
        </div>

        {loading && events.length === 0 ? (
          <div className="empty-state">Loading events...</div>
        ) : events.length === 0 ? (
          <div className="empty-state">No persisted events yet.</div>
        ) : (
          events.map((event) => (
            <article className="event-row" key={event.id ?? `${event.topic}-${event.partitionId}-${event.messageOffset}`}>
              <div>
                <span className={`event-pill ${eventTone(event.eventType)}`}>{event.eventType || 'UNKNOWN'}</span>
                <p>{event.eventTimestamp ? formatDate(event.eventTimestamp) : 'No event timestamp'}</p>
              </div>
              <div>
                <strong>{event.taskId ?? '-'}</strong>
                <p>User {event.userId ?? '-'}</p>
              </div>
              <div>
                <strong>{event.topic}</strong>
                <p>
                  partition {event.partitionId}, offset {event.messageOffset}
                </p>
              </div>
              <div>
                <strong>{formatDate(event.receivedAt)}</strong>
                <details>
                  <summary>Payload</summary>
                  <pre>{event.payload}</pre>
                </details>
              </div>
            </article>
          ))
        )}
      </section>
    </main>
  )
}

export default App
