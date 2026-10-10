import { CalendarDays, MapPin, ShieldCheck, Sparkles } from 'lucide-react'
import type { Match, Signal } from '../types'
import ItemImage from './ItemImage'
import { formatDate } from './UI'

const labels: Record<Signal, string> = {
  text: 'Description match',
  image: 'Photo match',
  location: 'Campus location match',
  time: 'Time match',
  category: 'Category match',
}
export default function MatchCard({
  match,
  rank,
  onVerify,
}: {
  match: Match
  rank: number
  onVerify: (match: Match) => void
}) {
  const percent = Math.round(match.score * 100)
  const level =
    match.label === 'High Match' ? 'high' : match.label === 'Possible Match' ? 'possible' : 'low'
  return (
    <article className={`match-card ${rank === 1 ? 'top-match' : ''}`}>
      <div className="match-card-main">
        <div className="match-photo">
          <ItemImage item={match.item} />
          <span className="rank-badge">
            {rank === 1 ? (
              <>
                <Sparkles size={12} /> TOP RESULT
              </>
            ) : (
              `MATCH ${String(rank).padStart(2, '0')}`
            )}
          </span>
        </div>
        <div className="match-summary">
          <div className="category-label">{match.item.category}</div>
          <h2>{match.item.name}</h2>
          <p className="match-description">
            Private identifying details and the original photo are withheld for ownership
            verification.
          </p>
          <div className="match-meta">
            <span>
              <MapPin size={14} />
              {match.item.location || 'Location unknown'}
            </span>
            <span>
              <CalendarDays size={14} />
              {formatDate(match.item.event_date)}
            </span>
          </div>
        </div>
        <div className="match-score">
          <span className={`match-label ${level}`}>{match.label}</span>
          <strong>
            {percent}
            <span>%</span>
          </strong>
          <p>similarity</p>
          <button className="button secondary verify-button" onClick={() => onVerify(match)}>
            <ShieldCheck size={15} /> Verify this match
          </button>
        </div>
      </div>
      <div className="score-breakdown">
        <div className="breakdown-title">THE DETAILS BEHIND THIS MATCH</div>
        <div className="signal-grid">
          {(Object.entries(match.components) as [Signal, number | null][]).map(([key, value]) => (
            <div className="signal" key={key}>
              <div>
                <span>{labels[key]}</span>
                <strong>{value === null ? '—' : `${Math.round(value * 100)}%`}</strong>
              </div>
              <div
                className="progress-track"
                role={value === null ? undefined : 'meter'}
                aria-label={value === null ? undefined : labels[key]}
                aria-valuemin={value === null ? undefined : 0}
                aria-valuemax={value === null ? undefined : 100}
                aria-valuenow={value === null ? undefined : Math.round(value * 100)}
              >
                <span style={{ width: `${(value || 0) * 100}%` }} />
              </div>
              <p>
                {value === null
                  ? 'Unavailable or not used'
                  : `${Math.round((match.effective_weights[key] || 0) * 100)}% of match score`}
              </p>
            </div>
          ))}
        </div>
      </div>
    </article>
  )
}
