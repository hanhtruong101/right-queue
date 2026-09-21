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

from .serializers import (
    ServiceRequestCreateSerializer,
    ServiceRequestDetailSerializer,
)
from .services import submit_service_request

class ServiceRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, organization_slug):
        organization = get_object_or_404(
            Organization,
            slug= organization_slug,
            is_active=True,
        )
        membership = OrganizationMembership.objects.filter(
            organization=organization,
            user=request.user,
            is_active=True,
        ).first()

        if membership is None:
            raise PermissionDenied("You are not an active member of this organization.")

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