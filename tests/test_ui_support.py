"""Tests for pure Streamlit UI support and reviewed-result reconstruction."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from architecture_governance_copilot.extractors import DeterministicDemoExtractor
from architecture_governance_copilot.governance_service import GovernanceReviewService
from architecture_governance_copilot.models import GovernanceResult
from architecture_governance_copilot.ui_support import (
    ANALYSIS_SUCCESS_KEY,
    ANALYZED_FINGERPRINT_KEY,
    ANALYZED_RESULT_KEY,
    CONTEXT_KEY,
    ERROR_KEY,
    LOADED_KEY,
    OUTPUT_SUCCESS_KEY,
    OUTPUTS_KEY,
    REVIEW_DRAFT_KEY,
    REVIEW_WIDGET_PREFIX,
    REVIEWED_RESULT_KEY,
    SOLUTION_INTENT_KEY,
    TRANSCRIPT_KEY,
    analysis_is_stale,
    build_reviewed_result,
    clear_outputs,
    default_review_form_data,
    humanize,
    initialize_session_state,
    input_fingerprint,
    load_sample_into_state,
    load_sample_review,
    optional_text,
    parse_optional_iso_date,
    reset_application_state,
    sample_paths,
    store_analysis,
    store_outputs,
)


@pytest.fixture
def sample_result() -> GovernanceResult:
    """Load the validated expected result through the deterministic extractor."""
    sample = load_sample_review()
    return DeterministicDemoExtractor().extract(
        sample.solution_intent,
        sample.transcript,
        sample.context,
    )


def _editable_mappings(
    values: tuple[object, ...],
) -> list[dict[str, object]]:
    return [dict(value) for value in values if isinstance(value, dict)]


def test_sample_paths_are_absolute_and_independent_of_working_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    expected = sample_paths()

    monkeypatch.chdir(tmp_path)
    actual = sample_paths()

    assert actual == expected
    assert actual.solution_intent.is_absolute()
    assert actual.solution_intent.is_file()
    assert actual.transcript.is_file()
    assert actual.metadata.is_file()


def test_sample_loading_returns_validated_bundled_inputs() -> None:
    sample = load_sample_review()

    assert sample.solution_intent.startswith("# Solution Intent")
    assert "[10:00] Priya Shah:" in sample.transcript
    assert sample.context.project_name == "Digital Payment Notification Service"
    assert sample.context.review_round == 2


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("changes_requested", "Changes Requested"),
        ("under_review", "Under Review"),
        ("high", "High"),
    ],
)
def test_humanize_returns_readable_labels(value: str, expected: str) -> None:
    assert humanize(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", None),
        ("   ", None),
        ("  Morgan Rivera  ", "Morgan Rivera"),
    ],
)
def test_optional_text_normalization(value: str, expected: str | None) -> None:
    assert optional_text(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", None),
        ("   ", None),
        ("2026-07-30", date(2026, 7, 30)),
    ],
)
def test_optional_date_parsing(value: str, expected: date | None) -> None:
    assert parse_optional_iso_date(value) == expected


def test_invalid_optional_date_has_concise_message() -> None:
    with pytest.raises(ValueError, match="Use YYYY-MM-DD"):
        parse_optional_iso_date("30 July 2026")


def test_loading_sample_clears_previous_analysis_outputs_and_review_widgets(
    sample_result: GovernanceResult,
) -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    state[ANALYZED_RESULT_KEY] = sample_result
    state[REVIEWED_RESULT_KEY] = sample_result
    state[OUTPUTS_KEY] = object()
    state[f"{REVIEW_WIDGET_PREFIX}finding_0_title"] = "Old edit"
    sample = load_sample_review()

    load_sample_into_state(state, sample)

    assert state[SOLUTION_INTENT_KEY] == sample.solution_intent
    assert state[TRANSCRIPT_KEY] == sample.transcript
    assert state[CONTEXT_KEY] == sample.context
    assert state[CONTEXT_KEY] is not sample.context
    assert state[ANALYZED_RESULT_KEY] is None
    assert state[REVIEWED_RESULT_KEY] is None
    assert state[OUTPUTS_KEY] is None
    assert state[LOADED_KEY] is True
    assert f"{REVIEW_WIDGET_PREFIX}finding_0_title" not in state


def test_storing_analysis_creates_independent_draft_and_clears_outputs(
    sample_result: GovernanceResult,
) -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    state[OUTPUTS_KEY] = object()

    store_analysis(state, sample_result, "fingerprint")

    assert state[ANALYZED_RESULT_KEY] is sample_result
    draft = state[REVIEW_DRAFT_KEY]
    assert isinstance(draft, GovernanceResult)
    assert draft == sample_result
    assert draft is not sample_result
    assert draft.findings[0] is not sample_result.findings[0]
    assert state[OUTPUTS_KEY] is None
    assert state[ANALYZED_FINGERPRINT_KEY] == "fingerprint"
    assert state[ANALYSIS_SUCCESS_KEY] is True


def test_reset_removes_application_state_and_restores_initial_values() -> None:
    state: dict[str, object] = {
        SOLUTION_INTENT_KEY: "old SI",
        OUTPUTS_KEY: object(),
        f"{REVIEW_WIDGET_PREFIX}action_0_owner": "Old owner",
        "unrelated": "preserved",
    }

    reset_application_state(state)

    assert state[SOLUTION_INTENT_KEY] == ""
    assert state[OUTPUTS_KEY] is None
    assert f"{REVIEW_WIDGET_PREFIX}action_0_owner" not in state
    assert state["unrelated"] == "preserved"


def test_input_fingerprint_detects_stale_si_transcript_and_context() -> None:
    sample = load_sample_review()
    fingerprint = input_fingerprint(sample.solution_intent, sample.transcript, sample.context)

    assert not analysis_is_stale(
        sample.solution_intent,
        sample.transcript,
        sample.context,
        fingerprint,
    )
    assert analysis_is_stale(
        f"{sample.solution_intent}\nEdited",
        sample.transcript,
        sample.context,
        fingerprint,
    )
    assert analysis_is_stale(
        sample.solution_intent,
        f"{sample.transcript}\nEdited",
        sample.context,
        fingerprint,
    )
    changed_context = sample.context.model_copy(update={"review_round": 3})
    assert analysis_is_stale(
        sample.solution_intent,
        sample.transcript,
        changed_context,
        fingerprint,
    )


def test_default_review_form_round_trips_without_mutating_analysis(
    sample_result: GovernanceResult,
) -> None:
    before = sample_result.model_dump(mode="json")

    reviewed = build_reviewed_result(sample_result, default_review_form_data(sample_result))

    assert reviewed == sample_result
    assert reviewed is not sample_result
    assert reviewed.findings[0] is not sample_result.findings[0]
    assert reviewed.findings[0].evidence == sample_result.findings[0].evidence
    assert reviewed.findings[0].evidence[0] is not sample_result.findings[0].evidence[0]
    assert sample_result.model_dump(mode="json") == before


def test_reviewed_result_preserves_edits_exclusions_and_evidence(
    sample_result: GovernanceResult,
) -> None:
    before = sample_result.model_dump(mode="json")
    defaults = default_review_form_data(sample_result)
    decisions = _editable_mappings(defaults.decisions)
    findings = _editable_mappings(defaults.findings)
    actions = _editable_mappings(defaults.action_items)
    questions = _editable_mappings(defaults.open_questions)
    decisions[0]["include"] = False
    findings[0].update(
        {
            "title": "Human-reviewed failover finding",
            "category": " ",
            "owner": "Morgan Rivera",
            "due_date": "",
        }
    )
    actions[0]["owner"] = "Taylor Kim"
    actions[1]["include"] = False
    questions[0]["include"] = False
    form_data = replace(
        defaults,
        decisions=tuple(decisions),
        findings=tuple(findings),
        action_items=tuple(actions),
        open_questions=tuple(questions),
    )

    reviewed = build_reviewed_result(sample_result, form_data)

    assert reviewed.decisions == []
    assert len(reviewed.findings) == 3
    assert reviewed.findings[0].title == "Human-reviewed failover finding"
    assert reviewed.findings[0].category is None
    assert reviewed.findings[0].owner == "Morgan Rivera"
    assert reviewed.findings[0].due_date is None
    assert reviewed.findings[0].evidence == sample_result.findings[0].evidence
    assert len(reviewed.action_items) == 1
    assert reviewed.action_items[0].owner == "Taylor Kim"
    assert reviewed.open_questions == []
    assert sample_result.model_dump(mode="json") == before


def test_invalid_reviewed_date_prevents_result_validation(
    sample_result: GovernanceResult,
) -> None:
    defaults = default_review_form_data(sample_result)
    findings = _editable_mappings(defaults.findings)
    findings[0]["due_date"] = "24 July 2026"

    with pytest.raises(ValueError, match="Use YYYY-MM-DD"):
        build_reviewed_result(
            sample_result,
            replace(defaults, findings=tuple(findings)),
        )


def test_outputs_are_generated_from_reviewed_result_and_are_deterministic(
    sample_result: GovernanceResult,
) -> None:
    defaults = default_review_form_data(sample_result)
    actions = _editable_mappings(defaults.action_items)
    questions = _editable_mappings(defaults.open_questions)
    actions[0]["owner"] = "Taylor Kim"
    questions[0]["include"] = False
    reviewed = build_reviewed_result(
        sample_result,
        replace(
            defaults,
            action_items=tuple(actions),
            open_questions=tuple(questions),
        ),
    )
    service = GovernanceReviewService(DeterministicDemoExtractor())

    first = service.generate_outputs(reviewed)
    second = service.generate_outputs(reviewed)

    assert first == second
    assert first.ado_work_items[0].assigned_to == "Taylor Kim"
    assert "Owner: Taylor Kim" in first.ado_work_items[0].description
    assert "Redis" not in first.review_minutes
    assert sample_result.action_items[0].owner == "Alex Chen"


def test_store_and_clear_outputs_manage_only_generated_state(
    sample_result: GovernanceResult,
) -> None:
    service = GovernanceReviewService(DeterministicDemoExtractor())
    outputs = service.generate_outputs(sample_result)
    state: dict[str, object] = {ERROR_KEY: "old error"}
    initialize_session_state(state)

    store_outputs(state, sample_result, outputs)

    assert state[REVIEWED_RESULT_KEY] is sample_result
    assert state[OUTPUTS_KEY] is outputs
    assert state[OUTPUT_SUCCESS_KEY] is True
    assert state[ERROR_KEY] is None

    clear_outputs(state)

    assert state[REVIEWED_RESULT_KEY] is None
    assert state[OUTPUTS_KEY] is None
    assert state[OUTPUT_SUCCESS_KEY] is False
