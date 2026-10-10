import { useEffect, useRef, useState } from 'react'
import { ArrowRight, CalendarDays, Check, MapPin, Trash2, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { Report } from '../types'
import { api, errorMessage } from '../services/api'
import ItemImage from './ItemImage'
import ImageUpload from './ImageUpload'
import { ErrorNotice, formatDate, Spinner } from './UI'

export default function ReportDetails({
  report,
  onClose,
  onChanged,
}: {
  report: Report
  onClose: () => void
  onChanged: () => void
}) {
  const dialog = useRef<HTMLDialogElement>(null)
  const [item, setItem] = useState(report)
  const [file, setFile] = useState<File | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [confirm, setConfirm] = useState(false)
  const [saved, setSaved] = useState(false)
  useEffect(() => {
    dialog.current?.showModal()
    const original = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = original
    }
  }, [])
  async function upload() {
    if (!file) return
    setBusy(true)
    setError('')
    setSaved(false)
    try {
      setItem(await api.upload(item.id, file))
      setFile(null)
      setSaved(true)
      onChanged()
    } catch (error) {
      setError(errorMessage(error))
    } finally {
      setBusy(false)
    }
  }
  async function remove() {
    setBusy(true)
    setError('')
    try {
      await api.remove(item.id)
      onChanged()
      onClose()
    } catch (error) {
      setError(errorMessage(error))
      setBusy(false)
    }
  }
  return (
    <dialog
      ref={dialog}
      className="details-dialog"
      aria-labelledby="details-title"
      onCancel={(e) => {
        if (busy) e.preventDefault()
        else onClose()
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget && !busy) onClose()
      }}
    >
      <div className="dialog-body">
        <div className="dialog-top">
          <span className={`inline-badge ${item.report_type}`}>
            {item.report_type === 'lost' ? 'Lost report' : 'Found report'} · #{item.id}
          </span>
          <button
            className="icon-button"
            aria-label="Close details"
            disabled={busy}
            onClick={onClose}
          >
            <X size={21} />
          </button>
        </div>
        <ItemImage item={item} className="detail-image" />
        <div className="category-label mt-6">{item.category}</div>
        <h2 id="details-title">{item.name}</h2>
        <div className="detail-meta">
          <span>
            <MapPin size={16} />
            {item.location || 'Location unknown'}
          </span>
          <span>
            <CalendarDays size={16} />
            {formatDate(item.event_date)}
          </span>
        </div>
        <p className="detail-description">
          {item.report_type === 'found'
            ? 'Identifying details and the original image are kept private for claim verification.'
            : item.description}
        </p>
        {item.report_type === 'lost' && (
          <Link
            className="button primary w-full"
            onClick={onClose}
            to={`/explore?view=matches&report=${item.id}`}
          >
            Find matches for this item <ArrowRight size={17} />
          </Link>
        )}
        {item.report_type === 'lost' && (
          <div className="manage-report">
            <h3>Manage this report</h3>
            <p className="small-muted">
              You can add a clearer photo or remove a report that’s no longer needed.
            </p>
            <ImageUpload file={file} onChange={setFile} disabled={busy} />
            {file && (
              <button className="button secondary mt-3" disabled={busy} onClick={upload}>
                {busy ? <Spinner /> : <Check size={16} />}Save photo
              </button>
            )}
            {saved && (
              <p role="status" className="success-inline">
                <Check size={16} /> Photo updated.
              </p>
            )}
            {error && (
              <div className="mt-4">
                <ErrorNotice message={error} />
              </div>
            )}
            <div className="delete-area">
              {confirm ? (
                <>
                  <p>Delete this report and its photo? This cannot be undone.</p>
                  <div className="flex gap-3">
                    <button className="button danger" disabled={busy} onClick={remove}>
                      {busy && <Spinner />}Delete report
                    </button>
                    <button
                      className="button secondary"
                      disabled={busy}
                      onClick={() => setConfirm(false)}
                    >
                      Keep report
                    </button>
                  </div>
                </>
              ) : (
                <button className="delete-link" disabled={busy} onClick={() => setConfirm(true)}>
                  <Trash2 size={15} />
                  Delete report
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </dialog>
  )
}
