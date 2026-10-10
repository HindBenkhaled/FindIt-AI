import { useEffect, useState } from 'react'
import { ArrowUpRight, Menu, Search, X } from 'lucide-react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'

const links = [
  ['/', 'Home'],
  ['/report', 'Report'],
  ['/explore', 'Explore'],
]
export function Brand() {
  return (
    <Link to="/" className="brand" aria-label="FindIt AI home">
      <span className="brand-mark">
        <Search size={22} strokeWidth={2.4} />
      </span>
      FindIt<span className="brand-ai">AI</span>
    </Link>
  )
}
export default function Layout() {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()
  useEffect(() => {
    setOpen(false)
    window.scrollTo(0, 0)
    const names: Record<string, string> = {
      '/': 'A little context. A better match.',
      '/report': 'Report an item',
      '/report/lost': 'Report a lost item',
      '/report/found': 'Report a found item',
      '/explore': 'Explore reports and matches',
      '/staff': 'Campus staff claim review',
    }
    document.title = `${names[pathname] || 'Page not found'} · FindIt AI`
  }, [pathname])
  return (
    <>
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <header className="site-header">
        <div className="shell nav-inner">
          <Brand />
          <nav aria-label="Main navigation" className="desktop-nav">
            {links.map(([to, label]) => (
              <NavLink key={to} to={to} end={to === '/'}>
                {label}
              </NavLink>
            ))}
          </nav>
          <span className="nav-note">
            <span className="status-dot" /> Campus lost &amp; found
          </span>
          <button
            className="icon-button mobile-toggle"
            aria-label={open ? 'Close menu' : 'Open menu'}
            aria-expanded={open}
            aria-controls="mobile-nav"
            onClick={() => setOpen(!open)}
          >
            {open ? <X /> : <Menu />}
          </button>
        </div>
        {open && (
          <nav id="mobile-nav" className="mobile-nav" aria-label="Mobile navigation">
            {links.map(([to, label]) => (
              <NavLink key={to} to={to} end={to === '/'}>
                {label}
                <ArrowUpRight size={17} />
              </NavLink>
            ))}
          </nav>
        )}
      </header>
      <main id="main" tabIndex={-1}>
        <Outlet />
      </main>
      <footer className="site-footer">
        <div className="shell">
          <div className="footer-top">
            <div>
              <Brand />
              <p>Privacy-aware campus lost &amp; found.</p>
            </div>
            <div className="footer-links">
              <Link to="/explore?view=lost">Lost on campus</Link>
              <Link to="/report/found">Help someone find it</Link>
              {/* /staff remains available for the demo; production access needs university SSO and staff roles. */}
            </div>
          </div>
          <div className="footer-bottom">
            <span>Designed for a university campus.</span>
            <span>Local demo · Sample reports and illustrations are synthetic.</span>
          </div>
        </div>
      </footer>
    </>
  )
}
