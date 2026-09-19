from django.conf import settings
from django.db import models

class Organization(models.Model): 
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=80, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class OrganizationMembership(models.Model):
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        related_name="memberships",)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta: 
        constraints=[
            models.UniqueConstraint(
                fields=["organization","user"],
                name="unique_organization_membership",
            )
        ]
    def __str__(self):
        return f"{self.user} has a membership of {self.organization}"

class OrganizationMembershipRole(models.Model):
    class Role(models.TextChoices):
            REQUESTER = "REQUESTER", "Requester"
            STAFF = "STAFF", "Staff"
            TRIAGE_COORDINATOR = "TRIAGE_COORDINATOR", "Triage Coordinator"
            ORGANIZATION_ADMIN = "ORGANIZATION_ADMIN", "Organization Admin"
    role = models.CharField(
        max_length=50,
        choices=Role,
    )
    membership = models.ForeignKey(
         OrganizationMembership,
         on_delete=models.CASCADE,
         related_name="roles")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: 
        constraints = [
             models.UniqueConstraint(
                  fields=["membership","role"],
                  name="unique_role_per_organization_membership"
             )
        ]
    def __str__(self):
         return f"{self.membership} has been given the role {self.get_role_display()}"
    
