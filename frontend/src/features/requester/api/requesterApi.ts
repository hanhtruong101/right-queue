import { apiRequest } from '../../../services/apiClient'
import type {
  CreatedServiceRequest,
  CreateServiceRequestPayload,
  ServiceListItem,
  ServiceRequestSummary,
} from '../types'

const organizationPath = (organizationSlug: string) =>
  `/organizations/${encodeURIComponent(organizationSlug)}`

export function getMyRequests(
  organizationSlug: string,
  signal?: AbortSignal,
): Promise<ServiceRequestSummary[]> {
  return apiRequest<ServiceRequestSummary[]>(
    `${organizationPath(organizationSlug)}/requests/`,
    { signal },
  )
}

export function getOrganizationServices(
  organizationSlug: string,
  signal?: AbortSignal,
): Promise<ServiceListItem[]> {
  return apiRequest<ServiceListItem[]>(
    `${organizationPath(organizationSlug)}/services/`,
    { signal },
  )
}

export function createServiceRequest(
  organizationSlug: string,
  payload: CreateServiceRequestPayload,
): Promise<CreatedServiceRequest> {
  return apiRequest<CreatedServiceRequest>(
    `${organizationPath(organizationSlug)}/requests/`,
    {
      method: 'POST',
      body: JSON.stringify({
        title: payload.title,
        description: payload.description,
      }),
    },
  )
}
