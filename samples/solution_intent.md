# Solution Intent - Digital Payment Notification Service

> Synthetic hackathon demonstration content. This document does not describe a real
> organization, system, or production environment.

## 1. Document Information

| Field | Value |
| --- | --- |
| Project | Digital Payment Notification Service |
| Document version | 1.2 |
| Status | Under review |
| Review round | 2 |
| Governance ticket | ARCH-POC-1024 |
| Review date | 18 July 2026 |

This Solution Intent is jointly prepared by the fictional Product Owner and development team.
It records the design proposed for Domain Architecture review and will be revised after review
feedback.

## 2. Executive Summary

The Digital Payment Notification Service provides timely customer notifications after a payment
event is received. The service consumes payment events and sends customers an email or SMS
notification according to their communication preference. It is intended to decouple payment
processing from channel-specific delivery while preserving a traceable notification status.

The proposed design uses stateless application components, asynchronous processing, and a
managed relational database. The initial release is planned for August 2026. This document
describes the current design baseline and calls out open items that require governance or product
input before production readiness can be confirmed.

## 3. Scope

In scope are payment-event intake, validation, customer preference lookup, message composition,
email and SMS dispatch, retry handling, delivery-status recording, operational telemetry, and
deployment of the notification service. The service starts processing only after a payment event
has been published by the upstream payment platform.

Out of scope are payment authorization, settlement, customer-profile maintenance, marketing
campaigns, and management of the external email and SMS providers. Those capabilities are
represented only as synthetic upstream or downstream dependencies.

## 4. Conceptual Architecture

The conceptual flow is event driven. A payment event is placed on a durable message topic. A
notification consumer validates the event, determines the required channel, and creates a
notification request. Channel workers then call the appropriate email or SMS provider. Delivery
status is returned asynchronously and recorded for operational support.

The service boundary contains the event consumer, notification application service, email
worker, and SMS worker. The application services are stateless and will run with two replicas.
A durable message broker separates event intake from channel delivery so that a temporary
provider delay does not block upstream payment processing.

## 5. Detailed Application Design

The notification application validates required event fields, applies idempotency checks, and
selects a message template by event type and preferred channel. A channel worker submits the
rendered message and records the provider correlation value. Transient provider errors are
retried with bounded exponential backoff; messages that exhaust retries are placed on a
dead-letter queue for investigation.

The two replicas use the same container image and configuration contract. No user session or
in-memory workflow state is required between requests. Redis may be introduced as a cache, but
the team has not recorded a decision to use it. The current design therefore does not rely on
Redis for correctness, idempotency, or retry behavior.

## 6. Data Design

Managed PostgreSQL is proposed as the system of record for notification requests and delivery
status. Records contain a synthetic notification identifier, payment-event identifier, channel,
template version, processing state, provider correlation value, attempt count, and timestamps.
Message bodies and customer contact details are not retained beyond what is necessary to submit
the notification.

The database schema will enforce uniqueness on the payment-event and notification-type
combination to support idempotent processing. Data retention is provisionally set to 90 days,
subject to final product confirmation. Production database sizing remains pending until the
final transaction-volume forecast is available. Schema migration will be performed as a
controlled deployment step before new application pods accept traffic.

## 7. Availability and Resilience

Message durability and bounded retries protect against short interruptions to a notification
provider. Failed messages remain available for replay after investigation. Application pods
have readiness and liveness probes, and Kubernetes will restart a pod that fails its health
check.

The deployment design shows two application replicas on the normal steady-state path; traffic
behaviour when one replica becomes unavailable is not described. Recovery time objective (RTO)
and recovery point objective (RPO) values are not yet defined. Regional disaster recovery and
the evidence needed to demonstrate recovery remain subject to the agreed business objectives.

## 8. Security

Service identities will be used for calls between the application, message broker, and managed
database. Secrets required for the synthetic external providers will be supplied through the
runtime secret store and will not be embedded in container images or source code. Transport
encryption is required for all service connections.

The service will minimize customer data in logs and database records. Access to operational data
will be restricted to the support role after ownership is confirmed. Threat modeling is planned
before release, with particular attention to event spoofing, duplicate notifications, template
tampering, and inappropriate access to contact information.

## 9. Observability

Application logs and service metrics will be produced for all production workloads. Logs will
include correlation identifiers, processing state, retry count, and failure category without
including message content or customer contact details. Metrics will cover event intake,
successful delivery, provider failure, retry volume, dead-letter depth, processing latency, and
database connection saturation.

Alerts are proposed for sustained delivery failures, growing dead-letter queues, and database
capacity thresholds. Dashboard ownership and alert routing depend on the final production
support arrangement.

## 10. Deployment Design

The service will run in Kubernetes. A continuous-delivery pipeline will build and scan the
container image, apply the database migration, and deploy two replicas with rolling replacement.
The deployment description covers the normal path from the message topic through the
notification workers to PostgreSQL and the external channel providers.

The current diagram is a steady-state view only. It shows healthy replicas receiving work behind
the Kubernetes service and does not add a failure-path annotation or an operator validation step.
Environment-specific resource limits will be finalized after performance testing and the volume
forecast.

## 11. Operational Support

Runbook topics will include provider outages, dead-letter replay, duplicate-event investigation,
database-capacity alerts, and rollback of a failed release. Operational dashboards will be
available before production readiness review.

Production support ownership has not yet been assigned. Until an owning team and escalation path
are confirmed, alert routing, after-hours coverage, and approval to replay failed notifications
remain open governance information.

## 12. Assumptions and Open Items

- The upstream payment event includes a stable synthetic event identifier and notification type.
- Email and SMS providers support correlation values and asynchronous delivery status.
- The final transaction-volume forecast will be supplied before production sizing is approved.
- Product stakeholders will define acceptable RTO and RPO values.
- The team will decide whether Redis provides sufficient benefit to justify operating it.
- A production support owner and escalation path will be confirmed before release approval.
