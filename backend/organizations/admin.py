from django.contrib import admin
from .models import Organization, OrganizationMembership, OrganizationMembershipRole

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")

@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "is_active")
    list_filter = ("organization", "is_active")
    search_fields = (
    "user__username",
    "user__email",
    "organization__name",
    "organization__slug",
)


@admin.register(OrganizationMembershipRole)
class OrganizationMembershipRoleAdmin(admin.ModelAdmin):
    list_display=("role", "membership")
    list_filter = ("role",)
    search_fields = (
    "membership__user__username",
    "membership__organization__name",
)
