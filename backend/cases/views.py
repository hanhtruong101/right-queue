from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError as DRFValidationError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from organizations.models import Organization, OrganizationMembership
from .models import ServiceRequest

from .serializers import (
    ServiceRequestCreateSerializer,
    ServiceRequestDetailSerializer,
    ServiceRequestSummarySerializer
)
from .services import submit_service_request

class ServiceRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_organization_and_membership(self, request, organization_slug,):
        organization = get_object_or_404(Organization, slug=organization_slug, is_active=True,)
        membership = OrganizationMembership.objects.filter(organization=organization, user=request.user, is_active=True,).first()
        if membership is None:
            raise PermissionDenied("You are not an active member of this organization")
        return organization, membership
        
    def post(self, request, organization_slug):
        organization, membership = self._get_organization_and_membership(request, organization_slug)
        
        input_serializer = ServiceRequestCreateSerializer(
            data=request.data,
            context={"organization": organization},
        )

        input_serializer.is_valid(raise_exception=True)

        try: 
            service_request = submit_service_request(
                organization=organization,
                requester=membership,
                **input_serializer.validated_data,
            )

        except DjangoValidationError as error:
            if hasattr(error, "message_dict"):
                details = error.message_dict
            else:
                details = {"detail": error.messages}

            raise DRFValidationError(details) from error

        output_serializer = ServiceRequestDetailSerializer(service_request)

        return Response(output_serializer.data, status=status.HTTP_201_CREATED,)

    def get(self, request, organization_slug):
        organization, membership = self._get_organization_and_membership(request, organization_slug)
        service_requests = (
            ServiceRequest.objects.filter(
                organization=organization,
                requester=membership,
            )
            .select_related("service", "assigned_team")
            .order_by("-submitted_at", "-id")
        )

        output_serializer = ServiceRequestSummarySerializer(
            service_requests,
            many=True,
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK,)