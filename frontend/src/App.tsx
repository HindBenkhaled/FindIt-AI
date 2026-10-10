import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import Layout from './components/Layout'
import { EmptyState } from './components/UI'
import Home from './pages/Home'
import ReportForm from './pages/ReportForm'
import Report from './pages/Report'
import Explore from './pages/Explore'
import StaffReview from './pages/StaffReview'
import ClaimStatus from './pages/ClaimStatus'

function LegacyExploreRedirect({ view }: { view: string }) {
  const { search } = useLocation()
  const legacy = new URLSearchParams(search)
  const legacyType = legacy.get('type')
  const destination =
    view === 'all' && ['lost', 'found'].includes(legacyType || '') ? legacyType! : view
  const next = new URLSearchParams({ view: destination })
  if (legacy.get('report')) next.set('report', legacy.get('report')!)
  return <Navigate replace to={`/explore?${next}`} />
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="report" element={<Report />} />
        <Route path="report/lost" element={<ReportForm key="lost" kind="lost" />} />
        <Route path="report/found" element={<ReportForm key="found" kind="found" />} />
        <Route path="explore" element={<Explore />} />
        <Route path="staff" element={<StaffReview />} />
        <Route path="claims/:id" element={<ClaimStatus />} />
        <Route path="matches" element={<LegacyExploreRedirect view="matches" />} />
        <Route path="browse" element={<LegacyExploreRedirect view="all" />} />
        <Route
          path="*"
          element={
            <div className="shell page-shell">
              <EmptyState
                title="This page seems to be missing."
                description="Let’s get you back to familiar ground."
                action="Back to home"
                to="/"
              />
            </div>
          }
        />
      </Route>
    </Routes>
  )
}
