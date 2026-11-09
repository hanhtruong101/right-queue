from rest_framework import serializers
from .models import ServiceRequest

# validates the input 
class ServiceRequestCreateSerializer(serializers.Serializer):
    title = serializers.CharField(
        max_length=150,
        trim_whitespace=True,
    )
    description = serializers.CharField(
        trim_whitespace=True,
    )

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError(
            "The title must contain at least 5 characters."
            )
        return value

# Serialize service requests for API responses
class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(
        source="service.name",
        read_only=True,
        allow_null=True,
    )
    assigned_team_name = serializers.CharField(
        source="assigned_team.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ServiceRequest
        fields=(
            "reference",
            "title",
            "description",
            "service",
            "service_name",
            "assigned_team",
            "assigned_team_name",
            "current_status",
            "submitted_at",
        )
        read_only_fields =(
            "reference",
            "title",
            "description",
            "service",
            "service_name",
            "assigned_team",
            "assigned_team_name",
            "current_status",
            "submitted_at",
        )

class ServiceRequestSummarySerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(
        source="service.name",
        read_only=True,
        allow_null=True,
    )
    assigned_team_name = serializers.CharField(
        source="assigned_team.name",
        read_only=True,
        allow_null=True,
    )
    class Meta: 
        model = ServiceRequest
        fields= (
            "reference",
            "title",
            "service_name",
            "assigned_team_name",
            "current_status",
            "submitted_at",
            "updated_at",)
        read_only_fields = fields