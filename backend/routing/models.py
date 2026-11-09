from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from organizations.models import Organization
from service_catalogue.models import Service

from .engine import normalize_text


class RoutingRule(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="routing_rules")
    name = models.CharField(max_length=150)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="routing_rules")
    minimum_score = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="unique_routing_rule_name_per_org"),
            models.CheckConstraint(condition=models.Q(minimum_score__gte=1), name="routing_rule_positive_minimum"),
        ]

    def clean(self):
        super().clean()
        if self.organization_id and self.service_id and self.service.organization_id != self.organization_id:
            raise ValidationError({"service": "The service must belong to the rule's organization."})

    def __str__(self):
        return f"{self.name} ({self.organization})"


class RoutingKeyword(models.Model):
    rule = models.ForeignKey(RoutingRule, on_delete=models.CASCADE, related_name="keywords")
    phrase = models.CharField(max_length=150)
    weight = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["rule", "phrase"], name="unique_routing_keyword_per_rule"),
            models.CheckConstraint(condition=models.Q(weight__gte=1), name="routing_keyword_positive_weight"),
            models.CheckConstraint(condition=~models.Q(phrase=""), name="routing_keyword_not_empty"),
        ]

    def clean_fields(self, exclude=None):
        if self.phrase is not None:
            self.phrase = normalize_text(self.phrase)
        super().clean_fields(exclude=exclude)

    def save(self, *args, **kwargs):
        # Normalize direct ORM creates as well as validated admin forms.
        self.phrase = normalize_text(self.phrase or "")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.phrase} (+{self.weight})"
