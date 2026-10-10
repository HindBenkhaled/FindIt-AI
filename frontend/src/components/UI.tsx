import type { ReactNode } from 'react'
import { AlertCircle, ArrowRight, LoaderCircle, SearchX, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'

export function PageHeading({
  eyebrow,
  title,
  description,
  aside,
}: {
  eyebrow: string
  title: string
  description: string
  aside?: ReactNode
}) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {aside}
    </div>
  )
}
export function ErrorNotice({ message, retry }: { message: string; retry?: () => void }) {
  return (
    <div className="notice error" role="alert">
      <AlertCircle size={19} />
      <div>
        {message}
        {retry && (
          <button type="button" className="text-link block mt-2" onClick={retry}>
            Try again <ArrowRight size={15} />
          </button>
        )}
      </div>
    </div>
  )
}
export function EmptyState({
  title,
  description,
  action,
  to,
}: {
  title: string
  description: string
  action?: string
  to?: string
}) {
  return (
    <div className="empty-state">
      <span className="empty-icon">
        <SearchX size={30} />
      </span>
      <h2>{title}</h2>
      <p>{description}</p>
      {action && to && (
        <Link className="button primary" to={to}>
          {action}
          <ArrowRight size={17} />
        </Link>
      )}
    </div>
  )
}
export function Skeletons({ count = 3 }: { count?: number }) {
  return (
    <div className="report-grid" aria-label="Loading reports" role="status">
      {Array.from({ length: count }, (_, i) => (
        <div className="skeleton-card" key={i}>
          <div className="skeleton h-44" />
          <div className="p-5 space-y-3">
            <div className="skeleton h-5 w-3/4" />
            <div className="skeleton h-3 w-1/2" />
            <div className="skeleton h-3 w-full" />
          </div>
        </div>
      ))}
      <span className="sr-only">Loading reports…</span>
    </div>
  )
}
export function Spinner() {
  return <LoaderCircle size={18} className="spin" aria-hidden="true" />
}
export function TrustNote() {
  return (
    <p className="trust-note">
      <ShieldCheck size={17} />
      <span>Match scores indicate similarity, not proof of ownership.</span>
    </p>
  )
}
export function formatDate(value: string | null) {
  return value
    ? new Date(`${value}T12:00:00`).toLocaleDateString('en', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : 'Date unknown'
}
