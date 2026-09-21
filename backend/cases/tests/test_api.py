from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from cases.models import RequestStatusHistory, ServiceRequest
from organizations.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
)
from service_catalogue.models import Service, ServiceTeam


class ServiceRequestCreateAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        cls.first_organization = Organization.objects.create(
            name="Northwind Services",
            slug="northwind-services",
        )
        cls.second_organization = Organization.objects.create(
            name="Contoso Support",
            slug="contoso-support",
        )
        cls.inactive_organization = Organization.objects.create(
            name="Fabrikam Services",
            slug="fabrikam-services",
            is_active=False,
        )

        cls.requester_user = user_model.objects.create_user(
            username="active.requester",
            password="test-password",
        )
        cls.inactive_member_user = user_model.objects.create_user(
            username="inactive.member",
            password="test-password",
        )
        cls.no_role_user = user_model.objects.create_user(
            username="no.requester.role",
            password="test-password",
        )
        cls.no_membership_user = user_model.objects.create_user(
            username="no.membership",
            password="test-password",
        )
        cls.other_organization_user = user_model.objects.create_user(
            username="other.organization",
            password="test-password",
        )
        cls.inactive_organization_user = user_model.objects.create_user(
            username="inactive.organization",
            password="test-password",
        )

        cls.requester_membership = OrganizationMembership.objects.create(
            organization=cls.first_organization,
            user=cls.requester_user,
        )
        cls.inactive_membership = OrganizationMembership.objects.create(
            organization=cls.first_organization,
            user=cls.inactive_member_user,
            is_active=False,
        )
        cls.membership_without_role = OrganizationMembership.objects.create(
            organization=cls.first_organization,
            user=cls.no_role_user,
        )
        cls.other_organization_membership = OrganizationMembership.objects.create(
            organization=cls.second_organization,
            user=cls.other_organization_user,
        )
        cls.inactive_organization_membership = (
            OrganizationMembership.objects.create(
                organization=cls.inactive_organization,
                user=cls.inactive_organization_user,
            )
        )

        requester_role = OrganizationMembershipRole.Role.REQUESTER
        OrganizationMembershipRole.objects.create(
            membership=cls.requester_membership,
            role=requester_role,
        )
        OrganizationMembershipRole.objects.create(
            membership=cls.inactive_membership,
            role=requester_role,
        )
        OrganizationMembershipRole.objects.create(
            membership=cls.other_organization_membership,
            role=requester_role,
        )
        OrganizationMembershipRole.objects.create(
            membership=cls.inactive_organization_membership,
            role=requester_role,
        )

        cls.active_team = ServiceTeam.objects.create(
            organization=cls.first_organization,
            name="IT Support",
            slug="it-support",
        )
        cls.inactive_team = ServiceTeam.objects.create(
            organization=cls.first_organization,
            name="Legacy Support",
            slug="legacy-support",
            is_active=False,
        )
        cls.other_organization_team = ServiceTeam.objects.create(
            organization=cls.second_organization,
            name="IT Support",
            slug="it-support",
        )

        cls.active_service = Service.objects.create(
            organization=cls.first_organization,
            default_team=cls.active_team,
            name="Account Access",
            slug="account-access",
        )
        cls.inactive_service = Service.objects.create(
            organization=cls.first_organization,
            default_team=cls.inactive_team,
            name="Legacy Account Access",
            slug="legacy-account-access",
            is_active=False,
        )
        cls.other_organization_service = Service.objects.create(
            organization=cls.second_organization,
            default_team=cls.other_organization_team,
            name="Account Access",
            slug="account-access",
        )

    def setUp(self):
        self.client = APIClient()
        self.url = reverse(
            "cases:service-request-create",
            kwargs={"organization_slug": self.first_organization.slug},
        )
        self.valid_payload = {
            "title": "Cannot access account",
            "description": "My account sign-in is not working.",
            "service": self.active_service.pk,
        }

    def test_active_requester_can_create_automatically_routed_request(self):
        self.client.force_authenticate(user=self.requester_user)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ServiceRequest.objects.count(), 1)

        service_request = ServiceRequest.objects.get()
        service_request.refresh_from_db()
        self.assertEqual(service_request.organization, self.first_organization)
        self.assertEqual(service_request.requester, self.requester_membership)
        self.assertEqual(service_request.service, self.active_service)
        self.assertEqual(service_request.title, self.valid_payload["title"])
        self.assertEqual(
            service_request.description,
            self.valid_payload["description"],
        )
        self.assertEqual(service_request.current_status, ServiceRequest.Status.QUEUED)
        self.assertEqual(service_request.assigned_team, self.active_team)

        history = list(service_request.status_history.all())
        self.assertEqual(len(history), 2)
        self.assertIsNone(history[0].from_status)
        self.assertEqual(history[0].to_status, ServiceRequest.Status.SUBMITTED)
        self.assertEqual(history[1].from_status, ServiceRequest.Status.SUBMITTED)
        self.assertEqual(history[1].to_status, ServiceRequest.Status.QUEUED)

        expected_response_fields = {
            "reference",
            "title",
            "description",
            "service",
            "service_name",
            "assigned_team",
            "assigned_team_name",
            "current_status",
            "submitted_at",
        }
        self.assertTrue(expected_response_fields.issubset(response.data.keys()))
        self.assertEqual(response.data["reference"], str(service_request.reference))
        self.assertEqual(response.data["title"], service_request.title)
        self.assertEqual(response.data["description"], service_request.description)
        self.assertEqual(response.data["service"], self.active_service.pk)
        self.assertEqual(response.data["service_name"], self.active_service.name)
        self.assertEqual(response.data["assigned_team"], self.active_team.pk)
        self.assertEqual(response.data["assigned_team_name"], self.active_team.name)
        self.assertEqual(response.data["current_status"], ServiceRequest.Status.QUEUED)
        self.assertIsNotNone(response.data["submitted_at"])

    def test_omitting_service_creates_pending_triage_request(self):
        self.client.force_authenticate(user=self.requester_user)
        payload = {
            "title": "General support request",
            "description": "I am not sure which service applies.",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        service_request = ServiceRequest.objects.get()
        service_request.refresh_from_db()
        self.assertIsNone(service_request.service)
        self.assertIsNone(service_request.assigned_team)
        self.assertEqual(
            service_request.current_status,
            ServiceRequest.Status.PENDING_TRIAGE,
        )
        history = list(service_request.status_history.all())
        self.assertEqual(len(history), 2)
        self.assertIsNone(history[0].from_status)
        self.assertEqual(history[0].to_status, ServiceRequest.Status.SUBMITTED)
        self.assertEqual(history[1].from_status, ServiceRequest.Status.SUBMITTED)
        self.assertEqual(
            history[1].to_status,
            ServiceRequest.Status.PENDING_TRIAGE,
        )

    def test_null_service_creates_pending_triage_request(self):
        self.client.force_authenticate(user=self.requester_user)
        payload = {
            "title": "General support request",
            "description": "I am not sure which service applies.",
            "service": None,
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        service_request = ServiceRequest.objects.get()
        service_request.refresh_from_db()
        self.assertIsNone(service_request.service)
        self.assertIsNone(service_request.assigned_team)
        self.assertEqual(
            service_request.current_status,
            ServiceRequest.Status.PENDING_TRIAGE,
        )
        self.assertEqual(
            list(
                service_request.status_history.values_list(
                    "from_status",
                    "to_status",
                )
            ),
            [
                (None, ServiceRequest.Status.SUBMITTED),
                (
                    ServiceRequest.Status.SUBMITTED,
                    ServiceRequest.Status.PENDING_TRIAGE,
                ),
            ],
        )

    def test_anonymous_client_is_forbidden(self):
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_user_without_any_membership_is_forbidden(self):
        self.client.force_authenticate(user=self.no_membership_user)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_inactive_membership_is_forbidden(self):
        self.client.force_authenticate(user=self.inactive_member_user)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_user_belonging_only_to_other_organization_is_forbidden(self):
        self.client.force_authenticate(user=self.other_organization_user)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_inactive_organization_url_returns_not_found(self):
        self.client.force_authenticate(user=self.inactive_organization_user)
        url = reverse(
            "cases:service-request-create",
            kwargs={"organization_slug": self.inactive_organization.slug},
        )

        response = self.client.post(url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_membership_without_requester_role_is_rejected(self):
        self.client.force_authenticate(user=self.no_role_user)

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("requester", response.data)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_service_from_another_organization_is_rejected(self):
        self.client.force_authenticate(user=self.requester_user)
        payload = {**self.valid_payload, "service": self.other_organization_service.pk}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("service", response.data)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_inactive_service_is_rejected(self):
        self.client.force_authenticate(user=self.requester_user)
        payload = {**self.valid_payload, "service": self.inactive_service.pk}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("service", response.data)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_title_shorter_than_five_characters_is_rejected(self):
        self.client.force_authenticate(user=self.requester_user)
        payload = {**self.valid_payload, "title": "Help"}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_blank_title_is_rejected(self):
        self.client.force_authenticate(user=self.requester_user)
        payload = {**self.valid_payload, "title": "   "}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_blank_description_is_rejected(self):
        self.client.force_authenticate(user=self.requester_user)
        payload = {**self.valid_payload, "description": "   "}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_missing_required_fields_are_rejected(self):
        self.client.force_authenticate(user=self.requester_user)

        response = self.client.post(
            self.url,
            {"service": self.active_service.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertIn("description", response.data)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_server_controlled_fields_cannot_be_overridden(self):
        self.client.force_authenticate(user=self.requester_user)
        payload = {
            **self.valid_payload,
            "organization": 999,
            "requester": 999,
            "assigned_team": 999,
            "current_status": ServiceRequest.Status.RESOLVED,
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        service_request = ServiceRequest.objects.get()
        service_request.refresh_from_db()
        self.assertEqual(service_request.organization, self.first_organization)
        self.assertEqual(service_request.requester, self.requester_membership)
        self.assertEqual(service_request.assigned_team, self.active_team)
        self.assertEqual(service_request.current_status, ServiceRequest.Status.QUEUED)
        self.assertNotEqual(service_request.organization_id, 999)
        self.assertNotEqual(service_request.requester_id, 999)
        self.assertNotEqual(service_request.assigned_team_id, 999)

    @patch("cases.views.submit_service_request")
    def test_dictionary_validation_error_becomes_field_error_response(
        self,
        mocked_submit,
    ):
        self.client.force_authenticate(user=self.requester_user)
        mocked_submit.side_effect = ValidationError(
            {"service": "The selected service cannot be used."}
        )

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("service", response.data)
        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    @patch("cases.views.submit_service_request")
    def test_message_validation_error_becomes_detail_response(self, mocked_submit):
        self.client.force_authenticate(user=self.requester_user)
        mocked_submit.side_effect = ValidationError("Submission failed.")

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertEqual(str(response.data["detail"][0]), "Submission failed.")
        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())
