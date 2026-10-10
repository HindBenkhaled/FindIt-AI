import { useEffect, useRef, useState } from 'react'
import { ArrowRight, Search, SlidersHorizontal, Sparkles } from 'lucide-react'
import { Link, useSearchParams } from 'react-router-dom'
import { useReports } from '../hooks/useReports'
import { api, errorMessage } from '../services/api'
import { methods, type MatchResponse, type Method, type Report } from '../types'
import { EmptyState, ErrorNotice, PageHeading, Spinner, TrustNote } from '../components/UI'
import ItemImage from '../components/ItemImage'
import MatchCard from '../components/MatchCard'
import ReportDetails from '../components/ReportDetails'
import ClaimForm from '../components/ClaimForm'
import type { Match } from '../types'

export default function Matches({ embedded = false }: { embedded?: boolean }) {
  const { items, loading, error: listError, reload } = useReports('lost')
  const [params] = useSearchParams()
  const [id, setId] = useState(params.get('report') || '')
  const [method, setMethod] = useState<Method>('full')
  const [count, setCount] = useState(5)
  const [result, setResult] = useState<MatchResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [details, setDetails] = useState<Report | null>(null)
  const [claimMatch, setClaimMatch] = useState<Match | null>(null)
  const activeRequest = useRef<AbortController | null>(null)
  const selected = items.find((item) => item.id === Number(id))
  useEffect(() => {
    if (items.length && !items.some((item) => item.id === Number(id))) setId(String(items[0].id))
  }, [items, id])
  useEffect(() => () => activeRequest.current?.abort(), [])
  function invalidate() {
    activeRequest.current?.abort()
    setResult(null)
    setError('')
    setBusy(false)
  }
  async function search() {
    if (!selected) return
    if (method === 'image' && !selected.image_available) {
      setError('Add a photo to this lost report, or choose a method that uses its description.')
      return
    }
    activeRequest.current?.abort()
    const controller = new AbortController()
    activeRequest.current = controller
    setBusy(true)
    setError('')
    setResult(null)
    try {
      const data = await api.matches(selected.id, method, count, controller.signal)
      if (!controller.signal.aborted) setResult(data)
    } catch (error) {
      if (!controller.signal.aborted) setError(errorMessage(error))
    } finally {
      if (!controller.signal.aborted) setBusy(false)
    }
  }
  return (
    <div className={embedded ? 'embedded-matches' : 'shell page-shell'}>
      {!embedded && (
        <PageHeading
          eyebrow="CONNECT THE DOTS"
          title="A familiar detail. A possible match."
          description="Choose a lost report. We’ll look for the things that make it unique."
          aside={
            <Link className="text-link" to="/report/lost">
              Report a lost item
              <ArrowRight size={17} />
            </Link>
          }
        />
      )}
      {listError ? (
        <ErrorNotice message={listError} retry={reload} />
      ) : !loading && !items.length ? (
        <EmptyState
          title="Your search starts with a report."
          description="Tell us what you lost, and we’ll help you look for a familiar match."
          action="Report a lost item"
          to="/report/lost"
        />
      ) : (
        <div className="matches-layout">
          <aside className="search-panel">
            <div className="panel-heading">
              <Search size={19} />
              <h2>What are we looking for?</h2>
            </div>
            <div className="field">
              <label htmlFor="lost-report">Lost report</label>
              <select
                id="lost-report"
                value={id}
                disabled={loading || busy}
                onChange={(e) => {
                  setId(e.target.value)
                  invalidate()
                }}
              >
                {loading && <option>Loading your reports…</option>}
                {items.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name} · #{item.id}
                  </option>
                ))}
              </select>
            </div>
            {selected && (
              <div className="selected-report">
                <ItemImage item={selected} />
                <div>
                  <strong>{selected.name}</strong>
                  <span>{selected.location || 'Location unknown'}</span>
                  <button className="text-link" onClick={() => setDetails(selected)}>
                    View report
                    <ArrowRight size={13} />
                  </button>
                </div>
              </div>
            )}
            <details className="advanced-options">
              <summary>
                <SlidersHorizontal size={15} /> Advanced options
              </summary>
              <div className="advanced-options-body">
                <div className="field">
                  <label htmlFor="method">Matching method</label>
                  <select
                    id="method"
                    value={method}
                    disabled={busy}
                    onChange={(e) => {
                      setMethod(e.target.value as Method)
                      invalidate()
                    }}
                  >
                    {methods.map((method) => (
                      <option key={method.value} value={method.value}>
                        {method.label}
                      </option>
                    ))}
                  </select>
                  <p className="field-hint">
                    {methods.find((option) => option.value === method)?.description}
                  </p>
                </div>
                <div className="field">
                  <label htmlFor="count">Number of results</label>
                  <select
                    id="count"
                    value={count}
                    disabled={busy}
                    onChange={(e) => {
                      setCount(Number(e.target.value))
                      invalidate()
                    }}
                  >
                    {[3, 5, 10, 20].map((number) => (
                      <option key={number} value={number}>
                        Top {number} matches
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </details>
            <button className="button primary w-full" disabled={!selected || busy} onClick={search}>
              {busy ? (
                <>
                  <Spinner />
                  Looking for matches…
                </>
              ) : (
                <>
                  <Search size={17} />
                  Find matches
                </>
              )}
            </button>
            <p className="panel-note">
              <Sparkles size={15} /> More details help. No photo is okay.
            </p>
          </aside>
          <section className="matches-results" aria-label="Match results" aria-busy={busy}>
            {error && <ErrorNotice message={error} />}
            {busy ? (
              <>
                <div className="search-loading" role="status">
                  <span className="empty-icon">
                    <ScanAnimation />
                  </span>
                  <h2>Looking for familiar details…</h2>
                  <p>
                    We’re comparing your item with found reports.
                    <br />
                    The first search can take a few minutes.
                  </p>
                  <button className="text-link" onClick={invalidate}>
                    Cancel search
                  </button>
                </div>
                <div className="skeleton-match skeleton" />
              </>
            ) : result ? (
              <>
                <div className="results-heading">
                  <div>
                    <h2>
                      {result.matches.length ? 'Your potential matches' : 'No matches just yet'}
                    </h2>
                    <p>
                      {result.candidate_count} found reports considered
                      {result.excluded_count
                        ? ` · ${result.excluded_count} without photos excluded`
                        : ''}
                    </p>
                  </div>
                  <span className="results-count">{result.matches.length} results</span>
                </div>
                {result.matches.length ? (
                  <div className="match-list">
                    {result.matches.map((match, index) => (
                      <MatchCard
                        key={match.item.id}
                        match={match}
                        rank={index + 1}
                        onVerify={setClaimMatch}
                      />
                    ))}
                  </div>
                ) : (
                  <EmptyState
                    title="Nothing to compare yet."
                    description="There aren’t any eligible found reports for this search. Try another method or check back later."
                  />
                )}
                <TrustNote />
              </>
            ) : (
              !error && (
                <div className="search-ready">
                  <span className="search-ready-icon">
                    <ScanAnimation />
                  </span>
                  <div className="eyebrow">YOUR NEXT LEAD STARTS HERE</div>
                  <h2>Let’s find what looks familiar.</h2>
                  <p>
                    Pick a lost report and we’ll compare the details.
                    <br />
                    Your closest matches will appear right here.
                  </p>
                  <div className="search-pills">
                    <span>Photos</span>
                    <span>Descriptions</span>
                    <span>Place & time</span>
                  </div>
                  <TrustNote />
                </div>
              )
            )}
          </section>
        </div>
      )}
      {details && (
        <ReportDetails
          report={details}
          onClose={() => setDetails(null)}
          onChanged={() => {
            reload()
            invalidate()
          }}
        />
      )}
      {claimMatch && selected && (
        <ClaimForm lostId={selected.id} match={claimMatch} onClose={() => setClaimMatch(null)} />
      )}
    </div>
  )
}
function ScanAnimation() {
  return <Search size={30} strokeWidth={1.4} />
}
