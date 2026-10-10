import { NavLink, useSearchParams } from 'react-router-dom'
import { PageHeading } from '../components/UI'
import Browse from './Browse'
import Matches from './Matches'

const tabs = [
  { value: 'matches', label: 'Matches' },
  { value: 'lost', label: 'Lost on campus' },
  { value: 'found', label: 'Found notices' },
] as const

export default function Explore() {
  const [params] = useSearchParams()
  const requested = params.get('view')
  const view = tabs.some((tab) => tab.value === requested) ? requested! : 'matches'
  return (
    <div className="shell page-shell explore-page">
      <PageHeading
        eyebrow="EXPLORE"
        title="Campus lost and found."
        description="Search for possible matches, recognize a lost item, or view privacy-safe found-item notices."
      />
      <nav className="explore-tabs" aria-label="Explore sections">
        {tabs.map((tab) => (
          <NavLink
            key={tab.value}
            to={`/explore?view=${tab.value}`}
            className={view === tab.value ? 'active' : ''}
            aria-current={view === tab.value ? 'page' : undefined}
          >
            {tab.label}
          </NavLink>
        ))}
      </nav>
      <div className="explore-content">
        {view === 'matches' ? <Matches embedded /> : <Browse embedded type={view} />}
      </div>
    </div>
  )
}
