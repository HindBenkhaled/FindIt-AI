import { useCallback, useEffect, useState } from 'react'
import { api, errorMessage } from '../services/api'
import type { Report, ReportType } from '../types'

export function useReports(type?: ReportType) {
  const [items, setItems] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  const reload = useCallback(() => setRevision((value) => value + 1), [])
  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    setError('')
    api
      .list(type, controller.signal)
      .then(setItems)
      .catch((error) => {
        if (!controller.signal.aborted) setError(errorMessage(error))
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [type, revision])
  return { items, loading, error, reload }
}
