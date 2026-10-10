import { ArrowUpRight, CalendarDays, MapPin } from 'lucide-react'
import type { Report } from '../types'
import ItemImage from './ItemImage'
import { formatDate } from './UI'

export default function ReportCard({
  item,
  onDetails,
}: {
  item: Report
  onDetails: (item: Report) => void
}) {
  return (
    <article className="report-card">
      <div className="relative">
        <ItemImage item={item} />
        <span className={`type-badge ${item.report_type}`}>
          {item.report_type === 'lost' ? 'Lost item' : 'Found notice'}
        </span>
      </div>
      <div className="report-card-body">
        <div className="category-label">{item.category}</div>
        <h3>{item.name}</h3>
        <p className="meta">
          <MapPin size={14} />
          <span>{item.location || 'Location unknown'}</span>
        </p>
        <p className="meta">
          <CalendarDays size={14} />
          {formatDate(item.event_date)}
        </p>
        <button className="card-details" onClick={() => onDetails(item)}>
          View details
          <ArrowUpRight size={18} />
        </button>
      </div>
    </article>
  )
}
