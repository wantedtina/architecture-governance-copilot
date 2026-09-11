"""Tests for pure Streamlit UI support and reviewed-result reconstruction."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

from architecture_governance_copilot.extractors import DeterministicDemoExtractor
from architecture_governance_copilot.governance_service import GovernanceReviewService
from architecture_governance_copilot.integrations.confluence import (
    ConfluencePagePayload,
    build_confluence_snapshot,
)
from architecture_governance_copilot.models import (
    GovernanceResult,
    ReviewInputProvenance,
)
from architecture_governance_copilot.publication import (
    AdoPublicationOperation,
    PublicationStatus,
)
from architecture_governance_copilot.runtime_dependencies import (
    OFFLINE_PROVIDER_CONFIGURATION_ID,
    ReviewMode,
)
from architecture_governance_copilot.ui_support import (
    ACTIVE_STAGE_KEY,
    ACTIVE_WORKFLOW_KEY,
    ADO_FAKE_GATEWAY_KEY,
    ADO_PUBLICATION_CONFIRMATION_KEY,
    ADO_PUBLICATION_HISTORY_KEY,
    ADO_PUBLICATION_OPERATION_KEY,
    ADO_PUBLICATION_PREVIEW_KEY,
    ANALYSIS_INVALIDATION_KEY,
    ANALYSIS_SUCCESS_KEY,
    ANALYZED_FINGERPRINT_KEY,
    ANALYZED_RESULT_KEY,
    CONFIRMED_SOURCE_PACKAGE_KEY,
    CONFLUENCE_SNAPSHOT_KEY,
    CONTEXT_EVIDENCE_IDS_KEY,
    CONTEXT_KEY,
    CONTEXT_REPOSITORY_ID_KEY,
    CONTEXT_STAGE,
    CONTEXT_TEMPLATE_ID_KEY,
    DRAFT_RESULT_KEY,
    DRAFT_STAGE,
    ERROR_KEY,
    HOME_STAGE,
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
    REVIEW_MODE_KEY,
    REVIEW_PROVIDER_CONFIGURATION_ID_KEY,
    REVIEW_STAGE,
    REVIEW_WIDGET_PREFIX,
    REVIEW_WIDGET_VALUES_KEY,
    REVIEWED_RESULT_KEY,
    SOLUTION_INTENT_KEY,
    SOLUTION_INTENT_WIDGET_KEY,
    STATE_SCHEMA_VERSION_KEY,
    TRANSCRIPT_KEY,
    TRANSCRIPT_WIDGET_KEY,
    AnalysisInvalidation,
    InputReadiness,
    Workflow,
    active_stage,
    analysis_is_stale,
    build_drafting_source_package,
    build_pending_review_changes,
    build_review_change_summary,
    build_reviewed_result,
    build_sample_review_snapshot,
    clear_outputs,
    confirm_project_context_for_drafting,
    confirm_review_input_manifest,
    current_analysis_invalidation,
    current_input_fingerprint,
    current_review_form_data,
    current_review_mode,
    current_workflow,
    default_review_form_data,
    drafting_evidence_is_saved,
    humanize,
    initialize_session_state,
    input_fingerprint,
    load_internal_review_into_state,
    load_sample_drafting_context,
    load_sample_into_state,
    load_sample_review,
    open_demonstration_project_into_state,
    optional_text,
    parse_optional_iso_date,
    prepare_analysis_attempt,
    preserve_review_widget_state,
    project_context_readiness,
    record_internal_source_load_failure,
    refresh_project_context,
    reset_application_state,
    reset_drafting_workflow,
    reset_review_workflow,
    restore_review_widget_state,
    review_input_readiness,
    sample_paths,
    save_drafting_evidence,
    set_active_stage,
    source_package_fingerprint,
    start_workflow,
    store_analysis,
    store_metadata_component,
    store_outputs,
    store_review_source_snapshot,
    store_transcript_component,
    switch_review_mode,
    update_live_drafting_source_package,
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

    state[CONTEXT_TEMPLATE_ID_KEY] = None
    assert project_context_readiness(state) == ("Select the required Solution Intent template.",)
    state[CONTEXT_TEMPLATE_ID_KEY] = "si-template-v1-1"
    state[CONTEXT_EVIDENCE_IDS_KEY] = ()

    assert project_context_readiness(state) == ("Add supporting evidence before continuing.",)
    state[CONTEXT_EVIDENCE_IDS_KEY] = ("supporting-context-v1",)

    confirm_project_context_for_drafting(state)

    assert state[PROJECT_CONTEXT_CONFIRMED_KEY] is True
    assert state[ACTIVE_STAGE_KEY] == DRAFT_STAGE
    assert state["agc_draft_project"] == sample.project_name
    assert state["agc_draft_supporting_docs"] == sample.supporting_documents
    assert state[CONFIRMED_SOURCE_PACKAGE_KEY] is not None


def test_drafting_source_manifest_is_stable_and_rejects_unknown_selection() -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    inventory = load_sample_drafting_context()
    open_demonstration_project_into_state(state, inventory)

    first = build_drafting_source_package(state)
    second = build_drafting_source_package(state)

    assert first == second
    assert source_package_fingerprint(first) == source_package_fingerprint(second)
    assert first.provider_configuration_identity == "deterministic-demo-drafter-v1"
    assert [resource.role.value for resource in first.resources] == [
        "template",
        "repository",
        "supporting_evidence",
    ]

    state[CONTEXT_REPOSITORY_ID_KEY] = "unauthorized-repository"
    update_live_drafting_source_package(state)

    assert project_context_readiness(state) == (
        "Resolve selections that are not in the authorized inventory.",
    )
    assert state[CONFIRMED_SOURCE_PACKAGE_KEY] is None


def test_source_change_invalidates_only_drafting_and_preserves_review_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    inventory = load_sample_drafting_context()
    open_demonstration_project_into_state(state, inventory)
    confirm_project_context_for_drafting(state)
    state[SOLUTION_INTENT_KEY] = "Independent review source"
    operation = AdoPublicationOperation(
        status=PublicationStatus.UNKNOWN_RESULT,
        correlation_id="agc-source-refresh",
        request_binding_fingerprint="binding",
        message="Manual reconciliation is required.",
    )
    state[ADO_PUBLICATION_OPERATION_KEY] = operation

    assert refresh_project_context(state) is False
    assert state[PROJECT_CONTEXT_CONFIRMED_KEY] is True

    changed = inventory.model_copy(update={"governance_reference": "WORK-CHANGED"})
    monkeypatch.setattr(
        "architecture_governance_copilot.ui_support.load_sample_drafting_context",
        lambda: changed,
    )

    assert refresh_project_context(state) is True
    assert state[PROJECT_CONTEXT_CONFIRMED_KEY] is False
    assert state[CONFIRMED_SOURCE_PACKAGE_KEY] is None
    assert state[DRAFT_RESULT_KEY] is None
    assert state[SOLUTION_INTENT_KEY] == "Independent review source"
    assert state[ADO_PUBLICATION_OPERATION_KEY] == operation
    assert state[ACTIVE_STAGE_KEY] == CONTEXT_STAGE


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

    assert state[SOLUTION_INTENT_KEY] == sample.solution_intent.strip()
    assert state[TRANSCRIPT_KEY] == sample.transcript.strip()
    assert state[CONTEXT_KEY] == sample.context
    assert state[CONTEXT_KEY] is not sample.context
    assert state[ANALYZED_RESULT_KEY] is sample_result
    assert state[REVIEWED_RESULT_KEY] is None
    assert state[OUTPUTS_KEY] is None
    invalidation = state[ANALYSIS_INVALIDATION_KEY]
    assert isinstance(invalidation, AnalysisInvalidation)
    assert invalidation.outputs_invalidated is True
    assert invalidation.reason == "The authoritative Solution Intent source changed."
    assert state[ANALYSIS_SUCCESS_KEY] is False
    assert state[LOADED_KEY] is True
    assert state[ACTIVE_STAGE_KEY] == INPUT_STAGE
    assert state[SOLUTION_INTENT_WIDGET_KEY] == sample.solution_intent.strip()
    assert state[TRANSCRIPT_WIDGET_KEY] == sample.transcript.strip()
    assert f"{REVIEW_WIDGET_PREFIX}finding_0_title" not in state


def test_real_input_change_without_outputs_invalidates_only_analysis(
    sample_result: GovernanceResult,
) -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample = load_sample_review()
    load_sample_into_state(state, sample)
    confirm_review_input_manifest(state)
    store_analysis(
        state,
        sample_result,
        current_input_fingerprint(state, sample.context),
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
    confirm_review_input_manifest(state)
    store_analysis(
        state,
        sample_result,
        current_input_fingerprint(state, sample.context),
    )

    changed = update_review_inputs(
        state,
        solution_intent=state[SOLUTION_INTENT_KEY],
        transcript=state[TRANSCRIPT_KEY],
        context=state[CONTEXT_KEY],
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
    confirm_review_input_manifest(state)
    fingerprint = current_input_fingerprint(state, sample.context)
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

    assert isinstance(current_analysis_invalidation(state), AnalysisInvalidation)
    assert state[ANALYSIS_SUCCESS_KEY] is False


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
    state: dict[str, object] = {}
    initialize_session_state(state)
    state[widget_key] = "Taylor Kim"

    preserve_review_widget_state(state)
    del state[widget_key]
    restore_review_widget_state(state)

    assert state[REVIEW_WIDGET_VALUES_KEY] == {widget_key: "Taylor Kim"}
    assert state[widget_key] == "Taylor Kim"


@pytest.mark.parametrize(
    "order",
    [
        ("source", "transcript", "metadata"),
        ("transcript", "metadata", "source"),
        ("metadata", "source", "transcript"),
    ],
)
def test_review_components_are_order_independent_and_require_exact_confirmation(
    order: tuple[str, str, str],
) -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample = load_sample_review()
    snapshot = build_sample_review_snapshot(sample)
    actions = {
        "source": lambda: store_review_source_snapshot(
            state,
            snapshot,
            feedback="Source loaded.",
        ),
        "transcript": lambda: store_transcript_component(
            state,
            sample.transcript,
            ReviewInputProvenance.SYNTHETIC_SAMPLE,
            establish_baseline=True,
        ),
        "metadata": lambda: store_metadata_component(
            state,
            sample.context,
            ReviewInputProvenance.SYNTHETIC_SAMPLE,
            establish_baseline=True,
        ),
    }

    for component in order:
        actions[component]()

    readiness = review_input_readiness(state)
    assert readiness.ready_to_confirm
    assert not readiness.ready_to_analyze
    assert readiness.solution_intent is InputReadiness.LOADED
    assert readiness.transcript is InputReadiness.LOADED
    assert readiness.metadata is InputReadiness.LOADED

    confirm_review_input_manifest(state)

    readiness = review_input_readiness(state)
    assert readiness.ready_to_analyze
    assert readiness.solution_intent is InputReadiness.CONFIRMED
    assert readiness.transcript is InputReadiness.CONFIRMED
    assert readiness.metadata is InputReadiness.CONFIRMED


def test_workflow_scoped_resets_preserve_peer_state_and_remote_reconciliation() -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    state[PROJECT_CONTEXT_KEY] = object()
    state[DRAFT_RESULT_KEY] = object()
    state[SOLUTION_INTENT_KEY] = "review source"
    operation = AdoPublicationOperation(
        status=PublicationStatus.UNKNOWN_RESULT,
        correlation_id="agc-scoped-reset",
        request_binding_fingerprint="binding",
        message="Manual reconciliation is required.",
    )
    state[ADO_PUBLICATION_OPERATION_KEY] = operation

    reset_drafting_workflow(state)

    assert state[PROJECT_CONTEXT_KEY] is None
    assert state[DRAFT_RESULT_KEY] is None
    assert state[SOLUTION_INTENT_KEY] == "review source"
    assert current_workflow(state) is Workflow.DRAFT
    assert state[ADO_PUBLICATION_OPERATION_KEY] == operation

    state[PROJECT_CONTEXT_KEY] = "draft context"
    reset_review_workflow(state)

    assert state[PROJECT_CONTEXT_KEY] == "draft context"
    assert state[SOLUTION_INTENT_KEY] == ""
    assert current_workflow(state) is Workflow.REVIEW
    assert state[ADO_PUBLICATION_OPERATION_KEY] == operation


def test_starting_workflow_clears_stale_route_error() -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    state[ERROR_KEY] = "A stale route error."

    start_workflow(state, Workflow.DRAFT)

    assert state[ERROR_KEY] is None


def test_schema_migration_clears_obsolete_workflow_state_but_preserves_reconciliation() -> None:
    operation = AdoPublicationOperation(
        status=PublicationStatus.UNKNOWN_RESULT,
        correlation_id="agc-schema-migration",
        request_binding_fingerprint="binding",
        message="Manual reconciliation is required.",
    )
    state: dict[str, object] = {
        STATE_SCHEMA_VERSION_KEY: 1,
        ACTIVE_STAGE_KEY: OUTPUT_STAGE,
        ACTIVE_WORKFLOW_KEY: Workflow.REVIEW.value,
        SOLUTION_INTENT_KEY: "obsolete source",
        ADO_PUBLICATION_OPERATION_KEY: operation,
        ADO_PUBLICATION_HISTORY_KEY: {operation.correlation_id: operation},
    }

    initialize_session_state(state)

    assert active_stage(state) == HOME_STAGE
    assert current_workflow(state) is Workflow.NONE
    assert state[SOLUTION_INTENT_KEY] == ""
    assert state[ADO_PUBLICATION_OPERATION_KEY] == operation
    assert state[ADO_PUBLICATION_HISTORY_KEY] == {operation.correlation_id: operation}


def test_reset_removes_application_state_and_restores_initial_values() -> None:
    operation = AdoPublicationOperation(
        status=PublicationStatus.UNKNOWN_RESULT,
        correlation_id="agc-retained",
        request_binding_fingerprint="binding",
        message="Manual reconciliation is required.",
    )
    gateway = object()
    state: dict[str, object] = {
        SOLUTION_INTENT_KEY: "old SI",
        OUTPUTS_KEY: object(),
        ANALYSIS_INVALIDATION_KEY: AnalysisInvalidation(
            reason="Inputs changed.",
            outputs_invalidated=True,
        ),
        f"{REVIEW_WIDGET_PREFIX}action_0_owner": "Old owner",
        ADO_PUBLICATION_PREVIEW_KEY: object(),
        ADO_PUBLICATION_CONFIRMATION_KEY: object(),
        ADO_PUBLICATION_OPERATION_KEY: operation,
        ADO_PUBLICATION_HISTORY_KEY: {operation.correlation_id: operation},
        ADO_FAKE_GATEWAY_KEY: gateway,
        "unrelated": "preserved",
    }

    reset_application_state(state)

    assert state[SOLUTION_INTENT_KEY] == ""
    assert state[OUTPUTS_KEY] is None
    assert state[ANALYSIS_INVALIDATION_KEY] is None
    assert state[ACTIVE_STAGE_KEY] == HOME_STAGE
    assert f"{REVIEW_WIDGET_PREFIX}action_0_owner" not in state
    assert state[ADO_PUBLICATION_PREVIEW_KEY] is None
    assert state[ADO_PUBLICATION_CONFIRMATION_KEY] is None
    assert state[ADO_PUBLICATION_OPERATION_KEY] == operation
    assert state[ADO_PUBLICATION_HISTORY_KEY] == {operation.correlation_id: operation}
    assert state[ADO_FAKE_GATEWAY_KEY] is gateway
    assert state["unrelated"] == "preserved"


def test_active_stage_navigation_accepts_only_known_route_stages() -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)

    assert active_stage(state) == HOME_STAGE
    set_active_stage(state, REVIEW_STAGE)
    assert active_stage(state) == REVIEW_STAGE
    set_active_stage(state, OUTPUT_STAGE)
    assert active_stage(state) == OUTPUT_STAGE

    state[ACTIVE_STAGE_KEY] = "corrupt"
    assert active_stage(state) == HOME_STAGE
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


def _internal_snapshot(
    *,
    version: int = 7,
    retrieved_at: datetime | None = None,
    raw_body: str = "# Synthetic SI\n\nComplete internal source.",
):
    payload = ConfluencePagePayload(
        page_id="synthetic-page-204",
        title="Synthetic Solution Intent",
        space="SYNTHETIC",
        version=version,
        url="https://example.invalid/wiki/synthetic-page-204",
        raw_body=raw_body,
        body_format="markdown",
    )
    return build_confluence_snapshot(
        payload,
        retrieved_at=retrieved_at or datetime(2026, 9, 9, tzinfo=UTC),
    )


def test_review_mode_defaults_offline_and_switch_revokes_previous_results(
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
    state[OUTPUTS_KEY] = object()
    state[OUTPUT_ACTION_SELECTION_KEY] = 0

    assert current_review_mode(state) is ReviewMode.OFFLINE
    assert state[REVIEW_PROVIDER_CONFIGURATION_ID_KEY] == OFFLINE_PROVIDER_CONFIGURATION_ID
    assert switch_review_mode(state, ReviewMode.INTERNAL_FAKE, "fake-aif-v2")

    assert current_review_mode(state) is ReviewMode.INTERNAL_FAKE
    assert state[REVIEW_MODE_KEY] == ReviewMode.INTERNAL_FAKE.value
    assert state[REVIEW_PROVIDER_CONFIGURATION_ID_KEY] == "fake-aif-v2"
    assert state[CONFLUENCE_SNAPSHOT_KEY] is None
    assert state[SOLUTION_INTENT_KEY] == ""
    assert state[TRANSCRIPT_KEY] == ""
    assert state[ANALYZED_RESULT_KEY] == sample_result
    assert state[OUTPUTS_KEY] is None
    assert state[OUTPUT_ACTION_SELECTION_KEY] is None
    assert current_analysis_invalidation(state) is not None
    assert not switch_review_mode(state, ReviewMode.INTERNAL_FAKE, "fake-aif-v2")


def test_internal_source_identity_excludes_retrieval_time_but_includes_version() -> None:
    sample = load_sample_review()
    first = _internal_snapshot()
    refreshed = _internal_snapshot(
        retrieved_at=first.retrieved_at + timedelta(minutes=5),
    )
    changed_version = _internal_snapshot(version=8)
    fingerprint = input_fingerprint(
        first.canonical_text,
        sample.transcript,
        sample.context,
        mode=ReviewMode.INTERNAL_FAKE,
        source_snapshot=first,
        provider_configuration_identity="fake-aif-v2",
    )

    assert not analysis_is_stale(
        refreshed.canonical_text,
        sample.transcript,
        sample.context,
        fingerprint,
        mode=ReviewMode.INTERNAL_FAKE,
        source_snapshot=refreshed,
        provider_configuration_identity="fake-aif-v2",
    )
    assert analysis_is_stale(
        changed_version.canonical_text,
        sample.transcript,
        sample.context,
        fingerprint,
        mode=ReviewMode.INTERNAL_FAKE,
        source_snapshot=changed_version,
        provider_configuration_identity="fake-aif-v2",
    )
    assert analysis_is_stale(
        first.canonical_text,
        sample.transcript,
        sample.context,
        fingerprint,
        mode=ReviewMode.INTERNAL_FAKE,
        source_snapshot=first,
        provider_configuration_identity="fake-aif-v3",
    )
    assert analysis_is_stale(
        first.canonical_text,
        sample.transcript,
        sample.context,
        fingerprint,
        mode=ReviewMode.OFFLINE,
        source_snapshot=None,
        provider_configuration_identity=OFFLINE_PROVIDER_CONFIGURATION_ID,
    )


def test_internal_refresh_keeps_same_content_eligible_and_revokes_changed_version(
    sample_result: GovernanceResult,
) -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample = load_sample_review()
    switch_review_mode(state, ReviewMode.INTERNAL_FAKE, "fake-aif-v2")
    first = _internal_snapshot()
    load_internal_review_into_state(
        state,
        snapshot=first,
        transcript=sample.transcript,
        context=sample.context,
        provider_configuration_identity="fake-aif-v2",
    )
    confirm_review_input_manifest(state)
    store_analysis(state, sample_result, current_input_fingerprint(state, sample.context))

    load_internal_review_into_state(
        state,
        snapshot=_internal_snapshot(
            retrieved_at=first.retrieved_at + timedelta(minutes=5),
        ),
        transcript=sample.transcript,
        context=sample.context,
        provider_configuration_identity="fake-aif-v2",
    )

    assert current_analysis_invalidation(state) is not None
    assert state[ANALYZED_RESULT_KEY] == sample_result

    load_internal_review_into_state(
        state,
        snapshot=_internal_snapshot(version=8),
        transcript=sample.transcript,
        context=sample.context,
        provider_configuration_identity="fake-aif-v2",
    )

    invalidation = current_analysis_invalidation(state)
    assert invalidation is not None
    assert invalidation.reason == "Review inputs changed."


def test_internal_source_load_and_failure_preserve_explicit_eligibility_rules(
    sample_result: GovernanceResult,
) -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample = load_sample_review()
    switch_review_mode(state, ReviewMode.INTERNAL_FAKE, "fake-aif-v2")
    snapshot = _internal_snapshot()

    load_internal_review_into_state(
        state,
        snapshot=snapshot,
        transcript=sample.transcript,
        context=sample.context,
        provider_configuration_identity="fake-aif-v2",
    )

    assert state[CONFLUENCE_SNAPSHOT_KEY] == snapshot
    assert state[SOLUTION_INTENT_KEY] == snapshot.canonical_text
    assert state[TRANSCRIPT_KEY] == sample.transcript.strip()
    confirm_review_input_manifest(state)
    fingerprint = current_input_fingerprint(state, sample.context)
    assert fingerprint == current_input_fingerprint(state, sample.context)
    store_analysis(state, sample_result, fingerprint)

    record_internal_source_load_failure(state)

    assert state[CONFLUENCE_SNAPSHOT_KEY] is None
    assert state[SOLUTION_INTENT_KEY] == ""
    assert state[CONTEXT_KEY] == sample.context
    assert state[TRANSCRIPT_KEY] == sample.transcript.strip()
    assert state[ANALYSIS_INVALIDATION_KEY] is not None


def test_internal_source_load_rejects_missing_provider_identity() -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample = load_sample_review()
    switch_review_mode(state, ReviewMode.INTERNAL_FAKE, "fake-aif-v2")

    with pytest.raises(ValueError, match="provider configuration"):
        load_internal_review_into_state(
            state,
            snapshot=_internal_snapshot(),
            transcript=sample.transcript,
            context=sample.context,
            provider_configuration_identity=" ",
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


def test_pending_review_changes_are_tolerant_reversible_and_match_confirmation(
    sample_result: GovernanceResult,
) -> None:
    defaults = default_review_form_data(sample_result)
    assert not build_pending_review_changes(sample_result, defaults).has_changes

    actions = _editable_mappings(defaults.action_items)
    findings = _editable_mappings(defaults.findings)
    risks = _editable_mappings(defaults.risks)
    actions[0]["owner"] = "  Taylor Kim  "
    actions[0]["due_date"] = " 2026-07-24 "
    actions[1]["priority"] = "low"
    findings[0]["include"] = False
    risks[0]["owner"] = "   "
    edited = replace(
        defaults,
        action_items=tuple(actions),
        findings=tuple(findings),
        risks=tuple(risks),
    )
    pending = build_pending_review_changes(sample_result, edited)

    assert len(pending.field_changes) == 2
    assert pending.field_changes[0].after == "Taylor Kim"
    assert pending.field_changes[1].field == "Priority"
    assert pending.field_changes[1].after == "low"
    assert len(pending.excluded_items) == 1
    assert pending.pending_item_count("Action item") == 2
    assert pending.item_state("Finding", 0) == (0, True, 0)
    reviewed = build_reviewed_result(sample_result, edited)
    confirmed = build_review_change_summary(sample_result, reviewed, edited)
    assert pending.field_changes == confirmed.field_changes
    assert pending.excluded_items == confirmed.excluded_items

    reverted_actions = _editable_mappings(defaults.action_items)
    reverted_actions[0]["owner"] = f"  {sample_result.action_items[0].owner}  "
    reverted = replace(defaults, action_items=tuple(reverted_actions))
    assert not build_pending_review_changes(sample_result, reverted).has_changes


def test_pending_review_changes_report_invalid_date_without_model_validation(
    sample_result: GovernanceResult,
) -> None:
    defaults = default_review_form_data(sample_result)
    findings = _editable_mappings(defaults.findings)
    findings[0]["due_date"] = "next Friday"

    pending = build_pending_review_changes(
        sample_result,
        replace(defaults, findings=tuple(findings)),
    )

    assert pending.has_changes
    assert pending.item_state("Finding", 0) == (1, False, 1)
    assert pending.validation_issues[0].message == "Use YYYY-MM-DD."


def test_current_review_form_data_overlays_routed_widget_values(
    sample_result: GovernanceResult,
) -> None:
    state = {
        f"{REVIEW_WIDGET_PREFIX}action_0_owner": "Taylor Kim",
        f"{REVIEW_WIDGET_PREFIX}question_0_include": False,
    }

    form_data = current_review_form_data(state, sample_result)

    assert form_data.action_items[0]["owner"] == "Taylor Kim"
    assert form_data.open_questions[0]["include"] is False
    assert form_data.findings[0]["title"] == sample_result.findings[0].title


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
    retained_operation = AdoPublicationOperation(
        status=PublicationStatus.SUCCEEDED,
        correlation_id="agc-existing",
        request_binding_fingerprint="binding",
        message="Verified.",
    )
    state[ADO_PUBLICATION_PREVIEW_KEY] = object()
    state[ADO_PUBLICATION_CONFIRMATION_KEY] = object()
    state[ADO_PUBLICATION_OPERATION_KEY] = retained_operation
    state[ADO_PUBLICATION_HISTORY_KEY] = {retained_operation.correlation_id: retained_operation}

    store_outputs(state, sample_result, change_summary, outputs)

    assert state[REVIEWED_RESULT_KEY] is sample_result
    assert state[REVIEW_CHANGE_SUMMARY_KEY] is change_summary
    assert state[OUTPUTS_KEY] is outputs
    assert state[OUTPUT_ACTION_SELECTION_KEY] == 0
    assert state[OUTPUT_SUCCESS_KEY] is True
    assert state[ACTIVE_STAGE_KEY] == OUTPUT_STAGE
    assert state[ERROR_KEY] is None
    assert state[ADO_PUBLICATION_PREVIEW_KEY] is None
    assert state[ADO_PUBLICATION_CONFIRMATION_KEY] is None

    clear_outputs(state)

    assert state[REVIEWED_RESULT_KEY] is None
    assert state[REVIEW_CHANGE_SUMMARY_KEY] is None
    assert state[OUTPUTS_KEY] is None
    assert state[OUTPUT_ACTION_SELECTION_KEY] is None
    assert state[OUTPUT_SUCCESS_KEY] is False
    assert state[ADO_PUBLICATION_OPERATION_KEY] == retained_operation
    assert state[ADO_PUBLICATION_HISTORY_KEY] == {
        retained_operation.correlation_id: retained_operation
    }


def test_delivery_selection_and_original_positions_are_separate_from_outputs(sample_result) -> None:
    from architecture_governance_copilot.ui_support import (
        DELIVERY_ACTION_SELECTION_KEY,
        DELIVERY_STAGE,
        delivery_original_action_index,
        delivery_outputs_available,
        select_delivery_action,
    )

    state = {}
    initialize_session_state(state)
    form = default_review_form_data(sample_result)
    actions = _editable_mappings(form.action_items)
    actions[0]["include"] = False
    form = replace(form, action_items=tuple(actions))
    reviewed = build_reviewed_result(sample_result, form)
    outputs = GovernanceReviewService(DeterministicDemoExtractor()).generate_outputs(reviewed)
    summary = build_review_change_summary(sample_result, reviewed, form)
    store_outputs(state, reviewed, summary, outputs)
    assert delivery_original_action_index(state, 0) == 1
    assert delivery_outputs_available(state)
    set_active_stage(state, DELIVERY_STAGE)
    select_delivery_action(state, 0)
    state[OUTPUT_ACTION_SELECTION_KEY] = None
    assert state[DELIVERY_ACTION_SELECTION_KEY] == 0
    assert state[OUTPUTS_KEY] is outputs
    reset_drafting_workflow(state)
    assert delivery_outputs_available(state)
    reset_review_workflow(state)
    assert not delivery_outputs_available(state)
    assert state[DELIVERY_ACTION_SELECTION_KEY] is None


@pytest.mark.parametrize("value", [None, date(1990, 1, 1), date(2099, 12, 31)])
def test_nullable_action_date_normalization_and_confirmed_summary(sample_result, value) -> None:
    form = default_review_form_data(sample_result)
    actions = _editable_mappings(form.action_items)
    actions[0]["due_date"] = value
    form = replace(form, action_items=tuple(actions))
    pending = build_pending_review_changes(sample_result, form)
    reviewed = build_reviewed_result(sample_result, form)
    confirmed = build_review_change_summary(sample_result, reviewed, form)
    assert reviewed.action_items[0].due_date == value
    assert pending.field_changes == confirmed.field_changes
    assert not pending.validation_issues


def test_migration_preserves_orphan_operation_as_indexed_history() -> None:
    operation = AdoPublicationOperation(
        status=PublicationStatus.UNKNOWN_RESULT,
        correlation_id="legacy-orphan",
        request_binding_fingerprint="binding",
        message="Needs reconciliation.",
    )
    state = {STATE_SCHEMA_VERSION_KEY: 3, ADO_PUBLICATION_OPERATION_KEY: operation}
    initialize_session_state(state)
    assert state[ADO_PUBLICATION_HISTORY_KEY][operation.correlation_id] == operation


def test_delivery_status_never_overstates_unknown_or_partial_success() -> None:
    from architecture_governance_copilot.publication import (
        ActionDeliveryReadiness,
        DeliveryReadiness,
        DeliveryStatus,
    )
    from architecture_governance_copilot.ui_support import delivery_status

    row = ActionDeliveryReadiness(
        action_index=0,
        title="Action",
        reviewed_owner="Owner",
        resolved_assignee="owner.invalid",
        due_date=None,
        reviewed_priority="high",
        mapped_priority=1,
        parent_reference="SYN-204",
        mapped_parent=204,
    )
    ready = DeliveryReadiness(capability_available=True, actions=(row, row))
    success = AdoPublicationOperation(
        status=PublicationStatus.SUCCEEDED,
        correlation_id="correlation",
        request_binding_fingerprint="binding",
        message="Verified.",
    )
    unknown = success.model_copy(update={"status": PublicationStatus.UNKNOWN_RESULT})
    assert delivery_status(ready, (None, None)) is DeliveryStatus.READY
    assert delivery_status(ready, (success, None)) is DeliveryStatus.IN_PROGRESS
    assert delivery_status(ready, (success, success)) is DeliveryStatus.SUCCEEDED
    assert delivery_status(ready, (success, unknown)) is DeliveryStatus.NEEDS_RECONCILIATION


@pytest.mark.parametrize("status", [PublicationStatus.SUCCEEDED, PublicationStatus.UNKNOWN_RESULT])
def test_policy_revokes_fake_work_without_erasing_drafting_or_operations(status) -> None:
    from architecture_governance_copilot.runtime_dependencies import resolve_deployment_policy
    from architecture_governance_copilot.ui_support import (
        REVIEW_POLICY_RECOVERY_KEY,
        apply_deployment_policy,
        recover_review_policy,
    )

    state = {}
    fake = resolve_deployment_policy({"AGC_INTERNAL_FAKE_ENABLED": "true"})
    demo = resolve_deployment_policy({})
    apply_deployment_policy(state, fake)
    state[REVIEW_MODE_KEY] = ReviewMode.INTERNAL_FAKE.value
    state[DRAFT_RESULT_KEY] = "independent draft"
    state[OUTPUTS_KEY] = "stale output"
    state[ADO_PUBLICATION_CONFIRMATION_KEY] = "stale confirmation"
    operation = AdoPublicationOperation(
        correlation_id="agc-policy",
        request_binding_fingerprint="fingerprint",
        status=status,
        message="Retained operation fact.",
    )
    state[ADO_PUBLICATION_HISTORY_KEY] = {operation.correlation_id: operation}
    apply_deployment_policy(state, demo)
    assert state[REVIEW_POLICY_RECOVERY_KEY] is True
    assert state[REVIEW_MODE_KEY] is None
    assert state[OUTPUTS_KEY] is None
    assert state[ADO_PUBLICATION_CONFIRMATION_KEY] is None
    assert state[DRAFT_RESULT_KEY] == "independent draft"
    assert state[ADO_PUBLICATION_HISTORY_KEY][operation.correlation_id] == operation
    apply_deployment_policy(state, fake)
    assert state[REVIEW_POLICY_RECOVERY_KEY] is True
    recover_review_policy(state, fake, ReviewMode.INTERNAL_FAKE)
    assert state[REVIEW_MODE_KEY] == "internal_fake"
    assert state[ADO_PUBLICATION_HISTORY_KEY][operation.correlation_id] == operation


def test_policy_production_blocks_both_workflows_and_requires_explicit_recovery() -> None:
    from architecture_governance_copilot.runtime_dependencies import resolve_deployment_policy
    from architecture_governance_copilot.ui_support import (
        REVIEW_POLICY_RECOVERY_KEY,
        apply_deployment_policy,
        recover_review_policy,
    )

    state = {}
    demo = resolve_deployment_policy({})
    apply_deployment_policy(state, demo)
    state[DRAFT_RESULT_KEY] = "draft"
    state[OUTPUTS_KEY] = "outputs"
    production = resolve_deployment_policy({"AGC_DEPLOYMENT_PROFILE": "production"})
    apply_deployment_policy(state, production)
    assert state[DRAFT_RESULT_KEY] is None
    assert state[OUTPUTS_KEY] is None
    with pytest.raises(ValueError, match="not allowed"):
        recover_review_policy(state, production, ReviewMode.OFFLINE)
    apply_deployment_policy(state, demo)
    assert state[REVIEW_POLICY_RECOVERY_KEY] is True
    recover_review_policy(state, demo, ReviewMode.OFFLINE)
    assert state[REVIEW_POLICY_RECOVERY_KEY] is False


def test_compatible_policy_change_preserves_work_and_identity_change_revokes_review() -> None:
    from architecture_governance_copilot.runtime_dependencies import resolve_deployment_policy
    from architecture_governance_copilot.ui_support import apply_deployment_policy

    state = {}
    apply_deployment_policy(state, resolve_deployment_policy({}))
    state[OUTPUTS_KEY] = "offline output"
    state[DRAFT_RESULT_KEY] = "draft"
    apply_deployment_policy(state, resolve_deployment_policy({"AGC_DEPLOYMENT_PROFILE": "test"}))
    assert state[OUTPUTS_KEY] == "offline output"
    state[REVIEW_MODE_KEY] = "internal_fake"
    state[REVIEW_PROVIDER_CONFIGURATION_ID_KEY] = "old-id"
    apply_deployment_policy(state, resolve_deployment_policy({"AGC_INTERNAL_FAKE_ENABLED": "1"}))
    assert state[OUTPUTS_KEY] is None
    assert state[DRAFT_RESULT_KEY] == "draft"


def test_migration_cannot_turn_disallowed_mode_into_offline() -> None:
    from architecture_governance_copilot.runtime_dependencies import resolve_deployment_policy
    from architecture_governance_copilot.ui_support import (
        REVIEW_POLICY_RECOVERY_KEY,
        apply_deployment_policy,
    )

    state = {STATE_SCHEMA_VERSION_KEY: 1, REVIEW_MODE_KEY: "internal_fake"}
    apply_deployment_policy(state, resolve_deployment_policy({}))
    assert state[REVIEW_MODE_KEY] is None
    assert state[REVIEW_POLICY_RECOVERY_KEY] is True


def test_policy_identity_is_compared_without_resetting_compatible_session() -> None:
    from architecture_governance_copilot.runtime_dependencies import resolve_deployment_policy
    from architecture_governance_copilot.ui_support import apply_deployment_policy

    state = {}
    demo = resolve_deployment_policy({})
    assert apply_deployment_policy(state, demo) is True
    state[OUTPUTS_KEY] = "compatible output"
    assert apply_deployment_policy(state, demo) is False
    assert state[OUTPUTS_KEY] == "compatible output"
    development = resolve_deployment_policy({"AGC_DEPLOYMENT_PROFILE": "development"})
    assert apply_deployment_policy(state, development) is True
    assert state[OUTPUTS_KEY] == "compatible output"


def test_user_drafting_evidence_is_preserved_in_manifest_and_blocks_fake_generation():
    from architecture_governance_copilot.ui_support import (
        DRAFT_EVIDENCE_KEY,
        add_drafting_evidence,
        edit_drafting_evidence,
        refresh_project_context,
        remove_drafting_evidence,
    )

    state = {}
    initialize_session_state(state)
    open_demonstration_project_into_state(state, load_sample_drafting_context())
    state[DRAFT_EVIDENCE_KEY] = ()
    add_drafting_evidence(state, title="business.md", data=b"# Synthetic business constraints")
    manifest = build_drafting_source_package(state)
    evidence = manifest.resources[-1]
    assert evidence.provenance.value == "user_uploaded"
    assert "sha256" in evidence.source_reference
    assert project_context_readiness(state) == ()
    assert project_context_readiness(state, check_provider=True) == ()
    with pytest.raises(ValueError, match="Save evidence"):
        confirm_project_context_for_drafting(state)
    save_drafting_evidence(state)
    confirm_project_context_for_drafting(state)
    assert drafting_evidence_is_saved(state)
    reference = evidence.source_reference
    edit_drafting_evidence(state, evidence.resource_id, "Edited synthetic constraints")
    assert not drafting_evidence_is_saved(state)
    assert not state[PROJECT_CONTEXT_CONFIRMED_KEY]
    edited = build_drafting_source_package(state).resources[-1]
    assert edited.provenance.value == "user_entered"
    assert edited.source_reference == reference
    assert edited.content_fingerprint != evidence.content_fingerprint
    refresh_project_context(state)
    assert state[DRAFT_EVIDENCE_KEY][0].text == "Edited synthetic constraints"
    remove_drafting_evidence(state, evidence.resource_id)
    assert project_context_readiness(state)


@pytest.mark.parametrize(
    "title,data",
    [
        ("bad.pdf", b"text"),
        ("bad.txt", b"\xff"),
        ("empty.md", b" "),
        ("binary.txt", b"a\x00b"),
        ("large.md", b"a" * (1024 * 1024 + 1)),
    ],
)
def test_invalid_drafting_upload_does_not_replace_evidence(title, data):
    from architecture_governance_copilot.ui_support import DRAFT_EVIDENCE_KEY, add_drafting_evidence

    state = {DRAFT_EVIDENCE_KEY: ()}
    with pytest.raises(ValueError):
        add_drafting_evidence(state, title=title, data=data)
    assert state[DRAFT_EVIDENCE_KEY] == ()


def test_explicit_sample_evidence_can_be_confirmed_but_edit_revokes_only_drafting():
    from architecture_governance_copilot.ui_support import (
        DRAFT_EVIDENCE_KEY,
        edit_drafting_evidence,
        load_drafting_sample_evidence,
    )

    state = {}
    initialize_session_state(state)
    open_demonstration_project_into_state(state, load_sample_drafting_context())
    state[DRAFT_EVIDENCE_KEY] = ()
    load_drafting_sample_evidence(state)
    save_drafting_evidence(state)
    confirm_project_context_for_drafting(state)
    state[OUTPUTS_KEY] = "independent review"
    edit_drafting_evidence(state, "supporting-context-v1", "User modification")
    assert state[PROJECT_CONTEXT_CONFIRMED_KEY] is False
    assert state[DRAFT_RESULT_KEY] is None
    assert state[OUTPUTS_KEY] == "independent review"


@pytest.mark.parametrize(
    "category", ["Decisions", "Findings", "Risks", "Actions", "Questions", "Missing Info"]
)
def test_review_tab_selection_survives_count_changes_and_reset(category: str) -> None:
    from architecture_governance_copilot.ui_support import (
        clear_review_widget_state,
        retain_review_tab_selection,
    )

    categories = ["Decisions", "Findings", "Risks", "Actions", "Questions", "Missing Info"]
    state = {"agc_human_review_tabs": f"{category} · 1"}
    for suffix in [" · 1 edited", " · 1 edited · 1 needs correction", " · 1 excluded", ""]:
        labels = [f"{name} · 1{suffix if name == category else ''}" for name in categories]
        retain_review_tab_selection(state, labels)
        assert state["agc_human_review_tabs"] == f"{category} · 1{suffix}"
    clear_review_widget_state(state)
    retain_review_tab_selection(state, labels)
    assert state["agc_human_review_tabs"] == "Decisions · 1"


def test_operation_error_clears_only_when_its_inputs_change():
    from architecture_governance_copilot.ui_support import (
        clear_stale_operation_error,
        remember_operation_error,
    )

    state = {"agc_error": "Invalid date", "agc_field_finding_0_due_date": "bad"}
    remember_operation_error(state)
    clear_stale_operation_error(state)
    assert state["agc_error"] == "Invalid date"
    state["agc_field_finding_0_due_date"] = "2026-07-24"
    clear_stale_operation_error(state)
    assert state["agc_error"] is None


def test_delivery_selection_clears_feedback_without_clearing_history():
    from architecture_governance_copilot.ui_support import (
        clear_stale_operation_error,
        remember_operation_error,
    )

    history = {"synthetic-correlation": "unknown"}
    state = {
        "agc_error": "Needs reconciliation",
        "agc_delivery_action_widget": 0,
        "agc_ado_publication_history": history,
    }
    remember_operation_error(state)
    state["agc_delivery_action_widget"] = 1
    clear_stale_operation_error(state)
    assert state["agc_error"] is None
    assert state["agc_ado_publication_history"] is history


def test_outcome_evidence_binding_and_guard():
    from dataclasses import replace

    from architecture_governance_copilot.evidence_validation import validate_governance_evidence
    from architecture_governance_copilot.models import GovernanceResult, ReviewOutcome
    from architecture_governance_copilot.ui_support import (
        build_reviewed_result,
        default_review_form_data,
        selected_outcome_evidence,
    )

    root = Path(__file__).resolve().parents[1] / "samples"
    canonical = GovernanceResult.model_validate_json((root / "expected_result.json").read_text())
    analyzed = canonical.model_copy(
        update={"review_outcome": ReviewOutcome.NOT_STATED, "outcome_evidence": []}
    )
    form = default_review_form_data(analyzed)
    assert build_reviewed_result(analyzed, form).review_outcome is ReviewOutcome.NOT_STATED
    stated = replace(form, review_outcome="changes_requested")
    with pytest.raises(ValueError, match="Select supporting transcript evidence"):
        build_reviewed_result(analyzed, stated)
    transcript = (root / "review_transcript.txt").read_text()
    bound = replace(stated, outcome_evidence=selected_outcome_evidence(transcript, [29]))
    reviewed = build_reviewed_result(analyzed, bound)
    validate_governance_evidence(reviewed, (root / "solution_intent.md").read_text(), transcript)
    assert reviewed.outcome_evidence[0].reference == "transcript-line-29"
    assert analyzed.outcome_evidence == []
    with pytest.raises(ValueError, match="Select evidence from the current transcript"):
        selected_outcome_evidence("New source", [29])


def test_nonproduction_outcome_does_not_relax_provider_contract():
    from dataclasses import replace

    from pydantic import ValidationError

    from architecture_governance_copilot.evidence_validation import EvidenceValidatingExtractor
    from architecture_governance_copilot.models import GovernanceResult, ReviewOutcome
    from architecture_governance_copilot.runtime_dependencies import resolve_deployment_policy
    from architecture_governance_copilot.ui_support import (
        build_reviewed_result,
        default_review_form_data,
    )

    root = Path(__file__).resolve().parents[1] / "samples"
    canonical = GovernanceResult.model_validate_json((root / "expected_result.json").read_text())
    analyzed = canonical.model_copy(
        update={"review_outcome": ReviewOutcome.NOT_STATED, "outcome_evidence": []}
    )
    form = replace(default_review_form_data(analyzed), review_outcome="approved")
    for profile in ("demo", "development", "test"):
        policy = resolve_deployment_policy({"AGC_DEPLOYMENT_PROFILE": profile})
        reviewed = build_reviewed_result(
            analyzed, form, allow_reviewer_outcome=policy.reviewer_outcome_allowed
        )
        assert reviewed.outcome_origin == "reviewer_selected"
    production = resolve_deployment_policy({"AGC_DEPLOYMENT_PROFILE": "production"})
    assert not production.review_modes
    assert not production.reviewer_outcome_allowed
    with pytest.raises(ValueError, match="Select supporting transcript evidence"):
        build_reviewed_result(
            analyzed, form, allow_reviewer_outcome=production.reviewer_outcome_allowed
        )

    class ForgedProvider:
        def extract(self, *args):
            return reviewed

    with pytest.raises(ValidationError):
        EvidenceValidatingExtractor(ForgedProvider()).extract("SI", "Transcript", canonical.context)
    with pytest.raises(ValidationError):
        GovernanceResult.model_validate(reviewed.model_dump())


def test_explicit_mapped_owner_choice_preserves_other_action_fields():
    from architecture_governance_copilot.ui_support import choose_review_action_owner

    state = {"agc_field_action_0_owner": "Unmapped", "agc_field_action_0_title": "Reviewed title"}
    choose_review_action_owner(state, 0, "Avery Patel")
    assert state["agc_field_action_0_owner"] == "Avery Patel"
    assert state["agc_field_action_0_title"] == "Reviewed title"


def test_custom_owner_is_preserved_in_reviewed_result_and_outputs(sample_result):
    form = default_review_form_data(sample_result)
    actions = _editable_mappings(form.action_items)
    actions[0]["owner"] = "Custom Owner / Team"
    form = replace(form, action_items=tuple(actions))
    reviewed = build_reviewed_result(sample_result, form)
    outputs = GovernanceReviewService(DeterministicDemoExtractor()).generate_outputs(reviewed)
    assert reviewed.action_items[0].owner == "Custom Owner / Team"
    assert reviewed.action_items[0].evidence == sample_result.action_items[0].evidence
    assert "Custom Owner / Team" in outputs.review_minutes


def test_delivery_attention_is_one_shot_and_revoked_with_preview():
    from architecture_governance_copilot.ui_support import (
        clear_publication_preview,
        consume_delivery_attention,
        request_delivery_attention,
    )

    state = {}
    request_delivery_attention(state, "preview")
    assert consume_delivery_attention(state) == ("preview", 1)
    assert consume_delivery_attention(state) is None
    request_delivery_attention(state, "confirmation")
    clear_publication_preview(state)
    assert consume_delivery_attention(state) is None
    request_delivery_attention(state, "result")
    assert consume_delivery_attention(state) == ("result", 3)
    with pytest.raises(ValueError):
        request_delivery_attention(state, "user-controlled-anchor")


def test_delivery_focus_markup_rejects_untrusted_values():
    from architecture_governance_copilot.ui_focus import delivery_focus_markup

    html = delivery_focus_markup("preview", 1)
    assert "agc-delivery-preview" in html
    assert "prefers-reduced-motion" in html
    for target, sequence in [("<script>", 1), ("result", "1"), ("preview", True)]:
        with pytest.raises(ValueError):
            delivery_focus_markup(target, sequence)
