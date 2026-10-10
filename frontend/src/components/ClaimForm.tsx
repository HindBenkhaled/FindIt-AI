import { useRef, useState, type FormEvent } from 'react'
import { CheckCircle2, ShieldCheck, X } from 'lucide-react'
import { api, errorMessage } from '../services/api'
import { Link } from 'react-router-dom'
import type { Match } from '../types'
import { ErrorNotice, Spinner } from './UI'

export default function ClaimForm({
  lostId,
  match,
  onClose,
}: {
  lostId: number
  match: Match
  onClose: () => void
}) {
  const dialog = useRef<HTMLDialogElement>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [claimId, setClaimId] = useState<number | null>(null)
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const answer = String(new FormData(event.currentTarget).get('verification') || '').trim()
    setBusy(true)
    setError('')
    try {
      setClaimId((await api.createClaim(lostId, match.item.id, answer)).id)
    } catch (error) {
      setError(errorMessage(error))
    } finally {
      setBusy(false)
    }
  }
  return (
    <dialog
      ref={(node) => {
        dialog.current = node
        node?.showModal()
      }}
      className="details-dialog"
      onCancel={onClose}
    >
      <div className="dialog-body claim-form">
        <div className="dialog-top">
          <span className="inline-badge found">Private verification</span>
          <button className="icon-button" aria-label="Close claim form" onClick={onClose}>
            <X />
          </button>
        </div>
        {claimId ? (
          <div className="claim-success" role="status">
            <CheckCircle2 size={38} />
            <h2>Verification submitted</h2>
            <p>
              Claim #{claimId} is pending campus staff review. Keep this number to check the claim
              status.
            </p>
            <Link className="button primary" to={`/claims/${claimId}`}>
              View claim status
            </Link>
          </div>
        ) : (
          <form onSubmit={submit}>
            <ShieldCheck size={35} />
            <h2>Verify this match</h2>
            <p className="detail-description">
              Describe details only the owner would know. Campus staff will compare your answer with
              the private found report.
            </p>
            <div className="field">
              <label htmlFor="verification">How can staff verify this item is yours?</label>
              <textarea
                id="verification"
                name="verification"
                required
                minLength={10}
                rows={6}
                placeholder="Brand or model, distinctive mark, case color, exact place, contents, sticker, engraving, or attached accessory"
              />
            </div>
            {error && <ErrorNotice message={error} />}
            <button className="button primary w-full" disabled={busy}>
              {busy ? <Spinner /> : <ShieldCheck size={17} />} Submit for staff review
            </button>
            <p className="field-hint mt-3">
              This MVP does not verify your identity. Do not include phone numbers, student IDs, or
              passwords.
            </p>
          </form>
        )}
      </div>
    </dialog>
  )
}
