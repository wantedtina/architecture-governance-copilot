"""Human-confirmed, duplicate-aware publication coordination for one ADO action."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
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


class AdoPublicationPreview(_PublicationModel):
    """Exact Create request plus every identity needed to detect staleness."""

    action_index: int = Field(ge=0)
    action_title: NonEmptyString
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


def build_ado_publication_preview(
    reviewed_result: GovernanceResult,
    source_snapshot: ConfluencePageSnapshot,
    action_index: int,
    target: AdoTargetConfiguration,
) -> AdoPublicationPreview:
    """Build one exact Create request directly from the confirmed governance model."""
    if not 0 <= action_index < len(reviewed_result.action_items):
        raise PublicationValidationError("Select one confirmed action for publication.")
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
        action_index,
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
    ) -> AdoPublicationOperation:
        """Publish the exact eligible preview once; never automatically retry Create."""
        rebuilt = build_ado_publication_preview(
            reviewed_result,
            source_snapshot,
            preview.action_index,
            target,
        )
        if rebuilt != preview or confirmation.preview_fingerprint != preview.preview_fingerprint:
            raise PublicationValidationError(
                "The publication preview changed and must be previewed and confirmed again."
            )
        prior = (prior_operations or {}).get(preview.request.correlation_id)
        if prior is not None and prior.status in {
            PublicationStatus.SUBMITTING,
            PublicationStatus.SUCCEEDED,
            PublicationStatus.UNKNOWN_RESULT,
        }:
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
            matches = self._gateway.find_by_correlation(target, preview.request.correlation_id)
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
