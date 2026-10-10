import { Check, MapPin, ScanLine, Sparkles } from 'lucide-react'
import { useId } from 'react'

/** Code-native illustration, intentionally distinct from actual report photography. */
function Earbuds({ dark = false }: { dark?: boolean }) {
  const id = useId().replace(/:/g, '')
  return (
    <svg viewBox="0 0 280 210" aria-hidden="true" className="earbuds-illustration">
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2=".7" y2="1">
          <stop offset="0" stopColor={dark ? '#555953' : '#fff'} />
          <stop offset="1" stopColor={dark ? '#242b26' : '#d8ddd5'} />
        </linearGradient>
        <filter id={`${id}s`} x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="8" />
        </filter>
      </defs>
      <ellipse
        cx="142"
        cy="183"
        rx="76"
        ry="10"
        fill="#596353"
        opacity=".15"
        filter={`url(#${id}s)`}
      />
      <g transform="rotate(-10 140 110)">
        <rect
          x="59"
          y="91"
          width="165"
          height="89"
          rx="36"
          fill={`url(#${id})`}
          stroke={dark ? '#535d54' : '#e4e8df'}
        />
        <path d="M63 120h157" fill="none" stroke={dark ? '#1e251f' : '#c4ccbf'} strokeWidth="1.5" />
        <rect x="129" y="139" width="14" height="3" rx="1.5" fill={dark ? '#a6c9a9' : '#9fac94'} />
        <g fill={`url(#${id})`} stroke={dark ? '#586058' : '#d1d9cc'}>
          <rect x="92" y="32" width="19" height="64" rx="9" transform="rotate(-15 102 62)" />
          <ellipse cx="97" cy="35" rx="21" ry="17" />
          <rect x="170" y="22" width="19" height="64" rx="9" transform="rotate(13 179 52)" />
          <ellipse cx="181" cy="27" rx="21" ry="17" />
        </g>
        <ellipse cx="84" cy="34" rx="5" ry="9" fill={dark ? '#151b16' : '#768171'} />
        <ellipse cx="195" cy="27" rx="5" ry="9" fill={dark ? '#151b16' : '#768171'} />
      </g>
    </svg>
  )
}
export default function HeroVisual() {
  return (
    <div
      className="hero-visual"
      aria-label="Illustrative example of a lost report connected to a found report"
    >
      <div className="visual-orbit orbit-one" />
      <div className="visual-orbit orbit-two" />
      <span className="visual-label">
        <span className="status-dot" /> SMALL DETAILS. BETTER CONNECTIONS.
      </span>
      <div className="example-card example-lost">
        <div className="example-photo">
          <span className="mini-badge">LOST</span>
          <Earbuds />
        </div>
        <div className="example-body">
          <h3>My wireless earbuds</h3>
          <p>
            <MapPin size={12} /> Main Library
          </p>
          <span className="example-tag">White case · Small scratch</span>
        </div>
      </div>
      <div className="connection-line" />
      <span className="connection-icon">
        <ScanLine size={27} />
      </span>
      <div className="example-card example-found">
        <div className="example-photo">
          <span className="mini-badge found">FOUND</span>
          <Earbuds />
        </div>
        <div className="example-body">
          <h3>Wireless earbuds</h3>
          <p>
            <MapPin size={12} /> Main Library
          </p>
          <span className="example-tag">
            <Check size={12} /> Familiar details
          </span>
        </div>
      </div>
      <div className="visual-result">
        <span>
          <Sparkles size={20} />
        </span>
        <div>
          <strong>A possible match. A new lead.</strong>
          <p>Connecting the details you might miss.</p>
        </div>
      </div>
      <span className="illustration-note">Illustrative example</span>
    </div>
  )
}
