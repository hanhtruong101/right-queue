from django.db import models
from organizations.models import Organization, OrganizationMembership
from django.core.exceptions import ValidationError

class ServiceTeam(models.Model):
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        related_name="service_teams",
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=80)
    description = models.TextField(
        blank=True,
        default="",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=["organization","name"],
                name="unique_service_team_name_per_organization",
            ),
        models.UniqueConstraint(
                fields=["organization", "slug"],
                name="unique_service_team_slug_per_organization",
            ),
        ]
    def __str__(self):
        return f"{self.name} is a service team of {self.organization}"

class Service(models.Model):
    organization=models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="services"
    )
    default_team =models.ForeignKey(
        ServiceTeam,
        on_delete=models.PROTECT,
        related_name="default_services"
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=80)
    description = models.TextField(
        blank=True,
        default="",
    ) 
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        if (self.organization_id
            and self.default_team_id
            and self.organization_id != self.default_team.organization_id):
            raise ValidationError(
                {
                    "default_team":(
                        "The selected team must belong to the same organization as the service."
                    )
                }
            )
    
    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_service_name_per_organization"
            ),
            models.UniqueConstraint(
                fields=["organization", "slug"],
                name="unique_service_slug_per_organization"
            ),
        ]
    def __str__(self):
        return f"{self.name} ({self.organization})"

class TeamMembership(models.Model):
    team = models.ForeignKey(
        ServiceTeam,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    membership = models.ForeignKey(
        OrganizationMembership,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    is_active = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if (self.team_id 
            and self.membership_id
            and self.team.organization_id != self.membership.organization_id):
            raise ValidationError(
                {
                    "membership":(
                        "The team and the membership must belong to the same organization."
                    )
                }
            )

    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=["team", "membership"],
                name="unique_member_per_team"
            )
        ]

    def __str__(self):
        return f"{self.membership.user} is in {self.team}"