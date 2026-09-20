from django.core.exceptions import ValidationError
from django.db import transaction

from organizations.models import Organization, OrganizationMembership, OrganizationMembershipRole
from service_catalogue.models import Service

from .models import RequestStatusHistory, ServiceRequest

# Submission Function
@transaction.atomic
def submit_service_request(
    *,
    organization: Organization,
    requester: OrganizationMembership,
    title: str,
    description: str,
    service: Service | None = None,
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
    if service is not None:
        if service.organization_id != organization.id:
            raise ValidationError(
                {
                    "service": (
                        "The service must belong to the selected organization."
                    )
                }
            )

        if not service.is_active:
            raise ValidationError(
                {"service": "The selected service is inactive."}
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
        service=service,
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

    # In case no team was assigned directly to that service yet
    destination_team = None
    next_status = ServiceRequest.Status.PENDING_TRIAGE
    routing_reason = "The request requires manual triage"

    # If there is a team associate with the service
    if service is not None and service.default_team.is_active:
        destination_team = service.default_team
        next_status = ServiceRequest.Status.QUEUED
        routing_reason = "Automatically routed to the service's default team."

    request.assigned_team = destination_team
    request.current_status = next_status

    # Validate again
    request.full_clean()
    request.save(
        update_fields=[
            "assigned_team",
            "current_status",
            "updated_at",
        ]
    )

    # Record the routing result
    routing_event = RequestStatusHistory(
    request=request,
    from_status=ServiceRequest.Status.SUBMITTED,
    to_status=next_status,
    changed_by=None, # System do the routing
    reason=routing_reason,
    )
    routing_event.full_clean()
    routing_event.save()

    return request