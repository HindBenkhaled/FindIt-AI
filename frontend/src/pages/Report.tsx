import { ArrowRight, Search, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'
import { PageHeading } from '../components/UI'

export default function Report() {
  return (
    <div className="shell page-shell report-entry">
      <PageHeading
        eyebrow="START A REPORT"
        title="What happened?"
        description="Choose the option that best describes your situation. We’ll guide you from there."
      />
      <div className="report-choice-grid">
        <Link className="report-choice lost" to="/report/lost">
          <span className="report-choice-icon">
            <Search size={28} />
          </span>
          <div>
            <span className="choice-label">LOST ITEM</span>
            <h2>I lost something</h2>
            <p>Tell us what went missing and we’ll look for possible matches.</p>
          </div>
          <span className="choice-arrow">
            <ArrowRight size={22} />
          </span>
        </Link>
        <Link className="report-choice found" to="/report/found">
          <span className="report-choice-icon">
            <Sparkles size={28} />
          </span>
          <div>
            <span className="choice-label">FOUND ITEM</span>
            <h2>I found something</h2>
            <p>Share what you found so we can connect it with a lost report.</p>
          </div>
          <span className="choice-arrow">
            <ArrowRight size={22} />
          </span>
        </Link>
      </div>
      <p className="report-entry-note">You can add a photo, but it isn’t required.</p>
    </div>
  )
}
