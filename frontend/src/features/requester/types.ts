export interface ServiceListItem {
  id: number
  name: string
  slug: string
  description: string
}

export interface CreateServiceRequestPayload {
  title: string
  description: string
}

export type RequestStatus = 'QUEUED' | 'PENDING_TRIAGE'

export type ServiceRequestStatus =
  | RequestStatus
  | 'SUBMITTED'
  | 'IN_PROGRESS'
  | 'WAITING_FOR_REQUESTER'
  | 'RESOLVED'

export interface ServiceRequestSummary {
  reference: string
  title: string
  service_name: string | null
  assigned_team_name: string | null
  current_status: ServiceRequestStatus
  submitted_at: string
  updated_at: string
}

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
