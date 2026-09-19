# RightQueue - Software Requirements Document

| Item | Value |
| --- | --- |
| Version | 0.1 (initial MVP baseline) |
| Status | Draft — to be validated with stakeholders |
| Project scope | Personal Complex Software Engineering project (140 hours) |
| Target deadline | 15 January 2027 |

## 1. Purpose

This document describes what RightQueue should do, how it should behave, and the conditions in which it must operate. It gives developers and testers one shared reference while keeping the first version small enough to build, test, and evaluate within the available project time.

RightQueue is a standalone platform that helps an organization direct a service request to the team most likely to own it. It is not a replacement for every existing service desk, email system, or portal.

## 2. Problem and intended outcome

At Fontys, people may be unsure which department should receive a question. A request can reach the wrong team and be forwarded several times. This can delay help, create duplicate work, and make ownership unclear.

RightQueue lets a requester describe a problem in ordinary language. The system uses a small, explainable set of rules to propose the right service team. A team can accept the request, or return it to central triage with a reason when the team is not responsible. A coordinator can then choose a new destination.

The first evaluation case is Fontys, but the design must work for more than one organization. An organization must never be able to view or manage another organization's requests.

### Intended MVP outcome

A requester can submit a request, the request reaches a team queue or central triage, a staff member can handle it, and every routing and status change can be traced afterwards.

## 3. Scope

### In scope for the MVP

- Separate, protected environments for organizations.
- Request submission with title, description, and limited context.
- A small service catalogue maintained per organization.
- Explainable, rule-based classification and routing.
- Team queues before individual assignment.
- Staff acceptance and controlled workflow changes.
- Return of a wrongly routed request with a required reason.
- Central triage and manual reassignment by a coordinator.
- Views for requesters and staff.
- Complete routing, ownership, and status history.
- Basic role-based authorization, essential validation, automated tests, and one measured quality or load experiment.

### Out of scope for the MVP

- AI-driven classification, summarization, or chat support.
- Direct integrations with Fontys email, forms, portals, or other third-party systems.
- Microservices, Redis, queues for background jobs, and complex capacity routing.
- Staff-skill matching, SLA management, multi-step approval flows, and advanced reporting.
- Native mobile applications.

## 4. Evidence, decisions, and assumptions

### Current decisions

- RightQueue is a standalone, multi-organization platform.
- The first prototype may use an organization slug in the URL and seeded Fontys-like data.
- Requests are routed to a service-team queue, not directly to a staff member.
- An uncertain route goes to central triage.
- A returned request needs a reason and must not immediately repeat the same failed route.
- The initial architecture is a modular monolith with PostgreSQL.

### Assumptions requiring validation

- Requesters prefer describing their issue over choosing a department or detailed tags.
- Teams need a central triage fallback for incorrect routes.
- The proposed roles and statuses match real working practices.
- A small service catalogue is enough for a meaningful first evaluation.

These are not presented as facts about Fontys. They must be checked through interviews, observations, anonymized request examples, prototype feedback, or document analysis.

## 5. Stakeholders and actors

| Actor | Main need | MVP permissions |
| --- | --- | --- |
| Requester | Ask for help and see progress | Create and view own requests; add permitted messages |
| Staff member | See work for their team and handle it | View team queue; accept, update, resolve, or return requests as allowed |
| Coordinator / triage operator | Correct unclear or rejected routes | View triage; review routing information; reassign requests |
| Organization administrator | Maintain local setup and access | Manage organization members, teams, services, and routing rules |
| Platform operator | Maintain the platform | Outside normal organization operations; access must be restricted and auditable |

## 6. System boundary

RightQueue owns request records, routing decisions, queues, workflow state, and audit history. It does not send or read external email, determine institutional policy, or solve the requester’s problem itself.

The MVP includes a web client and an application API. They must apply the same authorization and workflow rules. The internal implementation may later change, but clients must not be able to bypass those rules.

## 7. Core concepts

- **Organization:** A customer environment with its own data, users, catalogue, teams, rules, and requests.
- **Service:** A request type or area of help shown in an organization’s catalogue.
- **Service team:** The department or group that owns a queue and handles requests.
- **Team queue:** The shared destination for a team before a staff member accepts a request.
- **Classification:** The internal interpretation of a request used for routing; it is separate from ownership.
- **Triage:** A central queue for uncertain, unassigned, or returned requests.
- **Owner:** The team queue or staff member currently responsible for acting.
- **Routing decision:** A recorded decision that moves a request to a team or triage.

## 8. Functional requirements

### Organization access and authorization

| ID | Requirement |
| --- | --- |
| FR-01 | The system shall identify the organization before a user can access organization data. |
| FR-02 | The system shall ensure that users can only access data belonging to their organization. |
| FR-03 | The system shall enforce permissions by role on every protected action. |
| FR-04 | The system shall prevent a requester from viewing another requester’s requests unless a future policy explicitly permits it. |
| FR-05 | The system shall let an organization administrator manage the initial service catalogue, teams, memberships, and routing rules. |

### Request submission and visibility

| ID | Requirement |
| --- | --- |
| FR-06 | A requester shall be able to create a request with a title, description, and only the defined context fields. |
| FR-07 | The system shall validate required fields and show clear messages when information is missing or invalid. |
| FR-08 | The system shall show a requester their own requests, current status, current owning team where appropriate, and message history. |
| FR-09 | The system shall assign each request a unique identifier within the platform. |

### Routing and triage

| ID | Requirement |
| --- | --- |
| FR-10 | On submission, the system shall evaluate active routing rules for the request’s organization. |
| FR-11 | The system shall record the classification inputs or result, matched rule where applicable, confidence/clarity outcome, and destination. |
| FR-12 | A clear rule match shall route the request to the matching team queue. |
| FR-13 | No match or an uncertain match shall route the request to central triage. |
| FR-14 | A staff member shall be able to return a request that their team does not own only by providing a reason. |
| FR-15 | A returned request shall move to central triage and retain its previous destination and return reason. |
| FR-16 | A coordinator shall be able to manually assign a triage request to an eligible team queue with a recorded reason or note. |
| FR-17 | The system shall block an automatic route that would immediately repeat the last failed destination. |

### Queue handling and workflow

| ID | Requirement |
| --- | --- |
| FR-18 | Staff members shall be able to view requests in queues belonging to their team. |
| FR-19 | An eligible staff member shall be able to accept an unassigned request from their team queue. |
| FR-20 | The system shall record the staff member when a request is accepted. |
| FR-21 | The system shall allow only valid status transitions defined in this document. |
| FR-22 | Authorized staff shall be able to add a message and change a request to waiting for requester, in progress, or resolved when the transition is valid. |
| FR-23 | The system shall show relevant request history to authorized staff and coordinators. |

### History and audit

| ID | Requirement |
| --- | --- |
| FR-24 | The system shall preserve status, ownership, routing, return, reassignment, and key access-management events. |
| FR-25 | Each history event shall include time, event type, affected request where relevant, and the actor or system process responsible. |
| FR-26 | Normal users shall not be able to edit or delete audit history. |

## 9. Workflow rules

### Status model

`Submitted → Routed → Queued → In progress → Waiting for requester → In progress → Resolved`

`Submitted → Routed → Central triage → Queued`

`Queued or In progress → Central triage` when a team returns the request with a reason.

The implementation may represent routing and queue placement as separate fields rather than public statuses. The visible behaviour must remain clear to users.

| From | To | Who may perform it | Rule |
| --- | --- | --- | --- |
| Submitted | Queued / Central triage | System | Evaluate routing rules and record the decision. |
| Queued | In progress | Eligible staff | Staff member accepts the request. |
| In progress | Waiting for requester | Assigned staff | A message or clear request for information is required. |
| Waiting for requester | In progress | Assigned staff or requester action, subject to policy | New information is received or work resumes. |
| In progress | Resolved | Assigned staff | Resolution information is required. |
| Queued / In progress | Central triage | Eligible staff | Return reason is required; failed team must be recorded. |
| Central triage | Queued | Coordinator | New team destination is selected and recorded. |

**Open policy question:** whether a resolved request may be reopened, and by whom, requires stakeholder validation.

## 10. Business rules

1. A request belongs to exactly one organization.
2. A service, team, routing rule, queue, and membership belongs to one organization.
3. A request has one current team queue or central triage destination at a time.
4. A request may have zero or one current staff handler.
5. A request cannot be accepted by staff outside its current team.
6. Returning a request requires a non-empty reason.
7. Reassignment does not erase prior routes, ownership, or return reasons.
8. Routing rules are evaluated only within the request’s organization.
9. A failed route must be considered when routing again to avoid an immediate repeat.
10. A user cannot perform an action that their role does not allow.

## 11. Non-functional requirements

| ID | Requirement |
| --- | --- |
| NFR-01 | The MVP shall protect organization isolation in the database, application logic, and authorization checks. |
| NFR-02 | The system shall use authenticated access for protected functions and store credentials securely using the selected framework’s recommended approach. |
| NFR-03 | The system shall validate input server-side and protect against common web risks appropriate to the chosen framework. |
| NFR-04 | For normal MVP data volumes, common actions such as loading a queue or submitting a request should feel responsive; the target and test conditions will be defined during validation. |
| NFR-05 | The system shall give clear, actionable validation and authorization messages without exposing sensitive data. |
| NFR-06 | The codebase shall use automated tests for essential authorization, workflow, routing, return, and organization-isolation rules. |
| NFR-07 | Deployment, configuration, database migrations, logging, and basic health monitoring shall be documented and repeatable. |
| NFR-08 | The design shall be a modular monolith so it can be understood, tested, and deployed within the project scope. |
| NFR-09 | The application shall use PostgreSQL because its relational transactions suit ownership, history, and concurrent updates. |

## 12. Acceptance-focused user stories

### US-01 — Submit a request

As a requester, I want to describe my question without choosing a department, so that I can ask for help even when I do not know who owns it.

Acceptance criteria:

- I can provide a title and description.
- I receive confirmation and a request identifier after valid submission.
- The request is routed to a team queue or central triage.
- I can later see its current status.

### US-02 — Accept team work

As a staff member, I want to accept a request from my team queue, so that responsibility is clear.

Acceptance criteria:

- I can see only queues for teams where I am a member.
- I can accept an unassigned request in an eligible queue.
- The request records me as the current handler and the history records the change.

### US-03 — Return a wrong request

As a staff member, I want to return a request my team does not own, so that a coordinator can correct the route.

Acceptance criteria:

- I must enter a reason before returning it.
- The request moves to central triage.
- Its previous team, return reason, and route remain visible in history.
- The same failed team is not immediately selected automatically again.

### US-04 — Reassign from triage

As a coordinator, I want to review and reassign a triage request, so that it reaches an appropriate team.

Acceptance criteria:

- I can see the request description, routing explanation, and prior route history.
- I can select a team in my organization.
- The new decision is stored with my identity and time.
- Staff in the selected team can see the request in their queue.

## 13. Environment and technical constraints

- The application will run as a web-based modular monolith.
- PostgreSQL is the intended relational database.
- Java/Spring Boot and Python/Django are both under consideration. The final choice must be recorded as an evidence-based technical decision before significant implementation proceeds.
- If Python is selected, a virtual environment is required; Django and Django REST Framework are the preferred platform stack.
- The prototype may use seeded, non-sensitive data. Real personal or request data must not be used without appropriate approval and safeguards.
- The product must be deployable in an environment suitable for a student project; the chosen hosting constraints remain open.

## 14. Validation and traceability plan

| Area | Validation approach | Evidence to retain |
| --- | --- | --- |
| Problem and user needs | Interviews, observations, short survey, or anonymized case analysis | Notes, consent-aware summaries, findings |
| Catalogue and rules | Review with service representatives or use controlled seed data | Approved examples and rule rationale |
| Workflow | Walkthrough or prototype usability sessions | Scenarios, feedback, changes made |
| Functional requirements | Automated tests and acceptance checks | Test results and coverage of critical rules |
| Performance / routing quality | One defined experiment with realistic seed scenarios | Test design, measurements, interpretation |
| Security and isolation | Role and cross-organization test cases | Test results and documented mitigations |

Each implemented feature should reference one or more IDs from this document. Test cases should use the same IDs where practical.

## 15. Open questions

1. What exact organizations, teams, services, locations, and sample requests should seed the first prototype?
2. Which sign-in method is practical and permitted for the prototype: local accounts, invitation links, verified domains, or an identity provider?
3. Which context fields are useful enough to request without making submission difficult?
4. Who can reopen a resolved request, if reopening is needed?
5. May requesters add messages while a request is waiting, and should that automatically resume work?
6. What information about routing should requesters see without causing confusion or exposing internal details?
7. What measurable success criterion best represents improvement for the evaluation case?
8. What privacy, retention, deployment, and security constraints apply to the final demonstration?

## 16. Research questions

The project will consolidate research into these five main questions:

1. What routing and handover problems do requesters and service teams experience, and what causes them?
2. Which request information, catalogue entries, and explainable rules are needed to identify likely team ownership?
3. Which domain model, workflow, and authorization design can enforce ownership, returns, history, and organization isolation?
4. How well does the MVP route and process requests under defined realistic scenarios and workload?
5. Which security, deployment, testing, monitoring, and technology choices are justified for a reliable 140-hour MVP?

AI, caching, asynchronous work, and alternative architecture styles may be researched as optional follow-up experiments only when evidence shows a need.

## 17. Glossary

| Term | Meaning |
| --- | --- |
| Audit event | A protected record of an important system action. |
| Central triage | The queue used when the correct owner is uncertain or a team rejects a request. |
| Classification | Internal categorization used to support routing. It does not itself make a team the owner. |
| Current handler | The staff member currently working on an accepted request. |
| Current owner | The team queue or individual currently responsible for the next action. |
| Organization isolation | Protection that keeps one organization’s data and actions separate from another’s. |
| Routing rule | A defined, explainable condition that selects a route. |
| Service catalogue | The organization’s list of available services and their related teams. |

## 18. Change history

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 11 September 2026 | Created initial MVP requirements baseline from project context. |

