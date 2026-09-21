from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from organizations.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
)


class AuthenticationAPITests(TestCase):
    trusted_origin = "http://localhost:5173"
    untrusted_origin = "https://untrusted.example"
    valid_password = "correct-test-password"

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        cls.active_user = user_model.objects.create_user(
            username="active.user",
            password=cls.valid_password,
            email="active.user@example.com",
            first_name="Active",
            last_name="User",
        )
        cls.inactive_user = user_model.objects.create_user(
            username="inactive.user",
            password=cls.valid_password,
            email="inactive.user@example.com",
            is_active=False,
        )
        cls.user_without_memberships = user_model.objects.create_user(
            username="no.memberships",
            password=cls.valid_password,
            email="no.memberships@example.com",
            first_name="No",
            last_name="Memberships",
        )

        cls.first_active_organization = Organization.objects.create(
            name="Northwind Services",
            slug="northwind-services",
        )
        cls.second_active_organization = Organization.objects.create(
            name="Contoso Support",
            slug="contoso-support",
        )
        cls.inactive_organization = Organization.objects.create(
            name="Fabrikam Services",
            slug="fabrikam-services",
            is_active=False,
        )

        cls.active_membership = OrganizationMembership.objects.create(
            organization=cls.first_active_organization,
            user=cls.active_user,
        )
        cls.inactive_membership = OrganizationMembership.objects.create(
            organization=cls.second_active_organization,
            user=cls.active_user,
            is_active=False,
        )
        cls.membership_in_inactive_organization = (
            OrganizationMembership.objects.create(
                organization=cls.inactive_organization,
                user=cls.active_user,
            )
        )

        OrganizationMembershipRole.objects.create(
            membership=cls.active_membership,
            role=OrganizationMembershipRole.Role.STAFF,
        )
        OrganizationMembershipRole.objects.create(
            membership=cls.active_membership,
            role=OrganizationMembershipRole.Role.REQUESTER,
        )
        OrganizationMembershipRole.objects.create(
            membership=cls.inactive_membership,
            role=OrganizationMembershipRole.Role.REQUESTER,
        )
        OrganizationMembershipRole.objects.create(
            membership=cls.membership_in_inactive_organization,
            role=OrganizationMembershipRole.Role.ORGANIZATION_ADMIN,
        )

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.csrf_url = reverse("accounts:csrf")
        self.login_url = reverse("accounts:login")
        self.logout_url = reverse("accounts:logout")
        self.me_url = reverse("accounts:me")

    def _get_csrf_token(self, client=None):
        client = client or self.client
        response = client.get(
            self.csrf_url,
            HTTP_ORIGIN=self.trusted_origin,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(settings.CSRF_COOKIE_NAME, response.cookies)
        return response.data["csrf_token"]

    def _login(self, *, user=None, password=None, client=None):
        client = client or self.client
        user = user or self.active_user
        password = password or self.valid_password
        csrf_token = self._get_csrf_token(client)
        return client.post(
            self.login_url,
            {"username": user.username, "password": password},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.trusted_origin,
        )

    def test_anonymous_user_can_obtain_csrf_token_and_cookie(self):
        response = self.client.get(self.csrf_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["csrf_token"])
        self.assertIn(settings.CSRF_COOKIE_NAME, response.cookies)
        self.assertTrue(response.cookies[settings.CSRF_COOKIE_NAME].value)

    def test_csrf_response_allows_trusted_frontend_origin_with_credentials(self):
        response = self.client.get(
            self.csrf_url,
            HTTP_ORIGIN=self.trusted_origin,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            self.trusted_origin,
        )
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Credentials"),
            "true",
        )

    def test_csrf_response_does_not_trust_unconfigured_origin(self):
        response = self.client.get(
            self.csrf_url,
            HTTP_ORIGIN=self.untrusted_origin,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.headers.get("Access-Control-Allow-Origin"))
        self.assertIsNone(response.headers.get("Access-Control-Allow-Credentials"))

    def test_login_without_csrf_token_is_forbidden(self):
        response = self.client.post(
            self.login_url,
            {
                "username": self.active_user.username,
                "password": self.valid_password,
            },
            format="json",
            HTTP_ORIGIN=self.trusted_origin,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn(settings.SESSION_COOKIE_NAME, self.client.cookies)

    def test_valid_csrf_token_allows_login_to_reach_credential_validation(self):
        csrf_token = self._get_csrf_token()

        response = self.client.post(
            self.login_url,
            {"username": self.active_user.username, "password": "wrong-password"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.trusted_origin,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_login_creates_session_and_returns_safe_user_data(self):
        response = self._login()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertTrue(self.client.cookies[settings.SESSION_COOKIE_NAME].value)
        self.assertEqual(response.data["id"], self.active_user.pk)
        self.assertEqual(response.data["username"], self.active_user.username)
        self.assertEqual(response.data["email"], self.active_user.email)
        self.assertEqual(response.data["first_name"], self.active_user.first_name)
        self.assertEqual(response.data["last_name"], self.active_user.last_name)
        self.assertEqual(
            response.data["memberships"],
            [
                {
                    "organization_name": self.first_active_organization.name,
                    "organization_slug": self.first_active_organization.slug,
                    "roles": [
                        OrganizationMembershipRole.Role.REQUESTER,
                        OrganizationMembershipRole.Role.STAFF,
                    ],
                }
            ],
        )

        sensitive_fields = {
            "password",
            "password_hash",
            "session",
            "session_key",
            "is_superuser",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
        }
        self.assertTrue(sensitive_fields.isdisjoint(response.data.keys()))

    def test_incorrect_password_is_rejected_without_session(self):
        response = self._login(password="wrong-password")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["detail"]),
            "The username or password is incorrect.",
        )
        self.assertNotIn(settings.SESSION_COOKIE_NAME, self.client.cookies)

    def test_unknown_username_is_rejected_with_generic_error_and_no_session(self):
        csrf_token = self._get_csrf_token()

        response = self.client.post(
            self.login_url,
            {"username": "unknown.user", "password": self.valid_password},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.trusted_origin,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["detail"]),
            "The username or password is incorrect.",
        )
        self.assertNotIn(settings.SESSION_COOKIE_NAME, self.client.cookies)

    def test_inactive_user_is_rejected_with_generic_error_and_no_session(self):
        response = self._login(user=self.inactive_user)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["detail"]),
            "The username or password is incorrect.",
        )
        self.assertNotIn(settings.SESSION_COOKIE_NAME, self.client.cookies)

    def test_missing_username_is_rejected_without_session(self):
        csrf_token = self._get_csrf_token()

        response = self.client.post(
            self.login_url,
            {"password": self.valid_password},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.trusted_origin,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertNotIn(settings.SESSION_COOKIE_NAME, self.client.cookies)

    def test_missing_password_is_rejected_without_session(self):
        csrf_token = self._get_csrf_token()

        response = self.client.post(
            self.login_url,
            {"username": self.active_user.username},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
            HTTP_ORIGIN=self.trusted_origin,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertNotIn(settings.SESSION_COOKIE_NAME, self.client.cookies)

    def test_anonymous_current_user_request_is_forbidden(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_current_user_returns_same_safe_active_membership_data_after_login(self):
        login_response = self._login()
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, login_response.data)
        self.assertEqual(len(response.data["memberships"]), 1)
        self.assertEqual(
            response.data["memberships"][0]["organization_slug"],
            self.first_active_organization.slug,
        )
        self.assertNotIn("password", response.data)
        self.assertNotIn("session_key", response.data)
        self.assertNotIn("is_superuser", response.data)

    def test_user_without_memberships_can_login_and_me_returns_empty_list(self):
        response = self._login(user=self.user_without_memberships)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["memberships"], [])

        me_response = self.client.get(self.me_url)

        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["memberships"], [])

    def test_anonymous_logout_is_forbidden(self):
        response = self.client.post(self.logout_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logged_in_logout_without_current_csrf_token_is_forbidden(self):
        login_response = self._login()
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            self.logout_url,
            {},
            format="json",
            HTTP_ORIGIN=self.trusted_origin,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get(self.me_url).status_code, status.HTTP_200_OK)

    def test_logout_with_rotated_csrf_token_clears_session(self):
        login_response = self._login()
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        current_csrf_token = self.client.cookies[settings.CSRF_COOKIE_NAME].value

        response = self.client.post(
            self.logout_url,
            {},
            format="json",
            HTTP_X_CSRFTOKEN=current_csrf_token,
            HTTP_ORIGIN=self.trusted_origin,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(self.client.cookies[settings.SESSION_COOKIE_NAME].value)
        self.assertEqual(
            self.client.get(self.me_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_get_logout_does_not_end_authenticated_session(self):
        login_response = self._login()
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.get(self.me_url).status_code, status.HTTP_200_OK)
