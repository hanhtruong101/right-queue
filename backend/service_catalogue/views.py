from django.shortcuts import get_object_or_404

from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Service
from organizations.models import Organization, OrganizationMembership
from .serializers import ServiceListSerializer

class ServiceListView(APIView):
    authentication_classes = [SessionAuthentication] 
    permission_classes = [IsAuthenticated]

    def get(self, request, organization_slug):
        organization = get_object_or_404(
            Organization, 
            slug=organization_slug,
            is_active=True,)
        
        has_active_membership = (OrganizationMembership.objects.filter(
            organization=organization,
            user=request.user,
            is_active=True,
            ).exists()
        )

        if not has_active_membership:
            raise PermissionDenied("You are not an active member of this organization")

        services = Service.objects.filter(
            organization=organization,
            is_active=True,
            default_team__is_active=True,
        ).order_by("name")

        serializer = ServiceListSerializer(
            services, many = True,
        )
        return Response(serializer.data)