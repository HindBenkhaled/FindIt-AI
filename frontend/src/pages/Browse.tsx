import { useState } from 'react'
import { ArrowUpRight, Search, SlidersHorizontal, X } from 'lucide-react'
import { Link, useSearchParams } from 'react-router-dom'
import { useReports } from '../hooks/useReports'
import { categories, type Report } from '../types'
import { EmptyState, ErrorNotice, PageHeading, Skeletons } from '../components/UI'
import ReportCard from '../components/ReportCard'
import ReportDetails from '../components/ReportDetails'

export default function Browse({
  embedded = false,
  type: fixedType,
}: {
  embedded?: boolean
  type?: string
}) {
  const { items, loading, error, reload } = useReports()
  const [params, setParams] = useSearchParams()
  const type =
    fixedType ||
    (['lost', 'found'].includes(params.get('type') || '') ? params.get('type')! : 'all')
  const [category, setCategory] = useState('all')
  const [search, setSearch] = useState('')
  const [limit, setLimit] = useState(12)
  const [details, setDetails] = useState<Report | null>(null)
  const filtered = items.filter(
    (item) =>
      (type === 'all' || item.report_type === type) &&
      (category === 'all' || item.category === category) &&
      `${item.name} ${item.description} ${item.location || ''}`
        .toLowerCase()
        .includes(search.toLowerCase().trim()),
  )
  return (
    <div className={embedded ? 'embedded-browse' : 'shell page-shell'}>
      {!embedded && (
        <PageHeading
          eyebrow="SOMETHING HERE MIGHT LOOK FAMILIAR"
          title="A place for lost. And found."
          description="Explore the latest reports. Your next lead could be right here."
          aside={
            <Link className="button primary" to="/report/found">
              I found something
              <ArrowUpRight size={17} />
            </Link>
          }
        />
      )}
      <div className="browse-toolbar">
        {!embedded && (
          <div className="filter-tabs" aria-label="Filter by report type">
            {['all', 'lost', 'found'].map((value) => (
              <button
                key={value}
                className={type === value ? 'active' : ''}
                aria-pressed={type === value}
                onClick={() => {
                  setParams(value === 'all' ? {} : { type: value })
                  setLimit(12)
                }}
              >
                {value === 'all' ? 'All reports' : value === 'lost' ? 'Lost' : 'Found'}
              </button>
            ))}
          </div>
        )}
        <div className="browse-controls">
          <div className="input-with-icon search-field">
            <Search size={17} />
            <input
              aria-label="Search reports"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setLimit(12)
              }}
              placeholder="Search items or locations"
            />
            {search && (
              <button
                className="clear-search"
                aria-label="Clear search"
                onClick={() => setSearch('')}
              >
                <X size={15} />
              </button>
            )}
          </div>
          <div className="input-with-icon category-filter">
            <SlidersHorizontal size={16} />
            <select
              aria-label="Filter by category"
              value={category}
              onChange={(e) => {
                setCategory(e.target.value)
                setLimit(12)
              }}
            >
              <option value="all">All categories</option>
              {categories.map((value) => (
                <option key={value}>{value}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      <div className="browse-summary">
        <p aria-live="polite">
          {loading
            ? 'Finding reports…'
            : `${filtered.length} ${filtered.length === 1 ? 'report' : 'reports'}${type === 'all' ? '' : ` · ${type}`}`}
        </p>
        <span>Newest first</span>
      </div>
      {loading ? (
        <Skeletons count={8} />
      ) : error ? (
        <ErrorNotice message={error} retry={reload} />
      ) : filtered.length ? (
        <>
          <div className="report-grid browse-grid">
            {filtered.slice(0, limit).map((item) => (
              <ReportCard key={item.id} item={item} onDetails={setDetails} />
            ))}
          </div>
          {limit < filtered.length && (
            <div className="load-more">
              <button className="button secondary" onClick={() => setLimit(limit + 12)}>
                Show more reports
                <ArrowUpRight size={17} />
              </button>
              <span>
                Showing {Math.min(limit, filtered.length)} of {filtered.length}
              </span>
            </div>
          )}
        </>
      ) : (
        <EmptyState
          title={items.length ? 'No reports fit those details.' : 'A fresh start.'}
          description={
            items.length
              ? 'Try a different category or a broader search.'
              : 'Be the first to report a lost or found item.'
          }
          action={items.length ? undefined : 'Report an item'}
          to="/report/lost"
        />
      )}
      {details && (
        <ReportDetails report={details} onClose={() => setDetails(null)} onChanged={reload} />
      )}
    </div>
  )
}
