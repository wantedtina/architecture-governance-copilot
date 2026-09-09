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
    ACTIVE_STAGE_KEY,
    ANALYSIS_INVALIDATION_KEY,
    ANALYSIS_SUCCESS_KEY,
    ANALYZED_FINGERPRINT_KEY,
    ANALYZED_RESULT_KEY,
    CONTEXT_KEY,
    CONTEXT_STAGE,
    CONTEXT_SUPPORTING_SELECTED_KEY,
    CONTEXT_TEMPLATE_SELECTED_KEY,
    DRAFT_STAGE,
    ERROR_KEY,
    INPUT_STAGE,
    LOADED_KEY,
    OUTPUT_ACTION_SELECTION_KEY,
    OUTPUT_STAGE,
    OUTPUT_SUCCESS_KEY,
    OUTPUTS_KEY,
    PROJECT_CONTEXT_CONFIRMED_KEY,
    PROJECT_CONTEXT_KEY,
    REVIEW_CHANGE_SUMMARY_KEY,
    REVIEW_DRAFT_KEY,
    REVIEW_STAGE,
    REVIEW_WIDGET_PREFIX,
    REVIEW_WIDGET_VALUES_KEY,
    REVIEWED_RESULT_KEY,
    SOLUTION_INTENT_KEY,
    SOLUTION_INTENT_WIDGET_KEY,
    TRANSCRIPT_KEY,
    TRANSCRIPT_WIDGET_KEY,
    AnalysisInvalidation,
    active_stage,
    analysis_is_stale,
    build_review_change_summary,
    build_reviewed_result,
    clear_outputs,
    confirm_project_context_for_drafting,
    current_analysis_invalidation,
    default_review_form_data,
    humanize,
    initialize_session_state,
    input_fingerprint,
    load_sample_drafting_context,
    load_sample_into_state,
    load_sample_review,
    open_demonstration_project_into_state,
    optional_text,
    parse_optional_iso_date,
    prepare_analysis_attempt,
    preserve_review_widget_state,
    project_context_readiness,
    reset_application_state,
    restore_review_widget_state,
    sample_paths,
    set_active_stage,
    store_analysis,
    store_outputs,
    update_review_inputs,
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


def test_project_context_open_readiness_and_confirmation() -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample = load_sample_drafting_context()

    assert project_context_readiness(state) == ("Open a demonstration project workspace.",)

    open_demonstration_project_into_state(state, sample)

    assert state[PROJECT_CONTEXT_KEY] == sample
    assert state[PROJECT_CONTEXT_CONFIRMED_KEY] is False
    assert state[ACTIVE_STAGE_KEY] == CONTEXT_STAGE
    assert project_context_readiness(state) == ()

    state[CONTEXT_TEMPLATE_SELECTED_KEY] = False
    assert project_context_readiness(state) == ("Select the required Solution Intent template.",)
    state[CONTEXT_TEMPLATE_SELECTED_KEY] = True
    state[CONTEXT_SUPPORTING_SELECTED_KEY] = False

    confirm_project_context_for_drafting(state)

    assert state[PROJECT_CONTEXT_CONFIRMED_KEY] is True
    assert state[ACTIVE_STAGE_KEY] == DRAFT_STAGE
    assert state["agc_draft_project"] == sample.project_name
    assert state["agc_draft_supporting_docs"] == ""


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


def test_loading_sample_invalidates_previous_outputs_and_review_widgets(
    sample_result: GovernanceResult,
) -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    state[ANALYZED_RESULT_KEY] = sample_result
    state[REVIEWED_RESULT_KEY] = sample_result
    state[OUTPUTS_KEY] = object()
    state[f"{REVIEW_WIDGET_PREFIX}finding_0_title"] = "Old edit"
    state[SOLUTION_INTENT_WIDGET_KEY] = ""
    state[TRANSCRIPT_WIDGET_KEY] = ""
    sample = load_sample_review()

    load_sample_into_state(state, sample)

    assert state[SOLUTION_INTENT_KEY] == sample.solution_intent
    assert state[TRANSCRIPT_KEY] == sample.transcript
    assert state[CONTEXT_KEY] == sample.context
    assert state[CONTEXT_KEY] is not sample.context
    assert state[ANALYZED_RESULT_KEY] is sample_result
    assert state[REVIEWED_RESULT_KEY] is None
    assert state[OUTPUTS_KEY] is None
    invalidation = state[ANALYSIS_INVALIDATION_KEY]
    assert isinstance(invalidation, AnalysisInvalidation)
    assert invalidation.outputs_invalidated is True
    assert invalidation.reason == "The sample review package changed the review inputs."
    assert state[ANALYSIS_SUCCESS_KEY] is False
    assert state[LOADED_KEY] is True
    assert state[ACTIVE_STAGE_KEY] == INPUT_STAGE
    assert state[SOLUTION_INTENT_WIDGET_KEY] == sample.solution_intent
    assert state[TRANSCRIPT_WIDGET_KEY] == sample.transcript
    assert f"{REVIEW_WIDGET_PREFIX}finding_0_title" not in state


def test_real_input_change_without_outputs_invalidates_only_analysis(
    sample_result: GovernanceResult,
) -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample = load_sample_review()
    load_sample_into_state(state, sample)
    store_analysis(
        state,
        sample_result,
        input_fingerprint(sample.solution_intent, sample.transcript, sample.context),
    )
    state[f"{REVIEW_WIDGET_PREFIX}action_0_owner"] = "Taylor Kim"

    changed = update_review_inputs(
        state,
        solution_intent=f"{sample.solution_intent}\nEdited",
        transcript=sample.transcript,
        context=sample.context,
        reason="The Solution Intent changed.",
    )

    assert changed is True
    invalidation = state[ANALYSIS_INVALIDATION_KEY]
    assert isinstance(invalidation, AnalysisInvalidation)
    assert invalidation.reason == "The Solution Intent changed."
    assert invalidation.outputs_invalidated is False
    assert state[ANALYZED_RESULT_KEY] is sample_result
    assert state[REVIEW_DRAFT_KEY] is not None
    assert state[REVIEWED_RESULT_KEY] is None
    assert state[REVIEW_CHANGE_SUMMARY_KEY] is None
    assert state[OUTPUTS_KEY] is None
    assert state[ANALYSIS_SUCCESS_KEY] is False
    assert state[OUTPUT_SUCCESS_KEY] is False
    assert f"{REVIEW_WIDGET_PREFIX}action_0_owner" not in state


def test_noop_input_update_does_not_invalidate_analysis(
    sample_result: GovernanceResult,
) -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample = load_sample_review()
    load_sample_into_state(state, sample)
    store_analysis(
        state,
        sample_result,
        input_fingerprint(sample.solution_intent, sample.transcript, sample.context),
    )

    changed = update_review_inputs(
        state,
        solution_intent=sample.solution_intent,
        transcript=sample.transcript,
        context=sample.context,
    )

    assert changed is False
    assert current_analysis_invalidation(state) is None
    assert state[ANALYSIS_SUCCESS_KEY] is True


def test_edit_revert_and_failed_attempt_do_not_restore_confirmation_eligibility(
    sample_result: GovernanceResult,
) -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample = load_sample_review()
    load_sample_into_state(state, sample)
    fingerprint = input_fingerprint(sample.solution_intent, sample.transcript, sample.context)
    store_analysis(state, sample_result, fingerprint)

    update_review_inputs(
        state,
        solution_intent=f"{sample.solution_intent}\nEdited",
        transcript=sample.transcript,
        context=sample.context,
    )
    update_review_inputs(
        state,
        solution_intent=sample.solution_intent,
        transcript=sample.transcript,
        context=sample.context,
    )
    prepare_analysis_attempt(state)

    assert isinstance(current_analysis_invalidation(state), AnalysisInvalidation)
    assert state[ANALYZED_RESULT_KEY] is sample_result
    assert state[ANALYSIS_SUCCESS_KEY] is False

    store_analysis(state, sample_result, fingerprint)

    assert current_analysis_invalidation(state) is None
    assert state[ANALYSIS_SUCCESS_KEY] is True


def test_missing_metadata_invalidates_an_existing_analysis(
    sample_result: GovernanceResult,
) -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample = load_sample_review()
    load_sample_into_state(state, sample)
    store_analysis(
        state,
        sample_result,
        input_fingerprint(sample.solution_intent, sample.transcript, sample.context),
    )

    state[CONTEXT_KEY] = None

    invalidation = current_analysis_invalidation(state)
    assert isinstance(invalidation, AnalysisInvalidation)
    assert invalidation.outputs_invalidated is False
    assert state[ANALYSIS_SUCCESS_KEY] is False


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
    assert state[ACTIVE_STAGE_KEY] == REVIEW_STAGE


def test_review_widget_values_are_preserved_across_routed_pages() -> None:
    widget_key = f"{REVIEW_WIDGET_PREFIX}action_0_owner"
    state: dict[str, object] = {widget_key: "Taylor Kim"}
    initialize_session_state(state)

    preserve_review_widget_state(state)
    del state[widget_key]
    restore_review_widget_state(state)

    assert state[REVIEW_WIDGET_VALUES_KEY] == {widget_key: "Taylor Kim"}
    assert state[widget_key] == "Taylor Kim"


def test_reset_removes_application_state_and_restores_initial_values() -> None:
    state: dict[str, object] = {
        SOLUTION_INTENT_KEY: "old SI",
        OUTPUTS_KEY: object(),
        ANALYSIS_INVALIDATION_KEY: AnalysisInvalidation(
            reason="Inputs changed.",
            outputs_invalidated=True,
        ),
        f"{REVIEW_WIDGET_PREFIX}action_0_owner": "Old owner",
        "unrelated": "preserved",
    }

    reset_application_state(state)

    assert state[SOLUTION_INTENT_KEY] == ""
    assert state[OUTPUTS_KEY] is None
    assert state[ANALYSIS_INVALIDATION_KEY] is None
    assert state[ACTIVE_STAGE_KEY] == CONTEXT_STAGE
    assert f"{REVIEW_WIDGET_PREFIX}action_0_owner" not in state
    assert state["unrelated"] == "preserved"


def test_active_stage_navigation_accepts_only_known_route_stages() -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)

    assert active_stage(state) == CONTEXT_STAGE
    set_active_stage(state, REVIEW_STAGE)
    assert active_stage(state) == REVIEW_STAGE
    set_active_stage(state, OUTPUT_STAGE)
    assert active_stage(state) == OUTPUT_STAGE

    state[ACTIVE_STAGE_KEY] = "corrupt"
    assert active_stage(state) == CONTEXT_STAGE
    with pytest.raises(ValueError, match="Unknown application stage"):
        set_active_stage(state, "later_phase")


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


def test_review_change_summary_covers_every_editable_field_after_normalization(
    sample_result: GovernanceResult,
) -> None:
    defaults = default_review_form_data(sample_result)
    decisions = _editable_mappings(defaults.decisions)
    findings = _editable_mappings(defaults.findings)
    risks = _editable_mappings(defaults.risks)
    actions = _editable_mappings(defaults.action_items)
    questions = _editable_mappings(defaults.open_questions)
    missing = _editable_mappings(defaults.missing_evidence)

    decisions[0].update({"statement": "Updated decision", "rationale": " "})
    findings[0].update(
        {
            "title": "Updated finding",
            "description": "Updated description",
            "category": " ",
            "si_section": "Operations",
            "severity": "critical",
            "status": "deferred",
            "recommended_change": "Updated recommendation",
            "owner": "Morgan Rivera",
            "due_date": "",
        }
    )
    risks[0].update(
        {
            "description": "Updated risk",
            "severity": "medium",
            "owner": "Risk Owner",
        }
    )
    actions[0].update(
        {
            "title": "Updated action",
            "owner": "Taylor Kim",
            "due_date": "2026-07-30",
            "priority": "medium",
        }
    )
    questions[0].update({"question": "Updated question?", "owner": "Question Owner"})
    missing[0].update({"item": "Updated evidence request", "reason": " "})
    form_data = replace(
        defaults,
        review_outcome="conditionally_approved",
        decisions=tuple(decisions),
        findings=tuple(findings),
        risks=tuple(risks),
        action_items=tuple(actions),
        open_questions=tuple(questions),
        missing_evidence=tuple(missing),
    )

    reviewed = build_reviewed_result(sample_result, form_data)
    summary = build_review_change_summary(sample_result, reviewed, form_data)

    assert summary.has_changes
    assert summary.excluded_items == ()
    assert {(change.collection, change.field) for change in summary.field_changes} == {
        ("Review", "Outcome"),
        ("Decision", "Statement"),
        ("Decision", "Rationale"),
        ("Finding", "Title"),
        ("Finding", "Description"),
        ("Finding", "Category"),
        ("Finding", "SI section"),
        ("Finding", "Severity"),
        ("Finding", "Status"),
        ("Finding", "Recommended change"),
        ("Finding", "Owner"),
        ("Finding", "Due date"),
        ("Risk", "Description"),
        ("Risk", "Severity"),
        ("Risk", "Owner"),
        ("Action item", "Title"),
        ("Action item", "Owner"),
        ("Action item", "Due date"),
        ("Action item", "Priority"),
        ("Open question", "Question"),
        ("Open question", "Owner"),
        ("Missing information", "Item"),
        ("Missing information", "Reason"),
    }
    category_change = next(
        change
        for change in summary.field_changes
        if change.collection == "Finding" and change.field == "Category"
    )
    assert category_change.before == "Resilience"
    assert category_change.after is None
    assert reviewed.findings[0].evidence == sample_result.findings[0].evidence
    assert all(change.field != "Evidence" for change in summary.field_changes)


def test_review_change_summary_ignores_equivalent_normalized_values(
    sample_result: GovernanceResult,
) -> None:
    defaults = default_review_form_data(sample_result)
    decisions = _editable_mappings(defaults.decisions)
    findings = _editable_mappings(defaults.findings)
    risks = _editable_mappings(defaults.risks)
    actions = _editable_mappings(defaults.action_items)
    questions = _editable_mappings(defaults.open_questions)
    decisions[0]["statement"] = f"  {sample_result.decisions[0].statement}  "
    findings[2]["owner"] = " "
    findings[2]["due_date"] = " "
    risks[0]["owner"] = " "
    actions[0]["due_date"] = " 2026-07-24 "
    questions[0]["owner"] = " "
    form_data = replace(
        defaults,
        decisions=tuple(decisions),
        findings=tuple(findings),
        risks=tuple(risks),
        action_items=tuple(actions),
        open_questions=tuple(questions),
    )

    reviewed = build_reviewed_result(sample_result, form_data)
    summary = build_review_change_summary(sample_result, reviewed, form_data)

    assert not summary.has_changes
    assert summary.field_changes == ()
    assert summary.excluded_items == ()


def test_review_change_summary_reports_only_original_names_for_excluded_items(
    sample_result: GovernanceResult,
) -> None:
    defaults = default_review_form_data(sample_result)
    replacements: dict[str, tuple[dict[str, object], ...]] = {}
    for attribute in (
        "decisions",
        "findings",
        "risks",
        "action_items",
        "open_questions",
        "missing_evidence",
    ):
        edits = _editable_mappings(getattr(defaults, attribute))
        for edit in edits:
            edit["include"] = False
        replacements[attribute] = tuple(edits)
    replacements["findings"][0]["title"] = "Ignored edited title"
    replacements["findings"][0]["due_date"] = "not a date"
    form_data = replace(defaults, **replacements)

    reviewed = build_reviewed_result(sample_result, form_data)
    summary = build_review_change_summary(sample_result, reviewed, form_data)

    assert not reviewed.decisions
    assert not reviewed.findings
    assert not reviewed.risks
    assert not reviewed.action_items
    assert not reviewed.open_questions
    assert not reviewed.missing_evidence
    assert summary.field_changes == ()
    assert len(summary.excluded_items) == 10
    assert summary.excluded_items[1].item_name == sample_result.findings[0].title
    assert all(item.item_name != "Ignored edited title" for item in summary.excluded_items)


def test_review_change_summary_distinguishes_duplicate_titles_by_original_position(
    sample_result: GovernanceResult,
) -> None:
    duplicate_title = sample_result.action_items[0].title
    duplicate_result = sample_result.model_copy(
        update={
            "action_items": [
                sample_result.action_items[0].model_copy(deep=True),
                sample_result.action_items[1].model_copy(
                    update={"title": duplicate_title},
                    deep=True,
                ),
            ]
        },
        deep=True,
    )
    defaults = default_review_form_data(duplicate_result)
    actions = _editable_mappings(defaults.action_items)
    actions[0]["owner"] = "First Owner"
    actions[1]["owner"] = "Second Owner"
    form_data = replace(defaults, action_items=tuple(actions))

    reviewed = build_reviewed_result(duplicate_result, form_data)
    summary = build_review_change_summary(duplicate_result, reviewed, form_data)
    owner_changes = [
        change
        for change in summary.field_changes
        if change.collection == "Action item" and change.field == "Owner"
    ]

    assert [change.item_index for change in owner_changes] == [0, 1]
    assert [change.item_name for change in owner_changes] == [duplicate_title, duplicate_title]
    assert [change.after for change in owner_changes] == ["First Owner", "Second Owner"]


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
    form_data = default_review_form_data(sample_result)
    change_summary = build_review_change_summary(sample_result, sample_result, form_data)
    state: dict[str, object] = {ERROR_KEY: "old error"}
    initialize_session_state(state)

    store_outputs(state, sample_result, change_summary, outputs)

    assert state[REVIEWED_RESULT_KEY] is sample_result
    assert state[REVIEW_CHANGE_SUMMARY_KEY] is change_summary
    assert state[OUTPUTS_KEY] is outputs
    assert state[OUTPUT_ACTION_SELECTION_KEY] == 0
    assert state[OUTPUT_SUCCESS_KEY] is True
    assert state[ACTIVE_STAGE_KEY] == OUTPUT_STAGE
    assert state[ERROR_KEY] is None

    clear_outputs(state)

    assert state[REVIEWED_RESULT_KEY] is None
    assert state[REVIEW_CHANGE_SUMMARY_KEY] is None
    assert state[OUTPUTS_KEY] is None
    assert state[OUTPUT_ACTION_SELECTION_KEY] is None
    assert state[OUTPUT_SUCCESS_KEY] is False
