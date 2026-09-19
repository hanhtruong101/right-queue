from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from cases.models import RequestStatusHistory, ServiceRequest
from organizations.models import Organization, OrganizationMembership
from service_catalogue.models import Service, ServiceTeam


class ServiceRequestModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.first_user = user_model.objects.create_user(
            username="first.requester",
            password="test-password",
        )
        cls.second_user = user_model.objects.create_user(
            username="second.requester",
            password="test-password",
        )
        cls.first_organization = Organization.objects.create(
            name="Northwind Services",
            slug="northwind-services",
        )
        cls.second_organization = Organization.objects.create(
            name="Contoso Support",
            slug="contoso-support",
        )
        cls.first_requester = OrganizationMembership.objects.create(
            organization=cls.first_organization,
            user=cls.first_user,
        )
        cls.second_requester = OrganizationMembership.objects.create(
            organization=cls.second_organization,
            user=cls.second_user,
        )
        cls.first_default_team = ServiceTeam.objects.create(
            organization=cls.first_organization,
            name="IT Support",
            slug="it-support",
        )
        cls.first_direct_team = ServiceTeam.objects.create(
            organization=cls.first_organization,
            name="Facilities",
            slug="facilities",
        )
        cls.second_team = ServiceTeam.objects.create(
            organization=cls.second_organization,
            name="IT Support",
            slug="it-support",
        )
        cls.first_service = Service.objects.create(
            organization=cls.first_organization,
            default_team=cls.first_default_team,
            name="Account Access",
            slug="account-access",
        )
        cls.second_service = Service.objects.create(
            organization=cls.second_organization,
            default_team=cls.second_team,
            name="Account Access",
            slug="account-access",
        )

    def test_request_can_be_created_with_matching_organization_relationships(self):
        service_request = ServiceRequest.objects.create(
            organization=self.first_organization,
            requester=self.first_requester,
            service=self.first_service,
            assigned_team=self.first_default_team,
            title="Cannot access account",
            description="My account sign-in is not working.",
        )

        self.assertEqual(service_request.organization, self.first_organization)
        self.assertEqual(service_request.requester, self.first_requester)
        self.assertEqual(service_request.service, self.first_service)
        self.assertEqual(service_request.assigned_team, self.first_default_team)
        self.assertEqual(
            service_request.current_status,
            ServiceRequest.Status.SUBMITTED,
        )

    def test_request_is_valid_without_selected_service(self):
        service_request = ServiceRequest(
            organization=self.first_organization,
            requester=self.first_requester,
            service=None,
            assigned_team=self.first_default_team,
            title="General support request",
            description="I am not sure which service applies.",
        )

        service_request.full_clean()

    def test_request_is_valid_without_assigned_team(self):
        service_request = ServiceRequest(
            organization=self.first_organization,
            requester=self.first_requester,
            service=self.first_service,
            assigned_team=None,
            title="Account access question",
            description="I need help accessing my account.",
        )

        service_request.full_clean()

    def test_full_clean_rejects_requester_from_another_organization(self):
        service_request = ServiceRequest(
            organization=self.first_organization,
            requester=self.second_requester,
            service=self.first_service,
            assigned_team=self.first_default_team,
            title="Account access question",
            description="I need help accessing my account.",
        )

        with self.assertRaises(ValidationError) as context:
            service_request.full_clean()

        self.assertIn("requester", context.exception.message_dict)

    def test_full_clean_rejects_service_from_another_organization(self):
        service_request = ServiceRequest(
            organization=self.first_organization,
            requester=self.first_requester,
            service=self.second_service,
            assigned_team=self.first_default_team,
            title="Account access question",
            description="I need help accessing my account.",
        )

        with self.assertRaises(ValidationError) as context:
            service_request.full_clean()

        self.assertIn("service", context.exception.message_dict)

    def test_full_clean_rejects_assigned_team_from_another_organization(self):
        service_request = ServiceRequest(
            organization=self.first_organization,
            requester=self.first_requester,
            service=self.first_service,
            assigned_team=self.second_team,
            title="Account access question",
            description="I need help accessing my account.",
        )

        with self.assertRaises(ValidationError) as context:
            service_request.full_clean()

        self.assertIn("assigned_team", context.exception.message_dict)

    def test_separately_created_requests_receive_different_references(self):
        first_request = ServiceRequest.objects.create(
            organization=self.first_organization,
            requester=self.first_requester,
            title="First request",
            description="The first request description.",
        )
        second_request = ServiceRequest.objects.create(
            organization=self.first_organization,
            requester=self.first_requester,
            title="Second request",
            description="The second request description.",
        )

        self.assertNotEqual(first_request.reference, second_request.reference)

    def test_string_representation_contains_reference_and_title(self):
        service_request = ServiceRequest.objects.create(
            organization=self.first_organization,
            requester=self.first_requester,
            title="Cannot access account",
            description="My account sign-in is not working.",
        )

        representation = str(service_request)
        self.assertIn(str(service_request.reference), representation)
        self.assertIn("Cannot access account", representation)

    def test_referenced_requester_membership_cannot_be_deleted(self):
        ServiceRequest.objects.create(
            organization=self.first_organization,
            requester=self.first_requester,
            title="Cannot access account",
            description="My account sign-in is not working.",
        )

        with self.assertRaises(ProtectedError):
            self.first_requester.delete()

    def test_referenced_service_cannot_be_deleted(self):
        ServiceRequest.objects.create(
            organization=self.first_organization,
            requester=self.first_requester,
            service=self.first_service,
            title="Cannot access account",
            description="My account sign-in is not working.",
        )

        with self.assertRaises(ProtectedError):
            self.first_service.delete()

    def test_directly_assigned_team_cannot_be_deleted(self):
        ServiceRequest.objects.create(
            organization=self.first_organization,
            requester=self.first_requester,
            service=None,
            assigned_team=self.first_direct_team,
            title="Building access issue",
            description="I need help with access to a building.",
        )

        self.assertFalse(self.first_direct_team.default_services.exists())
        with self.assertRaises(ProtectedError):
            self.first_direct_team.delete()


class RequestStatusHistoryModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.requester_user = user_model.objects.create_user(
            username="requester.user",
            password="test-password",
        )
        cls.coordinator_user = user_model.objects.create_user(
            username="coordinator.user",
            password="test-password",
        )
        cls.other_user = user_model.objects.create_user(
            username="other.user",
            password="test-password",
        )
        cls.first_organization = Organization.objects.create(
            name="Northwind Services",
            slug="northwind-services",
        )
        cls.second_organization = Organization.objects.create(
            name="Contoso Support",
            slug="contoso-support",
        )
        cls.requester = OrganizationMembership.objects.create(
            organization=cls.first_organization,
            user=cls.requester_user,
        )
        cls.coordinator = OrganizationMembership.objects.create(
            organization=cls.first_organization,
            user=cls.coordinator_user,
        )
        cls.other_membership = OrganizationMembership.objects.create(
            organization=cls.second_organization,
            user=cls.other_user,
        )
        cls.service_request = ServiceRequest.objects.create(
            organization=cls.first_organization,
            requester=cls.requester,
            title="Cannot access account",
            description="My account sign-in is not working.",
        )

    def test_initial_submitted_history_entry_is_valid(self):
        history = RequestStatusHistory(
            request=self.service_request,
            from_status=None,
            to_status=ServiceRequest.Status.SUBMITTED,
        )

        history.full_clean()

    def test_initial_non_submitted_history_entry_is_rejected(self):
        history = RequestStatusHistory(
            request=self.service_request,
            from_status=None,
            to_status=ServiceRequest.Status.QUEUED,
        )

        with self.assertRaises(ValidationError) as context:
            history.full_clean()

        self.assertIn("to_status", context.exception.message_dict)

    def test_submitted_to_queued_transition_is_valid(self):
        history = RequestStatusHistory(
            request=self.service_request,
            from_status=ServiceRequest.Status.SUBMITTED,
            to_status=ServiceRequest.Status.QUEUED,
        )

        history.full_clean()

    def test_identical_from_and_to_status_is_rejected(self):
        history = RequestStatusHistory(
            request=self.service_request,
            from_status=ServiceRequest.Status.QUEUED,
            to_status=ServiceRequest.Status.QUEUED,
        )

        with self.assertRaises(ValidationError) as context:
            history.full_clean()

        self.assertIn("to_status", context.exception.message_dict)

    def test_changed_by_membership_from_request_organization_is_valid(self):
        history = RequestStatusHistory(
            request=self.service_request,
            from_status=ServiceRequest.Status.SUBMITTED,
            to_status=ServiceRequest.Status.QUEUED,
            changed_by=self.coordinator,
        )

        history.full_clean()

    def test_changed_by_membership_from_another_organization_is_rejected(self):
        history = RequestStatusHistory(
            request=self.service_request,
            from_status=ServiceRequest.Status.SUBMITTED,
            to_status=ServiceRequest.Status.QUEUED,
            changed_by=self.other_membership,
        )

        with self.assertRaises(ValidationError) as context:
            history.full_clean()

        self.assertIn("changed_by", context.exception.message_dict)

    def test_changed_by_none_is_valid_for_system_event(self):
        history = RequestStatusHistory(
            request=self.service_request,
            from_status=None,
            to_status=ServiceRequest.Status.SUBMITTED,
            changed_by=None,
        )

        history.full_clean()

    def test_status_history_is_returned_in_chronological_order(self):
        first_history = RequestStatusHistory.objects.create(
            request=self.service_request,
            from_status=None,
            to_status=ServiceRequest.Status.SUBMITTED,
        )
        second_history = RequestStatusHistory.objects.create(
            request=self.service_request,
            from_status=ServiceRequest.Status.SUBMITTED,
            to_status=ServiceRequest.Status.QUEUED,
        )

        self.assertEqual(
            list(self.service_request.status_history.all()),
            [first_history, second_history],
        )

    def test_deleting_request_deletes_status_history(self):
        history = RequestStatusHistory.objects.create(
            request=self.service_request,
            from_status=None,
            to_status=ServiceRequest.Status.SUBMITTED,
        )
        history_id = history.pk

        self.service_request.delete()

        self.assertFalse(
            RequestStatusHistory.objects.filter(pk=history_id).exists()
        )

    def test_string_representation_contains_reference_and_status_labels(self):
        history = RequestStatusHistory.objects.create(
            request=self.service_request,
            from_status=ServiceRequest.Status.SUBMITTED,
            to_status=ServiceRequest.Status.QUEUED,
        )

        representation = str(history)
        self.assertIn(str(self.service_request.reference), representation)
        self.assertIn("Submitted", representation)
        self.assertIn("Queued", representation)
