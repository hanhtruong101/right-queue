import uuid

from django.core.exceptions import ValidationError
from django.db import models

from organizations.models import Organization, OrganizationMembership
from service_catalogue.models import Service, ServiceTeam

class ServiceRequest(models.Model):
    reference = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="service_requests",
    )
    requester = models.ForeignKey(
        OrganizationMembership,
        on_delete=models.PROTECT,
        related_name="service_requests",
    )
    service=models.ForeignKey(
        Service, 
        on_delete=models.PROTECT,
        related_name="service_requests",
        null=True,
        blank=True,
    )
    assigned_team=models.ForeignKey(
        ServiceTeam,
        on_delete=models.PROTECT,
        related_name="service_requests",
        null=True,
        blank=True,
    )
    title=models.CharField(max_length=150)
    description=models.TextField()
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        PENDING_TRIAGE = "PENDING_TRIAGE", "Pending triage"
        QUEUED = "QUEUED", "Queued"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        WAITING_FOR_REQUESTER = (
            "WAITING_FOR_REQUESTER",
            "Waiting for requester",
        )
        RESOLVED = "RESOLVED", "Resolved"

    current_status=models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.SUBMITTED)
    
    submitted_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.organization_id
            and self.requester_id
            and self.organization_id
            != self.requester.organization_id
        ):
            errors["requester"] = (
                "The requester must belong to the same "
                "organization as the request."
            )

        if (
            self.organization_id
            and self.service_id
            and self.organization_id
            != self.service.organization_id
        ):
            errors["service"] = (
                "The service must belong to the same "
                "organization as the request."
            )

        if (
            self.organization_id
            and self.assigned_team_id
            and self.organization_id
            != self.assigned_team.organization_id
        ):
            errors["assigned_team"] = (
                "The assigned team must belong to the same "
                "organization as the request."
            )

        if errors:
            raise ValidationError(errors)
        
    def __str__(self):
        return f"{self.reference} - {self.title}"

class RequestStatusHistory(models.Model):
    request=models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="status_history",)
    from_status=models.CharField(
        max_length=30,
        choices=ServiceRequest.Status.choices,
        null=True,
        blank=True,
    )
    to_status = models.CharField(
        max_length=30,
        choices=ServiceRequest.Status.choices,
    )
    changed_by = models.ForeignKey(
        OrganizationMembership,
        on_delete=models.SET_NULL,
        related_name="request_status_changes",
        null=True,
        blank=True,
    )
    reason = models.TextField(
        blank=True,
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.request_id
            and self.changed_by_id
            and self.request.organization_id
            != self.changed_by.organization_id
        ):
            errors["changed_by"] = (
                "The person changing the status must belong "
                "to the request's organization."
            )

        if self.from_status and self.from_status == self.to_status:
            errors["to_status"] = (
                "The new status must be different from the previous status."
            )

        if (
            not self.from_status
            and self.to_status != ServiceRequest.Status.SUBMITTED
        ):
            errors["to_status"] = (
                "The first status history entry must be Submitted."
            )

        if errors:
            raise ValidationError(errors)

    class Meta:
        ordering = ("created_at", "id")

    def __str__(self):
        from_status = (
            self.get_from_status_display()
            if self.from_status
            else "Created"
        )

        return (
            f"{self.request.reference}: "
            f"{from_status} → {self.get_to_status_display()}"
        )