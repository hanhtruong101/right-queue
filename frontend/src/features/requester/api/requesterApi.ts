import { apiRequest } from '../../../services/apiClient'
import type {
  CreatedServiceRequest,
  CreateServiceRequestPayload,
  ServiceListItem,
} from '../types'

const organizationPath = (organizationSlug: string) =>
  `/organizations/${encodeURIComponent(organizationSlug)}`

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
      body: JSON.stringify(payload),
    },
  )
}
