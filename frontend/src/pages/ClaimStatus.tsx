import { useEffect, useState } from 'react'
import { CheckCircle2, Clock3, XCircle } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { ErrorNotice, PageHeading, Spinner } from '../components/UI'
import { api, errorMessage } from '../services/api'
import type { Claim } from '../types'

export default function ClaimStatus() {
  const id = Number(useParams().id)
  const [claim, setClaim] = useState<Claim | null>(null)
  const [error, setError] = useState('')
  async function load() {
    try {
      setClaim(await api.claim(id))
      setError('')
    } catch (error) {
      setError(errorMessage(error))
    }
  }
  useEffect(() => {
    void load()
  }, [id])
  return (
    <div className="shell page-shell">
      <PageHeading
        eyebrow="CLAIM STATUS"
        title={`Claim #${id}`}
        description="Campus staff compare your verification response with the private found-item report."
      />
      {error ? (
        <ErrorNotice message={error} retry={load} />
      ) : !claim ? (
        <Spinner />
      ) : (
        <div className="success-card claim-status-card">
          {claim.status === 'approved' ? (
            <>
              <CheckCircle2 size={42} />
              <h2>Claim approved</h2>
              <p>Please collect the item from:</p>
              <strong className="collection-point">{claim.collection_point}</strong>
            </>
          ) : claim.status === 'rejected' ? (
            <>
              <XCircle size={42} />
              <h2>Claim not approved</h2>
              <p>Campus staff could not verify this claim from the information provided.</p>
            </>
          ) : (
            <>
              <Clock3 size={42} />
              <h2>Staff review pending</h2>
              <p>Keep this page or your claim number and check again later.</p>
              <button className="button secondary" onClick={load}>
                Check again
              </button>
            </>
          )}
          <Link className="text-link" to="/explore?view=matches">
            Back to matches
          </Link>
        </div>
      )}
    </div>
  )
}
