from django.contrib import admin

from .models import RoutingKeyword, RoutingRule


class RoutingKeywordInline(admin.TabularInline):
    model = RoutingKeyword
    extra = 1


@admin.register(RoutingRule)
class RoutingRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "service", "minimum_score", "is_active")
    list_filter = ("organization", "is_active")
    search_fields = ("name", "organization__name", "service__name")
    list_select_related = ("organization", "service")
    inlines = (RoutingKeywordInline,)


@admin.register(RoutingKeyword)
class RoutingKeywordAdmin(admin.ModelAdmin):
    list_display = ("phrase", "rule", "weight", "is_active")
    list_filter = ("rule__organization", "is_active")
    search_fields = ("phrase", "rule__name")
    list_select_related = ("rule__organization",)
