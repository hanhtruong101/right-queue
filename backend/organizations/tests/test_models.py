from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from organizations.models import (
    Organization,
    OrganizationMembership,
    OrganizationMembershipRole,
)


class OrganizationModelTests(TestCase):
    def test_organization_can_be_created_with_name_and_unique_slug(self):
        organization = Organization.objects.create(
            name="Northwind Services",
            slug="northwind-services",
        )

        self.assertEqual(organization.name, "Northwind Services")
        self.assertEqual(organization.slug, "northwind-services")
        self.assertTrue(Organization.objects.filter(pk=organization.pk).exists())

    def test_duplicate_organization_slug_is_rejected(self):
        Organization.objects.create(
            name="Northwind Services",
            slug="northwind-services",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Organization.objects.create(
                    name="Another Organization",
                    slug="northwind-services",
                )


class OrganizationMembershipModelTests(TestCase):
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

    def test_user_can_have_active_memberships_in_two_organizations(self):
        first_membership = OrganizationMembership.objects.create(
            organization=self.first_organization,
            user=self.first_user,
        )
        second_membership = OrganizationMembership.objects.create(
            organization=self.second_organization,
            user=self.first_user,
        )

        self.assertTrue(first_membership.is_active)
        self.assertTrue(second_membership.is_active)
        self.assertEqual(self.first_user.organization_memberships.count(), 2)

    def test_organization_can_have_memberships_for_two_users(self):
        OrganizationMembership.objects.create(
            organization=self.first_organization,
            user=self.first_user,
        )
        OrganizationMembership.objects.create(
            organization=self.first_organization,
            user=self.second_user,
        )

        self.assertEqual(self.first_organization.memberships.count(), 2)

    def test_duplicate_membership_for_user_and_organization_is_rejected(self):
        OrganizationMembership.objects.create(
            organization=self.first_organization,
            user=self.first_user,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                OrganizationMembership.objects.create(
                    organization=self.first_organization,
                    user=self.first_user,
                )

    def test_inactive_membership_is_stored(self):
        membership = OrganizationMembership.objects.create(
            organization=self.first_organization,
            user=self.first_user,
            is_active=False,
        )

        membership.refresh_from_db()
        self.assertFalse(membership.is_active)


class OrganizationMembershipRoleModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(
            username="role.user",
            password="test-password",
        )
        organization = Organization.objects.create(
            name="Northwind Services",
            slug="northwind-services",
        )
        cls.membership = OrganizationMembership.objects.create(
            organization=organization,
            user=user,
        )

    def test_membership_can_receive_two_different_roles(self):
        OrganizationMembershipRole.objects.create(
            membership=self.membership,
            role=OrganizationMembershipRole.Role.REQUESTER,
        )
        OrganizationMembershipRole.objects.create(
            membership=self.membership,
            role=OrganizationMembershipRole.Role.STAFF,
        )

        self.assertSetEqual(
            set(self.membership.roles.values_list("role", flat=True)),
            {
                OrganizationMembershipRole.Role.REQUESTER,
                OrganizationMembershipRole.Role.STAFF,
            },
        )

    def test_assigning_same_role_twice_to_membership_is_rejected(self):
        OrganizationMembershipRole.objects.create(
            membership=self.membership,
            role=OrganizationMembershipRole.Role.REQUESTER,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                OrganizationMembershipRole.objects.create(
                    membership=self.membership,
                    role=OrganizationMembershipRole.Role.REQUESTER,
                )
