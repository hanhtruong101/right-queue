from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from organizations.models import Organization, OrganizationMembership
from service_catalogue.models import Service, ServiceTeam, TeamMembership


class ServiceTeamModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.first_organization = Organization.objects.create(
            name="Northwind Services",
            slug="northwind-services",
        )
        cls.second_organization = Organization.objects.create(
            name="Contoso Support",
            slug="contoso-support",
        )

    def test_service_team_can_be_created(self):
        team = ServiceTeam.objects.create(
            organization=self.first_organization,
            name="IT Support",
            slug="it-support",
        )

        self.assertEqual(team.organization, self.first_organization)
        self.assertEqual(team.name, "IT Support")
        self.assertEqual(team.slug, "it-support")
        self.assertTrue(team.is_active)

    def test_same_organization_cannot_have_duplicate_team_name(self):
        ServiceTeam.objects.create(
            organization=self.first_organization,
            name="IT Support",
            slug="it-support",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ServiceTeam.objects.create(
                    organization=self.first_organization,
                    name="IT Support",
                    slug="technical-support",
                )

    def test_same_organization_cannot_have_duplicate_team_slug(self):
        ServiceTeam.objects.create(
            organization=self.first_organization,
            name="IT Support",
            slug="it-support",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ServiceTeam.objects.create(
                    organization=self.first_organization,
                    name="Technical Support",
                    slug="it-support",
                )

    def test_different_organizations_can_use_same_team_name_and_slug(self):
        first_team = ServiceTeam.objects.create(
            organization=self.first_organization,
            name="IT Support",
            slug="it-support",
        )
        second_team = ServiceTeam.objects.create(
            organization=self.second_organization,
            name="IT Support",
            slug="it-support",
        )

        self.assertNotEqual(first_team.organization, second_team.organization)
        self.assertEqual(ServiceTeam.objects.filter(name="IT Support").count(), 2)

    def test_string_representation_is_readable(self):
        team = ServiceTeam.objects.create(
            organization=self.first_organization,
            name="IT Support",
            slug="it-support",
        )

        self.assertEqual(
            str(team),
            "IT Support is a service team of Northwind Services",
        )


class ServiceModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.first_organization = Organization.objects.create(
            name="Northwind Services",
            slug="northwind-services",
        )
        cls.second_organization = Organization.objects.create(
            name="Contoso Support",
            slug="contoso-support",
        )
        cls.first_team = ServiceTeam.objects.create(
            organization=cls.first_organization,
            name="IT Support",
            slug="it-support",
        )
        cls.second_team = ServiceTeam.objects.create(
            organization=cls.second_organization,
            name="IT Support",
            slug="it-support",
        )

    def test_service_can_be_created_with_team_from_same_organization(self):
        service = Service.objects.create(
            organization=self.first_organization,
            default_team=self.first_team,
            name="Account Access",
            slug="account-access",
        )

        self.assertEqual(service.organization, self.first_organization)
        self.assertEqual(service.default_team, self.first_team)
        self.assertTrue(service.is_active)

    def test_full_clean_rejects_default_team_from_another_organization(self):
        service = Service(
            organization=self.first_organization,
            default_team=self.second_team,
            name="Account Access",
            slug="account-access",
        )

        with self.assertRaises(ValidationError) as context:
            service.full_clean()

        self.assertIn("default_team", context.exception.message_dict)

    def test_same_organization_cannot_have_duplicate_service_name(self):
        Service.objects.create(
            organization=self.first_organization,
            default_team=self.first_team,
            name="Account Access",
            slug="account-access",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Service.objects.create(
                    organization=self.first_organization,
                    default_team=self.first_team,
                    name="Account Access",
                    slug="login-support",
                )

    def test_same_organization_cannot_have_duplicate_service_slug(self):
        Service.objects.create(
            organization=self.first_organization,
            default_team=self.first_team,
            name="Account Access",
            slug="account-access",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Service.objects.create(
                    organization=self.first_organization,
                    default_team=self.first_team,
                    name="Login Support",
                    slug="account-access",
                )

    def test_different_organizations_can_use_same_service_name_and_slug(self):
        first_service = Service.objects.create(
            organization=self.first_organization,
            default_team=self.first_team,
            name="Account Access",
            slug="account-access",
        )
        second_service = Service.objects.create(
            organization=self.second_organization,
            default_team=self.second_team,
            name="Account Access",
            slug="account-access",
        )

        self.assertNotEqual(
            first_service.organization,
            second_service.organization,
        )
        self.assertEqual(Service.objects.filter(name="Account Access").count(), 2)

    def test_string_representation_is_readable(self):
        service = Service.objects.create(
            organization=self.first_organization,
            default_team=self.first_team,
            name="Account Access",
            slug="account-access",
        )

        self.assertEqual(str(service), "Account Access (Northwind Services)")

    def test_deleting_protected_default_team_is_rejected(self):
        Service.objects.create(
            organization=self.first_organization,
            default_team=self.first_team,
            name="Account Access",
            slug="account-access",
        )

        with self.assertRaises(ProtectedError):
            self.first_team.delete()


class TeamMembershipModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.first_user = user_model.objects.create_user(
            username="first.user",
            password="test-password",
        )
        cls.second_user = user_model.objects.create_user(
            username="second.user",
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
        cls.first_membership = OrganizationMembership.objects.create(
            organization=cls.first_organization,
            user=cls.first_user,
        )
        cls.second_membership = OrganizationMembership.objects.create(
            organization=cls.first_organization,
            user=cls.second_user,
        )
        cls.other_organization_membership = OrganizationMembership.objects.create(
            organization=cls.second_organization,
            user=cls.first_user,
        )
        cls.first_team = ServiceTeam.objects.create(
            organization=cls.first_organization,
            name="IT Support",
            slug="it-support",
        )
        cls.second_team = ServiceTeam.objects.create(
            organization=cls.first_organization,
            name="Facilities",
            slug="facilities",
        )

    def test_organization_membership_can_be_added_to_team_in_same_organization(self):
        team_membership = TeamMembership.objects.create(
            team=self.first_team,
            membership=self.first_membership,
        )

        self.assertEqual(team_membership.team, self.first_team)
        self.assertEqual(team_membership.membership, self.first_membership)
        self.assertTrue(team_membership.is_active)

    def test_full_clean_rejects_membership_from_another_organization(self):
        team_membership = TeamMembership(
            team=self.first_team,
            membership=self.other_organization_membership,
        )

        with self.assertRaises(ValidationError) as context:
            team_membership.full_clean()

        self.assertIn("membership", context.exception.message_dict)

    def test_same_membership_cannot_be_added_to_same_team_twice(self):
        TeamMembership.objects.create(
            team=self.first_team,
            membership=self.first_membership,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TeamMembership.objects.create(
                    team=self.first_team,
                    membership=self.first_membership,
                )

    def test_membership_can_belong_to_multiple_teams_in_same_organization(self):
        TeamMembership.objects.create(
            team=self.first_team,
            membership=self.first_membership,
        )
        TeamMembership.objects.create(
            team=self.second_team,
            membership=self.first_membership,
        )

        self.assertEqual(self.first_membership.team_memberships.count(), 2)

    def test_multiple_organization_memberships_can_belong_to_same_team(self):
        TeamMembership.objects.create(
            team=self.first_team,
            membership=self.first_membership,
        )
        TeamMembership.objects.create(
            team=self.first_team,
            membership=self.second_membership,
        )

        self.assertEqual(self.first_team.team_memberships.count(), 2)

    def test_inactive_team_membership_is_stored(self):
        team_membership = TeamMembership.objects.create(
            team=self.first_team,
            membership=self.first_membership,
            is_active=False,
        )

        team_membership.refresh_from_db()
        self.assertFalse(team_membership.is_active)

    def test_string_representation_is_readable(self):
        team_membership = TeamMembership.objects.create(
            team=self.first_team,
            membership=self.first_membership,
        )

        self.assertEqual(
            str(team_membership),
            "first.user is in IT Support is a service team of Northwind Services",
        )
