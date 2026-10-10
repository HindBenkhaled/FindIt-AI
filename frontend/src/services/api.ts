import type {
  Claim,
  MatchResponse,
  Method,
  Report,
  ReportInput,
  ReportType,
  StaffClaim,
} from '../types'

/** Keep raw backend exceptions out of the consumer interface. */
export class ApiError extends Error {
  constructor(
    message: string,
    public status = 0,
  ) {
    super(message)
  }
}
async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 600_000)
  const abort = () => controller.abort()
  init.signal?.addEventListener('abort', abort)
  if (init.signal?.aborted) controller.abort()
  try {
    const response = await fetch(`/api${path}`, { ...init, signal: controller.signal })
    if (!response.ok) {
      const messages: Record<number, string> = {
        404: 'This report is no longer available. Refresh the page to see the latest reports.',
        413: 'That photo is too large. Please choose one smaller than 8 MB.',
        422: path.endsWith('/image')
          ? 'We couldn’t use that photo. Choose a valid JPG, PNG or WebP under 8 MB and 20 megapixels.'
          : 'Please check your report details and try again.',
        503: 'AI matching is temporarily unavailable. Try Simple matching, or come back in a moment.',
      }
      throw new ApiError(
        messages[response.status] ||
          'We couldn’t complete that request. Please try again in a moment.',
        response.status,
      )
    }
    return response.status === 204 ? (undefined as T) : ((await response.json()) as T)
  } catch (error) {
    if (error instanceof ApiError) throw error
    if (init.signal?.aborted) throw error
    throw new ApiError(
      controller.signal.aborted
        ? 'This is taking longer than expected. Please try again.'
        : 'We can’t connect right now. Please check your connection and try again.',
    )
  } finally {
    clearTimeout(timeout)
    init.signal?.removeEventListener('abort', abort)
  }
}

export const api = {
  async list(type?: ReportType, signal?: AbortSignal): Promise<Report[]> {
    const all: Report[] = []
    for (let offset = 0; ; offset += 500) {
      const params = new URLSearchParams({ limit: '500', offset: String(offset) })
      if (type) params.set('report_type', type)
      const page = await request<Report[]>(`/items?${params}`, { signal })
      all.push(...page)
      if (page.length < 500) return all
    }
  },
  create: (data: ReportInput) =>
    request<Report>('/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),
  upload: (id: number, file: File) => {
    const body = new FormData()
    body.append('file', file)
    return request<Report>(`/items/${id}/image`, { method: 'POST', body })
  },
  remove: (id: number) => request<void>(`/items/${id}`, { method: 'DELETE' }),
  matches: (id: number, method: Method, count: number, signal?: AbortSignal) =>
    request<MatchResponse>(`/matches/${id}?method=${method}&top_k=${count}`, { signal }),
  image: (item: Report) => `/api/items/${item.id}/image`,
  createClaim: (lostId: number, foundId: number, verification: string) =>
    request<Claim>('/claims', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lost_report_id: lostId,
        found_report_id: foundId,
        verification_response: verification,
      }),
    }),
  claim: (id: number) => request<Claim>(`/claims/${id}`),
  staffClaims: (key: string) =>
    request<StaffClaim[]>('/staff/claims', { headers: { 'X-Staff-Key': key } }),
  reviewClaim: (
    id: number,
    status: 'approved' | 'rejected',
    collectionPoint: string | null,
    key: string,
  ) =>
    request<Claim>(`/staff/claims/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'X-Staff-Key': key },
      body: JSON.stringify({ status, collection_point: collectionPoint }),
    }),
}
export const errorMessage = (error: unknown) =>
  error instanceof ApiError ? error.message : 'Something went wrong. Please try again.'
