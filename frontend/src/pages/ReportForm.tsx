import { useState, type FormEvent } from 'react'
import {
  ArrowLeft,
  ArrowRight,
  Camera,
  Check,
  CheckCheck,
  Lightbulb,
  MapPin,
  ShieldCheck,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import ImageUpload from '../components/ImageUpload'
import { ErrorNotice, PageHeading, Spinner } from '../components/UI'
import { api, errorMessage } from '../services/api'
import {
  campusLocations,
  categories,
  handoverLocations,
  type Report,
  type ReportType,
} from '../types'

export default function ReportForm({ kind }: { kind: ReportType }) {
  const lost = kind === 'lost'
  const [file, setFile] = useState<File | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState<Report | null>(null)
  const [photoError, setPhotoError] = useState('')
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    const name = String(data.get('name') || '').trim()
    const description = String(data.get('description') || '').trim()
    if (name.length < 2 || description.length < 3) {
      setError(
        'Add an item name of at least 2 characters and a description of at least 3 characters.',
      )
      return
    }
    setBusy(true)
    setError('')
    setPhotoError('')
    try {
      const item = await api.create({
        report_type: kind,
        name,
        description,
        category: String(data.get('category')),
        location: String(data.get('location')),
        location_detail: String(data.get('location_detail') || '').trim() || null,
        event_date: String(data.get('event_date') || '') || null,
        identifying_details: String(data.get('identifying_details') || '').trim() || null,
        handover_location: lost ? null : String(data.get('handover_location') || '') || null,
      })
      // Creation succeeded. Keep its ID even if the separate photo upload fails.
      setSaved(item)
      if (file) {
        try {
          setSaved(await api.upload(item.id, file))
          setFile(null)
        } catch (error) {
          setPhotoError(errorMessage(error))
        }
      }
    } catch (error) {
      setError(errorMessage(error))
    } finally {
      setBusy(false)
    }
  }
  async function retryPhoto() {
    if (!file || !saved) return
    setBusy(true)
    setPhotoError('')
    try {
      setSaved(await api.upload(saved.id, file))
      setFile(null)
    } catch (error) {
      setPhotoError(errorMessage(error))
    } finally {
      setBusy(false)
    }
  }
  if (saved)
    return (
      <div className="shell success-page">
        <div className="success-card" role="status">
          <span className="success-mark">
            <CheckCheck size={35} />
          </span>
          <div className="eyebrow">ONE STEP CLOSER</div>
          <h1>{lost ? 'Report submitted' : 'Thanks for helping'}</h1>
          <p>
            <strong>{saved.name}</strong> has been added to {lost ? 'lost' : 'found'} reports.
          </p>
          <span className="report-reference">Report #{saved.id}</span>
          {busy ? (
            <div className="notice mt-6">
              <Spinner /> Finishing your photo upload…
            </div>
          ) : photoError ? (
            <div className="photo-retry">
              <p>Your report is saved, but its photo needs another try.</p>
              <ErrorNotice message={photoError} />
              <ImageUpload file={file} onChange={setFile} />
              <button className="button secondary mt-3" disabled={!file} onClick={retryPhoto}>
                Retry photo upload
              </button>
            </div>
          ) : (
            <p className="success-context">
              {lost
                ? 'Let’s see if someone has already found it.'
                : 'Thank you for helping someone find their way back to something that matters.'}
            </p>
          )}
          <div className="success-actions">
            <Link
              className={`button primary ${busy ? 'disabled-link' : ''}`}
              aria-disabled={busy}
              to={lost ? `/explore?view=matches&report=${saved.id}` : '/explore?view=lost'}
            >
              {lost ? 'Find possible matches' : 'Explore lost reports'}
              <ArrowRight size={17} />
            </Link>
            {lost ? (
              <button
                className="text-link"
                disabled={busy}
                onClick={() => {
                  setSaved(null)
                  setPhotoError('')
                  setFile(null)
                }}
              >
                Report another item
              </button>
            ) : (
              <Link className="text-link" to="/">
                Back to home
              </Link>
            )}
          </div>
        </div>
      </div>
    )
  return (
    <div className="shell page-shell">
      <Link className="back-link" to="/report">
        <ArrowLeft size={16} /> Change report type
      </Link>
      <PageHeading
        eyebrow={lost ? 'LET’S RETRACE YOUR STEPS' : 'A LITTLE KINDNESS GOES A LONG WAY'}
        title={lost ? 'Tell us what’s missing.' : 'Help it find its way home.'}
        description={
          lost
            ? 'The right details can turn a lost item into a promising lead.'
            : 'Share a few details about the item you found. We’ll help connect the dots.'
        }
      />
      <div className="form-layout">
        <form className="form-card" onSubmit={submit}>
          <div className="form-card-heading">
            <span className="section-number">01</span>
            <div>
              <h2>Item details</h2>
              <p>
                {lost
                  ? 'Start with what makes this item yours.'
                  : 'Share the details that make this item stand out.'}
              </p>
            </div>
          </div>
          <fieldset disabled={busy} className="form-fields">
            <div className="field-row">
              <div className="field">
                <label htmlFor="name">
                  Item name <span className="required">*</span>
                </label>
                <input
                  id="name"
                  name="name"
                  required
                  minLength={2}
                  maxLength={120}
                  placeholder="e.g. AirPods Pro"
                  autoComplete="off"
                />
              </div>
              <div className="field">
                <label htmlFor="category">
                  Category <span className="required">*</span>
                </label>
                <select id="category" name="category" required defaultValue="">
                  <option value="" disabled>
                    Select a category
                  </option>
                  {categories.map((category) => (
                    <option key={category}>{category}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="field">
              <label htmlFor="description">
                Description <span className="required">*</span>
              </label>
              <textarea
                id="description"
                name="description"
                required
                minLength={3}
                maxLength={3000}
                rows={4}
                placeholder="Black AirPods Pro case with a white scratch on the front"
                aria-describedby="description-hint"
              />
              <p id="description-hint" className="field-hint">
                Think color, brand, markings, or anything that makes it stand out.
              </p>
            </div>
            <div className="field-row">
              <div className="field">
                <label htmlFor="location">
                  Campus location <span className="required">*</span>
                </label>
                <div className="input-with-icon">
                  <MapPin size={17} />
                  <select id="location" name="location" required defaultValue="">
                    <option value="" disabled>
                      Select a campus location
                    </option>
                    {campusLocations.map((location) => (
                      <option key={location}>{location}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="field">
                <label htmlFor="event-date">
                  Date {kind} <span className="optional">Optional</span>
                </label>
                <input type="date" id="event-date" name="event_date" />
              </div>
            </div>
            <div className="field">
              <label htmlFor="location-detail">
                Location detail{' '}
                <span className="optional">Optional · kept private for found items</span>
              </label>
              <input
                id="location-detail"
                name="location_detail"
                maxLength={300}
                placeholder="e.g. Second floor, near lab 204"
              />
            </div>
            <div className="field">
              <label htmlFor="identifying-details">
                Private identifying details <span className="optional">Optional</span>
              </label>
              <textarea
                id="identifying-details"
                name="identifying_details"
                maxLength={2000}
                rows={3}
                placeholder="Scratch, sticker, engraving, case color, model, contents, or attached accessory"
              />
              <p className="field-hint">
                Used for matching and claim review. These details are never shown in public
                found-item previews.
              </p>
            </div>
            {!lost && (
              <div className="field">
                <label htmlFor="handover-location">
                  Item handed to <span className="optional">Optional</span>
                </label>
                <select id="handover-location" name="handover_location" defaultValue="">
                  <option value="">Not handed in yet</option>
                  {handoverLocations.map((location) => (
                    <option key={location}>{location}</option>
                  ))}
                </select>
              </div>
            )}
            <div className="form-divider" />
            <div className="form-card-heading small">
              <span className="section-number">02</span>
              <div>
                <h2>A picture helps</h2>
                <p>No photo? You can still get matches from your description.</p>
              </div>
            </div>
            <ImageUpload file={file} onChange={setFile} disabled={busy} />
            {error && <ErrorNotice message={error} />}
            <div className="form-submit-row">
              <p>
                <ShieldCheck size={16} /> Leave out personal or sensitive details.
              </p>
              <button className="button primary" type="submit" disabled={busy}>
                {busy ? (
                  <>
                    <Spinner />
                    Saving your report…
                  </>
                ) : (
                  <>
                    Submit {kind} report
                    <ArrowRight size={17} />
                  </>
                )}
              </button>
            </div>
          </fieldset>
        </form>
        <aside className="form-aside">
          <span className="advice-icon">
            <Lightbulb size={24} strokeWidth={1.6} />
          </span>
          <h3>
            Little details.
            <br />
            Better matches.
          </h3>
          <p>A few specific clues help us tell similar items apart.</p>
          <div className="tip">
            <Check size={17} />
            <div>
              <strong>Be a little specific</strong>
              <p>“Blue backpack with a yellow pocket” is better than “a bag.”</p>
            </div>
          </div>
          <div className="tip">
            <Camera size={17} />
            <div>
              <strong>Give it a clear photo</strong>
              <p>A simple background and good lighting go a long way.</p>
            </div>
          </div>
          <div className="tip">
            <MapPin size={17} />
            <div>
              <strong>Add the place and date</strong>
              <p>Even an approximate location can help narrow the search.</p>
            </div>
          </div>
          <div className="aside-note">
            {lost
              ? 'A familiar detail might be all it takes.'
              : 'Your report could make someone’s day.'}
          </div>
        </aside>
      </div>
    </div>
  )
}
