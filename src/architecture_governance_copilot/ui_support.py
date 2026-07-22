"""Pure support functions for the routed Streamlit proof of concept."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from typing import Any

from architecture_governance_copilot.governance_service import GovernanceOutputs
from architecture_governance_copilot.models import (
    GovernanceResult,
    SolutionIntentDraft,
    SolutionIntentDraftRequest,
    SolutionIntentReviewContext,
    SourceEvidence,
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
OUTPUTS_KEY = f"{STATE_PREFIX}generated_outputs"
ANALYZED_FINGERPRINT_KEY = f"{STATE_PREFIX}analyzed_fingerprint"
ERROR_KEY = f"{STATE_PREFIX}error"
LOADED_KEY = f"{STATE_PREFIX}sample_loaded"
ANALYSIS_SUCCESS_KEY = f"{STATE_PREFIX}analysis_success"
OUTPUT_SUCCESS_KEY = f"{STATE_PREFIX}output_success"
ACTIVE_STAGE_KEY = f"{STATE_PREFIX}active_stage"

CONTEXT_STAGE = "context"
DRAFT_STAGE = "drafting"
INPUT_STAGE = "inputs"
REVIEW_STAGE = "review"
OUTPUT_STAGE = "outputs"
VALID_STAGES = frozenset({CONTEXT_STAGE, DRAFT_STAGE, INPUT_STAGE, REVIEW_STAGE, OUTPUT_STAGE})


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
        OUTPUTS_KEY: None,
        ANALYZED_FINGERPRINT_KEY: None,
        ERROR_KEY: None,
        LOADED_KEY: False,
        ANALYSIS_SUCCESS_KEY: False,
        OUTPUT_SUCCESS_KEY: False,
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
    """Clear analysis, reviewed records, outputs, and related messages."""
    clear_review_widget_state(state)
    state[ANALYZED_RESULT_KEY] = None
    state[REVIEW_DRAFT_KEY] = None
    state[REVIEWED_RESULT_KEY] = None
    state[OUTPUTS_KEY] = None
    state[ANALYZED_FINGERPRINT_KEY] = None
    state[ERROR_KEY] = None
    state[ANALYSIS_SUCCESS_KEY] = False
    state[OUTPUT_SUCCESS_KEY] = False
    state[ACTIVE_STAGE_KEY] = INPUT_STAGE


def load_sample_into_state(
    state: MutableMapping[str, Any],
    sample: SampleReview,
) -> None:
    """Populate sample inputs while invalidating all previous derived state."""
    clear_analysis_state(state)
    state[SOLUTION_INTENT_KEY] = sample.solution_intent
    state[TRANSCRIPT_KEY] = sample.transcript
    state[SOLUTION_INTENT_WIDGET_KEY] = sample.solution_intent
    state[TRANSCRIPT_WIDGET_KEY] = sample.transcript
    state[CONTEXT_KEY] = sample.context.model_copy(deep=True)
    state[LOADED_KEY] = True
    state[PROJECT_CONTEXT_CONFIRMED_KEY] = False
    state[DRAFT_CONFIRMED_KEY] = False


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
    clear_analysis_state(state)
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
    state[SOLUTION_INTENT_KEY] = ""
    state[TRANSCRIPT_KEY] = ""
    state[CONTEXT_KEY] = None
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
    clear_analysis_state(state)
    state[SOLUTION_INTENT_KEY] = normalized
    state[SOLUTION_INTENT_WIDGET_KEY] = normalized
    state[TRANSCRIPT_KEY] = ""
    state[TRANSCRIPT_WIDGET_KEY] = ""
    state[CONTEXT_KEY] = None
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
    clear_analysis_state(state)
    state[SOLUTION_INTENT_KEY] = solution_intent
    state[SOLUTION_INTENT_WIDGET_KEY] = solution_intent
    state[TRANSCRIPT_KEY] = sample.transcript
    state[TRANSCRIPT_WIDGET_KEY] = sample.transcript
    state[CONTEXT_KEY] = sample.context.model_copy(deep=True)
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
    state[OUTPUTS_KEY] = None
    state[ANALYZED_FINGERPRINT_KEY] = fingerprint
    state[ERROR_KEY] = None
    state[ANALYSIS_SUCCESS_KEY] = True
    state[OUTPUT_SUCCESS_KEY] = False
    state[ACTIVE_STAGE_KEY] = REVIEW_STAGE


def store_outputs(
    state: MutableMapping[str, Any],
    reviewed_result: GovernanceResult,
    outputs: GovernanceOutputs,
) -> None:
    """Store validated reviewed data and its generated outputs."""
    state[REVIEWED_RESULT_KEY] = reviewed_result
    state[OUTPUTS_KEY] = outputs
    state[ERROR_KEY] = None
    state[OUTPUT_SUCCESS_KEY] = True
    state[ACTIVE_STAGE_KEY] = OUTPUT_STAGE


def clear_outputs(state: MutableMapping[str, Any]) -> None:
    """Clear reviewed and generated output state after an invalid submission."""
    state[REVIEWED_RESULT_KEY] = None
    state[OUTPUTS_KEY] = None
    state[OUTPUT_SUCCESS_KEY] = False


def reset_application_state(state: MutableMapping[str, Any]) -> None:
    """Remove every application-owned value and restore the initial state."""
    for key in tuple(state):
        if key.startswith(STATE_PREFIX):
            del state[key]
    initialize_session_state(state)
    state[DRAFT_PROJECT_WIDGET_KEY] = ""
    state[DRAFT_TEMPLATE_WIDGET_KEY] = ""
    state[DRAFT_SOURCE_CODE_WIDGET_KEY] = ""
    state[DRAFT_SUPPORTING_DOCS_WIDGET_KEY] = ""
    state[DRAFT_CONTENT_WIDGET_KEY] = ""
    state[SOLUTION_INTENT_WIDGET_KEY] = ""
    state[TRANSCRIPT_WIDGET_KEY] = ""


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
) -> str:
    """Create a stable fingerprint for the current analyzed inputs."""
    digest = hashlib.sha256()
    for value in (solution_intent, transcript, context.model_dump_json()):
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def analysis_is_stale(
    solution_intent: str,
    transcript: str,
    context: SolutionIntentReviewContext | None,
    analyzed_fingerprint: str | None,
) -> bool:
    """Return whether current inputs differ from a previous analysis."""
    if analyzed_fingerprint is None:
        return False
    if context is None:
        return True
    return input_fingerprint(solution_intent, transcript, context) != analyzed_fingerprint


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
