import { useState } from 'react'
import { Backpack, Glasses, Headphones, KeyRound, Package, Shirt, Wallet } from 'lucide-react'
import { api } from '../services/api'
import type { Report } from '../types'

const icons = {
  Electronics: Headphones,
  Wallets: Wallet,
  Keys: KeyRound,
  Bags: Backpack,
  Glasses,
  Clothing: Shirt,
  Other: Package,
}
export default function ItemImage({ item, className = '' }: { item: Report; className?: string }) {
  const [failedSource, setFailedSource] = useState('')
  const source = api.image(item)
  const Icon = icons[item.category as keyof typeof icons] || Package
  return (
    <div className={`item-image ${className}`}>
      {item.image_available && failedSource !== source ? (
        <img src={source} alt={item.name} loading="lazy" onError={() => setFailedSource(source)} />
      ) : (
        <div className="image-placeholder">
          <Icon size={42} strokeWidth={1.2} />
          <span>
            {item.report_type === 'found'
              ? 'Private found-item photo'
              : item.image_available
                ? 'Photo unavailable'
                : 'No photo added'}
          </span>
        </div>
      )}
    </div>
  )
}
