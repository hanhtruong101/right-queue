from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from organizations.models import Organization
from routing.models import RoutingKeyword, RoutingRule
from service_catalogue.models import Service, ServiceTeam


class RoutingModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org = Organization.objects.create(name="College", slug="college")
        team = ServiceTeam.objects.create(organization=cls.org, name="IT", slug="it")
        cls.service = Service.objects.create(organization=cls.org, name="Wifi", slug="wifi", default_team=team)
        cls.rule = RoutingRule.objects.create(organization=cls.org, service=cls.service, name="Wireless")

    def test_creation_and_inactive_flags(self):
        self.rule.full_clean()
        self.assertEqual(self.rule.minimum_score, 3)
        self.rule.is_active = False
        self.rule.save()
        keyword = RoutingKeyword.objects.create(rule=self.rule, phrase="  Wi-Fi   HELP  ", is_active=False)
        keyword.refresh_from_db()
        self.assertEqual(keyword.phrase, "wi fi help")
        self.assertEqual(keyword.weight, 1)
        self.assertFalse(keyword.is_active)
        self.assertFalse(RoutingRule.objects.get(pk=self.rule.pk).is_active)

    def test_rule_service_must_belong_to_organization(self):
        other = Organization.objects.create(name="Other", slug="other")
        rule = RoutingRule(organization=other, service=self.service, name="Other")
        with self.assertRaises(ValidationError) as cm:
            rule.full_clean()
        self.assertIn("service", cm.exception.message_dict)

    def test_rule_name_unique_per_organization(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            RoutingRule.objects.create(organization=self.org, service=self.service, name=self.rule.name)

    def test_canonical_phrase_unique_within_rule(self):
        RoutingKeyword.objects.create(rule=self.rule, phrase="Wi fi HELP")
        duplicate = RoutingKeyword(rule=self.rule, phrase="  WI-fi  help! ")
        with self.assertRaises(ValidationError):
            duplicate.full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicate.save()
        other_rule = RoutingRule.objects.create(organization=self.org, service=self.service, name="Alternate")
        RoutingKeyword.objects.create(rule=other_rule, phrase=duplicate.phrase)

    def test_nonpositive_thresholds_and_weights(self):
        for value in [0, -1]:
            with self.subTest(value=value):
                self.rule.minimum_score = value
                keyword = RoutingKeyword(rule=self.rule, phrase="help", weight=value)
                for obj in [self.rule, keyword]:
                    with self.assertRaises(ValidationError):
                        obj.full_clean()
                    with self.assertRaises(IntegrityError), transaction.atomic():
                        obj.save()

    def test_phrase_needs_at_least_one_word(self):
        with self.assertRaises(ValidationError):
            RoutingKeyword(rule=self.rule, phrase=" -- ").full_clean()
