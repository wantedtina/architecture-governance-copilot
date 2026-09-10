"""Streamlit application smoke and workflow tests."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import architecture_governance_copilot.ui_support as ui_support
from architecture_governance_copilot.integrations.azure_devops import InMemoryFakeAdoGateway
from architecture_governance_copilot.minutes_generator import format_action_item_entry
from architecture_governance_copilot.publication import (
    AdoPublicationOperation,
    PublicationStatus,
)
from architecture_governance_copilot.ui_support import (
    ADO_FAKE_GATEWAY_KEY,
    ADO_PUBLICATION_HISTORY_KEY,
    ADO_PUBLICATION_OPERATION_KEY,
    ANALYSIS_INVALIDATION_KEY,
    ANALYSIS_SUCCESS_KEY,
    ANALYZED_RESULT_KEY,
    CONTEXT_KEY,
    DRAFT_CONTENT_WIDGET_KEY,
    DRAFT_SOURCE_CODE_WIDGET_KEY,
    DRAFT_SUPPORTING_DOCS_WIDGET_KEY,
    DRAFT_TEMPLATE_WIDGET_KEY,
    OUTPUT_ACTION_SELECTION_KEY,
    OUTPUTS_KEY,
    REVIEW_CHANGE_SUMMARY_KEY,
    REVIEWED_RESULT_KEY,
    SOLUTION_INTENT_WIDGET_KEY,
    TRANSCRIPT_WIDGET_KEY,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = REPOSITORY_ROOT / "app.py"


def _initial_app() -> AppTest:
    return AppTest.from_file(str(APP_PATH), default_timeout=10).run()


def _review_inputs_app() -> AppTest:
    app = _initial_app()
    app.button(key="agc_start_review_workflow").click().run()
    assert [item.value for item in app.header] == ["Review step 1 — Review Inputs"]
    # AppTest does not persist a programmatic route selection between later
    # interactions, so explicitly select the routed page.
    app.switch_page("pages/review_inputs.py").run()
    return app


def _analyzed_app() -> AppTest:
    app = _review_inputs_app()
    app.button(key="agc_load_review_transcript").click().run()
    app.button(key="agc_load_review_metadata").click().run()
    app.button(key="agc_load_review_source").click().run()
    app.button(key="agc_confirm_review_inputs").click().run()
    app.button(key="agc_analyze").click().run()
    # AppTest does not persist a programmatic route selection between later
    # interactions, so explicitly select the routed page after asserting the
    # navigation triggered by Analyze Review.
    assert [item.value for item in app.header] == ["Review step 2 — Human Review"]
    app.switch_page("pages/human_review.py").run()
    return app


def _assert_active_step(app: AppTest, label: str) -> None:
    stepper_markup = next(
        item.value for item in app.markdown if item.value.startswith('<div class="agc-stepper">')
    )
    assert "\n" not in stepper_markup
    expected_count = 2 if label in {"Project Context", "Draft Solution Intent"} else 3
    assert stepper_markup.count('<div class="agc-step ') == expected_count
    assert "agc-step--active" in stepper_markup
    assert f"<strong>{label}</strong><span>In progress</span>" in stepper_markup


def _assert_completed_workflow(app: AppTest) -> None:
    stepper_markup = next(
        item.value for item in app.markdown if item.value.startswith('<div class="agc-stepper">')
    )
    assert "agc-step--active" not in stepper_markup
    assert stepper_markup.count("agc-step--complete") == 3
    assert "Project Context" not in stepper_markup
    assert "Draft Solution Intent" not in stepper_markup
    assert "<strong>Review Inputs</strong><span>Complete</span>" in stepper_markup
    assert "<strong>Human Review</strong><span>Complete</span>" in stepper_markup
    assert "<strong>Generated Outputs</strong><span>Complete</span>" in stepper_markup


def test_importing_app_does_not_load_sample_files(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_loaded() -> object:
        raise AssertionError("app import must not load sample files")

    monkeypatch.setattr(ui_support, "load_sample_review", fail_if_loaded)

    namespace = runpy.run_path(str(APP_PATH), run_name="app_import_smoke")

    assert "main" in namespace


def test_review_mode_is_offline_only_without_internal_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AGC_INTERNAL_FAKE_ENABLED", raising=False)
    app = _review_inputs_app()

    control = app.segmented_control(key="agc_review_mode_widget")
    assert control.value == "offline"
    assert control.options == ["Offline demo"]
    assert app.button(key="agc_load_review_source")
    assert all(item.key != "agc_prepare_ado_publication" for item in app.button)
    assert any("Zero-configuration deterministic mode" in item.value for item in app.caption)


def test_configured_internal_fake_flow_uses_separate_sources_and_human_review(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGC_INTERNAL_FAKE_ENABLED", "1")
    monkeypatch.setenv("AGC_DEMO_STEP_DELAY_SECONDS", "0")
    app = _review_inputs_app()

    control = app.segmented_control(key="agc_review_mode_widget")
    assert control.options == ["Offline demo", "Internal fake · no network"]
    control.set_value("internal_fake").run()

    assert app.button(key="agc_analyze").disabled
    assert not app.button(key="agc_load_review_source").disabled
    assert any("Configured fake only" in item.value for item in app.warning)
    assert any("Internal fake · no network" in item.value for item in app.markdown)

    app.button(key="agc_load_review_transcript").click().run()
    app.button(key="agc_load_review_metadata").click().run()
    app.button(key="agc_load_review_source").click().run()

    solution_intent = app.text_area(key=SOLUTION_INTENT_WIDGET_KEY)
    transcript = app.text_area(key=TRANSCRIPT_WIDGET_KEY)
    assert solution_intent.disabled
    assert "Synthetic Order Routing Service" in solution_intent.value
    assert "Morgan Lee" in transcript.value
    assert "Priya Shah" not in transcript.value
    assert app.button(key="agc_analyze").disabled
    assert not app.button(key="agc_confirm_review_inputs").disabled

    app.button(key="agc_confirm_review_inputs").click().run()

    assert not app.button(key="agc_analyze").disabled

    app.button(key="agc_analyze").click().run()

    assert [item.value for item in app.header] == ["Review step 2 — Human Review"]
    assert any("No outputs were generated automatically" in item.value for item in app.success)
    app.switch_page("pages/human_review.py").run()
    assert any("Fake AIF" in item.value for item in app.caption)

    app.button(key="agc_confirm_review").click().run()

    assert [item.value for item in app.header] == ["Review step 3 — Generated Outputs"]
    assert any(item.value == "Generated Review Record" for item in app.subheader)
    app.switch_page("pages/generated_outputs.py").run()
    assert app.button(key="agc_prepare_ado_publication")

    app.button(key="agc_prepare_ado_publication").click().run()

    assert app.button(key="agc_confirm_ado_publication")
    assert all(item.key != "agc_submit_ado_publication" for item in app.button)
    assert any("$Governance%20Action?api-version=7.1" in item.value for item in app.code)

    app.button(key="agc_confirm_ado_publication").click().run()

    assert app.button(key="agc_submit_ado_publication")
    assert any("No request has been sent yet" in item.value for item in app.success)

    app.button(key="agc_submit_ado_publication").click().run()

    operation = app.session_state[ADO_PUBLICATION_OPERATION_KEY]
    gateway = app.session_state[ADO_FAKE_GATEWAY_KEY]
    history = app.session_state[ADO_PUBLICATION_HISTORY_KEY]
    assert isinstance(operation, AdoPublicationOperation)
    assert operation.status is PublicationStatus.SUCCEEDED
    assert operation.receipt is not None and operation.receipt.verified
    assert isinstance(gateway, InMemoryFakeAdoGateway)
    assert len(gateway.create_calls) == 1
    assert history[operation.correlation_id] == operation
    assert all(item.key != "agc_submit_ado_publication" for item in app.button)
    assert any("Created work item verified" in item.value for item in app.success)
    assert not app.exception


@pytest.mark.parametrize(
    ("configured_value", "expected"),
    [
        ("0", 0.0),
        ("0.25", 0.25),
        ("-2", 0.0),
        ("20", 1.5),
        ("invalid", 0.4),
    ],
)
def test_demo_transition_delay_is_configurable_and_bounded(
    monkeypatch: pytest.MonkeyPatch,
    configured_value: str,
    expected: float,
) -> None:
    monkeypatch.setenv("AGC_DEMO_STEP_DELAY_SECONDS", configured_value)
    namespace = runpy.run_path(str(APP_PATH), run_name="app_delay_config_test")

    assert namespace["_demo_step_delay_seconds"]() == expected


def test_successful_si_draft_generation_clears_processing_overlay() -> None:
    class Placeholder:
        def __init__(self) -> None:
            self.empty_calls = 0
            self.markdown_calls = 0

        def markdown(self, *_args: object, **_kwargs: object) -> None:
            self.markdown_calls += 1

        def empty(self) -> None:
            self.empty_calls += 1

    class Status:
        def __enter__(self) -> Status:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def update(self, **_kwargs: object) -> None:
            return None

    class FakeStreamlit:
        def __init__(self, state: dict[str, object], placeholder: Placeholder) -> None:
            self.session_state = state
            self._placeholder = placeholder

        def empty(self) -> Placeholder:
            return self._placeholder

        def status(self, *_args: object, **_kwargs: object) -> Status:
            return Status()

        def write(self, _value: object) -> None:
            return None

    state: dict[str, object] = {}
    ui_support.initialize_session_state(state)
    ui_support.load_drafting_context_into_state(
        state,
        ui_support.load_sample_drafting_context(),
    )
    placeholder = Placeholder()
    namespace = runpy.run_path(str(APP_PATH), run_name="app_draft_overlay_test")
    function_globals = namespace["_generate_si_draft"].__globals__
    function_globals["st"] = FakeStreamlit(state, placeholder)
    function_globals["_demo_pause"] = lambda: None

    assert namespace["_generate_si_draft"]()
    assert placeholder.markdown_calls == 3
    assert placeholder.empty_calls == 1
    assert state[ui_support.DRAFT_RESULT_KEY] is not None


def test_si_confirmation_shows_two_phases_and_always_clears_overlay() -> None:
    class Placeholder:
        def __init__(self) -> None:
            self.empty_calls = 0
            self.markdown_calls = 0

        def markdown(self, *_args: object, **_kwargs: object) -> None:
            self.markdown_calls += 1

        def empty(self) -> None:
            self.empty_calls += 1

    class Status:
        def __enter__(self) -> Status:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def update(self, **_kwargs: object) -> None:
            return None

    class FakeStreamlit:
        def __init__(self, state: dict[str, object], placeholder: Placeholder) -> None:
            self.session_state = state
            self._placeholder = placeholder

        def empty(self) -> Placeholder:
            return self._placeholder

        def status(self, *_args: object, **_kwargs: object) -> Status:
            return Status()

        def write(self, _value: object) -> None:
            return None

    state: dict[str, object] = {}
    ui_support.initialize_session_state(state)
    ui_support.load_drafting_context_into_state(
        state,
        ui_support.load_sample_drafting_context(),
    )
    placeholder = Placeholder()
    namespace = runpy.run_path(str(APP_PATH), run_name="app_draft_confirmation_overlay_test")
    function_globals = namespace["_generate_si_draft"].__globals__
    function_globals["st"] = FakeStreamlit(state, placeholder)
    function_globals["_demo_pause"] = lambda: None
    assert namespace["_generate_si_draft"]()

    placeholder.empty_calls = 0
    placeholder.markdown_calls = 0
    reviewed_content = state[ui_support.DRAFT_CONTENT_WIDGET_KEY]
    assert isinstance(reviewed_content, str)

    assert namespace["_confirm_si_draft"](reviewed_content)
    assert placeholder.markdown_calls == 2
    assert placeholder.empty_calls == 1
    assert state[ui_support.DRAFT_CONFIRMED_KEY] is True

    placeholder.empty_calls = 0
    placeholder.markdown_calls = 0

    assert not namespace["_confirm_si_draft"](" ")
    assert placeholder.markdown_calls == 2
    assert placeholder.empty_calls == 1
    assert "must not be blank" in str(state[ui_support.ERROR_KEY])


def test_initial_page_has_required_controls_and_no_generated_outputs() -> None:
    app = _initial_app()

    assert not app.exception
    brand_markup = next(
        item.value for item in app.markdown if item.value.startswith('<div class="agc-brandbar">')
    )
    assert "Standard Chartered" in brand_markup
    assert "Technology &amp; Operations" in brand_markup
    assert "Architecture Governance Copilot" in brand_markup
    assert "INTERNAL · HACKATHON PoC" in brand_markup
    assert any("synthetic data" in item.value.lower() for item in app.info)
    assert {button.label for button in app.button} >= {
        "Draft a Solution Intent",
        "Review a Solution Intent",
        "Reset all local demo state",
    }
    assert [item.value for item in app.header] == ["Choose a governance workflow"]
    assert all(not item.value.startswith('<div class="agc-stepper">') for item in app.markdown)
    assert all("Generated Outputs" not in item.value for item in app.header)
    assert not app.text_area


def test_drafted_si_confirmation_ends_drafting_before_separate_review() -> None:
    app = _initial_app()

    assert not app.exception
    app.button(key="agc_start_drafting_workflow").click().run()
    assert [item.value for item in app.header] == ["Drafting step 1 — Project Context"]
    app.switch_page("pages/project_context.py").run()
    _assert_active_step(app, "Project Context")

    app.button(key="agc_open_demonstration_project").click().run()
    app.switch_page("pages/project_context.py").run()

    _assert_active_step(app, "Project Context")
    assert not app.button(key="agc_refresh_project_context").disabled
    assert app.checkbox(key="agc_context_template_selected").value is True
    assert app.checkbox(key="agc_context_repository_selected").value is True
    project_snapshot = next(
        item.value
        for item in app.markdown
        if item.value.startswith('<div class="agc-intake-grid">')
    )
    assert "Digital Payment Notification Service" in project_snapshot
    assert "ADO Workitem - Solution Intent 12658902" in project_snapshot
    assert "v1.1" in project_snapshot
    assert "55390-19-payment-notification-service · main" in project_snapshot

    app.button(key="agc_confirm_project_context").click().run()
    assert [item.value for item in app.header] == ["Drafting step 2 — Draft Solution Intent"]
    app.switch_page("pages/solution_intent_drafting.py").run()

    _assert_active_step(app, "Draft Solution Intent")
    assert not app.button(key="agc_generate_si_draft").disabled
    assert app.text_area(key=DRAFT_TEMPLATE_WIDGET_KEY).value.startswith("# Solution Intent")
    assert "notification_routes.py" in app.text_area(key=DRAFT_SOURCE_CODE_WIDGET_KEY).value
    assert "Planned initial release" in app.text_area(key=DRAFT_SUPPORTING_DOCS_WIDGET_KEY).value
    context_snapshot = next(
        item.value
        for item in app.markdown
        if item.value.startswith('<div class="agc-intake-grid">')
    )
    assert "Enterprise SI template snapshot" in context_snapshot
    assert "12 governed chapters detected" in context_snapshot
    assert "6 selected repository artefacts" in context_snapshot
    assert "4 context domains supplied" in context_snapshot

    app.button(key="agc_generate_si_draft").click().run()

    assert not app.exception
    _assert_active_step(app, "Draft Solution Intent")
    generated = app.text_area(key=DRAFT_CONTENT_WIDGET_KEY).value
    assert generated.startswith("# Solution Intent")
    assert "Managed PostgreSQL" in generated
    assert app.button(key="agc_generate_si_draft").label == "Regenerate SI Draft"
    assert any(item.label == "View drafting sources" for item in app.expander)
    assert {tab.label for tab in app.tabs} >= {
        "Markdown editor",
        "Rendered preview",
        "Rendered",
        "Markdown source",
    }
    assert app.button(key="agc_confirm_si_draft")

    app.button(key="agc_confirm_si_draft").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Drafting step 2 — Draft Solution Intent"]
    assert app.text_area(key=DRAFT_CONTENT_WIDGET_KEY).disabled
    assert app.download_button(key="agc_download_confirmed_si")
    assert {tab.label for tab in app.tabs} >= {"Rendered", "Markdown source"}
    assert any("not been published" in item.value for item in app.success)
    assert all(item.key != SOLUTION_INTENT_WIDGET_KEY for item in app.text_area)

    app.button(key="agc_start_separate_review").click().run()

    assert [item.value for item in app.header] == ["Review step 1 — Review Inputs"]
    assert app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).value == ""
    assert app.text_area(key=TRANSCRIPT_WIDGET_KEY).value == ""


def test_review_components_load_in_any_order_and_require_confirmation() -> None:
    app = _review_inputs_app()

    assert app.button(key="agc_analyze").disabled
    app.button(key="agc_load_review_transcript").click().run()
    assert app.button(key="agc_analyze").disabled
    app.button(key="agc_load_review_metadata").click().run()
    assert app.button(key="agc_analyze").disabled
    app.button(key="agc_load_review_source").click().run()

    assert app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).value.startswith("# Solution Intent")
    assert "[10:00] Priya Shah:" in app.text_area(key=TRANSCRIPT_WIDGET_KEY).value
    assert app.button(key="agc_analyze").disabled
    assert not app.button(key="agc_confirm_review_inputs").disabled

    app.button(key="agc_confirm_review_inputs").click().run()
    assert not app.button(key="agc_analyze").disabled

    app.button(key="agc_analyze").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Review step 2 — Human Review"]


@pytest.mark.parametrize(
    ("page_path", "message"),
    [
        (
            "pages/human_review.py",
            "Complete review analysis before opening the Human Review page.",
        ),
        (
            "pages/generated_outputs.py",
            "Complete review analysis before opening the Generated Outputs page.",
        ),
    ],
)
def test_deep_links_redirect_to_review_inputs_when_prerequisites_are_missing(
    page_path: str,
    message: str,
) -> None:
    app = _initial_app()

    app.switch_page(page_path).run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Review step 1 — Review Inputs"]
    assert any(item.value == message for item in app.error)


def test_drafting_deep_link_requires_confirmed_project_context() -> None:
    app = _initial_app()

    app.switch_page("pages/solution_intent_drafting.py").run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Drafting step 1 — Project Context"]
    assert any(
        item.value == "Confirm a Project Context package before drafting a Solution Intent."
        for item in app.error
    )


def test_sample_load_and_analysis_show_draft_without_automatic_outputs() -> None:
    app = _review_inputs_app()

    app.button(key="agc_load_review_source").click().run()
    app.button(key="agc_load_review_transcript").click().run()
    app.button(key="agc_load_review_metadata").click().run()

    assert not app.exception
    assert app.button(key="agc_analyze").disabled
    assert app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).value.startswith("# Solution Intent")
    assert "[10:00] Priya Shah:" in app.text_area(key=TRANSCRIPT_WIDGET_KEY).value
    assert any("Synthetic review metadata loaded" in item.value for item in app.success)
    assert {tab.label for tab in app.tabs} >= {"Rendered", "Canonical Markdown source"}

    app.button(key="agc_confirm_review_inputs").click().run()
    assert not app.button(key="agc_analyze").disabled
    app.button(key="agc_analyze").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Review step 2 — Human Review"]
    _assert_active_step(app, "Human Review")
    assert all(item.key != SOLUTION_INTENT_WIDGET_KEY for item in app.text_area)
    assert all(item.key != TRANSCRIPT_WIDGET_KEY for item in app.text_area)
    assert app.button(key="agc_back_to_inputs")
    assert [(item.label, item.value) for item in app.metric] == [
        ("Outcome", "Changes Requested"),
        ("Decisions", "1"),
        ("Findings", "3"),
        ("Risks", "1"),
        ("Actions", "2"),
        ("Open Questions", "1"),
        ("Missing Information", "2"),
    ]
    assert [tab.label for tab in app.tabs] == [
        "Decisions · 1",
        "Findings · 3",
        "Risks · 1",
        "Actions · 2",
        "Questions · 1",
        "Missing Info · 2",
    ]
    assert any(
        "no outputs were generated automatically" in item.value.lower() for item in app.success
    )
    assert all("Review step 3" not in item.value for item in app.header)


def test_human_edit_and_exclusion_generate_reviewed_outputs() -> None:
    app = _analyzed_app()

    app.text_input(key="agc_field_action_0_owner").input("Taylor Kim")
    app.checkbox(key="agc_field_question_0_include").uncheck()
    app.button(key="agc_confirm_review").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Review step 3 — Generated Outputs"]
    _assert_completed_workflow(app)
    assert app.button(key="agc_back_to_review")
    assert app.button(key="agc_start_new_review")
    assert any("Governance package ready" in item.value for item in app.markdown)
    assert {tab.label for tab in app.tabs} >= {"Rendered", "Markdown source"}
    output_metrics = {
        item.label: item.value
        for item in app.metric
        if item.label
        in {
            "Workflow",
            "Review Outcome",
            "Meeting Minutes",
            "Work Item Previews",
        }
    }
    assert output_metrics == {
        "Workflow": "Complete",
        "Review Outcome": "Changes Requested",
        "Meeting Minutes": "1",
        "Work Item Previews": "2",
    }
    assert any(item.value == "Generated Review Record" for item in app.subheader)
    assert any(item.value == "Human Review Changes" for item in app.subheader)
    assert any(item.value == "Azure DevOps Work Item Previews" for item in app.subheader)
    assert any(
        item.value == "Preview only · No work items were submitted to Azure DevOps."
        for item in app.warning
    )
    assert any("Taylor Kim" in item.value for item in app.markdown)
    assert any("Action item 1" in item.value and "Owner" in item.value for item in app.markdown)
    assert sum("Should Redis be used as a cache?" in item.value for item in app.markdown) == 1
    assert sum("Work Item Preview" in item.value for item in app.markdown) == 2


def test_output_comparison_uses_reviewed_index_with_duplicate_titles() -> None:
    app = _analyzed_app()
    duplicate_title = "Resolve the confirmed governance action"
    app.text_input(key="agc_field_action_0_title").input(duplicate_title)
    app.text_input(key="agc_field_action_0_owner").input("First Owner")
    app.text_input(key="agc_field_action_1_title").input(duplicate_title)
    app.text_input(key="agc_field_action_1_owner").input("Second Owner")

    app.button(key="agc_confirm_review").click().run()
    app.switch_page("pages/generated_outputs.py").run()

    selector = app.selectbox(key=OUTPUT_ACTION_SELECTION_KEY)
    assert selector.options == [
        f"Action 1 · {duplicate_title}",
        f"Action 2 · {duplicate_title}",
    ]
    selector.select(1).run()

    reviewed = app.session_state[REVIEWED_RESULT_KEY]
    outputs = app.session_state[OUTPUTS_KEY]
    expected_entry = format_action_item_entry(reviewed.action_items[1], 2)
    assert expected_entry in outputs.review_minutes
    assert any(item.value == expected_entry for item in app.markdown)
    assert any(
        "Assigned to: Second Owner" in item.value and "Source action index: 1" in item.value
        for item in app.caption
    )


def test_output_comparison_reindexes_after_first_action_is_excluded() -> None:
    app = _analyzed_app()
    app.checkbox(key="agc_field_action_0_include").uncheck()

    app.button(key="agc_confirm_review").click().run()

    reviewed = app.session_state[REVIEWED_RESULT_KEY]
    outputs = app.session_state[OUTPUTS_KEY]
    selector = app.selectbox(key=OUTPUT_ACTION_SELECTION_KEY)
    expected_entry = format_action_item_entry(reviewed.action_items[0], 1)
    assert selector.options == [f"Action 1 · {reviewed.action_items[0].title}"]
    assert outputs.ado_work_items[0].source_action_index == 0
    assert expected_entry in outputs.review_minutes
    assert any(item.value == expected_entry for item in app.markdown)
    assert any(
        "Assigned to: Priya Shah" in item.value and "Source action index: 0" in item.value
        for item in app.caption
    )
    assert any(reviewed.action_items[0].evidence[0].quote in item.value for item in app.code)


def test_output_comparison_has_clear_empty_state_without_actions() -> None:
    app = _analyzed_app()
    app.checkbox(key="agc_field_action_0_include").uncheck()
    app.checkbox(key="agc_field_action_1_include").uncheck()

    app.button(key="agc_confirm_review").click().run()

    assert not app.exception
    assert app.session_state[OUTPUT_ACTION_SELECTION_KEY] is None
    assert all(item.key != OUTPUT_ACTION_SELECTION_KEY for item in app.selectbox)
    assert any(
        "No action items were included in the reviewed record" in item.value for item in app.info
    )
    assert not app.session_state[OUTPUTS_KEY].ado_work_items


def test_no_change_confirmation_shows_explicit_review_summary_state() -> None:
    app = _analyzed_app()

    app.button(key="agc_confirm_review").click().run()

    assert not app.exception
    assert any(item.value == "Human Review Changes" for item in app.subheader)
    assert any("No changes were made during human review" in item.value for item in app.info)


def test_start_new_review_clears_completed_workflow_and_returns_to_inputs() -> None:
    app = _analyzed_app()
    app.button(key="agc_confirm_review").click().run()
    app.switch_page("pages/generated_outputs.py").run()

    app.button(key="agc_start_new_review").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Review step 1 — Review Inputs"]
    assert app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).value == ""
    assert app.text_area(key=TRANSCRIPT_WIDGET_KEY).value == ""
    assert app.session_state[OUTPUTS_KEY] is None


def test_invalid_review_date_shows_error_without_stale_outputs() -> None:
    app = _analyzed_app()
    app.text_input(key="agc_field_action_0_due_date").input("24 July 2026")

    app.button(key="agc_confirm_review").click().run()

    assert not app.exception
    assert any("Use YYYY-MM-DD" in item.value for item in app.error)
    assert all(item.value != "Review step 3 — Generated Outputs" for item in app.header)


def test_generation_failure_clears_previous_review_change_summary() -> None:
    app = _analyzed_app()
    app.button(key="agc_confirm_review").click().run()
    assert app.session_state[REVIEW_CHANGE_SUMMARY_KEY] is not None

    app.button(key="agc_back_to_review").click().run()
    app.switch_page("pages/human_review.py").run()
    app.text_input(key="agc_field_action_0_due_date").input("24 July 2026")
    app.button(key="agc_confirm_review").click().run()

    assert not app.exception
    assert any("Use YYYY-MM-DD" in item.value for item in app.error)
    assert app.session_state[REVIEW_CHANGE_SUMMARY_KEY] is None
    assert app.session_state[OUTPUTS_KEY] is None


def test_changed_inputs_make_analysis_stale_and_hide_previous_outputs() -> None:
    app = _analyzed_app()
    app.button(key="agc_confirm_review").click().run()
    assert any(item.value == "Review step 3 — Generated Outputs" for item in app.header)

    app.button(key="agc_back_to_review").click().run()
    app.switch_page("pages/human_review.py").run()
    app.button(key="agc_back_to_inputs").click().run()
    app.switch_page("pages/review_inputs.py").run()
    transcript = app.text_area(key=TRANSCRIPT_WIDGET_KEY).value
    app.text_area(key=TRANSCRIPT_WIDGET_KEY).input(f"{transcript}\nEdited after analysis").run()

    assert not app.exception
    assert any(
        "Inputs changed → outputs invalidated. Run Analyze Review again" in item.value
        for item in app.warning
    )
    assert all(item.key != "agc_confirm_review" for item in app.button)
    assert app.session_state[OUTPUTS_KEY] is None
    assert app.session_state[REVIEWED_RESULT_KEY] is None
    assert app.session_state[REVIEW_CHANGE_SUMMARY_KEY] is None
    assert app.session_state[ANALYSIS_SUCCESS_KEY] is False
    assert app.session_state[ANALYZED_RESULT_KEY] is not None
    assert all("Review analysis completed" not in item.value for item in app.success)
    assert all(item.value != "Review step 3 — Generated Outputs" for item in app.header)


def test_returning_from_outputs_restores_sources_without_false_invalidation() -> None:
    app = _analyzed_app()
    app.button(key="agc_confirm_review").click().run()
    app.switch_page("pages/generated_outputs.py").run()

    app.button(key="agc_back_to_review").click().run()
    app.switch_page("pages/human_review.py").run()
    app.button(key="agc_back_to_inputs").click().run()
    app.switch_page("pages/review_inputs.py").run()

    assert app.session_state[ANALYSIS_INVALIDATION_KEY] is None
    assert app.session_state[OUTPUTS_KEY] is not None
    assert app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).value.startswith("# Solution Intent")
    assert "[10:00] Priya Shah:" in app.text_area(key=TRANSCRIPT_WIDGET_KEY).value
    assert app.button(key="agc_return_to_review")


def test_edit_revert_and_failed_reanalysis_keep_invalidation_notice() -> None:
    app = _analyzed_app()
    app.button(key="agc_back_to_inputs").click().run()
    app.switch_page("pages/review_inputs.py").run()
    original = app.text_area(key=TRANSCRIPT_WIDGET_KEY).value

    app.text_area(key=TRANSCRIPT_WIDGET_KEY).input(f"{original}\nEdited").run()
    app.text_area(key=TRANSCRIPT_WIDGET_KEY).input(original).run()

    assert app.session_state[ANALYSIS_INVALIDATION_KEY] is not None
    assert any("Inputs changed → analysis invalidated" in item.value for item in app.warning)
    assert all(item.key != "agc_return_to_review" for item in app.button)

    app.text_area(key=TRANSCRIPT_WIDGET_KEY).input(f"{original}\nUnsupported edit").run()
    app.button(key="agc_confirm_review_inputs").click().run()
    app.button(key="agc_analyze").click().run()

    assert not app.exception
    assert any("Analysis failed" in item.value for item in app.error)
    assert app.session_state[ANALYSIS_INVALIDATION_KEY] is not None
    assert app.session_state[ANALYSIS_SUCCESS_KEY] is False
    assert any("Inputs changed → analysis invalidated" in item.value for item in app.warning)


def test_sample_reload_requires_and_successful_reanalysis_restores_review() -> None:
    app = _analyzed_app()
    app.button(key="agc_back_to_inputs").click().run()
    app.switch_page("pages/review_inputs.py").run()
    original = app.text_area(key=TRANSCRIPT_WIDGET_KEY).value
    app.text_area(key=TRANSCRIPT_WIDGET_KEY).input(f"{original}\nEdited").run()

    app.button(key="agc_load_review_transcript").click().run()
    app.button(key="agc_load_review_metadata").click().run()
    app.button(key="agc_load_review_source").click().run()

    assert app.session_state[ANALYSIS_INVALIDATION_KEY] is not None
    assert all(item.key != "agc_return_to_review" for item in app.button)

    app.button(key="agc_confirm_review_inputs").click().run()
    app.button(key="agc_analyze").click().run()
    app.switch_page("pages/human_review.py").run()

    assert not app.exception
    assert app.session_state[ANALYSIS_INVALIDATION_KEY] is None
    assert app.session_state[ANALYSIS_SUCCESS_KEY] is True
    assert app.button(key="agc_confirm_review")
    assert any("Review analysis completed" in item.value for item in app.success)


def test_missing_metadata_and_output_deep_link_route_to_invalid_review_snapshot() -> None:
    app = _analyzed_app()
    app.session_state[CONTEXT_KEY] = None

    app.switch_page("pages/generated_outputs.py").run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Review step 2 — Human Review"]
    assert app.session_state[ANALYSIS_INVALIDATION_KEY] is not None
    assert any("Inputs changed → analysis invalidated" in item.value for item in app.warning)
    assert any("Previous Analysis Snapshot" in item.value for item in app.markdown)
    assert all(item.key != "agc_confirm_review" for item in app.button)


def test_unsubmitted_review_edits_do_not_replace_confirmed_snapshot() -> None:
    app = _analyzed_app()
    app.button(key="agc_confirm_review").click().run()
    confirmed_result = app.session_state[REVIEWED_RESULT_KEY]
    confirmed_summary = app.session_state[REVIEW_CHANGE_SUMMARY_KEY]
    confirmed_outputs = app.session_state[OUTPUTS_KEY]

    app.button(key="agc_back_to_review").click().run()
    app.switch_page("pages/human_review.py").run()
    app.text_input(key="agc_field_action_0_owner").input("Taylor Kim").run()
    app.button(key="agc_view_outputs").click().run()

    assert not app.exception
    assert app.session_state[REVIEWED_RESULT_KEY] == confirmed_result
    assert app.session_state[REVIEW_CHANGE_SUMMARY_KEY] == confirmed_summary
    assert app.session_state[OUTPUTS_KEY] == confirmed_outputs


def test_routed_back_navigation_preserves_pending_review_edits() -> None:
    app = _analyzed_app()
    app.text_input(key="agc_field_action_0_owner").input("Taylor Kim")

    app.button(key="agc_back_to_inputs").click().run()

    assert [item.value for item in app.header] == ["Review step 1 — Review Inputs"]
    app.switch_page("pages/review_inputs.py").run()
    assert app.session_state[ANALYSIS_INVALIDATION_KEY] is None
    assert app.button(key="agc_return_to_review")

    app.button(key="agc_return_to_review").click().run()

    assert [item.value for item in app.header] == ["Review step 2 — Human Review"]
    app.switch_page("pages/human_review.py").run()
    assert app.text_input(key="agc_field_action_0_owner").value == "Taylor Kim"
    assert [(item.label, item.value) for item in app.metric][0] == (
        "Outcome",
        "Changes Requested",
    )

    app.button(key="agc_confirm_review").click().run()

    assert any("Action item 1" in item.value and "Owner" in item.value for item in app.markdown)
    assert any("After — Taylor Kim" in item.value for item in app.caption)


def test_pending_review_awareness_updates_reverts_and_survives_routing() -> None:
    app = _analyzed_app()
    assert any("No pending human changes" in item.value for item in app.info)

    original_owner = app.text_input(key="agc_field_action_0_owner").value
    app.text_input(key="agc_field_action_0_owner").input("Taylor Kim").run()

    metrics = {item.label: item.value for item in app.metric}
    assert metrics["Modified fields"] == "1"
    assert metrics["Excluded items"] == "0"
    assert metrics["Affected sections"] == "1"
    assert metrics["Validation issues"] == "0"
    assert "Actions · 2 · 1 pending" in [tab.label for tab in app.tabs]
    assert any("Pending · 1 modified · Unconfirmed" in item.value for item in app.caption)

    app.checkbox(key="agc_field_question_0_include").uncheck().run()
    assert "Questions · 1 · 1 pending" in [tab.label for tab in app.tabs]
    assert any("Pending · Excluded · Unconfirmed" in item.value for item in app.caption)

    app.text_input(key="agc_field_action_0_due_date").input("next Friday").run()
    assert any("Action item 1 · Due date: Use YYYY-MM-DD." in item.value for item in app.warning)
    assert {item.label: item.value for item in app.metric}["Validation issues"] == "1"

    app.button(key="agc_back_to_inputs").click().run()
    app.switch_page("pages/review_inputs.py").run()
    app.button(key="agc_return_to_review").click().run()
    app.switch_page("pages/human_review.py").run()
    assert app.text_input(key="agc_field_action_0_owner").value == "Taylor Kim"
    assert any("Action item 1 · Due date: Use YYYY-MM-DD." in item.value for item in app.warning)

    app.text_input(key="agc_field_action_0_owner").input(original_owner).run()
    app.text_input(key="agc_field_action_0_due_date").input("2026-07-24").run()
    app.checkbox(key="agc_field_question_0_include").check().run()
    assert any("No pending human changes" in item.value for item in app.info)
    assert all("pending" not in tab.label for tab in app.tabs)


def test_incomplete_analysis_is_disabled_and_reset_restores_initial_screen() -> None:
    app = _review_inputs_app()
    assert app.button(key="agc_analyze").disabled
    app.button(key="agc_load_review_source").click().run()
    app.button(key="agc_load_review_transcript").click().run()
    app.button(key="agc_load_review_metadata").click().run()
    app.button(key="agc_confirm_review_inputs").click().run()
    app.button(key="agc_analyze").click().run()
    app.switch_page("pages/human_review.py").run()
    app.button(key="agc_confirm_review").click().run()
    app.switch_page("pages/generated_outputs.py").run()
    app.button(key="agc_reset_from_outputs").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Review step 1 — Review Inputs"]
    assert app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).value == ""
    assert app.session_state[ANALYSIS_INVALIDATION_KEY] is None
    assert all(item.value != "Review step 3 — Generated Outputs" for item in app.header)
