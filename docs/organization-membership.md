# Organization and Membership

## Purpose

RightQueue is used by different organizations. Each organization has its own users, teams, services, requests, and routing rules.

A user must only be able to access the organizations they belong to. This is important because users must never see or submit requests in another organization's environment by accident.

## Main concepts

### Organization

An organization is one separate RightQueue environment.

Examples:

- Fontys University of Applied Sciences
- Another university
- A company using RightQueue for internal service requests

Each organization has:

- a name, shown to people;
- a unique slug, used in URLs, such as `fontys`;
- an active status, so it can be disabled without deleting its data;
- created and updated timestamps.

Example URL:

```text
/fontys/portal/requests/new
```

## Membership

A membership connects one user to one organization.

A user can belong to more than one organization. Their role can be different in each organization.

For example, Alex could be:

- a requester in Fontys;
- a staff member in another organization.

The role must belong to the membership, not directly to the global user account.

Each membership has:

- a user;
- an organization;
- one controlled role;
- an active status;
- created and updated timestamps.

There can only be one membership for the same user and organization. This rule is enforced by the database.

## Roles for the first MVP

| Role | What the person can do |
| --- | --- |
| Requester | Submit requests and view only their own requests. |
| Staff | View and work on requests for their authorized service teams. |
| Triage coordinator | View uncertain and returned requests, then assign a destination team. |
| Organization administrator | Manage organization settings, memberships, teams, services, and routing rules through Django Admin. |

## Access rule

Every protected backend action must check all of the following:

1. The user is signed in.
2. The user has an active membership in the organization from the URL or requested object.
3. The user's role permits the action.
4. The user is allowed to access the specific object.

Frontend route hiding is not security. The Django backend must enforce these checks.

## First MVP login approach

For the first MVP, there is no public account registration.

An organization administrator creates users and memberships in Django Admin. Users already know their credentials when they sign in.

This keeps the first version focused on safe organization access. Invitation emails, public registration, email verification, and account recovery can be added later if they become necessary.

## Acceptance criteria

This part of the system is complete when:

- an administrator can create an organization with a unique slug;
- an administrator can create an active membership for a user;
- a user can belong to multiple organizations;
- duplicate membership in the same organization is rejected;
- each membership has one valid role;
- inactive memberships can be stored;
- the organization and memberships can be managed in Django Admin;
- automated tests cover the important membership rules.

## Next step

After the organization and membership foundation is complete, the next backend slice is the service catalogue. It will define service teams, services, and simple routing rules.
