from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from cases.models import RequestStatusHistory, ServiceRequest
from cases.services import submit_service_request
from organizations.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
)
from service_catalogue.models import Service, ServiceTeam


class SubmitServiceRequestTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        cls.active_organization = Organization.objects.create(
            name="Northwind Services",
            slug="northwind-services",
        )
        cls.inactive_organization = Organization.objects.create(
            name="Contoso Support",
            slug="contoso-support",
            is_active=False,
        )

        cls.requester_user = user_model.objects.create_user(
            username="active.requester",
            password="test-password",
        )
        cls.inactive_user = user_model.objects.create_user(
            username="inactive.requester",
            password="test-password",
        )
        cls.no_role_user = user_model.objects.create_user(
            username="no.role",
            password="test-password",
        )
        cls.multi_role_user = user_model.objects.create_user(
            username="multi.role",
            password="test-password",
        )
        cls.other_organization_user = user_model.objects.create_user(
            username="other.requester",
            password="test-password",
        )

        cls.active_requester = OrganizationMembership.objects.create(
            organization=cls.active_organization,
            user=cls.requester_user,
        )
        cls.inactive_requester = OrganizationMembership.objects.create(
            organization=cls.active_organization,
            user=cls.inactive_user,
            is_active=False,
        )
        cls.requester_without_role = OrganizationMembership.objects.create(
            organization=cls.active_organization,
            user=cls.no_role_user,
        )
        cls.multi_role_requester = OrganizationMembership.objects.create(
            organization=cls.active_organization,
            user=cls.multi_role_user,
        )
        cls.other_organization_requester = OrganizationMembership.objects.create(
            organization=cls.inactive_organization,
            user=cls.other_organization_user,
        )

        requester_role = OrganizationMembershipRole.Role.REQUESTER
        OrganizationMembershipRole.objects.create(
            membership=cls.active_requester,
            role=requester_role,
        )
        OrganizationMembershipRole.objects.create(
            membership=cls.inactive_requester,
            role=requester_role,
        )
        OrganizationMembershipRole.objects.create(
            membership=cls.multi_role_requester,
            role=requester_role,
        )
        OrganizationMembershipRole.objects.create(
            membership=cls.multi_role_requester,
            role=OrganizationMembershipRole.Role.STAFF,
        )
        OrganizationMembershipRole.objects.create(
            membership=cls.other_organization_requester,
            role=requester_role,
        )

        cls.active_team = ServiceTeam.objects.create(
            organization=cls.active_organization,
            name="IT Support",
            slug="it-support",
        )
        cls.inactive_team = ServiceTeam.objects.create(
            organization=cls.active_organization,
            name="Legacy Support",
            slug="legacy-support",
            is_active=False,
        )
        cls.other_organization_team = ServiceTeam.objects.create(
            organization=cls.inactive_organization,
            name="IT Support",
            slug="it-support",
        )

        cls.active_service = Service.objects.create(
            organization=cls.active_organization,
            default_team=cls.active_team,
            name="Account Access",
            slug="account-access",
        )
        cls.inactive_service = Service.objects.create(
            organization=cls.active_organization,
            default_team=cls.active_team,
            name="Legacy Account Access",
            slug="legacy-account-access",
            is_active=False,
        )
        cls.service_with_inactive_team = Service.objects.create(
            organization=cls.active_organization,
            default_team=cls.inactive_team,
            name="Legacy Software",
            slug="legacy-software",
        )
        cls.other_organization_service = Service.objects.create(
            organization=cls.inactive_organization,
            default_team=cls.other_organization_team,
            name="Account Access",
            slug="account-access",
        )

    def test_active_requester_and_service_are_automatically_routed(self):
        service_request = submit_service_request(
            organization=self.active_organization,
            requester=self.active_requester,
            service=self.active_service,
            title="  Cannot access account  ",
            description="  My account sign-in is not working.  ",
        )

        service_request.refresh_from_db()
        self.assertEqual(service_request.current_status, ServiceRequest.Status.QUEUED)
        self.assertEqual(service_request.assigned_team, self.active_team)
        self.assertEqual(service_request.organization, self.active_organization)
        self.assertEqual(service_request.requester, self.active_requester)
        self.assertEqual(service_request.service, self.active_service)
        self.assertEqual(service_request.title, "Cannot access account")
        self.assertEqual(
            service_request.description,
            "My account sign-in is not working.",
        )

        history = list(service_request.status_history.all())
        self.assertEqual(len(history), 2)
        self.assertIsNone(history[0].from_status)
        self.assertEqual(history[0].to_status, ServiceRequest.Status.SUBMITTED)
        self.assertEqual(history[0].changed_by, self.active_requester)
        self.assertEqual(history[1].from_status, ServiceRequest.Status.SUBMITTED)
        self.assertEqual(history[1].to_status, ServiceRequest.Status.QUEUED)
        self.assertIsNone(history[1].changed_by)
        self.assertLess(history[0].created_at, history[1].created_at)

    def test_request_without_service_is_sent_to_manual_triage(self):
        service_request = submit_service_request(
            organization=self.active_organization,
            requester=self.active_requester,
            service=None,
            title="General support request",
            description="I am not sure which service applies.",
        )

        service_request.refresh_from_db()
        self.assertEqual(
            service_request.current_status,
            ServiceRequest.Status.PENDING_TRIAGE,
        )
        self.assertIsNone(service_request.assigned_team)

        history = list(service_request.status_history.all())
        self.assertEqual(len(history), 2)
        self.assertIsNone(history[0].from_status)
        self.assertEqual(history[0].to_status, ServiceRequest.Status.SUBMITTED)
        self.assertEqual(history[1].from_status, ServiceRequest.Status.SUBMITTED)
        self.assertEqual(
            history[1].to_status,
            ServiceRequest.Status.PENDING_TRIAGE,
        )

    def test_service_with_inactive_default_team_is_sent_to_manual_triage(self):
        service_request = submit_service_request(
            organization=self.active_organization,
            requester=self.active_requester,
            service=self.service_with_inactive_team,
            title="Legacy software request",
            description="I need help with legacy software.",
        )

        service_request.refresh_from_db()
        self.assertEqual(
            service_request.current_status,
            ServiceRequest.Status.PENDING_TRIAGE,
        )
        self.assertIsNone(service_request.assigned_team)

    def test_inactive_organization_is_rejected_without_persisting_records(self):
        with self.assertRaises(ValidationError):
            submit_service_request(
                organization=self.inactive_organization,
                requester=self.other_organization_requester,
                service=self.other_organization_service,
                title="Account access request",
                description="I need help accessing my account.",
            )

        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_inactive_membership_is_rejected_without_persisting_records(self):
        with self.assertRaises(ValidationError):
            submit_service_request(
                organization=self.active_organization,
                requester=self.inactive_requester,
                service=self.active_service,
                title="Account access request",
                description="I need help accessing my account.",
            )

        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_membership_from_another_organization_is_rejected_without_records(self):
        with self.assertRaises(ValidationError):
            submit_service_request(
                organization=self.active_organization,
                requester=self.other_organization_requester,
                service=self.active_service,
                title="Account access request",
                description="I need help accessing my account.",
            )

        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_service_from_another_organization_is_rejected_without_records(self):
        with self.assertRaises(ValidationError):
            submit_service_request(
                organization=self.active_organization,
                requester=self.active_requester,
                service=self.other_organization_service,
                title="Account access request",
                description="I need help accessing my account.",
            )

        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_inactive_service_is_rejected_without_persisting_records(self):
        with self.assertRaises(ValidationError):
            submit_service_request(
                organization=self.active_organization,
                requester=self.active_requester,
                service=self.inactive_service,
                title="Legacy account request",
                description="I need help with a legacy account.",
            )

        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_membership_without_requester_role_is_rejected_without_records(self):
        with self.assertRaises(ValidationError):
            submit_service_request(
                organization=self.active_organization,
                requester=self.requester_without_role,
                service=self.active_service,
                title="Account access request",
                description="I need help accessing my account.",
            )

        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_membership_with_requester_and_other_roles_is_accepted(self):
        service_request = submit_service_request(
            organization=self.active_organization,
            requester=self.multi_role_requester,
            service=self.active_service,
            title="Account access request",
            description="I need help accessing my account.",
        )

        service_request.refresh_from_db()
        self.assertEqual(service_request.current_status, ServiceRequest.Status.QUEUED)
        self.assertEqual(service_request.requester, self.multi_role_requester)
        self.assertEqual(service_request.status_history.count(), 2)

    def test_blank_title_is_rejected_without_persisting_records(self):
        with self.assertRaises(ValidationError):
            submit_service_request(
                organization=self.active_organization,
                requester=self.active_requester,
                service=self.active_service,
                title="   ",
                description="I need help accessing my account.",
            )

        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_blank_description_is_rejected_without_persisting_records(self):
        with self.assertRaises(ValidationError):
            submit_service_request(
                organization=self.active_organization,
                requester=self.active_requester,
                service=self.active_service,
                title="Account access request",
                description="   ",
            )

        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())

    def test_second_history_failure_rolls_back_entire_submission(self):
        original_full_clean = RequestStatusHistory.full_clean
        validation_calls = 0

        def fail_on_second_history_validation(history, *args, **kwargs):
            nonlocal validation_calls
            validation_calls += 1
            if validation_calls == 2:
                raise RuntimeError("Simulated routing history failure")
            return original_full_clean(history, *args, **kwargs)

        with patch.object(
            RequestStatusHistory,
            "full_clean",
            autospec=True,
            side_effect=fail_on_second_history_validation,
        ):
            with self.assertRaisesMessage(
                RuntimeError,
                "Simulated routing history failure",
            ):
                submit_service_request(
                    organization=self.active_organization,
                    requester=self.active_requester,
                    service=self.active_service,
                    title="Account access request",
                    description="I need help accessing my account.",
                )

        self.assertEqual(validation_calls, 2)
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())
