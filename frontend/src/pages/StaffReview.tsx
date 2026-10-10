import { useState, type FormEvent } from 'react'
import { Check, ShieldCheck, X } from 'lucide-react'
import { ErrorNotice, PageHeading, Spinner } from '../components/UI'
import { api, errorMessage } from '../services/api'
import { handoverLocations, type StaffClaim } from '../types'

export default function StaffReview() {
  const [key, setKey] = useState('')
  const [claims, setClaims] = useState<StaffClaim[]>([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function load(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      setClaims(await api.staffClaims(key))
    } catch (error) {
      setError(errorMessage(error))
    } finally {
      setBusy(false)
    }
  }
  async function review(
    claim: StaffClaim,
    status: 'approved' | 'rejected',
    collection: string | null,
  ) {
    setBusy(true)
    setError('')
    try {
      const updated = await api.reviewClaim(claim.id, status, collection, key)
      setClaims(claims.map((item) => (item.id === claim.id ? { ...item, ...updated } : item)))
    } catch (error) {
      setError(errorMessage(error))
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="shell page-shell">
      <PageHeading
        eyebrow="CAMPUS STAFF DEMO"
        title="Claim review"
        description="Compare a claimant’s answer with private found-item details, then approve or reject the claim."
      />
      {!claims.length && (
        <form className="staff-access form-card" onSubmit={load}>
          <ShieldCheck size={32} />
          <h2>Staff access</h2>
          <p className="small-muted">
            This portfolio MVP uses a local demo key. It is not production authentication.
          </p>
          <div className="field">
            <label htmlFor="staff-key">Staff demo key</label>
            <input
              id="staff-key"
              type="password"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              required
            />
          </div>
          <button className="button primary" disabled={busy}>
            {busy && <Spinner />}Open claim review
          </button>
        </form>
      )}
      {error && <ErrorNotice message={error} />}
      <div className="claim-review-list">
        {claims.map((claim) => (
          <article className="claim-review-card" key={claim.id}>
            <div className="claim-review-header">
              <div>
                <span className="eyebrow">CLAIM #{claim.id}</span>
                <h2>{claim.lost_item.name}</h2>
              </div>
              <span className={`claim-status ${claim.status}`}>{claim.status}</span>
            </div>
            <div className="claim-comparison">
              <section>
                <h3>Claimant says</h3>
                <p>{claim.verification_response}</p>
                <h3>Lost report</h3>
                <p>{claim.lost_item.description}</p>
              </section>
              <section className="private-panel">
                <h3>Private found detail</h3>
                <p>{claim.found_item.identifying_details || claim.found_item.description}</p>
                <p>
                  <strong>Exact location detail:</strong>{' '}
                  {claim.found_item.location_detail || 'Not provided'}
                </p>
                <p>
                  <strong>Handed to:</strong> {claim.found_item.handover_location || 'Not provided'}
                </p>
              </section>
            </div>
            {claim.status === 'pending' && (
              <div className="review-actions">
                <select
                  aria-label={`Collection point for claim ${claim.id}`}
                  defaultValue={claim.found_item.handover_location || ''}
                  id={`collection-${claim.id}`}
                >
                  <option value="">Select collection point</option>
                  {handoverLocations.map((place) => (
                    <option key={place}>{place}</option>
                  ))}
                </select>
                <button
                  className="button primary"
                  disabled={busy}
                  onClick={() =>
                    review(
                      claim,
                      'approved',
                      (document.getElementById(`collection-${claim.id}`) as HTMLSelectElement)
                        .value || null,
                    )
                  }
                >
                  <Check size={16} />
                  Approve
                </button>
                <button
                  className="button danger"
                  disabled={busy}
                  onClick={() => review(claim, 'rejected', null)}
                >
                  <X size={16} />
                  Reject
                </button>
              </div>
            )}
          </article>
        ))}
      </div>
    </div>
  )
}
