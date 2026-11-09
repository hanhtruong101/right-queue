from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from cases.models import RequestStatusHistory, ServiceRequest
from cases.services import submit_service_request
from organizations.models import Organization, OrganizationMembership, OrganizationMembershipRole
from routing.models import RoutingKeyword, RoutingRule
from routing.services import _candidates
from service_catalogue.models import Service, ServiceTeam


class SubmissionRoutingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org = Organization.objects.create(name="College", slug="college")
        user = get_user_model().objects.create_user(username="student")
        cls.member = OrganizationMembership.objects.create(organization=cls.org, user=user)
        OrganizationMembershipRole.objects.create(membership=cls.member, role=OrganizationMembershipRole.Role.REQUESTER)
        cls.team = ServiceTeam.objects.create(organization=cls.org, name="IT", slug="it")
        cls.service = Service.objects.create(organization=cls.org, name="Networks", slug="net", default_team=cls.team)
        cls.rule = RoutingRule.objects.create(organization=cls.org, name="Wireless", service=cls.service)
        cls.keyword = RoutingKeyword.objects.create(rule=cls.rule, phrase="wifi", weight=4)

    def submit(self, description="Wifi is down"):
        request = submit_service_request(
            organization=self.org, requester=self.member, title="Please help", description=description
        )
        request.refresh_from_db()
        return request

    def assert_route(self, request, status, reason, service=None, team=None):
        self.assertEqual((request.current_status, request.service, request.assigned_team), (status, service, team))
        first, second = list(request.status_history.all())
        self.assertEqual((first.from_status, first.to_status, first.changed_by), (None, "SUBMITTED", self.member))
        self.assertEqual((second.from_status, second.to_status, second.changed_by), ("SUBMITTED", status, None))
        self.assertIn(reason, second.reason)

    def test_success_and_explanation(self):
        self.assert_route(self.submit(), "QUEUED", "'Wireless' with score 4", self.service, self.team)

    def test_no_match(self):
        self.assert_route(self.submit("Lost my keys"), "PENDING_TRIAGE", "No qualifying")

    def test_tie(self):
        rule = RoutingRule.objects.create(organization=self.org, name="Alternate", service=self.service)
        RoutingKeyword.objects.create(rule=rule, phrase="down", weight=4)
        self.assert_route(self.submit(), "PENDING_TRIAGE", "Ambiguous")

    def test_disabled_configuration_cannot_route(self):
        for obj in [self.rule, self.keyword, self.service, self.team]:
            with self.subTest(model=type(obj).__name__):
                obj.is_active = False
                obj.save()
                self.assert_route(self.submit(), "PENDING_TRIAGE", "No qualifying")
                obj.is_active = True
                obj.save()

    def test_foreign_rules_are_not_candidates(self):
        other = Organization.objects.create(name="Other", slug="other")
        team = ServiceTeam.objects.create(organization=other, name="IT", slug="it")
        service = Service.objects.create(organization=other, name="Mail", slug="mail", default_team=team)
        rule = RoutingRule.objects.create(organization=other, name="Mail", service=service)
        RoutingKeyword.objects.create(rule=rule, phrase="email", weight=10)
        self.assert_route(self.submit("email"), "PENDING_TRIAGE", "No qualifying")

    def test_candidate_loading_uses_two_queries_for_multiple_rules(self):
        RoutingRule.objects.create(organization=self.org, name="Extra", service=self.service)
        with self.assertNumQueries(2):
            self.assertEqual(len(list(_candidates(self.org.pk))), 2)

    def test_routing_history_write_failure_rolls_back_submission(self):
        save = RequestStatusHistory.save

        def fail_system_write(event, *args, **kwargs):
            if event.changed_by_id is None:
                raise RuntimeError("Routing history write failed")
            return save(event, *args, **kwargs)

        with patch.object(RequestStatusHistory, "save", fail_system_write):
            with self.assertRaisesMessage(RuntimeError, "Routing history write failed"):
                self.submit()
        self.assertFalse(ServiceRequest.objects.exists())
        self.assertFalse(RequestStatusHistory.objects.exists())
