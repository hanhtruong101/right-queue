from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from organizations.models import Organization, OrganizationMembership
from service_catalogue.models import Service, ServiceTeam


class ServiceListAPITests(TestCase):
    password = "catalogue-test-password"

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        cls.member_user = user_model.objects.create_user(
            username="catalogue.member",
            password=cls.password,
        )
        cls.no_membership_user = user_model.objects.create_user(
            username="catalogue.no-membership",
            password=cls.password,
        )
        cls.inactive_member_user = user_model.objects.create_user(
            username="catalogue.inactive-member",
            password=cls.password,
        )
        cls.other_organization_user = user_model.objects.create_user(
            username="catalogue.other-organization",
            password=cls.password,
        )

        cls.first_organization = Organization.objects.create(
            name="Northwind Services",
            slug="northwind-services",
        )
        cls.second_organization = Organization.objects.create(
            name="Contoso Support",
            slug="contoso-support",
        )
        cls.empty_organization = Organization.objects.create(
            name="Empty Services",
            slug="empty-services",
        )
        cls.inactive_organization = Organization.objects.create(
            name="Inactive Services",
            slug="inactive-services",
            is_active=False,
        )

        OrganizationMembership.objects.create(
            organization=cls.first_organization,
            user=cls.member_user,
        )
        OrganizationMembership.objects.create(
            organization=cls.empty_organization,
            user=cls.member_user,
        )
        OrganizationMembership.objects.create(
            organization=cls.first_organization,
            user=cls.inactive_member_user,
            is_active=False,
        )
        OrganizationMembership.objects.create(
            organization=cls.second_organization,
            user=cls.other_organization_user,
        )

        cls.active_team = ServiceTeam.objects.create(
            organization=cls.first_organization,
            name="General Support",
            slug="general-support",
        )
        cls.inactive_team = ServiceTeam.objects.create(
            organization=cls.first_organization,
            name="Retired Support",
            slug="retired-support",
            is_active=False,
        )
        cls.other_organization_team = ServiceTeam.objects.create(
            organization=cls.second_organization,
            name="General Support",
            slug="general-support",
        )

        cls.alpha_service = Service.objects.create(
            organization=cls.first_organization,
            default_team=cls.active_team,
            name="Alpha Access",
            slug="alpha-access",
            description="Help with account access.",
        )
        cls.middle_service = Service.objects.create(
            organization=cls.first_organization,
            default_team=cls.active_team,
            name="Middle Support",
            slug="middle-support",
            description="General support requests.",
        )
        cls.zulu_service = Service.objects.create(
            organization=cls.first_organization,
            default_team=cls.active_team,
            name="Zulu Facilities",
            slug="zulu-facilities",
            description="Facilities-related requests.",
        )
        cls.inactive_service = Service.objects.create(
            organization=cls.first_organization,
            default_team=cls.active_team,
            name="Inactive Service",
            slug="inactive-service",
            is_active=False,
        )
        cls.service_with_inactive_team = Service.objects.create(
            organization=cls.first_organization,
            default_team=cls.inactive_team,
            name="Unavailable Team Service",
            slug="unavailable-team-service",
        )
        cls.other_organization_service = Service.objects.create(
            organization=cls.second_organization,
            default_team=cls.other_organization_team,
            name="Other Organization Service",
            slug="other-organization-service",
        )

    def setUp(self):
        self.client = APIClient()
        self.first_organization_url = reverse(
            "service_catalogue:service-list",
            kwargs={"organization_slug": self.first_organization.slug},
        )

    def _login(self, user):
        self.assertTrue(
            self.client.login(username=user.username, password=self.password)
        )

    def test_active_member_receives_available_services_in_alphabetical_order(self):
        self._login(self.member_user)

        response = self.client.get(self.first_organization_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["name"] for item in response.data],
            ["Alpha Access", "Middle Support", "Zulu Facilities"],
        )

    def test_each_service_exposes_exactly_the_approved_public_fields(self):
        self._login(self.member_user)

        response = self.client.get(self.first_organization_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        approved_fields = {"id", "name", "slug", "description"}
        forbidden_fields = {
            "organization",
            "default_team",
            "created_at",
            "updated_at",
            "is_active",
        }
        for item in response.data:
            self.assertEqual(set(item), approved_fields)
            self.assertTrue(forbidden_fields.isdisjoint(item))

    def test_returned_service_id_identifies_the_service_for_request_submission(self):
        self._login(self.member_user)

        response = self.client.get(self.first_organization_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        alpha_item = next(
            item for item in response.data if item["slug"] == self.alpha_service.slug
        )
        self.assertEqual(alpha_item["id"], self.alpha_service.pk)
        self.assertTrue(Service.objects.filter(pk=alpha_item["id"]).exists())

    def test_inactive_service_is_excluded(self):
        self._login(self.member_user)

        response = self.client.get(self.first_organization_url)

        returned_ids = {item["id"] for item in response.data}
        self.assertNotIn(self.inactive_service.pk, returned_ids)

    def test_service_with_inactive_default_team_is_excluded(self):
        self._login(self.member_user)

        response = self.client.get(self.first_organization_url)

        returned_ids = {item["id"] for item in response.data}
        self.assertNotIn(self.service_with_inactive_team.pk, returned_ids)

    def test_services_from_another_organization_are_excluded(self):
        self._login(self.member_user)

        response = self.client.get(self.first_organization_url)

        returned_ids = {item["id"] for item in response.data}
        self.assertNotIn(self.other_organization_service.pk, returned_ids)

    def test_active_organization_without_available_services_returns_empty_list(self):
        self._login(self.member_user)
        url = reverse(
            "service_catalogue:service-list",
            kwargs={"organization_slug": self.empty_organization.slug},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_each_available_service_is_returned_only_once(self):
        self._login(self.member_user)

        response = self.client.get(self.first_organization_url)

        returned_ids = [item["id"] for item in response.data]
        self.assertEqual(len(returned_ids), 3)
        self.assertEqual(len(returned_ids), len(set(returned_ids)))

    def test_anonymous_request_is_forbidden(self):
        response = self.client.get(self.first_organization_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_without_membership_is_forbidden(self):
        self._login(self.no_membership_user)

        response = self.client.get(self.first_organization_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_membership_is_forbidden(self):
        self._login(self.inactive_member_user)

        response = self.client.get(self.first_organization_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_belonging_only_to_another_organization_is_forbidden(self):
        self._login(self.other_organization_user)

        response = self.client.get(self.first_organization_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_organization_slug_returns_not_found(self):
        self._login(self.member_user)
        url = reverse(
            "service_catalogue:service-list",
            kwargs={"organization_slug": self.inactive_organization.slug},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unknown_organization_slug_returns_not_found(self):
        self._login(self.member_user)
        url = reverse(
            "service_catalogue:service-list",
            kwargs={"organization_slug": "unknown-organization"},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_is_not_allowed_and_does_not_change_services(self):
        self._login(self.member_user)
        service_count = Service.objects.count()

        response = self.client.post(
            self.first_organization_url,
            {"name": "Unexpected Service", "slug": "unexpected-service"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Service.objects.count(), service_count)
        self.assertFalse(Service.objects.filter(slug="unexpected-service").exists())
