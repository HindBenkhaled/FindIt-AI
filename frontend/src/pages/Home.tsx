import { useState } from 'react'
import {
  ArrowRight,
  ArrowUpRight,
  Check,
  FileText,
  HeartHandshake,
  ScanLine,
  Sparkles,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import HeroVisual from '../components/HeroVisual'
import ReportCard from '../components/ReportCard'
import ReportDetails from '../components/ReportDetails'
import { ErrorNotice, Skeletons, TrustNote } from '../components/UI'
import { useReports } from '../hooks/useReports'
import type { Report } from '../types'

export default function Home() {
  const { items, loading, error, reload } = useReports('found')
  const [selected, setSelected] = useState<Report | null>(null)
  return (
    <>
      <section className="shell hero">
        <div className="hero-copy">
          <span className="hero-eyebrow">
            <Sparkles size={14} /> CAMPUS LOST &amp; FOUND
          </span>
          <h1>
            Lost something on campus?
            <br />
            <span>FindIt can help.</span>
          </h1>
          <p className="hero-description">
            FindIt AI helps students reconnect with lost items using images, descriptions, campus
            location, and time.
          </p>
          <div className="hero-actions">
            <Link className="button primary" to="/report/lost">
              I lost something
              <ArrowUpRight size={18} />
            </Link>
            <Link className="button secondary" to="/report/found">
              I found something
              <ArrowRight size={18} />
            </Link>
          </div>
          <div className="hero-reassurance">
            <span>
              <Check size={15} /> Simple to report
            </span>
            <span>
              <Check size={15} /> Easy to understand
            </span>
          </div>
        </div>
        <HeroVisual />
      </section>
      <section className="shell section-spacing">
        <div className="section-heading">
          <div>
            <div className="eyebrow">FROM LOST TO A NEW LEAD</div>
            <h2>Four simple steps.</h2>
          </div>
          <p>
            Less searching in circles.
            <br />
            More useful connections.
          </p>
        </div>
        <div className="steps-grid">
          {[
            {
              n: '01',
              Icon: FileText,
              title: 'Report',
              text: 'Describe your item and add a photo if you have one. The little details make a difference.',
            },
            {
              n: '02',
              Icon: ScanLine,
              title: 'Match',
              text: 'FindIt compares descriptions, photos, locations and dates to find possible connections.',
            },
            {
              n: '03',
              Icon: HeartHandshake,
              title: 'Verify',
              text: 'Share a private identifying detail so campus staff can review your claim.',
            },
            {
              n: '04',
              Icon: HeartHandshake,
              title: 'Collect',
              text: 'If approved, collect the item from its campus handover point.',
            },
          ].map(({ n, Icon, title, text }) => (
            <div className="step" key={n}>
              <div className="step-top">
                <span className="step-icon">
                  <Icon size={23} strokeWidth={1.6} />
                </span>
                <span className="step-number">{n}</span>
              </div>
              <h3>{title}</h3>
              <p>{text}</p>
            </div>
          ))}
        </div>
        <TrustNote />
      </section>
      <section className="recent-section">
        <div className="shell section-spacing">
          <div className="section-heading">
            <div>
              <div className="eyebrow">A GOOD PLACE TO START</div>
              <h2>Recent found notices.</h2>
            </div>
            <Link className="text-link" to="/explore?view=found">
              View found notices
              <ArrowRight size={17} />
            </Link>
          </div>
          {loading ? (
            <Skeletons count={4} />
          ) : error ? (
            <ErrorNotice message={error} retry={reload} />
          ) : items.length ? (
            <div className="report-grid home-reports">
              {items.slice(0, 4).map((item) => (
                <ReportCard key={item.id} item={item} onDetails={setSelected} />
              ))}
            </div>
          ) : (
            <div className="soft-empty">
              <HeartHandshake size={25} />
              <p>No found notices yet. Yours could be someone’s first lead.</p>
              <Link className="text-link" to="/report/found">
                Report a found item <ArrowRight size={16} />
              </Link>
            </div>
          )}
        </div>
      </section>
      {selected && (
        <ReportDetails report={selected} onClose={() => setSelected(null)} onChanged={reload} />
      )}
    </>
  )
}
