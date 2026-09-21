from rest_framework import serializers
from organizations.models import OrganizationMembership
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    username =serializers.CharField(
        max_length=150, trim_whitespace = True,)

    password = serializers.CharField(
        write_only = True, 
        trim_whitespace=False,
        style={"input_type": "password"},
    )

class OrganizationMembershipSummarySerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
    )

    organization_slug = serializers.CharField(
        source="organization.slug",
        read_only=True,
    )

    roles=serializers.SerializerMethodField()

    class Meta:
        model = OrganizationMembership
        fields = ("organization_name",
                  "organization_slug",
                  "roles")
        read_only_fields = fields

    def get_roles(self, membership):
        return list(
            membership.roles.order_by("role").values_list(
                "role",
                flat=True,
            )
        )

class CurrentUserSerializer(serializers.ModelSerializer):
    memberships = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "memberships",
        )
        read_only_fields = fields

    def get_memberships(self, user):
        memberships = user.organization_memberships.filter(
            is_active=True,
            organization__is_active=True,
        ).select_related("organization").prefetch_related("roles")

        return OrganizationMembershipSummarySerializer(
            memberships,
            many=True,
        ).data


