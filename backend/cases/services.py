from django.core.exceptions import ValidationError
from django.db import transaction

from organizations.models import Organization, OrganizationMembership, OrganizationMembershipRole
from routing.services import route_service_request

from .models import RequestStatusHistory, ServiceRequest

# Submission Function
@transaction.atomic
def submit_service_request(
    *,
    organization: Organization,
    requester: OrganizationMembership,
    title: str,
    description: str,
) -> ServiceRequest:
    if not organization.is_active:
        raise ValidationError({
            "organization": "The organization is inactive."
        })
    if not requester.is_active:
        raise ValidationError(
            {"requester": "The organization membership is inactive."}
        )

    if requester.organization_id != organization.id:
        raise ValidationError(
            {
                "requester": (
                    "The requester must belong to the selected organization."
                )
            }
        )
    has_requester_role = requester.roles.filter(
        role=OrganizationMembershipRole.Role.REQUESTER
    ).exists()

    if not has_requester_role:
        raise ValidationError(
            {
                "requester": (
                    "The organization membership does not have "
                    "the Requester role."
                )
            }
        )
    
    # Create submitted request
    request = ServiceRequest(
        organization=organization,
        requester=requester,
        assigned_team=None,
        title=title.strip(),
        description=description.strip(),
        current_status=ServiceRequest.Status.SUBMITTED,
    )
    # Validate the model object before saving
    request.full_clean()
    request.save()

    # Record submission
    submitted_event = RequestStatusHistory(
    request=request,
    from_status=None,
    to_status=ServiceRequest.Status.SUBMITTED,
    changed_by=requester,
    reason="Request submitted.",
    )
    # Ensure this is valid
    submitted_event.full_clean()
    submitted_event.save()

    return route_service_request(request)
