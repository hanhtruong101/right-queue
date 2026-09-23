export interface ServiceListItem {
  id: number
  name: string
  slug: string
  description: string
}

export interface CreateServiceRequestPayload {
  title: string
  description: string
  service: number | null
}

export type RequestStatus = 'QUEUED' | 'PENDING_TRIAGE'

export interface CreatedServiceRequest {
  reference: string
  title: string
  description: string
  service: number | null
  service_name: string | null
  assigned_team: number | null
  assigned_team_name: string | null
  current_status: RequestStatus
  submitted_at: string
}
