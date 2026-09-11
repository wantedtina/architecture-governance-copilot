"""Pure support functions for the routed Streamlit proof of concept."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from architecture_governance_copilot.governance_service import GovernanceOutputs
from architecture_governance_copilot.integrations.confluence import (
    ConfluenceBodyFormat,
    ConfluencePagePayload,
    ConfluencePageSnapshot,
    build_confluence_snapshot,
)
from architecture_governance_copilot.models import (
    DraftingRevisionKind,
    DraftingSourceInventory,
    DraftingSourcePackageManifest,
    DraftingSourceProvenance,
    DraftingSourceResource,
    DraftingSourceRole,
    DraftingValidationStatus,
    GovernanceResult,
    ReviewInputManifest,
    ReviewInputProvenance,
    SelectedDraftingSource,
    SolutionIntentDraft,
    SolutionIntentDraftRequest,
    SolutionIntentReviewContext,
    SourceEvidence,
)
from architecture_governance_copilot.publication import (
    AdoPublicationConfirmation,
    AdoPublicationOperation,
    AdoPublicationPreview,
    DeliveryReadiness,
    DeliveryStatus,
    PublicationStatus,
)
from architecture_governance_copilot.runtime_dependencies import (
    OFFLINE_PROVIDER_CONFIGURATION_ID,
    DeploymentPolicy,
    ReviewMode,
)
from architecture_governance_copilot.si_drafting import (
    DETERMINISTIC_DRAFTING_PROVIDER_CONFIGURATION_ID,
    DeterministicDemoDrafter,
)

STATE_PREFIX = "agc_"
DRAFT_EVIDENCE_KEY = f"{STATE_PREFIX}draft_evidence"
DRAFT_REPOSITORY_NAME_KEY = f"{STATE_PREFIX}draft_repository_name"
DEPLOYMENT_POLICY_ID_KEY = f"{STATE_PREFIX}deployment_policy_id"
REVIEW_POLICY_RECOVERY_KEY = f"{STATE_PREFIX}review_policy_recovery"
REVIEW_WIDGET_PREFIX = f"{STATE_PREFIX}field_"
STATE_SCHEMA_VERSION = 4
STATE_SCHEMA_VERSION_KEY = f"{STATE_PREFIX}state_schema_version"
ACTIVE_WORKFLOW_KEY = f"{STATE_PREFIX}active_workflow"

PROJECT_CONTEXT_KEY = f"{STATE_PREFIX}project_context"
PROJECT_CONTEXT_CONFIRMED_KEY = f"{STATE_PREFIX}project_context_confirmed"
PROJECT_CONTEXT_REFRESHED_KEY = f"{STATE_PREFIX}project_context_refreshed"
CONTEXT_TEMPLATE_ID_KEY = f"{STATE_PREFIX}context_template_id"
CONTEXT_REPOSITORY_ID_KEY = f"{STATE_PREFIX}context_repository_id"
CONTEXT_EVIDENCE_IDS_KEY = f"{STATE_PREFIX}context_evidence_ids"
CONTEXT_TEMPLATE_WIDGET_KEY = f"{STATE_PREFIX}context_template_widget"
CONTEXT_REPOSITORY_WIDGET_KEY = f"{STATE_PREFIX}context_repository_widget"
CONTEXT_EVIDENCE_WIDGET_KEY = f"{STATE_PREFIX}context_evidence_widget"
LIVE_SOURCE_PACKAGE_KEY = f"{STATE_PREFIX}live_source_package"
CONFIRMED_SOURCE_PACKAGE_KEY = f"{STATE_PREFIX}confirmed_source_package"
CONFIRMED_SOURCE_PACKAGE_FINGERPRINT_KEY = f"{STATE_PREFIX}confirmed_source_package_fingerprint"
DRAFT_PROJECT_KEY = f"{STATE_PREFIX}draft_project"
DRAFT_TEMPLATE_KEY = f"{STATE_PREFIX}draft_template"
DRAFT_SOURCE_CODE_KEY = f"{STATE_PREFIX}draft_source_code"
DRAFT_SUPPORTING_DOCS_KEY = f"{STATE_PREFIX}draft_supporting_docs"
DRAFT_RESULT_KEY = f"{STATE_PREFIX}draft_result"
DRAFT_FINGERPRINT_KEY = f"{STATE_PREFIX}draft_fingerprint"
DRAFT_CONFIRMED_KEY = f"{STATE_PREFIX}draft_confirmed"
DRAFT_PROJECT_WIDGET_KEY = f"{STATE_PREFIX}draft_project_widget"
DRAFT_TEMPLATE_WIDGET_KEY = f"{STATE_PREFIX}draft_template_widget"
DRAFT_SOURCE_CODE_WIDGET_KEY = f"{STATE_PREFIX}draft_source_code_widget"
DRAFT_SUPPORTING_DOCS_WIDGET_KEY = f"{STATE_PREFIX}draft_supporting_docs_widget"
DRAFT_CONTENT_WIDGET_KEY = f"{STATE_PREFIX}draft_content_widget"
SOLUTION_INTENT_KEY = f"{STATE_PREFIX}solution_intent"
TRANSCRIPT_KEY = f"{STATE_PREFIX}review_transcript"
SOLUTION_INTENT_WIDGET_KEY = f"{STATE_PREFIX}input_solution_intent"
TRANSCRIPT_WIDGET_KEY = f"{STATE_PREFIX}input_review_transcript"
CONTEXT_KEY = f"{STATE_PREFIX}review_context"
TRANSCRIPT_BASELINE_FINGERPRINT_KEY = f"{STATE_PREFIX}transcript_baseline_fingerprint"
TRANSCRIPT_PROVENANCE_KEY = f"{STATE_PREFIX}transcript_provenance"
METADATA_BASELINE_FINGERPRINT_KEY = f"{STATE_PREFIX}metadata_baseline_fingerprint"
METADATA_PROVENANCE_KEY = f"{STATE_PREFIX}metadata_provenance"
REVIEW_INPUT_MANIFEST_KEY = f"{STATE_PREFIX}review_input_manifest"
REVIEW_INPUT_CONFIRMATION_KEY = f"{STATE_PREFIX}review_input_confirmation"
REVIEW_INPUT_FEEDBACK_KEY = f"{STATE_PREFIX}review_input_feedback"
METADATA_REVIEW_ROUND_WIDGET_KEY = f"{STATE_PREFIX}metadata_review_round"
METADATA_REVIEW_DATE_WIDGET_KEY = f"{STATE_PREFIX}metadata_review_date"
METADATA_ARCHITECT_WIDGET_KEY = f"{STATE_PREFIX}metadata_domain_architect"
METADATA_TICKET_WIDGET_KEY = f"{STATE_PREFIX}metadata_ticket"
ANALYZED_RESULT_KEY = f"{STATE_PREFIX}analyzed_result"
REVIEW_DRAFT_KEY = f"{STATE_PREFIX}review_draft"
REVIEW_WIDGET_VALUES_KEY = f"{STATE_PREFIX}review_widget_values"
REVIEWED_RESULT_KEY = f"{STATE_PREFIX}reviewed_result"
REVIEW_CHANGE_SUMMARY_KEY = f"{STATE_PREFIX}review_change_summary"
OUTPUTS_KEY = f"{STATE_PREFIX}generated_outputs"
ANALYZED_FINGERPRINT_KEY = f"{STATE_PREFIX}analyzed_fingerprint"
ANALYSIS_INVALIDATION_KEY = f"{STATE_PREFIX}analysis_invalidation"
ERROR_KEY = f"{STATE_PREFIX}error"
LOADED_KEY = f"{STATE_PREFIX}sample_loaded"
ANALYSIS_SUCCESS_KEY = f"{STATE_PREFIX}analysis_success"
OUTPUT_SUCCESS_KEY = f"{STATE_PREFIX}output_success"
DELIVERY_ACTION_SELECTION_KEY = f"{STATE_PREFIX}delivery_action_selection"
DELIVERY_ACTION_WIDGET_KEY = f"{STATE_PREFIX}delivery_action_widget"
DELIVERY_ORIGINAL_INDICES_KEY = f"{STATE_PREFIX}delivery_original_indices"
OUTPUT_ACTION_SELECTION_KEY = f"{STATE_PREFIX}output_action_selection"
ADO_PUBLICATION_PREVIEW_KEY = f"{STATE_PREFIX}ado_publication_preview"
ADO_PUBLICATION_CONFIRMATION_KEY = f"{STATE_PREFIX}ado_publication_confirmation"
ADO_PUBLICATION_OPERATION_KEY = f"{STATE_PREFIX}ado_publication_operation"
ADO_PUBLICATION_HISTORY_KEY = f"{STATE_PREFIX}ado_publication_history"
ADO_FAKE_GATEWAY_KEY = f"{STATE_PREFIX}ado_fake_gateway"
REVIEW_MODE_KEY = f"{STATE_PREFIX}review_mode"
REVIEW_MODE_WIDGET_KEY = f"{STATE_PREFIX}review_mode_widget"
REVIEW_PROVIDER_CONFIGURATION_ID_KEY = f"{STATE_PREFIX}review_provider_configuration_id"
CONFLUENCE_SNAPSHOT_KEY = f"{STATE_PREFIX}confluence_snapshot"
ACTIVE_STAGE_KEY = f"{STATE_PREFIX}active_stage"
ROUTE_SOURCE_STAGE_KEY = f"{STATE_PREFIX}route_source_stage"

HOME_STAGE = "home"
CONTEXT_STAGE = "context"
DRAFT_STAGE = "drafting"
INPUT_STAGE = "inputs"
REVIEW_STAGE = "review"
OUTPUT_STAGE = "outputs"
DELIVERY_STAGE = "delivery"
VALID_STAGES = frozenset(
    {
        HOME_STAGE,
        CONTEXT_STAGE,
        DRAFT_STAGE,
        INPUT_STAGE,
        REVIEW_STAGE,
        OUTPUT_STAGE,
        DELIVERY_STAGE,
    }
)


class Workflow(StrEnum):
    """Independent user tasks available from the application landing page."""

    NONE = "none"
    DRAFT = "draft"
    REVIEW = "review"


class InputReadiness(StrEnum):
    """Visible lifecycle states for one review-input component."""

    MISSING = "Missing"
    LOADED = "Loaded"
    EDITED = "Edited"
    INVALID = "Invalid"
    CONFIRMED = "Confirmed"


_REVIEW_FIELD_LABELS = {
    "statement": "Statement",
    "rationale": "Rationale",
    "title": "Title",
    "description": "Description",
    "category": "Category",
    "si_section": "SI section",
    "severity": "Severity",
    "status": "Status",
    "recommended_change": "Recommended change",
    "owner": "Owner",
    "due_date": "Due date",
    "priority": "Priority",
    "question": "Question",
    "item": "Item",
    "reason": "Reason",
}


@dataclass(frozen=True, slots=True)
class DraftingSamplePaths:
    """Absolute paths for bundled deterministic SI-drafting inputs."""

    template: Path
    source_code_context: Path
    supporting_documents: Path


@dataclass(frozen=True, slots=True)
class SamplePaths:
    """Absolute paths for the bundled deterministic review inputs."""

    solution_intent: Path
    transcript: Path
    metadata: Path


@dataclass(frozen=True, slots=True)
class SampleReview:
    """Loaded and validated bundled review inputs."""

    solution_intent: str
    transcript: str
    context: SolutionIntentReviewContext


@dataclass(frozen=True, slots=True)
class ReviewFormData:
    """Submitted editable fields for one reviewed governance result."""

    review_outcome: str
    decisions: tuple[Mapping[str, object], ...]
    findings: tuple[Mapping[str, object], ...]
    risks: tuple[Mapping[str, object], ...]
    action_items: tuple[Mapping[str, object], ...]
    open_questions: tuple[Mapping[str, object], ...]
    missing_evidence: tuple[Mapping[str, object], ...]


@dataclass(frozen=True, slots=True)
class ReviewFieldChange:
    """One normalized field change confirmed during human review."""

    collection: str
    item_index: int | None
    item_name: str
    field: str
    before: str | None
    after: str | None


@dataclass(frozen=True, slots=True)
class ReviewExcludedItem:
    """One analyzed item excluded during human review."""

    collection: str
    item_index: int
    item_name: str


@dataclass(frozen=True, slots=True)
class ReviewChangeSummary:
    """Normalized differences between provider analysis and human confirmation."""

    field_changes: tuple[ReviewFieldChange, ...]
    excluded_items: tuple[ReviewExcludedItem, ...]

    @property
    def has_changes(self) -> bool:
        """Return whether the reviewer changed or excluded anything."""
        return bool(self.field_changes or self.excluded_items)


@dataclass(frozen=True, slots=True)
class ReviewValidationIssue:
    """One invalid value in the unconfirmed Human Review form."""

    collection: str
    item_index: int | None
    item_name: str
    field: str
    message: str


@dataclass(frozen=True, slots=True)
class PendingReviewChanges:
    """Tolerant session-local differences from the analyzed proposal."""

    field_changes: tuple[ReviewFieldChange, ...]
    excluded_items: tuple[ReviewExcludedItem, ...]
    validation_issues: tuple[ReviewValidationIssue, ...]

    @property
    def has_changes(self) -> bool:
        """Return whether any unconfirmed edit or exclusion exists."""
        return bool(self.field_changes or self.excluded_items)

    @property
    def affected_collections(self) -> tuple[str, ...]:
        """Return affected display collections in stable encounter order."""
        values: list[str] = []
        for item in (*self.field_changes, *self.excluded_items, *self.validation_issues):
            if item.collection not in values:
                values.append(item.collection)
        return tuple(values)

    def pending_item_count(self, collection: str) -> int:
        """Count distinct affected items in one review collection."""
        positions = {
            item.item_index
            for item in (*self.field_changes, *self.excluded_items, *self.validation_issues)
            if item.collection == collection and item.item_index is not None
        }
        return len(positions)

    def item_state(self, collection: str, item_index: int) -> tuple[int, bool, int]:
        """Return modified-field, excluded, and invalid-field counts for one item."""
        modified = sum(
            item.collection == collection and item.item_index == item_index
            for item in self.field_changes
        )
        excluded = any(
            item.collection == collection and item.item_index == item_index
            for item in self.excluded_items
        )
        invalid = sum(
            item.collection == collection and item.item_index == item_index
            for item in self.validation_issues
        )
        return modified, excluded, invalid


@dataclass(frozen=True, slots=True)
class AnalysisInvalidation:
    """Reason an earlier analysis can no longer be confirmed or published."""

    reason: str
    outputs_invalidated: bool


@dataclass(frozen=True, slots=True)
class ReviewInputReadiness:
    """Component and overall readiness for the governance-review package."""

    solution_intent: InputReadiness
    transcript: InputReadiness
    metadata: InputReadiness
    confirmed: bool
    blockers: tuple[str, ...]

    @property
    def ready_to_confirm(self) -> bool:
        """Return whether every component is valid before confirmation."""
        return not self.blockers

    @property
    def ready_to_analyze(self) -> bool:
        """Return whether the exact complete manifest is confirmed."""
        return self.ready_to_confirm and self.confirmed


def drafting_sample_paths() -> DraftingSamplePaths:
    """Resolve bundled SI-drafting paths independently of the working directory."""
    samples_dir = Path(__file__).resolve().parents[2] / "samples"
    return DraftingSamplePaths(
        template=samples_dir / "si_template.md",
        source_code_context=samples_dir / "source_context.txt",
        supporting_documents=samples_dir / "supporting_context.md",
    )


def load_sample_drafting_context() -> DraftingSourceInventory:
    """Load and validate the authorized synthetic drafting inventory."""
    paths = drafting_sample_paths()
    template = _read_drafting_source(paths.template, "SI template")
    source_code_context = _read_drafting_source(paths.source_code_context, "source-code context")
    supporting_documents = _read_drafting_source(
        paths.supporting_documents, "supporting-document context"
    )
    resources = (
        _drafting_source_resource(
            resource_id="si-template-v1-1",
            role=DraftingSourceRole.TEMPLATE,
            display_name="Governed Solution Intent template",
            source_reference="synthetic://confluence/templates/solution-intent",
            revision_kind=DraftingRevisionKind.VERSION,
            revision="v1.1",
            content=template,
        ),
        _drafting_source_resource(
            resource_id="payment-notification-repository-main",
            role=DraftingSourceRole.REPOSITORY,
            display_name="55390-19-payment-notification-service",
            source_reference="synthetic://source/architecture-governance/payment-notification-service",
            revision_kind=DraftingRevisionKind.BRANCH,
            revision="main",
            content=source_code_context,
        ),
        _drafting_source_resource(
            resource_id="supporting-context-v1",
            role=DraftingSourceRole.SUPPORTING_EVIDENCE,
            display_name="Supporting context package",
            source_reference="synthetic://evidence/payment-notification/supporting-context",
            revision_kind=DraftingRevisionKind.VERSION,
            revision="v1",
            content=supporting_documents,
        ),
    )
    return DraftingSourceInventory(
        project_id="digital-payment-notification-service",
        project_name="Digital Payment Notification Service",
        governance_reference="ADO Workitem - Solution Intent 12658902",
        provider_configuration_identity=DETERMINISTIC_DRAFTING_PROVIDER_CONFIGURATION_ID,
        resources=resources,
    )


def _drafting_source_resource(
    *,
    resource_id: str,
    role: DraftingSourceRole,
    display_name: str,
    source_reference: str,
    revision_kind: DraftingRevisionKind,
    revision: str,
    content: str,
) -> DraftingSourceResource:
    """Build one validated local resource with its exact content identity."""
    return DraftingSourceResource(
        resource_id=resource_id,
        role=role,
        display_name=display_name,
        source_reference=source_reference,
        revision_kind=revision_kind,
        revision=revision,
        content_fingerprint=hashlib.sha256(content.strip().encode("utf-8")).hexdigest(),
        validation_status=DraftingValidationStatus.VALIDATED,
        provenance=DraftingSourceProvenance.SYNTHETIC_LOCAL_FIXTURE,
        authorized=True,
        content=content,
    )


def _read_drafting_source(path: Path, label: str) -> str:
    """Read one bundled source with a user-safe deterministic failure."""
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"Bundled {label} is unavailable.") from exc
    if not content.strip():
        raise ValueError(f"Bundled {label} is empty.")
    return content


def sample_paths() -> SamplePaths:
    """Resolve bundled sample paths independently of the working directory."""
    samples_dir = Path(__file__).resolve().parents[2] / "samples"
    return SamplePaths(
        solution_intent=samples_dir / "solution_intent.md",
        transcript=samples_dir / "review_transcript.txt",
        metadata=samples_dir / "review_metadata.json",
    )


def load_sample_review() -> SampleReview:
    """Load and validate the bundled deterministic review inputs."""
    paths = sample_paths()
    solution_intent = paths.solution_intent.read_text(encoding="utf-8")
    transcript = paths.transcript.read_text(encoding="utf-8")
    context = SolutionIntentReviewContext.model_validate_json(
        paths.metadata.read_text(encoding="utf-8")
    )
    if not solution_intent.strip():
        raise ValueError("Bundled Solution Intent is empty.")
    if not transcript.strip():
        raise ValueError("Bundled review transcript is empty.")
    return SampleReview(
        solution_intent=solution_intent,
        transcript=transcript,
        context=context,
    )


def build_sample_review_snapshot(sample: SampleReview) -> ConfluencePageSnapshot:
    """Build the authoritative no-network SI snapshot for the Offline review."""
    return build_confluence_snapshot(
        ConfluencePagePayload(
            page_id="synthetic-page-12658902",
            title=sample.context.si_title,
            space="SYNTHETIC-ARCH",
            version=12,
            url="https://example.invalid/confluence/pages/synthetic-page-12658902",
            raw_body=sample.solution_intent,
            body_format=ConfluenceBodyFormat.MARKDOWN.value,
        ),
        retrieved_at=datetime(2026, 7, 18, 9, 0, tzinfo=UTC),
    )


def initial_state_values() -> dict[str, object]:
    """Return independent initial values for application-owned session state."""
    return {
        STATE_SCHEMA_VERSION_KEY: STATE_SCHEMA_VERSION,
        ACTIVE_WORKFLOW_KEY: Workflow.NONE.value,
        PROJECT_CONTEXT_KEY: None,
        PROJECT_CONTEXT_CONFIRMED_KEY: False,
        PROJECT_CONTEXT_REFRESHED_KEY: False,
        CONTEXT_TEMPLATE_ID_KEY: None,
        CONTEXT_REPOSITORY_ID_KEY: None,
        CONTEXT_EVIDENCE_IDS_KEY: (),
        LIVE_SOURCE_PACKAGE_KEY: None,
        CONFIRMED_SOURCE_PACKAGE_KEY: None,
        CONFIRMED_SOURCE_PACKAGE_FINGERPRINT_KEY: None,
        DRAFT_PROJECT_KEY: "",
        DRAFT_TEMPLATE_KEY: "",
        DRAFT_SOURCE_CODE_KEY: "",
        DRAFT_SUPPORTING_DOCS_KEY: "",
        DRAFT_RESULT_KEY: None,
        DRAFT_FINGERPRINT_KEY: None,
        DRAFT_CONFIRMED_KEY: False,
        SOLUTION_INTENT_KEY: "",
        TRANSCRIPT_KEY: "",
        CONTEXT_KEY: None,
        TRANSCRIPT_BASELINE_FINGERPRINT_KEY: None,
        TRANSCRIPT_PROVENANCE_KEY: None,
        METADATA_BASELINE_FINGERPRINT_KEY: None,
        METADATA_PROVENANCE_KEY: None,
        REVIEW_INPUT_MANIFEST_KEY: None,
        REVIEW_INPUT_CONFIRMATION_KEY: None,
        REVIEW_INPUT_FEEDBACK_KEY: None,
        ANALYZED_RESULT_KEY: None,
        REVIEW_DRAFT_KEY: None,
        REVIEW_WIDGET_VALUES_KEY: {},
        REVIEWED_RESULT_KEY: None,
        REVIEW_CHANGE_SUMMARY_KEY: None,
        OUTPUTS_KEY: None,
        ANALYZED_FINGERPRINT_KEY: None,
        ANALYSIS_INVALIDATION_KEY: None,
        ERROR_KEY: None,
        LOADED_KEY: False,
        ANALYSIS_SUCCESS_KEY: False,
        OUTPUT_SUCCESS_KEY: False,
        OUTPUT_ACTION_SELECTION_KEY: None,
        DELIVERY_ACTION_SELECTION_KEY: None,
        DELIVERY_ORIGINAL_INDICES_KEY: (),
        ADO_PUBLICATION_PREVIEW_KEY: None,
        ADO_PUBLICATION_CONFIRMATION_KEY: None,
        ADO_PUBLICATION_OPERATION_KEY: None,
        ADO_PUBLICATION_HISTORY_KEY: {},
        ADO_FAKE_GATEWAY_KEY: None,
        REVIEW_MODE_KEY: ReviewMode.OFFLINE.value,
        REVIEW_PROVIDER_CONFIGURATION_ID_KEY: OFFLINE_PROVIDER_CONFIGURATION_ID,
        CONFLUENCE_SNAPSHOT_KEY: None,
        ACTIVE_STAGE_KEY: HOME_STAGE,
        ROUTE_SOURCE_STAGE_KEY: None,
    }


def initialize_session_state(state: MutableMapping[str, Any]) -> None:
    """Initialize state and safely retire the obsolete monolithic workflow schema."""
    existing_schema = state.get(STATE_SCHEMA_VERSION_KEY)
    has_application_state = any(key.startswith(STATE_PREFIX) for key in state)
    if has_application_state and existing_schema != STATE_SCHEMA_VERSION:
        publication_history = state.get(ADO_PUBLICATION_HISTORY_KEY)
        retained_history = (
            dict(publication_history) if isinstance(publication_history, Mapping) else {}
        )
        retained_operation = state.get(ADO_PUBLICATION_OPERATION_KEY)
        if isinstance(retained_operation, AdoPublicationOperation):
            retained_history.setdefault(retained_operation.correlation_id, retained_operation)
        retained_gateway = state.get(ADO_FAKE_GATEWAY_KEY)
        for key in tuple(state):
            if key.startswith(STATE_PREFIX):
                del state[key]
        state.update(initial_state_values())
        state[ADO_PUBLICATION_HISTORY_KEY] = retained_history
        if isinstance(retained_operation, AdoPublicationOperation):
            state[ADO_PUBLICATION_OPERATION_KEY] = retained_operation
        if retained_gateway is not None:
            state[ADO_FAKE_GATEWAY_KEY] = retained_gateway
        return
    for key, value in initial_state_values().items():
        state.setdefault(key, value)


def current_workflow(state: Mapping[str, Any]) -> Workflow:
    """Return the active peer workflow without inferring it from provider mode."""
    value = state.get(ACTIVE_WORKFLOW_KEY)
    try:
        return Workflow(value)
    except (TypeError, ValueError):
        return Workflow.NONE


def start_workflow(state: MutableMapping[str, Any], workflow: Workflow) -> None:
    """Open one workflow while retaining the other workflow's local state."""
    state[ERROR_KEY] = None
    if workflow is Workflow.NONE:
        state[ACTIVE_WORKFLOW_KEY] = Workflow.NONE.value
        state[ACTIVE_STAGE_KEY] = HOME_STAGE
        return
    state[ACTIVE_WORKFLOW_KEY] = workflow.value
    if workflow is Workflow.DRAFT:
        state[ACTIVE_STAGE_KEY] = (
            DRAFT_STAGE if state.get(PROJECT_CONTEXT_CONFIRMED_KEY) is True else CONTEXT_STAGE
        )
    else:
        stage = active_stage(state)
        state[ACTIVE_STAGE_KEY] = (
            stage
            if stage in {INPUT_STAGE, REVIEW_STAGE, OUTPUT_STAGE, DELIVERY_STAGE}
            else INPUT_STAGE
        )


def reset_drafting_workflow(state: MutableMapping[str, Any]) -> None:
    """Clear only drafting inputs and outputs, then return to drafting entry."""
    for key in tuple(state):
        if key.startswith("agc_evidence_") or key in {
            DRAFT_EVIDENCE_KEY,
            DRAFT_REPOSITORY_NAME_KEY,
        }:
            state.pop(key, None)
    defaults = initial_state_values()
    drafting_keys = (
        PROJECT_CONTEXT_KEY,
        PROJECT_CONTEXT_CONFIRMED_KEY,
        PROJECT_CONTEXT_REFRESHED_KEY,
        CONTEXT_TEMPLATE_ID_KEY,
        CONTEXT_REPOSITORY_ID_KEY,
        CONTEXT_EVIDENCE_IDS_KEY,
        LIVE_SOURCE_PACKAGE_KEY,
        CONFIRMED_SOURCE_PACKAGE_KEY,
        CONFIRMED_SOURCE_PACKAGE_FINGERPRINT_KEY,
        DRAFT_PROJECT_KEY,
        DRAFT_TEMPLATE_KEY,
        DRAFT_SOURCE_CODE_KEY,
        DRAFT_SUPPORTING_DOCS_KEY,
        DRAFT_RESULT_KEY,
        DRAFT_FINGERPRINT_KEY,
        DRAFT_CONFIRMED_KEY,
    )
    for key in drafting_keys:
        state[key] = defaults[key]
    for key in (
        "agc_context_repository_name_widget",
        CONTEXT_TEMPLATE_WIDGET_KEY,
        CONTEXT_REPOSITORY_WIDGET_KEY,
        CONTEXT_EVIDENCE_WIDGET_KEY,
        DRAFT_PROJECT_WIDGET_KEY,
        DRAFT_TEMPLATE_WIDGET_KEY,
        DRAFT_SOURCE_CODE_WIDGET_KEY,
        DRAFT_SUPPORTING_DOCS_WIDGET_KEY,
        DRAFT_CONTENT_WIDGET_KEY,
    ):
        state.pop(key, None)
    state[ACTIVE_WORKFLOW_KEY] = Workflow.DRAFT.value
    state[ACTIVE_STAGE_KEY] = CONTEXT_STAGE
    state[ERROR_KEY] = None


def reset_review_workflow(state: MutableMapping[str, Any]) -> None:
    """Clear review-local state while preserving drafting and reconciliation facts."""
    defaults = initial_state_values()
    review_keys = (
        SOLUTION_INTENT_KEY,
        TRANSCRIPT_KEY,
        CONTEXT_KEY,
        TRANSCRIPT_BASELINE_FINGERPRINT_KEY,
        TRANSCRIPT_PROVENANCE_KEY,
        METADATA_BASELINE_FINGERPRINT_KEY,
        METADATA_PROVENANCE_KEY,
        REVIEW_INPUT_MANIFEST_KEY,
        REVIEW_INPUT_CONFIRMATION_KEY,
        REVIEW_INPUT_FEEDBACK_KEY,
        ANALYZED_RESULT_KEY,
        REVIEW_DRAFT_KEY,
        REVIEW_WIDGET_VALUES_KEY,
        REVIEWED_RESULT_KEY,
        REVIEW_CHANGE_SUMMARY_KEY,
        OUTPUTS_KEY,
        ANALYZED_FINGERPRINT_KEY,
        ANALYSIS_INVALIDATION_KEY,
        ERROR_KEY,
        LOADED_KEY,
        ANALYSIS_SUCCESS_KEY,
        OUTPUT_SUCCESS_KEY,
        OUTPUT_ACTION_SELECTION_KEY,
        DELIVERY_ACTION_SELECTION_KEY,
        DELIVERY_ORIGINAL_INDICES_KEY,
        ADO_PUBLICATION_PREVIEW_KEY,
        ADO_PUBLICATION_CONFIRMATION_KEY,
        REVIEW_MODE_KEY,
        REVIEW_PROVIDER_CONFIGURATION_ID_KEY,
        CONFLUENCE_SNAPSHOT_KEY,
    )
    for key in review_keys:
        state[key] = defaults[key]
    for key in tuple(state):
        if key.startswith(REVIEW_WIDGET_PREFIX) or key in {
            SOLUTION_INTENT_WIDGET_KEY,
            TRANSCRIPT_WIDGET_KEY,
            REVIEW_MODE_WIDGET_KEY,
            METADATA_REVIEW_ROUND_WIDGET_KEY,
            METADATA_REVIEW_DATE_WIDGET_KEY,
            METADATA_ARCHITECT_WIDGET_KEY,
            METADATA_TICKET_WIDGET_KEY,
            DELIVERY_ACTION_WIDGET_KEY,
        }:
            del state[key]
    state[ACTIVE_WORKFLOW_KEY] = Workflow.REVIEW.value
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE


def clear_review_widget_state(state: MutableMapping[str, Any]) -> None:
    """Remove widget values belonging to a previous human-review form."""
    for key in tuple(state):
        if key.startswith(REVIEW_WIDGET_PREFIX):
            del state[key]
    state[REVIEW_WIDGET_VALUES_KEY] = {}


def preserve_review_widget_state(state: MutableMapping[str, Any]) -> None:
    """Copy human-review widget values into page-independent durable state."""
    stored = state.get(REVIEW_WIDGET_VALUES_KEY)
    values = dict(stored) if isinstance(stored, Mapping) else {}
    for key in tuple(state):
        if key.startswith(REVIEW_WIDGET_PREFIX):
            values[key] = state[key]
    state[REVIEW_WIDGET_VALUES_KEY] = values


def retain_drafting_source_widget_state(state: MutableMapping[str, Any]) -> None:
    """Retain routed source-widget values from durable source selections."""
    values = (
        ("agc_context_repository_name_widget", DRAFT_REPOSITORY_NAME_KEY),
        (CONTEXT_TEMPLATE_WIDGET_KEY, CONTEXT_TEMPLATE_ID_KEY),
        (CONTEXT_REPOSITORY_WIDGET_KEY, CONTEXT_REPOSITORY_ID_KEY),
        (CONTEXT_EVIDENCE_WIDGET_KEY, CONTEXT_EVIDENCE_IDS_KEY),
    )
    for widget_key, durable_key in values:
        value = state.get(durable_key)
        state[widget_key] = list(value) if isinstance(value, tuple) else value


def restore_review_widget_state(state: MutableMapping[str, Any]) -> None:
    """Restore durable human-review values before routed widgets are created."""
    stored = state.get(REVIEW_WIDGET_VALUES_KEY)
    if not isinstance(stored, Mapping):
        return
    for key, value in stored.items():
        if isinstance(key, str) and key.startswith(REVIEW_WIDGET_PREFIX):
            state.setdefault(key, value)


def retain_review_widget_state(state: MutableMapping[str, Any]) -> None:
    """Detach routed review widget values from Streamlit's page cleanup cycle."""
    stored = state.get(REVIEW_WIDGET_VALUES_KEY)
    if not isinstance(stored, Mapping):
        return
    for key, value in stored.items():
        if isinstance(key, str) and key.startswith(REVIEW_WIDGET_PREFIX):
            state[key] = value


def clear_analysis_state(state: MutableMapping[str, Any]) -> None:
    """Clear analysis and derived records without erasing an invalidation notice."""
    clear_review_widget_state(state)
    state[ANALYZED_RESULT_KEY] = None
    state[REVIEW_DRAFT_KEY] = None
    state[REVIEWED_RESULT_KEY] = None
    state[REVIEW_CHANGE_SUMMARY_KEY] = None
    state[OUTPUTS_KEY] = None
    state[OUTPUT_ACTION_SELECTION_KEY] = None
    state[DELIVERY_ACTION_SELECTION_KEY] = None
    state[DELIVERY_ORIGINAL_INDICES_KEY] = ()
    clear_publication_preview(state)
    state[ANALYZED_FINGERPRINT_KEY] = None
    state[ERROR_KEY] = None
    state[ANALYSIS_SUCCESS_KEY] = False
    state[OUTPUT_SUCCESS_KEY] = False
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE


def update_review_inputs(
    state: MutableMapping[str, Any],
    *,
    solution_intent: str,
    transcript: str,
    context: SolutionIntentReviewContext | None,
    reason: str = "Review inputs changed.",
) -> bool:
    """Store review inputs and invalidate derived state after a real change."""
    changed = (
        state.get(SOLUTION_INTENT_KEY) != solution_intent
        or state.get(TRANSCRIPT_KEY) != transcript
        or state.get(CONTEXT_KEY) != context
    )
    state[SOLUTION_INTENT_KEY] = solution_intent
    state[TRANSCRIPT_KEY] = transcript
    state[CONTEXT_KEY] = context
    if changed:
        state[REVIEW_INPUT_MANIFEST_KEY] = None
        state[REVIEW_INPUT_CONFIRMATION_KEY] = None
        invalidate_analysis_for_input_change(state, reason)
    return changed


def content_fingerprint(value: str) -> str:
    """Return a stable SHA-256 fingerprint for one exact text snapshot."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def metadata_fingerprint(context: SolutionIntentReviewContext) -> str:
    """Return a stable fingerprint for one validated review-metadata snapshot."""
    return content_fingerprint(context.model_dump_json())


def store_review_source_snapshot(
    state: MutableMapping[str, Any],
    snapshot: ConfluencePageSnapshot,
    *,
    feedback: str,
) -> None:
    """Store one read-only SI source without clearing independent review inputs."""
    state[CONFLUENCE_SNAPSHOT_KEY] = snapshot.model_copy(deep=True)
    transcript = state.get(TRANSCRIPT_KEY)
    context = state.get(CONTEXT_KEY)
    update_review_inputs(
        state,
        solution_intent=snapshot.canonical_text,
        transcript=transcript if isinstance(transcript, str) else "",
        context=context if isinstance(context, SolutionIntentReviewContext) else None,
        reason="The authoritative Solution Intent source changed.",
    )
    state[SOLUTION_INTENT_WIDGET_KEY] = snapshot.canonical_text
    state[REVIEW_INPUT_FEEDBACK_KEY] = feedback
    state[ERROR_KEY] = None
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE


def store_transcript_component(
    state: MutableMapping[str, Any],
    transcript: str,
    provenance: ReviewInputProvenance,
    *,
    establish_baseline: bool,
    sync_widget: bool = True,
    feedback: str | None = None,
) -> None:
    """Store an explicit transcript snapshot and its truthful session provenance."""
    normalized = transcript.strip()
    current_si = state.get(SOLUTION_INTENT_KEY)
    context = state.get(CONTEXT_KEY)
    update_review_inputs(
        state,
        solution_intent=current_si if isinstance(current_si, str) else "",
        transcript=normalized,
        context=context if isinstance(context, SolutionIntentReviewContext) else None,
        reason="The review transcript changed.",
    )
    state[TRANSCRIPT_PROVENANCE_KEY] = provenance.value
    if establish_baseline:
        state[TRANSCRIPT_BASELINE_FINGERPRINT_KEY] = (
            content_fingerprint(normalized) if normalized else None
        )
    if sync_widget:
        state[TRANSCRIPT_WIDGET_KEY] = normalized
    if feedback is not None:
        state[REVIEW_INPUT_FEEDBACK_KEY] = feedback
    state[ERROR_KEY] = None


def store_metadata_component(
    state: MutableMapping[str, Any],
    context: SolutionIntentReviewContext,
    provenance: ReviewInputProvenance,
    *,
    establish_baseline: bool,
    sync_widgets: bool = True,
    feedback: str | None = None,
) -> None:
    """Store validated review metadata independently of SI and transcript order."""
    current_si = state.get(SOLUTION_INTENT_KEY)
    transcript = state.get(TRANSCRIPT_KEY)
    update_review_inputs(
        state,
        solution_intent=current_si if isinstance(current_si, str) else "",
        transcript=transcript if isinstance(transcript, str) else "",
        context=context.model_copy(deep=True),
        reason="The review metadata changed.",
    )
    state[METADATA_PROVENANCE_KEY] = provenance.value
    if establish_baseline:
        state[METADATA_BASELINE_FINGERPRINT_KEY] = metadata_fingerprint(context)
    if sync_widgets:
        _set_metadata_widgets(state, context)
    if feedback is not None:
        state[REVIEW_INPUT_FEEDBACK_KEY] = feedback
    state[ERROR_KEY] = None


def current_review_input_manifest(state: Mapping[str, Any]) -> ReviewInputManifest:
    """Build the exact current review package or raise a concise readiness error."""
    snapshot = state.get(CONFLUENCE_SNAPSHOT_KEY)
    transcript = state.get(TRANSCRIPT_KEY)
    context = state.get(CONTEXT_KEY)
    provider_identity = state.get(REVIEW_PROVIDER_CONFIGURATION_ID_KEY)
    if not isinstance(snapshot, ConfluencePageSnapshot):
        raise ValueError("Load an authoritative Solution Intent snapshot.")
    if not isinstance(transcript, str) or not transcript.strip():
        raise ValueError("Provide a review transcript.")
    if not isinstance(context, SolutionIntentReviewContext):
        raise ValueError("Provide valid review metadata.")
    if not isinstance(provider_identity, str) or not provider_identity.strip():
        raise ValueError("Select a valid review provider configuration.")
    transcript_provenance = _review_input_provenance(
        state.get(TRANSCRIPT_PROVENANCE_KEY), "transcript"
    )
    metadata_provenance = _review_input_provenance(state.get(METADATA_PROVENANCE_KEY), "metadata")
    transcript_hash = content_fingerprint(transcript.strip())
    metadata_hash = metadata_fingerprint(context)
    return ReviewInputManifest(
        source_page_id=snapshot.page_id,
        source_space=snapshot.space,
        source_url=snapshot.url,
        source_version=snapshot.version,
        source_retrieved_at=snapshot.retrieved_at,
        source_canonicalizer_version=snapshot.canonicalizer_version,
        source_content_fingerprint=snapshot.content_fingerprint,
        transcript_fingerprint=transcript_hash,
        transcript_provenance=transcript_provenance,
        transcript_edited=(
            state.get(TRANSCRIPT_BASELINE_FINGERPRINT_KEY) not in {None, transcript_hash}
        ),
        metadata_fingerprint=metadata_hash,
        metadata_provenance=metadata_provenance,
        metadata_edited=(state.get(METADATA_BASELINE_FINGERPRINT_KEY) not in {None, metadata_hash}),
        review_mode=current_review_mode(state).value,
        provider_configuration_identity=provider_identity,
    )


def review_input_manifest_fingerprint(manifest: ReviewInputManifest) -> str:
    """Fingerprint every source, provenance, mode, and provider fact in a manifest."""
    return content_fingerprint(manifest.model_dump_json())


def review_input_readiness(state: Mapping[str, Any]) -> ReviewInputReadiness:
    """Return component states and actionable blockers for the current package."""
    snapshot = state.get(CONFLUENCE_SNAPSHOT_KEY)
    solution_intent = state.get(SOLUTION_INTENT_KEY)
    transcript = state.get(TRANSCRIPT_KEY)
    context = state.get(CONTEXT_KEY)
    blockers: list[str] = []

    if not isinstance(snapshot, ConfluencePageSnapshot):
        si_state = InputReadiness.MISSING
        blockers.append("Load an authoritative Solution Intent snapshot.")
    elif solution_intent != snapshot.canonical_text:
        si_state = InputReadiness.INVALID
        blockers.append("Reload the authoritative Solution Intent snapshot.")
    else:
        si_state = InputReadiness.LOADED

    if not isinstance(transcript, str) or not transcript.strip():
        transcript_state = InputReadiness.MISSING
        blockers.append("Provide a review transcript.")
    elif state.get(TRANSCRIPT_PROVENANCE_KEY) is None:
        transcript_state = InputReadiness.INVALID
        blockers.append("Confirm the transcript provenance.")
    elif state.get(TRANSCRIPT_BASELINE_FINGERPRINT_KEY) not in {
        None,
        content_fingerprint(transcript.strip()),
    }:
        transcript_state = InputReadiness.EDITED
    else:
        transcript_state = InputReadiness.LOADED

    if not isinstance(context, SolutionIntentReviewContext):
        metadata_state = InputReadiness.MISSING
        blockers.append("Provide valid review metadata.")
    elif state.get(METADATA_PROVENANCE_KEY) is None:
        metadata_state = InputReadiness.INVALID
        blockers.append("Confirm the review metadata provenance.")
    elif state.get(METADATA_BASELINE_FINGERPRINT_KEY) not in {
        None,
        metadata_fingerprint(context),
    }:
        metadata_state = InputReadiness.EDITED
    else:
        metadata_state = InputReadiness.LOADED

    confirmed = False
    try:
        manifest = current_review_input_manifest(state)
    except ValueError:
        pass
    else:
        confirmed = state.get(REVIEW_INPUT_CONFIRMATION_KEY) == (
            review_input_manifest_fingerprint(manifest)
        )
    if confirmed:
        si_state = InputReadiness.CONFIRMED
        transcript_state = InputReadiness.CONFIRMED
        metadata_state = InputReadiness.CONFIRMED

    return ReviewInputReadiness(
        solution_intent=si_state,
        transcript=transcript_state,
        metadata=metadata_state,
        confirmed=confirmed,
        blockers=tuple(blockers),
    )


def confirm_review_input_manifest(state: MutableMapping[str, Any]) -> ReviewInputManifest:
    """Freeze the exact valid review package before analysis is allowed."""
    manifest = current_review_input_manifest(state)
    state[REVIEW_INPUT_MANIFEST_KEY] = manifest.model_copy(deep=True)
    state[REVIEW_INPUT_CONFIRMATION_KEY] = review_input_manifest_fingerprint(manifest)
    state[REVIEW_INPUT_FEEDBACK_KEY] = (
        "Review input manifest confirmed. The exact package is ready for analysis."
    )
    state[ERROR_KEY] = None
    return manifest


def _review_input_provenance(value: object, label: str) -> ReviewInputProvenance:
    try:
        return ReviewInputProvenance(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"The {label} provenance is missing or invalid.") from exc


def _set_metadata_widgets(
    state: MutableMapping[str, Any], context: SolutionIntentReviewContext
) -> None:
    state[METADATA_REVIEW_ROUND_WIDGET_KEY] = context.review_round
    state[METADATA_REVIEW_DATE_WIDGET_KEY] = context.review_date
    state[METADATA_ARCHITECT_WIDGET_KEY] = context.domain_architect or ""
    state[METADATA_TICKET_WIDGET_KEY] = context.ado_ticket_id or ""


def invalidate_analysis_for_input_change(
    state: MutableMapping[str, Any],
    reason: str,
) -> AnalysisInvalidation | None:
    """Revoke confirmation eligibility while retaining why inputs became stale."""
    existing = state.get(ANALYSIS_INVALIDATION_KEY)
    analyzed_result = state.get(ANALYZED_RESULT_KEY)
    if not isinstance(existing, AnalysisInvalidation) and analyzed_result is None:
        return None

    had_outputs = any(
        state.get(key) is not None
        for key in (
            REVIEWED_RESULT_KEY,
            REVIEW_CHANGE_SUMMARY_KEY,
            OUTPUTS_KEY,
        )
    )
    if isinstance(existing, AnalysisInvalidation):
        reason = existing.reason
        had_outputs = had_outputs or existing.outputs_invalidated

    clear_review_widget_state(state)
    state[REVIEWED_RESULT_KEY] = None
    state[REVIEW_CHANGE_SUMMARY_KEY] = None
    state[OUTPUTS_KEY] = None
    state[OUTPUT_ACTION_SELECTION_KEY] = None
    state[DELIVERY_ACTION_SELECTION_KEY] = None
    state[DELIVERY_ORIGINAL_INDICES_KEY] = ()
    clear_publication_preview(state)
    state[ANALYSIS_SUCCESS_KEY] = False
    state[OUTPUT_SUCCESS_KEY] = False
    invalidation = AnalysisInvalidation(
        reason=reason.strip() or "Review inputs changed.",
        outputs_invalidated=had_outputs,
    )
    state[ANALYSIS_INVALIDATION_KEY] = invalidation
    return invalidation


def current_analysis_invalidation(
    state: MutableMapping[str, Any],
) -> AnalysisInvalidation | None:
    """Return or derive the invalidation state for the current review inputs."""
    existing = state.get(ANALYSIS_INVALIDATION_KEY)
    if isinstance(existing, AnalysisInvalidation):
        return existing

    analyzed_result = state.get(ANALYZED_RESULT_KEY)
    if not isinstance(analyzed_result, GovernanceResult):
        return None
    fingerprint = state.get(ANALYZED_FINGERPRINT_KEY)
    if not isinstance(fingerprint, str):
        return invalidate_analysis_for_input_change(state, "Analysis state is incomplete.")
    try:
        manifest = current_review_input_manifest(state)
    except ValueError:
        return invalidate_analysis_for_input_change(state, "Review inputs changed.")
    current_fingerprint = review_input_manifest_fingerprint(manifest)
    if (
        state.get(REVIEW_INPUT_CONFIRMATION_KEY) != current_fingerprint
        or fingerprint != current_fingerprint
    ):
        return invalidate_analysis_for_input_change(state, "Review inputs changed.")
    return None


def prepare_analysis_attempt(state: MutableMapping[str, Any]) -> None:
    """Clear derived confirmation state without clearing an invalidation marker."""
    clear_review_widget_state(state)
    state[REVIEWED_RESULT_KEY] = None
    state[REVIEW_CHANGE_SUMMARY_KEY] = None
    state[OUTPUTS_KEY] = None
    state[OUTPUT_ACTION_SELECTION_KEY] = None
    state[DELIVERY_ACTION_SELECTION_KEY] = None
    state[DELIVERY_ORIGINAL_INDICES_KEY] = ()
    clear_publication_preview(state)
    state[ERROR_KEY] = None
    state[ANALYSIS_SUCCESS_KEY] = False
    state[OUTPUT_SUCCESS_KEY] = False
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE


def load_sample_into_state(
    state: MutableMapping[str, Any],
    sample: SampleReview,
) -> None:
    """Populate all Offline components without implicitly confirming the manifest."""
    state[REVIEW_MODE_KEY] = ReviewMode.OFFLINE.value
    state[REVIEW_PROVIDER_CONFIGURATION_ID_KEY] = OFFLINE_PROVIDER_CONFIGURATION_ID
    store_review_source_snapshot(
        state,
        build_sample_review_snapshot(sample),
        feedback="Authoritative synthetic SI snapshot loaded; transcript and metadata followed.",
    )
    store_transcript_component(
        state,
        sample.transcript,
        ReviewInputProvenance.SYNTHETIC_SAMPLE,
        establish_baseline=True,
    )
    store_metadata_component(
        state,
        sample.context,
        ReviewInputProvenance.SYNTHETIC_SAMPLE,
        establish_baseline=True,
    )
    state[REVIEW_INPUT_FEEDBACK_KEY] = (
        "Complete synthetic review package loaded. Confirm the exact manifest before analysis."
    )
    state[LOADED_KEY] = True
    state[ERROR_KEY] = None
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE


def current_review_mode(state: Mapping[str, Any]) -> ReviewMode:
    """Return the current supported review mode, defaulting safely to offline."""
    value = state.get(REVIEW_MODE_KEY)
    try:
        return ReviewMode(value)
    except (TypeError, ValueError):
        return ReviewMode.OFFLINE


def switch_review_mode(
    state: MutableMapping[str, Any],
    mode: ReviewMode,
    provider_configuration_identity: str,
) -> bool:
    """Switch source/provider identity and revoke eligibility from the old mode."""
    normalized_identity = provider_configuration_identity.strip()
    if not normalized_identity:
        raise ValueError("A provider configuration identity is required.")
    changed = (
        current_review_mode(state) is not mode
        or state.get(REVIEW_PROVIDER_CONFIGURATION_ID_KEY) != normalized_identity
    )
    if not changed:
        return False
    state[REVIEW_MODE_KEY] = mode.value
    state[REVIEW_PROVIDER_CONFIGURATION_ID_KEY] = normalized_identity
    transcript_provenance = state.get(TRANSCRIPT_PROVENANCE_KEY)
    metadata_provenance = state.get(METADATA_PROVENANCE_KEY)
    preserve_transcript = transcript_provenance == ReviewInputProvenance.USER_ENTERED.value
    preserve_metadata = metadata_provenance == ReviewInputProvenance.USER_ENTERED.value
    existing_transcript = state.get(TRANSCRIPT_KEY)
    existing_context = state.get(CONTEXT_KEY)
    state[CONFLUENCE_SNAPSHOT_KEY] = None
    update_review_inputs(
        state,
        solution_intent="",
        transcript=(
            existing_transcript
            if preserve_transcript and isinstance(existing_transcript, str)
            else ""
        ),
        context=(
            existing_context
            if preserve_metadata and isinstance(existing_context, SolutionIntentReviewContext)
            else None
        ),
        reason="The review source or analysis provider changed.",
    )
    state[SOLUTION_INTENT_WIDGET_KEY] = ""
    if not preserve_transcript:
        state[TRANSCRIPT_WIDGET_KEY] = ""
        state[TRANSCRIPT_BASELINE_FINGERPRINT_KEY] = None
        state[TRANSCRIPT_PROVENANCE_KEY] = None
    if not preserve_metadata:
        state[METADATA_BASELINE_FINGERPRINT_KEY] = None
        state[METADATA_PROVENANCE_KEY] = None
    state[LOADED_KEY] = False
    state[REVIEW_INPUT_MANIFEST_KEY] = None
    state[REVIEW_INPUT_CONFIRMATION_KEY] = None
    state[REVIEW_INPUT_FEEDBACK_KEY] = (
        "Review mode changed. Load an authoritative SI snapshot for the selected mode."
    )
    state[ERROR_KEY] = None
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE
    return True


def load_internal_review_into_state(
    state: MutableMapping[str, Any],
    *,
    snapshot: ConfluencePageSnapshot,
    transcript: str,
    context: SolutionIntentReviewContext,
    provider_configuration_identity: str,
) -> None:
    """Load one fake internal source package without bundled review companions."""
    if current_review_mode(state) is not ReviewMode.INTERNAL_FAKE:
        raise ValueError("Internal review sources require Internal fake mode.")
    normalized_transcript = transcript.strip()
    if not normalized_transcript:
        raise ValueError("The internal review transcript must not be blank.")
    normalized_provider_identity = provider_configuration_identity.strip()
    if not normalized_provider_identity:
        raise ValueError("A provider configuration identity is required.")
    previous_snapshot = state.get(CONFLUENCE_SNAPSHOT_KEY)
    state[REVIEW_PROVIDER_CONFIGURATION_ID_KEY] = normalized_provider_identity
    store_review_source_snapshot(
        state,
        snapshot,
        feedback="Fake Confluence SI snapshot loaded; synthetic companions followed.",
    )
    store_transcript_component(
        state,
        normalized_transcript,
        ReviewInputProvenance.INTERNAL_FAKE,
        establish_baseline=True,
    )
    store_metadata_component(
        state,
        context,
        ReviewInputProvenance.INTERNAL_FAKE,
        establish_baseline=True,
    )
    if isinstance(previous_snapshot, ConfluencePageSnapshot) and _source_snapshot_identity(
        previous_snapshot
    ) != _source_snapshot_identity(snapshot):
        invalidate_analysis_for_input_change(state, "The Confluence source snapshot changed.")
    state[REVIEW_INPUT_FEEDBACK_KEY] = (
        "Complete Internal fake package loaded. Confirm the exact manifest before analysis."
    )
    state[LOADED_KEY] = True
    state[ERROR_KEY] = None
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE


def record_internal_source_load_failure(state: MutableMapping[str, Any]) -> None:
    """Clear an unusable source so prior eligibility cannot survive a load failure."""
    state[CONFLUENCE_SNAPSHOT_KEY] = None
    existing_transcript = state.get(TRANSCRIPT_KEY)
    existing_context = state.get(CONTEXT_KEY)
    transcript = existing_transcript if isinstance(existing_transcript, str) else ""
    update_review_inputs(
        state,
        solution_intent="",
        transcript=transcript,
        context=(
            existing_context if isinstance(existing_context, SolutionIntentReviewContext) else None
        ),
        reason="The internal source could not be loaded.",
    )
    state[SOLUTION_INTENT_WIDGET_KEY] = ""
    state[LOADED_KEY] = False
    state[REVIEW_INPUT_FEEDBACK_KEY] = (
        "The fake Confluence SI could not be loaded; independent transcript and metadata remain."
    )
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE


def load_drafting_context_into_state(
    state: MutableMapping[str, Any],
    inventory: DraftingSourceInventory,
    manifest: DraftingSourcePackageManifest | None = None,
) -> None:
    """Populate synthetic drafting context and clear a previous draft result."""
    selected_manifest = manifest or default_drafting_source_package(inventory)
    resources = {resource.resource_id: resource for resource in inventory.resources}
    selected = [resources[item.resource_id] for item in selected_manifest.resources]
    template = _single_selected_resource(selected, DraftingSourceRole.TEMPLATE)
    repository = _single_selected_resource(selected, DraftingSourceRole.REPOSITORY)
    evidence = sorted(
        (
            resource
            for resource in selected
            if resource.role is DraftingSourceRole.SUPPORTING_EVIDENCE
        ),
        key=lambda resource: resource.resource_id,
    )
    supporting_documents = "\n\n".join(resource.content for resource in evidence)
    state[PROJECT_CONTEXT_KEY] = inventory
    state[PROJECT_CONTEXT_CONFIRMED_KEY] = True
    state[LIVE_SOURCE_PACKAGE_KEY] = selected_manifest
    state[CONFIRMED_SOURCE_PACKAGE_KEY] = selected_manifest.model_copy(deep=True)
    state[CONFIRMED_SOURCE_PACKAGE_FINGERPRINT_KEY] = source_package_fingerprint(selected_manifest)
    state[DRAFT_PROJECT_KEY] = inventory.project_name
    state[DRAFT_TEMPLATE_KEY] = template.content
    state[DRAFT_SOURCE_CODE_KEY] = repository.content
    state[DRAFT_SUPPORTING_DOCS_KEY] = supporting_documents
    state[DRAFT_PROJECT_WIDGET_KEY] = inventory.project_name
    state[DRAFT_TEMPLATE_WIDGET_KEY] = template.content
    state[DRAFT_SOURCE_CODE_WIDGET_KEY] = repository.content
    state[DRAFT_SUPPORTING_DOCS_WIDGET_KEY] = supporting_documents
    state[DRAFT_CONTENT_WIDGET_KEY] = ""
    state[DRAFT_RESULT_KEY] = None
    state[DRAFT_FINGERPRINT_KEY] = None
    state[DRAFT_CONFIRMED_KEY] = False
    state[ERROR_KEY] = None
    state[ACTIVE_STAGE_KEY] = DRAFT_STAGE


def open_demonstration_project_into_state(
    state: MutableMapping[str, Any],
    inventory: DraftingSourceInventory,
) -> None:
    """Open the synthetic workspace without pretending to connect externally."""
    state[PROJECT_CONTEXT_KEY] = inventory
    state[PROJECT_CONTEXT_CONFIRMED_KEY] = False
    state[PROJECT_CONTEXT_REFRESHED_KEY] = False
    state[CONTEXT_TEMPLATE_ID_KEY] = _resource_ids_for_role(inventory, DraftingSourceRole.TEMPLATE)[
        0
    ]
    state[CONTEXT_REPOSITORY_ID_KEY] = _resource_ids_for_role(
        inventory, DraftingSourceRole.REPOSITORY
    )[0]
    state[CONTEXT_EVIDENCE_IDS_KEY] = _resource_ids_for_role(
        inventory, DraftingSourceRole.SUPPORTING_EVIDENCE
    )
    state[CONTEXT_TEMPLATE_WIDGET_KEY] = state[CONTEXT_TEMPLATE_ID_KEY]
    state[CONTEXT_REPOSITORY_WIDGET_KEY] = state[CONTEXT_REPOSITORY_ID_KEY]
    state[CONTEXT_EVIDENCE_WIDGET_KEY] = list(state[CONTEXT_EVIDENCE_IDS_KEY])
    state[LIVE_SOURCE_PACKAGE_KEY] = default_drafting_source_package(inventory)
    state[CONFIRMED_SOURCE_PACKAGE_KEY] = None
    state[CONFIRMED_SOURCE_PACKAGE_FINGERPRINT_KEY] = None
    state[DRAFT_PROJECT_KEY] = ""
    state[DRAFT_TEMPLATE_KEY] = ""
    state[DRAFT_SOURCE_CODE_KEY] = ""
    state[DRAFT_SUPPORTING_DOCS_KEY] = ""
    state[DRAFT_RESULT_KEY] = None
    state[DRAFT_FINGERPRINT_KEY] = None
    state[DRAFT_CONFIRMED_KEY] = False
    state[LOADED_KEY] = False
    state[ERROR_KEY] = None
    state[ACTIVE_STAGE_KEY] = CONTEXT_STAGE


def project_context_readiness(
    state: Mapping[str, Any], *, check_provider: bool = False
) -> tuple[str, ...]:
    """Return concise blockers for the currently selected drafting sources."""
    try:
        inventory = drafting_inventory_with_evidence(state)
    except ValueError as exc:
        return (str(exc),)
    if not isinstance(inventory, DraftingSourceInventory):
        return ("Open a demonstration project workspace.",)
    blockers: list[str] = []
    template_id = state.get(CONTEXT_TEMPLATE_ID_KEY)
    repository_id = state.get(CONTEXT_REPOSITORY_ID_KEY)
    evidence_ids = drafting_evidence_ids(state)
    if not isinstance(template_id, str) or not template_id:
        blockers.append("Select the required Solution Intent template.")
    if not isinstance(repository_id, str) or not repository_id:
        blockers.append("Select the required repository revision.")
    if not isinstance(evidence_ids, (tuple, list)) or not evidence_ids:
        blockers.append("Add supporting evidence before continuing.")
    inventory_ids = {resource.resource_id for resource in inventory.resources}
    selected_ids = {
        resource_id
        for resource_id in (template_id, repository_id)
        if isinstance(resource_id, str) and resource_id
    }
    if isinstance(evidence_ids, (tuple, list)):
        selected_ids.update(item for item in evidence_ids if isinstance(item, str))
    if selected_ids - inventory_ids:
        blockers.append("Resolve selections that are not in the authorized inventory.")
    if (
        inventory.provider_configuration_identity
        != DETERMINISTIC_DRAFTING_PROVIDER_CONFIGURATION_ID
    ):
        blockers.append("Select a source package compatible with the configured drafter.")
    if not blockers and check_provider:
        try:
            selected = {r.resource_id: r for r in inventory.resources}
            request = SolutionIntentDraftRequest(
                project_name=inventory.project_name,
                template=selected[template_id].content,
                source_code_context=selected[repository_id].content,
                supporting_documents="\n\n".join(selected[k].content for k in sorted(evidence_ids)),
            )
            DeterministicDemoDrafter().validate_request(request)
        except ValueError:
            blockers.append(
                "Your inputs are retained, but this demo drafter requires the bundled "
                "project, template, and repository context. Custom evidence is supported."
            )
    return tuple(blockers)


def refresh_project_context(state: MutableMapping[str, Any]) -> bool:
    """Reload local facts, invalidating drafting only when exact facts changed."""
    existing = state.get(PROJECT_CONTEXT_KEY)
    if not isinstance(existing, DraftingSourceInventory):
        raise ValueError("Open a demonstration project before refreshing context.")
    refreshed = load_sample_drafting_context()
    changed = refreshed != existing
    state[PROJECT_CONTEXT_KEY] = refreshed
    if changed:
        _invalidate_drafting_source_confirmation(state)
        available_ids = {resource.resource_id for resource in refreshed.resources}
        template_id = state.get(CONTEXT_TEMPLATE_ID_KEY)
        repository_id = state.get(CONTEXT_REPOSITORY_ID_KEY)
        evidence_ids = state.get(CONTEXT_EVIDENCE_IDS_KEY)
        retained_evidence_ids = evidence_ids if isinstance(evidence_ids, (tuple, list)) else ()
        if template_id not in available_ids:
            state[CONTEXT_TEMPLATE_ID_KEY] = None
        if repository_id not in available_ids:
            state[CONTEXT_REPOSITORY_ID_KEY] = None
        state[CONTEXT_EVIDENCE_IDS_KEY] = tuple(
            item for item in retained_evidence_ids if item in available_ids
        )
    state[PROJECT_CONTEXT_REFRESHED_KEY] = True
    update_live_drafting_source_package(state)
    state[ERROR_KEY] = None
    state[ACTIVE_STAGE_KEY] = CONTEXT_STAGE
    return changed


def confirm_project_context_for_drafting(state: MutableMapping[str, Any]) -> None:
    """Confirm selected synthetic sources and hand them to SI drafting."""
    blockers = project_context_readiness(state)
    if DRAFT_EVIDENCE_KEY in state and not drafting_evidence_is_saved(state):
        blockers += ("Save evidence before confirming the context.",)
    if blockers:
        raise ValueError(" ".join(blockers))
    inventory = drafting_inventory_with_evidence(state)
    if not isinstance(inventory, DraftingSourceInventory):
        raise ValueError("Open a demonstration project workspace.")
    manifest = build_drafting_source_package(state)
    original_inventory = state[PROJECT_CONTEXT_KEY]
    load_drafting_context_into_state(state, inventory, manifest)
    state[PROJECT_CONTEXT_KEY] = original_inventory
    state[PROJECT_CONTEXT_REFRESHED_KEY] = True
    state[PROJECT_CONTEXT_CONFIRMED_KEY] = True


def default_drafting_source_package(
    inventory: DraftingSourceInventory,
) -> DraftingSourcePackageManifest:
    """Build the complete provider-compatible default package."""
    selected_ids = tuple(resource.resource_id for resource in inventory.resources)
    return _manifest_from_inventory(inventory, selected_ids)


def build_drafting_source_package(
    state: Mapping[str, Any],
) -> DraftingSourcePackageManifest:
    """Build the exact live package from authorized state selections."""
    blockers = project_context_readiness(state, check_provider=False)
    if blockers:
        raise ValueError(" ".join(blockers))
    inventory = drafting_inventory_with_evidence(state)
    if not isinstance(inventory, DraftingSourceInventory):
        raise ValueError("Open a demonstration project workspace.")
    evidence_ids = drafting_evidence_ids(state)
    selected_evidence_ids = evidence_ids if isinstance(evidence_ids, (tuple, list)) else ()
    selected_ids = (
        str(state[CONTEXT_TEMPLATE_ID_KEY]),
        str(state[CONTEXT_REPOSITORY_ID_KEY]),
        *(str(item) for item in selected_evidence_ids),
    )
    return _manifest_from_inventory(inventory, selected_ids)


def update_live_drafting_source_package(state: MutableMapping[str, Any]) -> bool:
    """Project selectors into a manifest and report confirmation invalidation."""
    try:
        manifest = build_drafting_source_package(state)
    except ValueError:
        manifest = None
    state[LIVE_SOURCE_PACKAGE_KEY] = manifest
    confirmed = state.get(CONFIRMED_SOURCE_PACKAGE_KEY)
    if isinstance(confirmed, DraftingSourcePackageManifest) and confirmed != manifest:
        _invalidate_drafting_source_confirmation(state)
        return True
    return False


def source_package_fingerprint(manifest: DraftingSourcePackageManifest) -> str:
    """Create a stable fingerprint for an exact selected source package."""
    return hashlib.sha256(manifest.model_dump_json().encode("utf-8")).hexdigest()


def _manifest_from_inventory(
    inventory: DraftingSourceInventory,
    selected_ids: tuple[str, ...],
) -> DraftingSourcePackageManifest:
    resources = {resource.resource_id: resource for resource in inventory.resources}
    unknown_ids = set(selected_ids) - resources.keys()
    if unknown_ids:
        raise ValueError("Selected resources are not in the authorized inventory.")
    selected = tuple(
        SelectedDraftingSource(**resources[resource_id].model_dump(exclude={"content"}))
        for resource_id in sorted(
            set(selected_ids),
            key=lambda resource_id: (
                list(DraftingSourceRole).index(resources[resource_id].role),
                resource_id,
            ),
        )
    )
    return DraftingSourcePackageManifest(
        project_id=inventory.project_id,
        project_name=inventory.project_name,
        governance_reference=inventory.governance_reference,
        provider_configuration_identity=inventory.provider_configuration_identity,
        offline=True,
        resources=selected,
    )


def _resource_ids_for_role(
    inventory: DraftingSourceInventory,
    role: DraftingSourceRole,
) -> tuple[str, ...]:
    return tuple(resource.resource_id for resource in inventory.resources if resource.role is role)


def _single_selected_resource(
    resources: list[DraftingSourceResource],
    role: DraftingSourceRole,
) -> DraftingSourceResource:
    matches = [resource for resource in resources if resource.role is role]
    if len(matches) != 1:
        raise ValueError(f"Selected source package requires exactly one {role.value}.")
    return matches[0]


def _invalidate_drafting_source_confirmation(state: MutableMapping[str, Any]) -> None:
    state[PROJECT_CONTEXT_CONFIRMED_KEY] = False
    state[CONFIRMED_SOURCE_PACKAGE_KEY] = None
    state[CONFIRMED_SOURCE_PACKAGE_FINGERPRINT_KEY] = None
    state[DRAFT_PROJECT_KEY] = ""
    state[DRAFT_TEMPLATE_KEY] = ""
    state[DRAFT_SOURCE_CODE_KEY] = ""
    state[DRAFT_SUPPORTING_DOCS_KEY] = ""
    clear_stale_si_draft(state)
    state[ACTIVE_STAGE_KEY] = CONTEXT_STAGE


def store_si_draft(
    state: MutableMapping[str, Any],
    draft: SolutionIntentDraft,
    fingerprint: str,
) -> None:
    """Store a provider-generated draft as an independent human-editable value."""
    independent_draft = draft.model_copy(deep=True)
    state[DRAFT_RESULT_KEY] = independent_draft
    state[DRAFT_FINGERPRINT_KEY] = fingerprint
    state[DRAFT_CONTENT_WIDGET_KEY] = independent_draft.content
    state[DRAFT_CONFIRMED_KEY] = False
    state[ERROR_KEY] = None
    state[ACTIVE_STAGE_KEY] = DRAFT_STAGE


def drafting_input_fingerprint(
    request: SolutionIntentDraftRequest,
    manifest: DraftingSourcePackageManifest | None = None,
) -> str:
    """Bind canonical drafting inputs to their source and provider identities."""
    payload = {
        "request": request.model_dump(mode="json"),
        "source_package_fingerprint": (
            source_package_fingerprint(manifest) if manifest is not None else None
        ),
        "provider_configuration_identity": (
            manifest.provider_configuration_identity if manifest is not None else None
        ),
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def drafting_result_is_stale(
    request: SolutionIntentDraftRequest,
    generated_fingerprint: str | None,
    manifest: DraftingSourcePackageManifest | None = None,
) -> bool:
    """Return whether drafting context changed after generation."""
    if generated_fingerprint is None:
        return False
    return drafting_input_fingerprint(request, manifest) != generated_fingerprint


def clear_stale_si_draft(state: MutableMapping[str, Any]) -> None:
    """Discard a generated draft after its source context changes."""
    state[DRAFT_RESULT_KEY] = None
    state[DRAFT_FINGERPRINT_KEY] = None
    state[DRAFT_CONTENT_WIDGET_KEY] = ""
    state[DRAFT_CONFIRMED_KEY] = False


def confirm_si_draft_for_review(
    state: MutableMapping[str, Any],
    confirmed_content: str,
    *,
    sync_widget: bool = True,
) -> None:
    """Confirm a drafting artifact without representing it as a review source."""
    normalized = confirmed_content.strip()
    if not normalized:
        raise ValueError("Confirmed Solution Intent must not be blank.")
    if sync_widget:
        state[DRAFT_CONTENT_WIDGET_KEY] = normalized
    state[DRAFT_CONFIRMED_KEY] = True
    state[ERROR_KEY] = None
    state[ACTIVE_STAGE_KEY] = DRAFT_STAGE


def load_sample_review_companions_into_state(
    state: MutableMapping[str, Any],
    sample: SampleReview,
) -> None:
    """Load Offline transcript and metadata in any order, preserving SI state."""
    store_transcript_component(
        state,
        sample.transcript,
        ReviewInputProvenance.SYNTHETIC_SAMPLE,
        establish_baseline=True,
    )
    store_metadata_component(
        state,
        sample.context,
        ReviewInputProvenance.SYNTHETIC_SAMPLE,
        establish_baseline=True,
    )
    state[REVIEW_INPUT_FEEDBACK_KEY] = (
        "Synthetic transcript and metadata loaded; the SI source remains independent."
    )
    state[LOADED_KEY] = True


def store_analysis(
    state: MutableMapping[str, Any],
    result: GovernanceResult,
    fingerprint: str,
) -> None:
    """Store an analysis and an independent draft while clearing old outputs."""
    clear_review_widget_state(state)
    state[ANALYZED_RESULT_KEY] = result
    state[REVIEW_DRAFT_KEY] = result.model_copy(deep=True)
    state[REVIEWED_RESULT_KEY] = None
    state[REVIEW_CHANGE_SUMMARY_KEY] = None
    state[OUTPUTS_KEY] = None
    state[OUTPUT_ACTION_SELECTION_KEY] = None
    state[DELIVERY_ACTION_SELECTION_KEY] = None
    state[DELIVERY_ORIGINAL_INDICES_KEY] = ()
    clear_publication_preview(state)
    state[ANALYZED_FINGERPRINT_KEY] = fingerprint
    state[ANALYSIS_INVALIDATION_KEY] = None
    state[ERROR_KEY] = None
    state[ANALYSIS_SUCCESS_KEY] = True
    state[OUTPUT_SUCCESS_KEY] = False
    state[ACTIVE_STAGE_KEY] = REVIEW_STAGE


def store_outputs(
    state: MutableMapping[str, Any],
    reviewed_result: GovernanceResult,
    change_summary: ReviewChangeSummary,
    outputs: GovernanceOutputs,
) -> None:
    """Store validated reviewed data, its change summary, and generated outputs."""
    state[REVIEWED_RESULT_KEY] = reviewed_result
    state[REVIEW_CHANGE_SUMMARY_KEY] = change_summary
    state[OUTPUTS_KEY] = outputs
    state[OUTPUT_ACTION_SELECTION_KEY] = 0 if reviewed_result.action_items else None
    excluded = {
        item.item_index
        for item in change_summary.excluded_items
        if item.collection == "Action item"
    }
    state[DELIVERY_ORIGINAL_INDICES_KEY] = tuple(
        index
        for index in range(len(reviewed_result.action_items) + len(excluded))
        if index not in excluded
    )
    state[DELIVERY_ACTION_SELECTION_KEY] = 0 if reviewed_result.action_items else None
    state.pop(DELIVERY_ACTION_WIDGET_KEY, None)
    clear_publication_preview(state)
    state[ERROR_KEY] = None
    state[OUTPUT_SUCCESS_KEY] = True
    state[ACTIVE_STAGE_KEY] = OUTPUT_STAGE


def clear_outputs(state: MutableMapping[str, Any]) -> None:
    """Clear reviewed and generated output state after an invalid submission."""
    state[REVIEWED_RESULT_KEY] = None
    state[REVIEW_CHANGE_SUMMARY_KEY] = None
    state[OUTPUTS_KEY] = None
    state[OUTPUT_ACTION_SELECTION_KEY] = None
    state[DELIVERY_ACTION_SELECTION_KEY] = None
    state[DELIVERY_ORIGINAL_INDICES_KEY] = ()
    clear_publication_preview(state)
    state[OUTPUT_SUCCESS_KEY] = False


def reset_application_state(state: MutableMapping[str, Any]) -> None:
    """Reset local workflow data while retaining remote-result reconciliation facts."""
    publication_history = state.get(ADO_PUBLICATION_HISTORY_KEY)
    retained_history = dict(publication_history) if isinstance(publication_history, Mapping) else {}
    retained_operation = state.get(ADO_PUBLICATION_OPERATION_KEY)
    if isinstance(retained_operation, AdoPublicationOperation):
        retained_history.setdefault(retained_operation.correlation_id, retained_operation)
    retained_gateway = state.get(ADO_FAKE_GATEWAY_KEY)
    for key in tuple(state):
        if key.startswith(STATE_PREFIX):
            del state[key]
    initialize_session_state(state)
    state[ADO_PUBLICATION_HISTORY_KEY] = retained_history
    if isinstance(retained_operation, AdoPublicationOperation):
        state[ADO_PUBLICATION_OPERATION_KEY] = retained_operation
    if retained_gateway is not None:
        state[ADO_FAKE_GATEWAY_KEY] = retained_gateway
    state[DRAFT_PROJECT_WIDGET_KEY] = ""
    state[DRAFT_TEMPLATE_WIDGET_KEY] = ""
    state[DRAFT_SOURCE_CODE_WIDGET_KEY] = ""
    state[DRAFT_SUPPORTING_DOCS_WIDGET_KEY] = ""
    state[DRAFT_CONTENT_WIDGET_KEY] = ""
    state[SOLUTION_INTENT_WIDGET_KEY] = ""
    state[TRANSCRIPT_WIDGET_KEY] = ""


def clear_publication_preview(state: MutableMapping[str, Any]) -> None:
    """Revoke current publication eligibility without erasing operation history."""
    state[ADO_PUBLICATION_PREVIEW_KEY] = None
    state[ADO_PUBLICATION_CONFIRMATION_KEY] = None


def store_publication_preview(
    state: MutableMapping[str, Any],
    preview: AdoPublicationPreview,
) -> None:
    """Store one exact preview and clear any confirmation for an older request."""
    state[ADO_PUBLICATION_PREVIEW_KEY] = preview
    state[ADO_PUBLICATION_CONFIRMATION_KEY] = None


def store_publication_confirmation(
    state: MutableMapping[str, Any],
    confirmation: AdoPublicationConfirmation,
) -> None:
    """Store a confirmation only when it matches the displayed exact preview."""
    preview = state.get(ADO_PUBLICATION_PREVIEW_KEY)
    if not isinstance(preview, AdoPublicationPreview):
        raise ValueError("Prepare an exact publication preview before confirming it.")
    if confirmation.preview_fingerprint != preview.preview_fingerprint:
        raise ValueError("The publication confirmation does not match the current preview.")
    state[ADO_PUBLICATION_CONFIRMATION_KEY] = confirmation


def record_publication_operation(
    state: MutableMapping[str, Any],
    operation: AdoPublicationOperation,
) -> None:
    """Retain the latest state and correlation-indexed receipt for reconciliation."""
    state[ADO_PUBLICATION_OPERATION_KEY] = operation
    history_value = state.get(ADO_PUBLICATION_HISTORY_KEY)
    history = dict(history_value) if isinstance(history_value, Mapping) else {}
    history[operation.correlation_id] = operation
    state[ADO_PUBLICATION_HISTORY_KEY] = history


def active_stage(state: Mapping[str, Any]) -> str:
    """Return the current valid route stage, defaulting safely to the landing page."""
    value = state.get(ACTIVE_STAGE_KEY)
    return value if isinstance(value, str) and value in VALID_STAGES else HOME_STAGE


def set_active_stage(state: MutableMapping[str, Any], stage: str) -> None:
    """Record a validated routed workflow stage."""
    if stage not in VALID_STAGES:
        raise ValueError(f"Unknown application stage: {stage}")
    state[ACTIVE_STAGE_KEY] = stage
    if stage == HOME_STAGE:
        state[ACTIVE_WORKFLOW_KEY] = Workflow.NONE.value
    elif stage in {CONTEXT_STAGE, DRAFT_STAGE}:
        state[ACTIVE_WORKFLOW_KEY] = Workflow.DRAFT.value
    else:
        state[ACTIVE_WORKFLOW_KEY] = Workflow.REVIEW.value


def input_fingerprint(
    solution_intent: str,
    transcript: str,
    context: SolutionIntentReviewContext,
    *,
    mode: ReviewMode = ReviewMode.OFFLINE,
    source_snapshot: ConfluencePageSnapshot | None = None,
    provider_configuration_identity: str = OFFLINE_PROVIDER_CONFIGURATION_ID,
) -> str:
    """Create a stable fingerprint for the current analyzed inputs."""
    digest = hashlib.sha256()
    source_identity = (
        _source_snapshot_identity(source_snapshot) if source_snapshot is not None else "none"
    )
    for value in (
        mode.value,
        provider_configuration_identity,
        source_identity,
        solution_intent,
        transcript,
        context.model_dump_json(),
    ):
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def analysis_is_stale(
    solution_intent: str,
    transcript: str,
    context: SolutionIntentReviewContext | None,
    analyzed_fingerprint: str | None,
    *,
    mode: ReviewMode = ReviewMode.OFFLINE,
    source_snapshot: ConfluencePageSnapshot | None = None,
    provider_configuration_identity: str = OFFLINE_PROVIDER_CONFIGURATION_ID,
) -> bool:
    """Return whether current inputs differ from a previous analysis."""
    if analyzed_fingerprint is None:
        return False
    if context is None:
        return True
    if mode is ReviewMode.INTERNAL_FAKE and source_snapshot is None:
        return True
    return (
        input_fingerprint(
            solution_intent,
            transcript,
            context,
            mode=mode,
            source_snapshot=source_snapshot,
            provider_configuration_identity=provider_configuration_identity,
        )
        != analyzed_fingerprint
    )


def current_input_fingerprint(
    state: Mapping[str, Any],
    context: SolutionIntentReviewContext,
) -> str:
    """Fingerprint the exact confirmed manifest used for analysis."""
    manifest = current_review_input_manifest(state)
    if metadata_fingerprint(context) != manifest.metadata_fingerprint:
        raise ValueError("Review metadata differs from the current manifest.")
    fingerprint = review_input_manifest_fingerprint(manifest)
    if state.get(REVIEW_INPUT_CONFIRMATION_KEY) != fingerprint:
        raise ValueError("Confirm the current review input manifest before analysis.")
    return fingerprint


def _source_snapshot_identity(snapshot: ConfluencePageSnapshot) -> str:
    return "|".join(
        (
            snapshot.page_id,
            str(snapshot.version),
            snapshot.canonicalizer_version,
            snapshot.content_fingerprint,
        )
    )


def humanize(value: str) -> str:
    """Render an enum-like string as a human-readable label."""
    return value.replace("_", " ").title()


def optional_text(value: str) -> str | None:
    """Convert an optional text field to stripped text or None."""
    stripped = value.strip()
    return stripped or None


def parse_optional_iso_date(value: str) -> date | None:
    """Parse optional ISO date text, raising a concise error when invalid."""
    normalized = optional_text(value)
    if normalized is None:
        return None
    try:
        return date.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"Invalid date '{normalized}'. Use YYYY-MM-DD.") from exc


def default_review_form_data(result: GovernanceResult) -> ReviewFormData:
    """Create editable default values from an analyzed governance result."""
    return ReviewFormData(
        review_outcome=result.review_outcome.value,
        decisions=tuple(
            {
                "include": True,
                "statement": item.statement,
                "rationale": item.rationale or "",
            }
            for item in result.decisions
        ),
        findings=tuple(
            {
                "include": True,
                "title": item.title,
                "description": item.description,
                "category": item.category or "",
                "si_section": item.si_section or "",
                "severity": item.severity.value,
                "status": item.status.value,
                "recommended_change": item.recommended_change or "",
                "owner": item.owner or "",
                "due_date": item.due_date.isoformat() if item.due_date else "",
            }
            for item in result.findings
        ),
        risks=tuple(
            {
                "include": True,
                "description": item.description,
                "severity": item.severity.value,
                "owner": item.owner or "",
            }
            for item in result.risks
        ),
        action_items=tuple(
            {
                "include": True,
                "title": item.title,
                "owner": item.owner or "",
                "due_date": item.due_date,
                "priority": item.priority.value,
            }
            for item in result.action_items
        ),
        open_questions=tuple(
            {
                "include": True,
                "question": item.question,
                "owner": item.owner or "",
            }
            for item in result.open_questions
        ),
        missing_evidence=tuple(
            {
                "include": True,
                "item": item.item,
                "reason": item.reason or "",
            }
            for item in result.missing_evidence
        ),
    )


def current_review_form_data(state: Mapping[str, Any], result: GovernanceResult) -> ReviewFormData:
    """Overlay current routed widget values on the analyzed proposal defaults."""
    defaults = default_review_form_data(result)

    def collection_values(
        values: tuple[Mapping[str, object], ...], widget_collection: str
    ) -> tuple[Mapping[str, object], ...]:
        return tuple(
            {
                field: state.get(
                    f"{REVIEW_WIDGET_PREFIX}{widget_collection}_{index}_{field}",
                    value,
                )
                for field, value in item.items()
            }
            for index, item in enumerate(values)
        )

    return ReviewFormData(
        review_outcome=str(state.get(f"{REVIEW_WIDGET_PREFIX}outcome", defaults.review_outcome)),
        decisions=collection_values(defaults.decisions, "decision"),
        findings=collection_values(defaults.findings, "finding"),
        risks=collection_values(defaults.risks, "risk"),
        action_items=collection_values(defaults.action_items, "action"),
        open_questions=collection_values(defaults.open_questions, "question"),
        missing_evidence=collection_values(defaults.missing_evidence, "missing"),
    )


def build_pending_review_changes(
    analyzed_result: GovernanceResult,
    form_data: ReviewFormData,
) -> PendingReviewChanges:
    """Compare an in-progress form without requiring it to be model-valid."""
    field_changes: list[ReviewFieldChange] = []
    excluded_items: list[ReviewExcludedItem] = []
    validation_issues: list[ReviewValidationIssue] = []

    outcome = form_data.review_outcome.strip()
    if outcome != analyzed_result.review_outcome.value:
        field_changes.append(
            ReviewFieldChange(
                collection="Review outcome",
                item_index=None,
                item_name="Governance outcome",
                field="Outcome",
                before=analyzed_result.review_outcome.value,
                after=outcome,
            )
        )

    collection_specs = (
        ("decisions", "Decision", "statement", ("statement", "rationale")),
        (
            "findings",
            "Finding",
            "title",
            (
                "title",
                "description",
                "category",
                "si_section",
                "severity",
                "status",
                "recommended_change",
                "owner",
                "due_date",
            ),
        ),
        ("risks", "Risk", "description", ("description", "severity", "owner")),
        (
            "action_items",
            "Action item",
            "title",
            ("title", "owner", "due_date", "priority"),
        ),
        (
            "open_questions",
            "Open question",
            "question",
            ("question", "owner"),
        ),
        (
            "missing_evidence",
            "Missing information",
            "item",
            ("item", "reason"),
        ),
    )
    optional_fields = {
        "rationale",
        "category",
        "si_section",
        "recommended_change",
        "owner",
        "reason",
        "due_date",
    }

    for attribute, collection, name_field, fields in collection_specs:
        originals = getattr(analyzed_result, attribute)
        edits = getattr(form_data, attribute)
        _require_edit_count(collection.lower(), edits, len(originals))
        for item_index, (original, edit) in enumerate(zip(originals, edits, strict=True)):
            item_name = str(getattr(original, name_field))
            if not _included(edit):
                excluded_items.append(
                    ReviewExcludedItem(
                        collection=collection,
                        item_index=item_index,
                        item_name=item_name,
                    )
                )
                continue
            for field in fields:
                before = _summary_value(getattr(original, field))
                raw_after = _text(edit, field)
                normalized_after = (
                    optional_text(raw_after) if field in optional_fields else raw_after.strip()
                )
                if field == "due_date" and normalized_after is not None:
                    try:
                        normalized_after = date.fromisoformat(normalized_after).isoformat()
                    except ValueError:
                        validation_issues.append(
                            ReviewValidationIssue(
                                collection=collection,
                                item_index=item_index,
                                item_name=item_name,
                                field=_REVIEW_FIELD_LABELS[field],
                                message="Use YYYY-MM-DD.",
                            )
                        )
                elif field not in optional_fields and not normalized_after:
                    validation_issues.append(
                        ReviewValidationIssue(
                            collection=collection,
                            item_index=item_index,
                            item_name=item_name,
                            field=_REVIEW_FIELD_LABELS[field],
                            message="A value is required.",
                        )
                    )
                if before != normalized_after:
                    field_changes.append(
                        ReviewFieldChange(
                            collection=collection,
                            item_index=item_index,
                            item_name=item_name,
                            field=_REVIEW_FIELD_LABELS[field],
                            before=before,
                            after=normalized_after,
                        )
                    )

    return PendingReviewChanges(
        field_changes=tuple(field_changes),
        excluded_items=tuple(excluded_items),
        validation_issues=tuple(validation_issues),
    )


def build_reviewed_result(
    analyzed_result: GovernanceResult,
    form_data: ReviewFormData,
) -> GovernanceResult:
    """Reconstruct and validate a reviewed result without mutating analysis."""
    _require_edit_count("decisions", form_data.decisions, len(analyzed_result.decisions))
    _require_edit_count("findings", form_data.findings, len(analyzed_result.findings))
    _require_edit_count("risks", form_data.risks, len(analyzed_result.risks))
    _require_edit_count("action items", form_data.action_items, len(analyzed_result.action_items))
    _require_edit_count(
        "open questions",
        form_data.open_questions,
        len(analyzed_result.open_questions),
    )
    _require_edit_count(
        "missing evidence",
        form_data.missing_evidence,
        len(analyzed_result.missing_evidence),
    )

    payload: dict[str, object] = {
        "context": analyzed_result.context.model_copy(deep=True),
        "review_outcome": form_data.review_outcome,
        "outcome_evidence": _copy_evidence(analyzed_result.outcome_evidence),
        "decisions": [
            {
                "statement": _required_text(edit, "statement"),
                "rationale": optional_text(_text(edit, "rationale")),
                "evidence": _copy_evidence(original.evidence),
            }
            for original, edit in zip(
                analyzed_result.decisions,
                form_data.decisions,
                strict=True,
            )
            if _included(edit)
        ],
        "findings": [
            {
                "title": _required_text(edit, "title"),
                "description": _required_text(edit, "description"),
                "category": optional_text(_text(edit, "category")),
                "si_section": optional_text(_text(edit, "si_section")),
                "severity": _required_text(edit, "severity"),
                "status": _required_text(edit, "status"),
                "recommended_change": optional_text(_text(edit, "recommended_change")),
                "owner": optional_text(_text(edit, "owner")),
                "due_date": parse_optional_iso_date(_text(edit, "due_date")),
                "evidence": _copy_evidence(original.evidence),
            }
            for original, edit in zip(
                analyzed_result.findings,
                form_data.findings,
                strict=True,
            )
            if _included(edit)
        ],
        "risks": [
            {
                "description": _required_text(edit, "description"),
                "severity": _required_text(edit, "severity"),
                "owner": optional_text(_text(edit, "owner")),
                "evidence": _copy_evidence(original.evidence),
            }
            for original, edit in zip(
                analyzed_result.risks,
                form_data.risks,
                strict=True,
            )
            if _included(edit)
        ],
        "action_items": [
            {
                "title": _required_text(edit, "title"),
                "owner": optional_text(_text(edit, "owner")),
                "due_date": parse_optional_iso_date(_text(edit, "due_date")),
                "priority": _required_text(edit, "priority"),
                "evidence": _copy_evidence(original.evidence),
            }
            for original, edit in zip(
                analyzed_result.action_items,
                form_data.action_items,
                strict=True,
            )
            if _included(edit)
        ],
        "open_questions": [
            {
                "question": _required_text(edit, "question"),
                "owner": optional_text(_text(edit, "owner")),
                "evidence": _copy_evidence(original.evidence),
            }
            for original, edit in zip(
                analyzed_result.open_questions,
                form_data.open_questions,
                strict=True,
            )
            if _included(edit)
        ],
        "missing_evidence": [
            {
                "item": _required_text(edit, "item"),
                "reason": optional_text(_text(edit, "reason")),
                "evidence": _copy_evidence(original.evidence),
            }
            for original, edit in zip(
                analyzed_result.missing_evidence,
                form_data.missing_evidence,
                strict=True,
            )
            if _included(edit)
        ],
    }
    return GovernanceResult.model_validate(payload)


def build_review_change_summary(
    analyzed_result: GovernanceResult,
    reviewed_result: GovernanceResult,
    form_data: ReviewFormData,
) -> ReviewChangeSummary:
    """Compare validated reviewed values with their original analyzed positions."""
    field_changes: list[ReviewFieldChange] = []
    excluded_items: list[ReviewExcludedItem] = []

    if analyzed_result.review_outcome != reviewed_result.review_outcome:
        field_changes.append(
            ReviewFieldChange(
                collection="Review",
                item_index=None,
                item_name="Governance outcome",
                field="Outcome",
                before=_summary_value(analyzed_result.review_outcome),
                after=_summary_value(reviewed_result.review_outcome),
            )
        )

    collection_specs = (
        ("decisions", "Decision", "statement", ("statement", "rationale")),
        (
            "findings",
            "Finding",
            "title",
            (
                "title",
                "description",
                "category",
                "si_section",
                "severity",
                "status",
                "recommended_change",
                "owner",
                "due_date",
            ),
        ),
        ("risks", "Risk", "description", ("description", "severity", "owner")),
        (
            "action_items",
            "Action item",
            "title",
            ("title", "owner", "due_date", "priority"),
        ),
        (
            "open_questions",
            "Open question",
            "question",
            ("question", "owner"),
        ),
        (
            "missing_evidence",
            "Missing information",
            "item",
            ("item", "reason"),
        ),
    )

    for attribute, collection, name_field, fields in collection_specs:
        originals = getattr(analyzed_result, attribute)
        reviewed_items = getattr(reviewed_result, attribute)
        edits = getattr(form_data, attribute)
        _require_edit_count(collection.lower(), edits, len(originals))
        retained_index = 0
        for item_index, (original, edit) in enumerate(zip(originals, edits, strict=True)):
            original_name = str(getattr(original, name_field))
            if not _included(edit):
                excluded_items.append(
                    ReviewExcludedItem(
                        collection=collection,
                        item_index=item_index,
                        item_name=original_name,
                    )
                )
                continue

            if retained_index >= len(reviewed_items):
                raise ValueError(f"Reviewed {collection.lower()} positions do not match analysis.")
            reviewed_item = reviewed_items[retained_index]
            retained_index += 1
            for field in fields:
                before = getattr(original, field)
                after = getattr(reviewed_item, field)
                if before == after:
                    continue
                field_changes.append(
                    ReviewFieldChange(
                        collection=collection,
                        item_index=item_index,
                        item_name=original_name,
                        field=_REVIEW_FIELD_LABELS[field],
                        before=_summary_value(before),
                        after=_summary_value(after),
                    )
                )
        if retained_index != len(reviewed_items):
            raise ValueError(f"Reviewed {collection.lower()} positions do not match analysis.")

    return ReviewChangeSummary(
        field_changes=tuple(field_changes),
        excluded_items=tuple(excluded_items),
    )


def _summary_value(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, str):
        return value
    raise TypeError(f"Unsupported review summary value: {type(value).__name__}")


def _copy_evidence(evidence: list[SourceEvidence]) -> list[SourceEvidence]:
    return [item.model_copy(deep=True) for item in evidence]


def _require_edit_count(
    label: str,
    edits: tuple[Mapping[str, object], ...],
    expected: int,
) -> None:
    if len(edits) != expected:
        raise ValueError(f"Expected {expected} {label} edit entries, received {len(edits)}.")


def _included(edit: Mapping[str, object]) -> bool:
    value = edit.get("include")
    if not isinstance(value, bool):
        raise ValueError("Each reviewed item requires an include selection.")
    return value


def _text(edit: Mapping[str, object], field: str) -> str:
    value = edit.get(field)
    if field == "due_date" and (value is None or type(value) is date):
        return value.isoformat() if value is not None else ""
    if not isinstance(value, str):
        raise ValueError(f"Reviewed field '{field}' must be text.")
    return value


def _required_text(edit: Mapping[str, object], field: str) -> str:
    return _text(edit, field)


def delivery_outputs_available(state: Mapping[str, Any]) -> bool:
    """Local completion is the prerequisite for the conditional delivery branch."""
    return (
        isinstance(state.get(REVIEWED_RESULT_KEY), GovernanceResult)
        and isinstance(state.get(OUTPUTS_KEY), GovernanceOutputs)
        and state.get(OUTPUT_SUCCESS_KEY) is True
    )


def select_delivery_action(state: MutableMapping[str, Any], index: int) -> None:
    """Revoke only the active request when the independent delivery selection changes."""
    result = state.get(REVIEWED_RESULT_KEY)
    if not isinstance(result, GovernanceResult) or not 0 <= index < len(result.action_items):
        raise ValueError("Select a confirmed action for delivery.")
    if state.get(DELIVERY_ACTION_SELECTION_KEY) != index:
        clear_publication_preview(state)
    state[DELIVERY_ACTION_SELECTION_KEY] = index


def delivery_original_action_index(state: Mapping[str, Any], index: int) -> int:
    """Require the original analyzed position retained by reviewed confirmation."""
    indices = state.get(DELIVERY_ORIGINAL_INDICES_KEY)
    if not isinstance(indices, tuple) or not 0 <= index < len(indices):
        raise ValueError("Confirm the reviewed record to restore delivery action identities.")
    return indices[index]


def delivery_operation_for_correlations(
    state: Mapping[str, Any],
    correlations: tuple[str, ...],
) -> AdoPublicationOperation | None:
    """Prefer reconciliation and protected history over a newer failed attempt."""
    history = state.get(ADO_PUBLICATION_HISTORY_KEY)
    if not isinstance(history, Mapping):
        return None
    operations = [
        history[c] for c in correlations if isinstance(history.get(c), AdoPublicationOperation)
    ]
    rank = {
        PublicationStatus.UNKNOWN_RESULT: 0,
        PublicationStatus.SUBMITTING: 1,
        PublicationStatus.SUCCEEDED: 2,
        PublicationStatus.DEFINITELY_FAILED: 3,
        PublicationStatus.NOT_SUBMITTED: 4,
    }
    return min(operations, key=lambda op: rank[op.status]) if operations else None


def delivery_status(
    readiness: DeliveryReadiness,
    operations: tuple[AdoPublicationOperation | None, ...],
    *,
    has_preview: bool = False,
) -> DeliveryStatus:
    """Summarize delivery without changing the local governance completion boundary."""
    statuses = {operation.status for operation in operations if operation is not None}
    if PublicationStatus.UNKNOWN_RESULT in statuses:
        return DeliveryStatus.NEEDS_RECONCILIATION
    if PublicationStatus.SUBMITTING in statuses:
        return DeliveryStatus.IN_PROGRESS
    if operations and all(op and op.status is PublicationStatus.SUCCEEDED for op in operations):
        return DeliveryStatus.SUCCEEDED
    if PublicationStatus.DEFINITELY_FAILED in statuses:
        return DeliveryStatus.FAILED
    if readiness.status in {DeliveryStatus.UNAVAILABLE, DeliveryStatus.NOT_APPLICABLE}:
        return readiness.status
    if has_preview or PublicationStatus.SUCCEEDED in statuses:
        return DeliveryStatus.IN_PROGRESS
    return readiness.status


def clear_review_action_due_date(state: MutableMapping[str, Any], index: int) -> None:
    """Explicitly clear a nullable calendar value before the next widget render."""
    key = f"{REVIEW_WIDGET_PREFIX}action_{index}_due_date"
    state[key] = None
    preserve_review_widget_state(state)


def apply_deployment_policy(state: MutableMapping[str, Any], policy: DeploymentPolicy) -> bool:
    """Revoke incompatible state before routing; report whether deployment identity changed."""
    policy_changed = state.get(DEPLOYMENT_POLICY_ID_KEY) != policy.identity
    previous_mode = state.get(REVIEW_MODE_KEY, ReviewMode.OFFLINE.value)
    recovery = bool(state.get(REVIEW_POLICY_RECOVERY_KEY))
    initialize_session_state(state)
    descriptors = {item.mode.value: item for item in policy.review_modes}
    old_stage = state.get(ACTIVE_STAGE_KEY)
    old_workflow = state.get(ACTIVE_WORKFLOW_KEY)
    if previous_mode not in descriptors or recovery:
        reset_review_workflow(state)
        state[REVIEW_MODE_KEY] = None
        state[REVIEW_PROVIDER_CONFIGURATION_ID_KEY] = None
        state[REVIEW_POLICY_RECOVERY_KEY] = True
        state[ACTIVE_STAGE_KEY] = old_stage
        state[ACTIVE_WORKFLOW_KEY] = old_workflow
    else:
        descriptor = descriptors[previous_mode]
        if state.get(REVIEW_PROVIDER_CONFIGURATION_ID_KEY) != (
            descriptor.provider_configuration_identity
        ):
            reset_review_workflow(state)
            state[REVIEW_MODE_KEY] = descriptor.mode.value
            state[REVIEW_PROVIDER_CONFIGURATION_ID_KEY] = descriptor.provider_configuration_identity
            if old_workflow != Workflow.REVIEW.value:
                state[ACTIVE_STAGE_KEY] = old_stage
                state[ACTIVE_WORKFLOW_KEY] = old_workflow
        state[REVIEW_POLICY_RECOVERY_KEY] = False
    if not policy.drafting_allowed:
        reset_drafting_workflow(state)
        state[ACTIVE_STAGE_KEY] = HOME_STAGE
        state[ACTIVE_WORKFLOW_KEY] = Workflow.NONE.value
    state[DEPLOYMENT_POLICY_ID_KEY] = policy.identity
    return policy_changed


def recover_review_policy(
    state: MutableMapping[str, Any], policy: DeploymentPolicy, mode: ReviewMode
) -> None:
    """Start an allowed review only after the user's explicit recovery action."""
    descriptor = next((item for item in policy.review_modes if item.mode is mode), None)
    if descriptor is None:
        raise ValueError("The requested review mode is not allowed by deployment policy.")
    reset_review_workflow(state)
    state[REVIEW_MODE_KEY] = descriptor.mode.value
    state[REVIEW_PROVIDER_CONFIGURATION_ID_KEY] = descriptor.provider_configuration_identity
    state[REVIEW_POLICY_RECOVERY_KEY] = False
    state[DEPLOYMENT_POLICY_ID_KEY] = policy.identity


@dataclass(frozen=True)
class DraftingEvidenceInput:
    """Editable user input, including incomplete text, before strict manifest validation."""

    evidence_id: str
    title: str
    text: str
    provenance: DraftingSourceProvenance
    source_reference: str


MAX_EVIDENCE_BYTES = 1024 * 1024
MAX_EVIDENCE_ITEMS = 10


def add_drafting_evidence(
    state: MutableMapping[str, Any], *, title: str = "Notes", data: bytes | None = None
) -> None:
    items = tuple(state.get(DRAFT_EVIDENCE_KEY, ()))
    if len(items) >= MAX_EVIDENCE_ITEMS:
        raise ValueError("A source package supports at most 10 evidence items.")
    text = ""
    provenance = DraftingSourceProvenance.USER_ENTERED
    reference = "user-entered://notes"
    if data is not None:
        if Path(title).suffix.lower() not in {".txt", ".md"}:
            raise ValueError("Upload a UTF-8 TXT or Markdown file.")
        if len(data) > MAX_EVIDENCE_BYTES:
            raise ValueError("Each evidence file must be at most 1 MiB.")
        try:
            text = data.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").strip()
        except UnicodeError as exc:
            raise ValueError("Evidence must be valid UTF-8 text.") from exc
        if not text or any(ord(c) < 32 and c not in "\n\t" for c in text):
            raise ValueError(
                "Evidence must contain nonempty text without binary control characters."
            )
        provenance = DraftingSourceProvenance.USER_UPLOADED
        reference = "user-upload://sha256/" + hashlib.sha256(data).hexdigest()
    counter = int(state.get("agc_evidence_counter", 0)) + 1
    state["agc_evidence_counter"] = counter
    state[DRAFT_EVIDENCE_KEY] = (
        *items,
        DraftingEvidenceInput(
            f"user-evidence-{counter:04d}", Path(title).name, text, provenance, reference
        ),
    )
    _invalidate_drafting_source_confirmation(state)


def edit_drafting_evidence(state: MutableMapping[str, Any], evidence_id: str, text: str) -> None:
    items = tuple(state.get(DRAFT_EVIDENCE_KEY, ()))
    state[DRAFT_EVIDENCE_KEY] = tuple(
        replace(item, text=text, provenance=DraftingSourceProvenance.USER_ENTERED)
        if item.evidence_id == evidence_id and item.text != text
        else item
        for item in items
    )
    if state[DRAFT_EVIDENCE_KEY] != items:
        _invalidate_drafting_source_confirmation(state)


def remove_drafting_evidence(state: MutableMapping[str, Any], evidence_id: str) -> None:
    state[DRAFT_EVIDENCE_KEY] = tuple(
        item for item in state.get(DRAFT_EVIDENCE_KEY, ()) if item.evidence_id != evidence_id
    )
    _invalidate_drafting_source_confirmation(state)


def load_drafting_sample_evidence(state: MutableMapping[str, Any]) -> None:
    sample = load_sample_drafting_context().resource_for_role(
        DraftingSourceRole.SUPPORTING_EVIDENCE
    )
    items = tuple(state.get(DRAFT_EVIDENCE_KEY, ()))
    if any(item.evidence_id == sample.resource_id for item in items):
        return
    if len(items) >= MAX_EVIDENCE_ITEMS:
        raise ValueError("A source package supports at most 10 evidence items.")
    state[DRAFT_EVIDENCE_KEY] = (
        *items,
        DraftingEvidenceInput(
            sample.resource_id,
            sample.display_name,
            sample.content,
            sample.provenance,
            sample.source_reference,
        ),
    )
    _invalidate_drafting_source_confirmation(state)


def drafting_evidence_ids(state: Mapping[str, Any]) -> tuple[str, ...]:
    if DRAFT_EVIDENCE_KEY in state:
        return tuple(item.evidence_id for item in state[DRAFT_EVIDENCE_KEY])
    return tuple(state.get(CONTEXT_EVIDENCE_IDS_KEY, ()))


def drafting_inventory_with_evidence(state: Mapping[str, Any]) -> DraftingSourceInventory | None:
    inventory = state.get(PROJECT_CONTEXT_KEY)
    if not isinstance(inventory, DraftingSourceInventory) or DRAFT_EVIDENCE_KEY not in state:
        return inventory
    resources = [
        r
        for r in inventory.resources
        if r.provenance is DraftingSourceProvenance.SYNTHETIC_LOCAL_FIXTURE
    ]
    for item in state[DRAFT_EVIDENCE_KEY]:
        normalized = item.text.replace("\r\n", "\n").replace("\r", "\n").strip()
        if not normalized:
            raise ValueError(f"Evidence '{item.title}' is empty. Add text or remove it.")
        if len(normalized.encode()) > MAX_EVIDENCE_BYTES:
            raise ValueError(f"Evidence '{item.title}' exceeds 1 MiB.")
        resources = [r for r in resources if r.resource_id != item.evidence_id]
        resources.append(
            DraftingSourceResource(
                resource_id=item.evidence_id,
                role=DraftingSourceRole.SUPPORTING_EVIDENCE,
                display_name=item.title,
                source_reference=item.source_reference,
                revision_kind=DraftingRevisionKind.VERSION,
                revision="session",
                content_fingerprint=hashlib.sha256(normalized.encode()).hexdigest(),
                validation_status=DraftingValidationStatus.VALIDATED,
                provenance=item.provenance,
                authorized=True,
                content=normalized,
            )
        )
    return DraftingSourceInventory(**{**inventory.model_dump(), "resources": tuple(resources)})


def drafting_evidence_is_saved(state: Mapping[str, Any]) -> bool:
    """Compare the current evidence with the last explicitly saved snapshot."""
    items = state.get(DRAFT_EVIDENCE_KEY, ())
    return bool(items) and state.get("agc_evidence_saved") == items


def save_drafting_evidence(state: MutableMapping[str, Any]) -> None:
    """Validate and save evidence locally without checking generation eligibility."""
    if not state.get(DRAFT_EVIDENCE_KEY):
        raise ValueError("Add evidence before saving.")
    drafting_inventory_with_evidence(state)
    state["agc_evidence_saved"] = tuple(state[DRAFT_EVIDENCE_KEY])
