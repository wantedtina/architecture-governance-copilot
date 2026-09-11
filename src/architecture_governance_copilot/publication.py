"""Human-confirmed, duplicate-aware publication coordination for one ADO action."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Annotated
from urllib.parse import quote, urlparse

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from architecture_governance_copilot.integrations.azure_devops import (
    JSON_PATCH_CONTENT_TYPE,
    AdoApiResponse,
    AdoCreateRequest,
    AdoGateway,
    AdoGatewayError,
    AdoGatewayErrorCategory,
    AdoJsonPatchOperation,
    AdoTargetConfiguration,
    AdoWorkItemRecord,
    parse_work_item_response,
)
from architecture_governance_copilot.integrations.confluence import ConfluencePageSnapshot
from architecture_governance_copilot.models import (
    ActionItem,
    GovernanceResult,
    ReviewInputManifest,
    SourceEvidence,
)

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class _PublicationModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class PublicationStatus(StrEnum):
    """Observable lifecycle states for one Create attempt."""

    NOT_SUBMITTED = "not_submitted"
    SUBMITTING = "submitting"
    SUCCEEDED = "succeeded"
    DEFINITELY_FAILED = "definitely_failed"
    UNKNOWN_RESULT = "unknown_result"


class DeliveryStatus(StrEnum):
    READY = "Ready"
    NOT_APPLICABLE = "Not applicable"
    UNAVAILABLE = "Unavailable"
    IN_PROGRESS = "In progress"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    NEEDS_RECONCILIATION = "Needs reconciliation"


class AdoDeliveryCapability(_PublicationModel):
    """Configured no-network delivery target and exact authorized source package."""

    provider_identity: NonEmptyString
    source_page_id: NonEmptyString
    source_space: NonEmptyString
    source_url: NonEmptyString
    source_version: int = Field(ge=1)
    source_canonicalizer_version: NonEmptyString
    source_content_fingerprint: NonEmptyString
    analysis_provider_identity: NonEmptyString
    transcript_fingerprint: NonEmptyString
    metadata_fingerprint: NonEmptyString
    target: AdoTargetConfiguration


class ActionDeliveryReadiness(_PublicationModel):
    """Reviewed values, explicit mappings, and every preflight blocker for an action."""

    action_index: int = Field(ge=0)
    title: NonEmptyString
    reviewed_owner: str | None
    resolved_assignee: str | None
    due_date: date | None
    reviewed_priority: NonEmptyString
    mapped_priority: int | None
    parent_reference: str | None
    mapped_parent: int | None
    blockers: tuple[NonEmptyString, ...] = ()

    @property
    def ready(self) -> bool:
        return not self.blockers


class DeliveryReadiness(_PublicationModel):
    """Package eligibility is independent from the visible analysis-mode label."""

    capability_available: bool
    blockers: tuple[NonEmptyString, ...] = ()
    actions: tuple[ActionDeliveryReadiness, ...] = ()

    @property
    def status(self) -> DeliveryStatus:
        if not self.actions:
            return DeliveryStatus.NOT_APPLICABLE
        if not self.capability_available:
            return DeliveryStatus.UNAVAILABLE
        return (
            DeliveryStatus.READY
            if any(a.ready for a in self.actions)
            else DeliveryStatus.UNAVAILABLE
        )


def assess_delivery_readiness(
    result: GovernanceResult,
    snapshot: ConfluencePageSnapshot | None,
    manifest: ReviewInputManifest | None,
    capability: AdoDeliveryCapability | None,
) -> DeliveryReadiness:
    """Assess all actions without preparing a request, changing a record, or calling a gateway."""
    blockers: list[str] = []
    if capability is None:
        blockers.append("No delivery provider is configured for this review package.")
    elif snapshot is None or manifest is None:
        blockers.append("The confirmed authoritative source package is missing.")
    else:
        for field in (
            "source_page_id",
            "source_space",
            "source_url",
            "source_version",
            "source_canonicalizer_version",
            "source_content_fingerprint",
            "transcript_fingerprint",
            "metadata_fingerprint",
        ):
            if getattr(manifest, field) != getattr(capability, field):
                blockers.append(
                    f"The confirmed {field.replace('_', ' ')} "
                    "does not match the configured capability."
                )
        if manifest.provider_configuration_identity != capability.analysis_provider_identity:
            blockers.append(
                "The confirmed provider identity does not match the configured capability."
            )
        if any(
            (
                snapshot.page_id != manifest.source_page_id,
                snapshot.space != manifest.source_space,
                snapshot.url != manifest.source_url,
                snapshot.version != manifest.source_version,
                snapshot.canonicalizer_version != manifest.source_canonicalizer_version,
                snapshot.content_fingerprint != manifest.source_content_fingerprint,
            )
        ):
            blockers.append("The source snapshot differs from the confirmed review package.")
        if (
            hashlib.sha256(result.context.model_dump_json().encode()).hexdigest()
            != capability.metadata_fingerprint
        ):
            blockers.append(
                "The reviewed metadata differs from the authorized source-controlled package."
            )
    target = capability.target if capability is not None else None
    rows = []
    for index, action in enumerate(result.action_items):
        action_blockers = list(blockers)
        assignee = target.owner_identities.get(action.owner) if target else None
        priority = target.priority_values.get(action.priority.value) if target else None
        parent = target.parent_work_item_ids.get(result.context.ado_ticket_id) if target else None
        if target:
            for check in (
                lambda action=action: _mapped_owner(action, target),
                lambda action=action: _required_due_date(action, target),
                lambda: _mapped_parent(result, target),
            ):
                try:
                    check()
                except PublicationValidationError as exc:
                    action_blockers.append(str(exc))
            if priority is None:
                action_blockers.append("The action priority has no approved target mapping.")
        rows.append(
            ActionDeliveryReadiness(
                action_index=index,
                title=action.title,
                reviewed_owner=action.owner,
                resolved_assignee=assignee,
                due_date=action.due_date,
                reviewed_priority=action.priority.value,
                mapped_priority=priority,
                parent_reference=result.context.ado_ticket_id,
                mapped_parent=parent,
                blockers=tuple(
                    f"Action {index + 1} ({action.title}), owner {action.owner or 'unset'}: {b}"
                    for b in action_blockers
                ),
            )
        )
    return DeliveryReadiness(
        capability_available=not blockers, blockers=tuple(blockers), actions=tuple(rows)
    )


class AdoPublicationPreview(_PublicationModel):
    """Exact Create request plus every identity needed to detect staleness."""

    action_index: int = Field(ge=0)
    action_title: NonEmptyString
    original_action_index: int = Field(ge=0)
    reviewed_owner: str | None
    reviewed_priority: NonEmptyString
    reviewed_result_fingerprint: NonEmptyString
    source_snapshot_fingerprint: NonEmptyString
    target_fingerprint: NonEmptyString
    mapping_fingerprint: NonEmptyString
    preview_fingerprint: NonEmptyString
    request: AdoCreateRequest


class AdoPublicationConfirmation(_PublicationModel):
    """Separate human confirmation bound to one exact preview."""

    preview_fingerprint: NonEmptyString
    confirmed_at: datetime


class AdoPublicationReceipt(_PublicationModel):
    """Known remote identity retained even when read-back cannot be verified."""

    work_item_id: int = Field(ge=1)
    revision: int | None = Field(default=None, ge=1)
    api_url: str | None = None
    browser_url: str | None = None
    correlation_id: NonEmptyString
    request_binding_fingerprint: NonEmptyString
    verified: bool
    verification_message: NonEmptyString


class AdoPublicationOperation(_PublicationModel):
    """One terminal or in-progress publication result retained for reconciliation."""

    status: PublicationStatus
    correlation_id: NonEmptyString
    request_binding_fingerprint: NonEmptyString
    message: NonEmptyString
    receipt: AdoPublicationReceipt | None = None


class PublicationValidationError(ValueError):
    """Reject stale, incomplete, or previously attempted publication requests."""


PROTECTED_PUBLICATION_STATUSES = frozenset(
    {
        PublicationStatus.SUBMITTING,
        PublicationStatus.SUCCEEDED,
        PublicationStatus.UNKNOWN_RESULT,
    }
)


def publication_correlations(
    result: GovernanceResult,
    snapshot: ConfluencePageSnapshot,
    preview: AdoPublicationPreview,
) -> tuple[str, ...]:
    """Stable correlation followed by possible pre-migration compact-index aliases."""
    action = result.action_items[preview.action_index]
    return tuple(
        dict.fromkeys(
            (
                preview.request.correlation_id,
                *(
                    _correlation_id(result, snapshot, action, index, preview.target_fingerprint)
                    for index in range(preview.original_action_index + 1)
                ),
            )
        )
    )


def build_ado_publication_preview(
    reviewed_result: GovernanceResult,
    source_snapshot: ConfluencePageSnapshot,
    action_index: int,
    target: AdoTargetConfiguration,
    *,
    original_action_index: int | None = None,
) -> AdoPublicationPreview:
    """Build one exact Create request directly from the confirmed governance model."""
    if not 0 <= action_index < len(reviewed_result.action_items):
        raise PublicationValidationError("Select one confirmed action for publication.")
    origin = action_index if original_action_index is None else original_action_index
    if isinstance(origin, bool) or not isinstance(origin, int) or origin < action_index:
        raise PublicationValidationError("The original analyzed action position is invalid.")
    action = reviewed_result.action_items[action_index]
    owner_identity = _mapped_owner(action, target)
    due_date = _required_due_date(action, target)
    parent_id = _mapped_parent(reviewed_result, target)
    priority_value = target.priority_values.get(action.priority.value)
    if priority_value is None:
        raise PublicationValidationError("The action priority has no approved target mapping.")

    reviewed_fingerprint = _fingerprint(reviewed_result.model_dump(mode="json"))
    source_fingerprint = _fingerprint(
        {
            "page_id": source_snapshot.page_id,
            "version": source_snapshot.version,
            "canonicalizer_version": source_snapshot.canonicalizer_version,
            "content_fingerprint": source_snapshot.content_fingerprint,
        }
    )
    target_fingerprint = _fingerprint(
        {
            "organization_url": target.organization_url,
            "project": target.project,
            "work_item_type": target.work_item_type,
            "api_version": target.api_version,
        }
    )
    mapping_fingerprint = _fingerprint(
        {
            "fields": target.fields.model_dump(mode="json"),
            "owner_identities": target.owner_identities,
            "parent_work_item_ids": target.parent_work_item_ids,
            "priority_values": target.priority_values,
            "requirements": {
                "owner": target.require_owner,
                "due_date": target.require_due_date,
                "parent": target.require_parent,
            },
        }
    )
    correlation_id = _correlation_id(
        reviewed_result,
        source_snapshot,
        action,
        origin,
        target_fingerprint,
    )
    operations = _build_patch_operations(
        reviewed_result,
        action,
        target,
        correlation_id=correlation_id,
        owner_identity=owner_identity,
        due_date=due_date,
        priority_value=priority_value,
        parent_id=parent_id,
    )
    request_url = _create_url(target)
    request_binding = _fingerprint(
        {
            "reviewed_result": reviewed_fingerprint,
            "source_snapshot": source_fingerprint,
            "action_index": action_index,
            "original_action_index": origin,
            "target": target_fingerprint,
            "mapping": mapping_fingerprint,
        }
    )
    request = AdoCreateRequest(
        url=request_url,
        content_type=JSON_PATCH_CONTENT_TYPE,
        operations=operations,
        correlation_id=correlation_id,
        binding_fingerprint=request_binding,
    )
    preview_fingerprint = _fingerprint(request.model_dump(mode="json"))
    return AdoPublicationPreview(
        action_index=action_index,
        action_title=action.title,
        original_action_index=origin,
        reviewed_owner=action.owner,
        reviewed_priority=action.priority.value,
        reviewed_result_fingerprint=reviewed_fingerprint,
        source_snapshot_fingerprint=source_fingerprint,
        target_fingerprint=target_fingerprint,
        mapping_fingerprint=mapping_fingerprint,
        preview_fingerprint=preview_fingerprint,
        request=request,
    )


def confirm_ado_publication_preview(
    preview: AdoPublicationPreview,
    *,
    confirmed_at: datetime | None = None,
) -> AdoPublicationConfirmation:
    """Create a separate confirmation for the currently displayed exact preview."""
    return AdoPublicationConfirmation(
        preview_fingerprint=preview.preview_fingerprint,
        confirmed_at=confirmed_at or datetime.now(UTC),
    )


class AdoPublicationCoordinator:
    """Reconcile, submit once, and verify one separately confirmed Create request."""

    def __init__(
        self,
        gateway: AdoGateway,
        *,
        transition: Callable[[AdoPublicationOperation], None] | None = None,
    ) -> None:
        self._gateway = gateway
        self._transition = transition

    def publish(
        self,
        *,
        preview: AdoPublicationPreview,
        confirmation: AdoPublicationConfirmation,
        reviewed_result: GovernanceResult,
        source_snapshot: ConfluencePageSnapshot,
        target: AdoTargetConfiguration,
        prior_operations: Mapping[str, AdoPublicationOperation] | None = None,
        original_action_index: int | None = None,
    ) -> AdoPublicationOperation:
        """Publish the exact eligible preview once; never automatically retry Create."""
        rebuilt = build_ado_publication_preview(
            reviewed_result,
            source_snapshot,
            preview.action_index,
            target,
            original_action_index=original_action_index,
        )
        if rebuilt != preview or confirmation.preview_fingerprint != preview.preview_fingerprint:
            raise PublicationValidationError(
                "The publication preview changed and must be previewed and confirmed again."
            )
        correlations = publication_correlations(reviewed_result, source_snapshot, preview)
        if any(
            operation.status in PROTECTED_PUBLICATION_STATUSES
            for correlation in correlations
            if (operation := (prior_operations or {}).get(correlation)) is not None
        ):
            raise PublicationValidationError(
                "This action already has a protected publication result. "
                "Reconcile it before retrying."
            )

        submitting = self._operation(
            preview,
            PublicationStatus.SUBMITTING,
            "Checking correlation and submitting the confirmed request.",
        )
        self._record_transition(submitting)

        try:
            matches_by_id: dict[int, str] = {}
            for correlation in correlations:
                for identifier in self._gateway.find_by_correlation(target, correlation):
                    matches_by_id[identifier] = correlation
            matches = tuple(matches_by_id)
        except AdoGatewayError:
            return self._finish(
                preview,
                PublicationStatus.DEFINITELY_FAILED,
                "Correlation reconciliation failed before Create; no request was submitted.",
            )
        except Exception:
            return self._finish(
                preview,
                PublicationStatus.DEFINITELY_FAILED,
                "Correlation reconciliation failed; Create was not attempted.",
            )

        if len(matches) > 1:
            return self._finish(
                preview,
                PublicationStatus.UNKNOWN_RESULT,
                "Multiple work items use this correlation; manual reconciliation is required.",
            )
        if len(matches) == 1:
            if matches_by_id[matches[0]] != preview.request.correlation_id:
                verified_operation = self._verify_known_item(
                    preview,
                    target,
                    matches[0],
                    created_record=None,
                    reconciled=True,
                )
                return self._finish(
                    preview,
                    PublicationStatus.UNKNOWN_RESULT,
                    "An existing legacy correlation identifies this action. "
                    f"Reconcile {matches_by_id[matches[0]]}; no Create was attempted.",
                    receipt=verified_operation.receipt,
                )
            return self._verify_known_item(
                preview,
                target,
                matches[0],
                created_record=None,
                reconciled=True,
            )

        try:
            create_response = self._gateway.create_work_item(preview.request)
        except AdoGatewayError as exc:
            status = (
                PublicationStatus.UNKNOWN_RESULT
                if exc.category is AdoGatewayErrorCategory.UNKNOWN_RESULT
                else PublicationStatus.DEFINITELY_FAILED
            )
            return self._finish(preview, status, str(exc))
        except Exception:
            return self._finish(
                preview,
                PublicationStatus.UNKNOWN_RESULT,
                "The Create result is unknown and requires correlation reconciliation.",
            )

        try:
            created_record = parse_work_item_response(create_response)
        except AdoGatewayError as exc:
            partial_receipt = _partial_receipt(create_response, preview)
            status = (
                PublicationStatus.DEFINITELY_FAILED
                if exc.category is AdoGatewayErrorCategory.DEFINITE_FAILURE
                else PublicationStatus.UNKNOWN_RESULT
            )
            return self._finish(
                preview,
                status,
                str(exc),
                receipt=partial_receipt,
            )
        return self._verify_known_item(
            preview,
            target,
            created_record.work_item_id,
            created_record=created_record,
            reconciled=False,
        )

    def _verify_known_item(
        self,
        preview: AdoPublicationPreview,
        target: AdoTargetConfiguration,
        work_item_id: int,
        *,
        created_record: AdoWorkItemRecord | None,
        reconciled: bool,
    ) -> AdoPublicationOperation:
        try:
            read_response = self._gateway.get_work_item(target, work_item_id)
            read_record = parse_work_item_response(read_response)
        except Exception:
            receipt = _receipt_from_record(
                created_record,
                preview,
                work_item_id=work_item_id,
                verified=False,
                message="The work item ID is known, but GET verification did not complete.",
            )
            return self._finish(
                preview,
                PublicationStatus.UNKNOWN_RESULT,
                receipt.verification_message,
                receipt=receipt,
            )

        mismatches = _verification_mismatches(preview, target, read_record)
        if mismatches:
            receipt = _receipt_from_record(
                read_record,
                preview,
                work_item_id=work_item_id,
                verified=False,
                message="Read-back fields did not match the confirmed request.",
            )
            return self._finish(
                preview,
                PublicationStatus.UNKNOWN_RESULT,
                f"{receipt.verification_message} Manual reconciliation is required.",
                receipt=receipt,
            )
        receipt = _receipt_from_record(
            read_record,
            preview,
            work_item_id=work_item_id,
            verified=True,
            message=(
                "Existing correlated work item verified without another Create."
                if reconciled
                else "Created work item verified by GET read-back."
            ),
        )
        return self._finish(
            preview,
            PublicationStatus.SUCCEEDED,
            receipt.verification_message,
            receipt=receipt,
        )

    def _operation(
        self,
        preview: AdoPublicationPreview,
        status: PublicationStatus,
        message: str,
        *,
        receipt: AdoPublicationReceipt | None = None,
    ) -> AdoPublicationOperation:
        return AdoPublicationOperation(
            status=status,
            correlation_id=preview.request.correlation_id,
            request_binding_fingerprint=preview.request.binding_fingerprint,
            message=message,
            receipt=receipt,
        )

    def _finish(
        self,
        preview: AdoPublicationPreview,
        status: PublicationStatus,
        message: str,
        *,
        receipt: AdoPublicationReceipt | None = None,
    ) -> AdoPublicationOperation:
        operation = self._operation(preview, status, message, receipt=receipt)
        self._record_transition(operation)
        return operation

    def _record_transition(self, operation: AdoPublicationOperation) -> None:
        if self._transition is not None:
            self._transition(operation)


def _build_patch_operations(
    result: GovernanceResult,
    action: ActionItem,
    target: AdoTargetConfiguration,
    *,
    correlation_id: str,
    owner_identity: str | None,
    due_date: str | None,
    priority_value: int,
    parent_id: int | None,
) -> tuple[AdoJsonPatchOperation, ...]:
    mapped_values: list[tuple[str, object | None]] = [
        (target.fields.title, action.title),
        (target.fields.description, _live_description(result, action, correlation_id)),
        (target.fields.assigned_to, owner_identity),
        (target.fields.due_date, due_date),
        (target.fields.priority, priority_value),
        (
            target.fields.tags,
            "; ".join(
                (
                    "Architecture Governance",
                    "Solution Intent",
                    f"Review Round {result.context.review_round}",
                )
            ),
        ),
        (target.fields.correlation, correlation_id),
        *target.fields.classification_values.items(),
    ]
    operations = [
        AdoJsonPatchOperation(path=f"/fields/{field}", value=value)
        for field, value in mapped_values
        if value is not None
    ]
    if parent_id is not None:
        parent_url = (
            f"{target.organization_url.rstrip('/')}/"
            f"{quote(target.project, safe='')}/_apis/wit/workItems/{parent_id}"
        )
        operations.append(
            AdoJsonPatchOperation(
                path="/relations/-",
                value={
                    "rel": "System.LinkTypes.Hierarchy-Reverse",
                    "url": parent_url,
                    "attributes": {"comment": "Linked from confirmed governance action."},
                },
            )
        )
    return tuple(operations)


def _mapped_owner(action: ActionItem, target: AdoTargetConfiguration) -> str | None:
    if action.owner is None:
        if target.require_owner:
            raise PublicationValidationError(
                "A confirmed action owner is required for publication."
            )
        return None
    identity = target.owner_identities.get(action.owner)
    if identity is None:
        raise PublicationValidationError(
            "The confirmed action owner has no approved identity mapping."
        )
    return identity


def _required_due_date(action: ActionItem, target: AdoTargetConfiguration) -> str | None:
    if action.due_date is None:
        if target.require_due_date:
            raise PublicationValidationError(
                "A confirmed action due date is required for publication."
            )
        return None
    return action.due_date.isoformat()


def _mapped_parent(
    result: GovernanceResult,
    target: AdoTargetConfiguration,
) -> int | None:
    parent_reference = result.context.ado_ticket_id
    if parent_reference is None:
        if target.require_parent:
            raise PublicationValidationError(
                "A mapped parent work item is required for publication."
            )
        return None
    parent_id = target.parent_work_item_ids.get(parent_reference)
    if parent_id is None:
        raise PublicationValidationError("The governance parent has no approved target mapping.")
    return parent_id


def _live_description(
    result: GovernanceResult,
    action: ActionItem,
    correlation_id: str,
) -> str:
    lines = [
        "Architecture Governance action from a human-confirmed review record.",
        "",
        f"Project: {result.context.project_name}",
        f"Solution Intent: {result.context.si_title}",
        f"SI Version: {result.context.si_version}",
        f"Review Round: {result.context.review_round}",
        "",
        f"Action: {action.title}",
        f"Owner: {action.owner or 'Unassigned'}",
        f"Due Date: {action.due_date.isoformat() if action.due_date else 'Not specified'}",
        f"Priority: {action.priority.value}",
        "",
        "Supporting Evidence:",
        *[f"- {_format_evidence(evidence)}" for evidence in action.evidence],
        "",
        f"Correlation: {correlation_id}",
    ]
    return "\n".join(lines)


def _format_evidence(evidence: SourceEvidence) -> str:
    locators = [evidence.source_type.value]
    for value in (
        evidence.section,
        evidence.timestamp,
        evidence.speaker,
        evidence.reference,
    ):
        if value is not None:
            locators.append(value.replace("|", r"\|"))
    return f'[{" | ".join(locators)}] "{evidence.quote}"'


def _create_url(target: AdoTargetConfiguration) -> str:
    encoded_project = quote(target.project, safe="")
    encoded_type = quote(target.work_item_type, safe="")
    encoded_version = quote(target.api_version, safe="")
    return (
        f"{target.organization_url.rstrip('/')}/{encoded_project}/_apis/wit/workitems/"
        f"${encoded_type}?api-version={encoded_version}"
    )


def _correlation_id(
    result: GovernanceResult,
    snapshot: ConfluencePageSnapshot,
    action: ActionItem,
    action_index: int,
    target_fingerprint: str,
) -> str:
    stable_action_identity = {
        "project": result.context.project_name,
        "si_title": result.context.si_title,
        "review_round": result.context.review_round,
        "page_id": snapshot.page_id,
        "action_index": action_index,
        "evidence": [
            {
                "source": evidence.source_type.value,
                "reference": evidence.reference,
                "quote": evidence.quote,
            }
            for evidence in action.evidence
        ],
        "target": target_fingerprint,
    }
    return f"agc-{_fingerprint(stable_action_identity)[:24]}"


def _verification_mismatches(
    preview: AdoPublicationPreview,
    target: AdoTargetConfiguration,
    record: AdoWorkItemRecord,
) -> tuple[str, ...]:
    mismatches: list[str] = []
    expected_fields = {
        operation.path.removeprefix("/fields/"): operation.value
        for operation in preview.request.operations
        if operation.path.startswith("/fields/")
    }
    for field, expected in expected_fields.items():
        if record.fields.get(field) != expected:
            mismatches.append(field)
    if record.fields.get("System.TeamProject") != target.project:
        mismatches.append("System.TeamProject")
    if record.fields.get("System.WorkItemType") != target.work_item_type:
        mismatches.append("System.WorkItemType")
    expected_relations = [
        operation.value
        for operation in preview.request.operations
        if operation.path == "/relations/-"
    ]
    for expected_relation in expected_relations:
        if expected_relation not in record.relations:
            mismatches.append("relations")
    return tuple(mismatches)


def _receipt_from_record(
    record: AdoWorkItemRecord | None,
    preview: AdoPublicationPreview,
    *,
    work_item_id: int,
    verified: bool,
    message: str,
) -> AdoPublicationReceipt:
    return AdoPublicationReceipt(
        work_item_id=work_item_id,
        revision=record.revision if record is not None else None,
        api_url=record.api_url if record is not None else None,
        browser_url=record.browser_url if record is not None else None,
        correlation_id=preview.request.correlation_id,
        request_binding_fingerprint=preview.request.binding_fingerprint,
        verified=verified,
        verification_message=message,
    )


def _partial_receipt(
    response: AdoApiResponse,
    preview: AdoPublicationPreview,
) -> AdoPublicationReceipt | None:
    body: object = response.body
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return None
    if not isinstance(body, Mapping):
        return None
    work_item_id = body.get("id")
    if isinstance(work_item_id, bool) or not isinstance(work_item_id, int) or work_item_id < 1:
        return None
    revision = body.get("rev")
    valid_revision = (
        revision
        if isinstance(revision, int) and not isinstance(revision, bool) and revision >= 1
        else None
    )
    api_url = _partial_safe_url(body.get("url"))
    links = body.get("_links")
    html = links.get("html") if isinstance(links, Mapping) else None
    browser_url = _partial_safe_url(html.get("href") if isinstance(html, Mapping) else None)
    return AdoPublicationReceipt(
        work_item_id=work_item_id,
        revision=valid_revision,
        api_url=api_url,
        browser_url=browser_url,
        correlation_id=preview.request.correlation_id,
        request_binding_fingerprint=preview.request.binding_fingerprint,
        verified=False,
        verification_message="The work item ID is known, but its response was incomplete.",
    )


def _partial_safe_url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = urlparse(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username
        or parsed.password
    ):
        return None
    return value


def _fingerprint(value: object) -> str:
    serialized = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def delivery_action_correlations(
    result: GovernanceResult,
    snapshot: ConfluencePageSnapshot,
    action_index: int,
    original_action_index: int,
    target: AdoTargetConfiguration,
) -> tuple[str, ...]:
    """Project operation identities even when a reviewed field currently blocks preparation."""
    if not 0 <= action_index < len(result.action_items) or original_action_index < action_index:
        raise PublicationValidationError("The delivery action identity is invalid.")
    target_fingerprint = _fingerprint(
        {
            "organization_url": target.organization_url,
            "project": target.project,
            "work_item_type": target.work_item_type,
            "api_version": target.api_version,
        }
    )
    positions = (original_action_index, *range(original_action_index))
    return tuple(
        _correlation_id(
            result, snapshot, result.action_items[action_index], index, target_fingerprint
        )
        for index in positions
    )


def publication_request_summary(
    preview: AdoPublicationPreview,
    target: AdoTargetConfiguration,
) -> dict[str, object]:
    """Readable labels over every exact outgoing field; no independently rebuilt payload."""
    labels = {
        target.fields.title: "Title",
        target.fields.description: "Description and evidence",
        target.fields.assigned_to: "Resolved assignee",
        target.fields.due_date: "Due date",
        target.fields.priority: "Mapped priority",
        target.fields.tags: "Tags",
        target.fields.correlation: "Correlation",
    }
    summary: dict[str, object] = {
        "Action": (
            f"Action {preview.action_index + 1} · "
            f"original action {preview.original_action_index + 1}"
        ),
        "Target project": target.project,
        "Work-item type": target.work_item_type,
        "API version": target.api_version,
        "Reviewed owner": preview.reviewed_owner or "Unset",
        "Reviewed priority": preview.reviewed_priority,
    }
    for operation in preview.request.operations:
        if operation.path.startswith("/fields/"):
            field = operation.path.removeprefix("/fields/")
            summary[labels.get(field, f"Classification · {field}")] = operation.value
        else:
            summary[f"Parent relation · {operation.path}"] = operation.value
    return summary
