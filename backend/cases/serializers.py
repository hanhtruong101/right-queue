from rest_framework import serializers
from service_catalogue.models import Service
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
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.none(),
        required=False,
        allow_null=True,
    )
    # converts the service id into a Service object
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        organization = self.context.get("organization")

        if organization is not None:
            service_field = self.fields["service"]

            if isinstance(
                service_field,
                serializers.PrimaryKeyRelatedField,
            ):
                service_field.queryset = Service.objects.filter(
                    organization=organization,
                    is_active=True,
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

