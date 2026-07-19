"""Pure support functions for the routed Streamlit proof of concept."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from architecture_governance_copilot.governance_service import GovernanceOutputs
from architecture_governance_copilot.models import (
    GovernanceResult,
    SolutionIntentReviewContext,
    SourceEvidence,
)

STATE_PREFIX = "agc_"
REVIEW_WIDGET_PREFIX = f"{STATE_PREFIX}field_"

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

INPUT_STAGE = "inputs"
REVIEW_STAGE = "review"
OUTPUT_STAGE = "outputs"
VALID_STAGES = frozenset({INPUT_STAGE, REVIEW_STAGE, OUTPUT_STAGE})


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
        ACTIVE_STAGE_KEY: INPUT_STAGE,
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
    state[SOLUTION_INTENT_WIDGET_KEY] = ""
    state[TRANSCRIPT_WIDGET_KEY] = ""


def active_stage(state: Mapping[str, Any]) -> str:
    """Return the current valid route stage, defaulting safely to inputs."""
    value = state.get(ACTIVE_STAGE_KEY)
    return value if isinstance(value, str) and value in VALID_STAGES else INPUT_STAGE


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
