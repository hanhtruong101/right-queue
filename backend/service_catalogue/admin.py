from django.contrib import admin

from .models import Service, ServiceTeam, TeamMembership


@admin.register(ServiceTeam)
class ServiceTeamAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "is_active")
    list_filter = ("organization", "is_active")
    search_fields = (
        "name",
        "slug",
        "organization__name",
        "organization__slug",
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "organization",
        "default_team",
        "is_active",
    )
    list_filter = (
        "organization",
        "default_team",
        "is_active",
    )
    search_fields = (
        "name",
        "slug",
        "organization__name",
        "organization__slug",
        "default_team__name",
    )


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "team",
        "membership",
        "is_active",
    )
    list_filter = (
        "team",
        "is_active",
    )
    search_fields = (
        "team__name",
        "team__organization__name",
        "membership__user__username",
        "membership__user__email",
        "membership__user__first_name",
        "membership__user__last_name",
    )