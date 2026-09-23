export type OrganizationRole =
  | "REQUESTER"
  | "STAFF"
  | "TRIAGE_COORDINATOR"
  | "ORGANIZATION_ADMIN";

export interface OrganizationMembershipSummary {
    organization_name: string;
    organization_slug: string;
    roles: OrganizationRole[];
}

export interface CurrentUser{
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    memberships: OrganizationMembershipSummary[];
}

export interface LoginCredentials{
    username: string;
    password: string;
}

export interface CsrfResponse{
    csrf_token: string;
}
