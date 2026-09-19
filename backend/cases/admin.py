from django.contrib import admin

from .models import RequestStatusHistory, ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "title",
        "organization",
        "requester",
        "service",
        "assigned_team",
        "current_status",
        "submitted_at",
    )
    list_filter = (
        "organization",
        "current_status",
        "assigned_team",
        "service",
    )
    search_fields = (
        "reference",
        "title",
        "description",
        "requester__user__username",
        "requester__user__email",
    )
    readonly_fields = (
        "reference",
        "submitted_at",
        "updated_at",
    )


@admin.register(RequestStatusHistory)
class RequestStatusHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "request",
        "from_status",
        "to_status",
        "changed_by",
        "created_at",
    )
    list_filter = (
        "from_status",
        "to_status",
        "request__organization",
    )
    search_fields = (
        "request__reference",
        "request__title",
        "changed_by__user__username",
        "reason",
    )
    readonly_fields = ("created_at",)