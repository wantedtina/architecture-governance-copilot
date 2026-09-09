"""Pure support functions for the routed Streamlit proof of concept."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass, replace
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Any

from architecture_governance_copilot.governance_service import GovernanceOutputs
from architecture_governance_copilot.integrations.confluence import ConfluencePageSnapshot
from architecture_governance_copilot.models import (
    GovernanceResult,
    SolutionIntentDraft,
    SolutionIntentDraftRequest,
    SolutionIntentReviewContext,
    SourceEvidence,
)
from architecture_governance_copilot.publication import (
    AdoPublicationConfirmation,
    AdoPublicationOperation,
    AdoPublicationPreview,
)
from architecture_governance_copilot.runtime_dependencies import (
    OFFLINE_PROVIDER_CONFIGURATION_ID,
    ReviewMode,
)

STATE_PREFIX = "agc_"
REVIEW_WIDGET_PREFIX = f"{STATE_PREFIX}field_"

PROJECT_CONTEXT_KEY = f"{STATE_PREFIX}project_context"
PROJECT_CONTEXT_CONFIRMED_KEY = f"{STATE_PREFIX}project_context_confirmed"
PROJECT_CONTEXT_REFRESHED_KEY = f"{STATE_PREFIX}project_context_refreshed"
CONTEXT_TEMPLATE_SELECTED_KEY = f"{STATE_PREFIX}context_template_selected"
CONTEXT_REPOSITORY_SELECTED_KEY = f"{STATE_PREFIX}context_repository_selected"
CONTEXT_SUPPORTING_SELECTED_KEY = f"{STATE_PREFIX}context_supporting_selected"
CONTEXT_ADO_SELECTED_KEY = f"{STATE_PREFIX}context_ado_selected"
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

CONTEXT_STAGE = "context"
DRAFT_STAGE = "drafting"
INPUT_STAGE = "inputs"
REVIEW_STAGE = "review"
OUTPUT_STAGE = "outputs"
VALID_STAGES = frozenset({CONTEXT_STAGE, DRAFT_STAGE, INPUT_STAGE, REVIEW_STAGE, OUTPUT_STAGE})

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
class DraftingSampleContext:
    """Loaded bundled synthetic context for SI drafting."""

    project_name: str
    template: str
    source_code_context: str
    supporting_documents: str
    governance_reference: str
    template_reference: str
    repository_reference: str
    branch: str


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
class AnalysisInvalidation:
    """Reason an earlier analysis can no longer be confirmed or published."""

    reason: str
    outputs_invalidated: bool


def drafting_sample_paths() -> DraftingSamplePaths:
    """Resolve bundled SI-drafting paths independently of the working directory."""
    samples_dir = Path(__file__).resolve().parents[2] / "samples"
    return DraftingSamplePaths(
        template=samples_dir / "si_template.md",
        source_code_context=samples_dir / "source_context.txt",
        supporting_documents=samples_dir / "supporting_context.md",
    )


def load_sample_drafting_context() -> DraftingSampleContext:
    """Load and validate the bundled synthetic SI-drafting context."""
    paths = drafting_sample_paths()
    template = paths.template.read_text(encoding="utf-8")
    source_code_context = paths.source_code_context.read_text(encoding="utf-8")
    supporting_documents = paths.supporting_documents.read_text(encoding="utf-8")
    for label, value in (
        ("SI template", template),
        ("source-code context", source_code_context),
        ("supporting-document context", supporting_documents),
    ):
        if not value.strip():
            raise ValueError(f"Bundled {label} is empty.")
    return DraftingSampleContext(
        project_name="Digital Payment Notification Service",
        template=template,
        source_code_context=source_code_context,
        supporting_documents=supporting_documents,
        governance_reference="ADO Workitem - Solution Intent 12658902",
        template_reference="v1.1",
        repository_reference="55390-19-payment-notification-service",
        branch="main",
    )


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


def initial_state_values() -> dict[str, object]:
    """Return independent initial values for application-owned session state."""
    return {
        PROJECT_CONTEXT_KEY: None,
        PROJECT_CONTEXT_CONFIRMED_KEY: False,
        PROJECT_CONTEXT_REFRESHED_KEY: False,
        CONTEXT_TEMPLATE_SELECTED_KEY: True,
        CONTEXT_REPOSITORY_SELECTED_KEY: True,
        CONTEXT_SUPPORTING_SELECTED_KEY: True,
        CONTEXT_ADO_SELECTED_KEY: True,
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
        ADO_PUBLICATION_PREVIEW_KEY: None,
        ADO_PUBLICATION_CONFIRMATION_KEY: None,
        ADO_PUBLICATION_OPERATION_KEY: None,
        ADO_PUBLICATION_HISTORY_KEY: {},
        ADO_FAKE_GATEWAY_KEY: None,
        REVIEW_MODE_KEY: ReviewMode.OFFLINE.value,
        REVIEW_PROVIDER_CONFIGURATION_ID_KEY: OFFLINE_PROVIDER_CONFIGURATION_ID,
        CONFLUENCE_SNAPSHOT_KEY: None,
        ACTIVE_STAGE_KEY: CONTEXT_STAGE,
    }


def initialize_session_state(state: MutableMapping[str, Any]) -> None:
    """Add any missing application-owned session-state values."""
    for key, value in initial_state_values().items():
        state.setdefault(key, value)


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


def restore_review_widget_state(state: MutableMapping[str, Any]) -> None:
    """Restore durable human-review values before routed widgets are created."""
    stored = state.get(REVIEW_WIDGET_VALUES_KEY)
    if not isinstance(stored, Mapping):
        return
    for key, value in stored.items():
        if isinstance(key, str) and key.startswith(REVIEW_WIDGET_PREFIX):
            state.setdefault(key, value)


def clear_analysis_state(state: MutableMapping[str, Any]) -> None:
    """Clear analysis and derived records without erasing an invalidation notice."""
    clear_review_widget_state(state)
    state[ANALYZED_RESULT_KEY] = None
    state[REVIEW_DRAFT_KEY] = None
    state[REVIEWED_RESULT_KEY] = None
    state[REVIEW_CHANGE_SUMMARY_KEY] = None
    state[OUTPUTS_KEY] = None
    state[OUTPUT_ACTION_SELECTION_KEY] = None
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
        invalidate_analysis_for_input_change(state, reason)
    return changed


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
    context = state.get(CONTEXT_KEY)
    valid_context = context if isinstance(context, SolutionIntentReviewContext) else None
    solution_intent = state.get(SOLUTION_INTENT_KEY)
    transcript = state.get(TRANSCRIPT_KEY)
    fingerprint = state.get(ANALYZED_FINGERPRINT_KEY)
    mode = current_review_mode(state)
    snapshot_value = state.get(CONFLUENCE_SNAPSHOT_KEY)
    snapshot = snapshot_value if isinstance(snapshot_value, ConfluencePageSnapshot) else None
    provider_identity = state.get(REVIEW_PROVIDER_CONFIGURATION_ID_KEY)
    valid_provider_identity = (
        provider_identity
        if isinstance(provider_identity, str) and provider_identity.strip()
        else OFFLINE_PROVIDER_CONFIGURATION_ID
    )
    if not isinstance(solution_intent, str) or not isinstance(transcript, str):
        return invalidate_analysis_for_input_change(state, "Review inputs changed.")
    if not isinstance(fingerprint, str):
        return invalidate_analysis_for_input_change(state, "Analysis state is incomplete.")
    if analysis_is_stale(
        solution_intent,
        transcript,
        valid_context,
        fingerprint,
        mode=mode,
        source_snapshot=snapshot,
        provider_configuration_identity=valid_provider_identity,
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
    clear_publication_preview(state)
    state[ERROR_KEY] = None
    state[ANALYSIS_SUCCESS_KEY] = False
    state[OUTPUT_SUCCESS_KEY] = False
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE


def load_sample_into_state(
    state: MutableMapping[str, Any],
    sample: SampleReview,
) -> None:
    """Populate sample inputs while retaining any required reanalysis notice."""
    state[REVIEW_MODE_KEY] = ReviewMode.OFFLINE.value
    state[REVIEW_PROVIDER_CONFIGURATION_ID_KEY] = OFFLINE_PROVIDER_CONFIGURATION_ID
    state[CONFLUENCE_SNAPSHOT_KEY] = None
    update_review_inputs(
        state,
        solution_intent=sample.solution_intent,
        transcript=sample.transcript,
        context=sample.context.model_copy(deep=True),
        reason="The sample review package changed the review inputs.",
    )
    state[SOLUTION_INTENT_WIDGET_KEY] = sample.solution_intent
    state[TRANSCRIPT_WIDGET_KEY] = sample.transcript
    state[LOADED_KEY] = True
    state[PROJECT_CONTEXT_CONFIRMED_KEY] = False
    state[DRAFT_CONFIRMED_KEY] = False
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
    state[CONFLUENCE_SNAPSHOT_KEY] = None
    update_review_inputs(
        state,
        solution_intent="",
        transcript="",
        context=None,
        reason="The review source or analysis provider changed.",
    )
    state[SOLUTION_INTENT_WIDGET_KEY] = ""
    state[TRANSCRIPT_WIDGET_KEY] = ""
    state[LOADED_KEY] = False
    state[DRAFT_CONFIRMED_KEY] = False
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
    state[CONFLUENCE_SNAPSHOT_KEY] = snapshot.model_copy(deep=True)
    state[REVIEW_PROVIDER_CONFIGURATION_ID_KEY] = normalized_provider_identity
    update_review_inputs(
        state,
        solution_intent=snapshot.canonical_text,
        transcript=normalized_transcript,
        context=context.model_copy(deep=True),
        reason="The internal review source package changed.",
    )
    if isinstance(previous_snapshot, ConfluencePageSnapshot) and _source_snapshot_identity(
        previous_snapshot
    ) != _source_snapshot_identity(snapshot):
        invalidate_analysis_for_input_change(state, "The Confluence source snapshot changed.")
    state[SOLUTION_INTENT_WIDGET_KEY] = snapshot.canonical_text
    state[TRANSCRIPT_WIDGET_KEY] = normalized_transcript
    state[LOADED_KEY] = True
    state[PROJECT_CONTEXT_CONFIRMED_KEY] = False
    state[DRAFT_CONFIRMED_KEY] = False
    state[ERROR_KEY] = None
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE


def record_internal_source_load_failure(state: MutableMapping[str, Any]) -> None:
    """Clear an unusable source so prior eligibility cannot survive a load failure."""
    state[CONFLUENCE_SNAPSHOT_KEY] = None
    existing_transcript = state.get(TRANSCRIPT_KEY)
    transcript = existing_transcript if isinstance(existing_transcript, str) else ""
    update_review_inputs(
        state,
        solution_intent="",
        transcript=transcript,
        context=None,
        reason="The internal source could not be loaded.",
    )
    state[SOLUTION_INTENT_WIDGET_KEY] = ""
    state[LOADED_KEY] = False
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE


def load_drafting_context_into_state(
    state: MutableMapping[str, Any],
    sample: DraftingSampleContext,
) -> None:
    """Populate synthetic drafting context and clear a previous draft result."""
    state[PROJECT_CONTEXT_KEY] = sample
    state[PROJECT_CONTEXT_CONFIRMED_KEY] = True
    state[DRAFT_PROJECT_KEY] = sample.project_name
    state[DRAFT_TEMPLATE_KEY] = sample.template
    state[DRAFT_SOURCE_CODE_KEY] = sample.source_code_context
    state[DRAFT_SUPPORTING_DOCS_KEY] = sample.supporting_documents
    state[DRAFT_PROJECT_WIDGET_KEY] = sample.project_name
    state[DRAFT_TEMPLATE_WIDGET_KEY] = sample.template
    state[DRAFT_SOURCE_CODE_WIDGET_KEY] = sample.source_code_context
    state[DRAFT_SUPPORTING_DOCS_WIDGET_KEY] = sample.supporting_documents
    state[DRAFT_CONTENT_WIDGET_KEY] = ""
    state[DRAFT_RESULT_KEY] = None
    state[DRAFT_FINGERPRINT_KEY] = None
    state[DRAFT_CONFIRMED_KEY] = False
    state[ERROR_KEY] = None
    state[ACTIVE_STAGE_KEY] = DRAFT_STAGE


def open_demonstration_project_into_state(
    state: MutableMapping[str, Any],
    sample: DraftingSampleContext,
) -> None:
    """Open the synthetic workspace without pretending to connect externally."""
    update_review_inputs(
        state,
        solution_intent="",
        transcript="",
        context=None,
        reason="The project workspace changed the review inputs.",
    )
    state[PROJECT_CONTEXT_KEY] = sample
    state[PROJECT_CONTEXT_CONFIRMED_KEY] = False
    state[PROJECT_CONTEXT_REFRESHED_KEY] = False
    state[CONTEXT_TEMPLATE_SELECTED_KEY] = True
    state[CONTEXT_REPOSITORY_SELECTED_KEY] = True
    state[CONTEXT_SUPPORTING_SELECTED_KEY] = True
    state[CONTEXT_ADO_SELECTED_KEY] = True
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


def project_context_readiness(state: Mapping[str, Any]) -> tuple[str, ...]:
    """Return concise blockers for the currently selected drafting sources."""
    if not isinstance(state.get(PROJECT_CONTEXT_KEY), DraftingSampleContext):
        return ("Open a demonstration project workspace.",)
    blockers: list[str] = []
    if state.get(CONTEXT_TEMPLATE_SELECTED_KEY) is not True:
        blockers.append("Select the required Solution Intent template.")
    if state.get(CONTEXT_REPOSITORY_SELECTED_KEY) is not True:
        blockers.append("Select the required repository context.")
    return tuple(blockers)


def refresh_project_context(state: MutableMapping[str, Any]) -> None:
    """Record a deterministic local validation of the selected source package."""
    if not isinstance(state.get(PROJECT_CONTEXT_KEY), DraftingSampleContext):
        raise ValueError("Open a demonstration project before refreshing context.")
    state[PROJECT_CONTEXT_REFRESHED_KEY] = True
    state[ERROR_KEY] = None
    state[ACTIVE_STAGE_KEY] = CONTEXT_STAGE


def confirm_project_context_for_drafting(state: MutableMapping[str, Any]) -> None:
    """Confirm selected synthetic sources and hand them to SI drafting."""
    blockers = project_context_readiness(state)
    if blockers:
        raise ValueError(" ".join(blockers))
    sample = state[PROJECT_CONTEXT_KEY]
    if not isinstance(sample, DraftingSampleContext):
        raise ValueError("Open a demonstration project workspace.")
    selected_sample = replace(
        sample,
        supporting_documents=(
            sample.supporting_documents
            if state.get(CONTEXT_SUPPORTING_SELECTED_KEY) is True
            else ""
        ),
    )
    load_drafting_context_into_state(state, selected_sample)
    state[PROJECT_CONTEXT_REFRESHED_KEY] = True
    state[PROJECT_CONTEXT_CONFIRMED_KEY] = True


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


def drafting_input_fingerprint(request: SolutionIntentDraftRequest) -> str:
    """Create a stable fingerprint for SI-drafting inputs."""
    return hashlib.sha256(request.model_dump_json().encode("utf-8")).hexdigest()


def drafting_result_is_stale(
    request: SolutionIntentDraftRequest,
    generated_fingerprint: str | None,
) -> bool:
    """Return whether drafting context changed after generation."""
    if generated_fingerprint is None:
        return False
    return drafting_input_fingerprint(request) != generated_fingerprint


def clear_stale_si_draft(state: MutableMapping[str, Any]) -> None:
    """Discard a generated draft after its source context changes."""
    state[DRAFT_RESULT_KEY] = None
    state[DRAFT_FINGERPRINT_KEY] = None
    state[DRAFT_CONTENT_WIDGET_KEY] = ""
    state[DRAFT_CONFIRMED_KEY] = False


def confirm_si_draft_for_review(
    state: MutableMapping[str, Any],
    confirmed_content: str,
) -> None:
    """Hand a non-empty human-confirmed SI draft to existing Review Inputs."""
    normalized = confirmed_content.strip()
    if not normalized:
        raise ValueError("Confirmed Solution Intent must not be blank.")
    update_review_inputs(
        state,
        solution_intent=normalized,
        transcript="",
        context=None,
        reason="The confirmed Solution Intent changed the review inputs.",
    )
    state[SOLUTION_INTENT_WIDGET_KEY] = normalized
    state[TRANSCRIPT_WIDGET_KEY] = ""
    state[LOADED_KEY] = False
    state[DRAFT_CONFIRMED_KEY] = True
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE


def load_sample_review_companions_into_state(
    state: MutableMapping[str, Any],
    sample: SampleReview,
) -> None:
    """Load transcript and metadata while preserving the current confirmed SI."""
    solution_intent = str(state.get(SOLUTION_INTENT_KEY, "")).strip()
    if not solution_intent:
        raise ValueError("Confirm or enter a Solution Intent before loading review companions.")
    update_review_inputs(
        state,
        solution_intent=solution_intent,
        transcript=sample.transcript,
        context=sample.context.model_copy(deep=True),
        reason="The review transcript or metadata changed.",
    )
    state[SOLUTION_INTENT_WIDGET_KEY] = solution_intent
    state[TRANSCRIPT_WIDGET_KEY] = sample.transcript
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
    clear_publication_preview(state)
    state[OUTPUT_SUCCESS_KEY] = False


def reset_application_state(state: MutableMapping[str, Any]) -> None:
    """Reset local workflow data while retaining remote-result reconciliation facts."""
    publication_history = state.get(ADO_PUBLICATION_HISTORY_KEY)
    retained_history = dict(publication_history) if isinstance(publication_history, Mapping) else {}
    retained_operation = state.get(ADO_PUBLICATION_OPERATION_KEY)
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
    """Return the current valid route stage, defaulting safely to Project Context."""
    value = state.get(ACTIVE_STAGE_KEY)
    return value if isinstance(value, str) and value in VALID_STAGES else CONTEXT_STAGE


def set_active_stage(state: MutableMapping[str, Any], stage: str) -> None:
    """Record a validated routed workflow stage."""
    if stage not in VALID_STAGES:
        raise ValueError(f"Unknown application stage: {stage}")
    state[ACTIVE_STAGE_KEY] = stage


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
    """Fingerprint current review inputs with their source and provider identity."""
    solution_intent = state.get(SOLUTION_INTENT_KEY)
    transcript = state.get(TRANSCRIPT_KEY)
    if not isinstance(solution_intent, str) or not isinstance(transcript, str):
        raise ValueError("Review inputs are incomplete.")
    snapshot_value = state.get(CONFLUENCE_SNAPSHOT_KEY)
    snapshot = snapshot_value if isinstance(snapshot_value, ConfluencePageSnapshot) else None
    provider_identity = state.get(REVIEW_PROVIDER_CONFIGURATION_ID_KEY)
    if not isinstance(provider_identity, str) or not provider_identity.strip():
        raise ValueError("Review provider configuration is missing.")
    return input_fingerprint(
        solution_intent,
        transcript,
        context,
        mode=current_review_mode(state),
        source_snapshot=snapshot,
        provider_configuration_identity=provider_identity,
    )


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
                "due_date": item.due_date.isoformat() if item.due_date else "",
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
    if not isinstance(value, str):
        raise ValueError(f"Reviewed field '{field}' must be text.")
    return value


def _required_text(edit: Mapping[str, object], field: str) -> str:
    return _text(edit, field)
