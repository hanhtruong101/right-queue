from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch

from cases.models import RequestStatusHistory, ServiceRequest

from .engine import Candidate, select_decision
from .models import RoutingKeyword, RoutingRule


def _candidates(organization_id):
    rules = RoutingRule.objects.filter(
        organization_id=organization_id, is_active=True,
        service__organization_id=organization_id, service__is_active=True,
        service__default_team__organization_id=organization_id, service__default_team__is_active=True,
    ).select_related("service__default_team").prefetch_related(
        Prefetch("keywords", queryset=RoutingKeyword.objects.filter(is_active=True), to_attr="active_keywords")
    )
    for rule in rules:
        yield Candidate(
            rule.pk, rule.name, rule.service_id, rule.service.default_team_id, rule.minimum_score,
            tuple((keyword.phrase, keyword.weight) for keyword in rule.active_keywords),
        )


@transaction.atomic
def route_service_request(service_request):
    """Apply initial routing to a newly submitted request, including its history."""
    if service_request.current_status != ServiceRequest.Status.SUBMITTED:
        raise ValidationError("Initial routing requires a submitted request.")
    decision = select_decision(
        service_request.title, service_request.description, _candidates(service_request.organization_id)
    )
    service_request.service_id = decision.service_id
    service_request.assigned_team_id = decision.team_id
    service_request.current_status = decision.status
    service_request.full_clean()
    service_request.save(update_fields=["service", "assigned_team", "current_status", "updated_at"])

    event = RequestStatusHistory(
        request=service_request, from_status=ServiceRequest.Status.SUBMITTED, to_status=decision.status,
        changed_by=None, reason=decision.reason,
    )
    event.full_clean()
    event.save()
    return service_request
