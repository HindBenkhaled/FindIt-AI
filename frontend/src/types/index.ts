export const categories = [
  'Electronics',
  'Student ID / Cards',
  'Keys',
  'Bags',
  'Wallets',
  'Clothing',
  'Books / Notes',
  'Chargers / Accessories',
  'Glasses',
  'Water Bottles',
  'Other',
] as const
export const campusLocations = [
  'Main Library',
  'Student Center',
  'Engineering Building',
  'Science Building',
  'Cafeteria',
  'Computer Lab',
  'Lecture Hall',
  'Gym',
  'Parking',
  'Reception',
  'Security Office',
  'Student Services',
] as const
export const handoverLocations = [
  'Campus Security',
  'Main Reception',
  'Library Desk',
  'Student Services',
  'Finder still has item',
  'Other approved campus location',
] as const
export type ReportType = 'lost' | 'found'
export type Method = 'full' | 'text' | 'image' | 'text_image' | 'baseline' | 'keyword'
export interface ReportInput {
  report_type: ReportType
  name: string
  category: string
  description: string
  location: string
  location_detail: string | null
  event_date: string | null
  identifying_details: string | null
  handover_location: string | null
}
export interface Report {
  id: number
  report_type: ReportType
  name: string
  category: string
  description: string | null
  location: string | null
  event_date: string | null
  image_available: boolean
  created_at: string
}
export type Signal = 'text' | 'image' | 'location' | 'time' | 'category'
export interface Match {
  item: Report
  score: number
  label: string
  components: Record<Signal, number | null>
  effective_weights: Partial<Record<Signal, number>>
}
export interface MatchResponse {
  query_id: number
  method: Method
  candidate_count: number
  excluded_count: number
  matches: Match[]
  note: string
}
export interface Claim {
  id: number
  lost_report_id: number
  found_report_id: number
  status: 'pending' | 'approved' | 'rejected'
  collection_point: string | null
  created_at: string
}
export interface StaffClaim extends Claim {
  verification_response: string
  lost_item: ReportInput & { id: number; image_path: string | null; created_at: string }
  found_item: ReportInput & { id: number; image_path: string | null; created_at: string }
}
export const methods: { value: Method; label: string; description: string }[] = [
  {
    value: 'full',
    label: 'Full multimodal',
    description: 'Uses photos, descriptions, campus location, date and category.',
  },
  {
    value: 'text',
    label: 'Description matching',
    description: 'Compares the meaning of item descriptions.',
  },
  {
    value: 'image',
    label: 'Images only',
    description: 'Compares photos when both reports include one.',
  },
  {
    value: 'text_image',
    label: 'Description + image',
    description: 'Compares descriptions and available photos.',
  },
  {
    value: 'baseline',
    label: 'Simple matching',
    description: 'Compares keywords and campus context.',
  },
  {
    value: 'keyword',
    label: 'Keywords only',
    description: 'Compares shared words in item descriptions.',
  },
]
