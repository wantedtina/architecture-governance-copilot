"""Streamlit application smoke and workflow tests."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import architecture_governance_copilot.ui_support as ui_support
from architecture_governance_copilot.ui_support import (
    DRAFT_CONTENT_WIDGET_KEY,
    DRAFT_SOURCE_CODE_WIDGET_KEY,
    DRAFT_SUPPORTING_DOCS_WIDGET_KEY,
    DRAFT_TEMPLATE_WIDGET_KEY,
    OUTPUTS_KEY,
    SOLUTION_INTENT_WIDGET_KEY,
    TRANSCRIPT_WIDGET_KEY,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = REPOSITORY_ROOT / "app.py"


def _initial_app() -> AppTest:
    return AppTest.from_file(str(APP_PATH), default_timeout=10).run()


def _review_inputs_app() -> AppTest:
    app = _initial_app()
    app.button(key="agc_use_existing_si").click().run()
    assert [item.value for item in app.header] == ["Stage 3 — Review Inputs"]
    # AppTest does not persist a programmatic route selection between later
    # interactions, so explicitly select the routed page.
    app.switch_page("pages/review_inputs.py").run()
    return app


def _analyzed_app() -> AppTest:
    app = _review_inputs_app()
    app.button(key="agc_load_sample").click().run()
    app.button(key="agc_analyze").click().run()
    # AppTest does not persist a programmatic route selection between later
    # interactions, so explicitly select the routed page after asserting the
    # navigation triggered by Analyze Review.
    assert [item.value for item in app.header] == ["Stage 4 — Human Review"]
    app.switch_page("pages/human_review.py").run()
    return app


def _assert_active_step(app: AppTest, label: str) -> None:
    stepper_markup = next(
        item.value for item in app.markdown if item.value.startswith('<div class="agc-stepper">')
    )
    assert "\n" not in stepper_markup
    assert stepper_markup.count('<div class="agc-step ') == 5
    assert "agc-step--active" in stepper_markup
    assert f"<strong>{label}</strong><span>In progress</span>" in stepper_markup


def _assert_completed_workflow(app: AppTest) -> None:
    stepper_markup = next(
        item.value for item in app.markdown if item.value.startswith('<div class="agc-stepper">')
    )
    assert "agc-step--active" not in stepper_markup
    assert stepper_markup.count("agc-step--complete") == 3
    assert "<strong>Project Context</strong><span>Skipped</span>" in stepper_markup
    assert "<strong>Draft Solution Intent</strong><span>Skipped</span>" in stepper_markup
    assert "<strong>Generated Outputs</strong><span>Complete</span>" in stepper_markup


def test_importing_app_does_not_load_sample_files(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_loaded() -> object:
        raise AssertionError("app import must not load sample files")

    monkeypatch.setattr(ui_support, "load_sample_review", fail_if_loaded)

    namespace = runpy.run_path(str(APP_PATH), run_name="app_import_smoke")

    assert "main" in namespace


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
    assert any("Domain Architect" in item.value for item in app.info)
    assert {button.label for button in app.button} >= {
        "Open Demonstration Project",
        "Use Existing Solution Intent",
        "Reset Workspace",
    }
    assert [item.value for item in app.header] == ["Stage 1 — Project Context"]
    _assert_active_step(app, "Project Context")
    assert app.button(key="agc_refresh_project_context").disabled
    assert all("Generated Outputs" not in item.value for item in app.header)
    assert not app.text_area


def test_drafted_si_can_be_confirmed_and_handed_to_existing_review_stage() -> None:
    app = _initial_app()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 1 — Project Context"]
    assert {button.label for button in app.button} >= {
        "Open Demonstration Project",
        "Use Existing Solution Intent",
    }
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
    assert [item.value for item in app.header] == ["Stage 2 — Draft Solution Intent"]
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
    assert any("Solution Intent draft generated" in item.value for item in app.success)

    app.button(key="agc_confirm_si_draft").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 3 — Review Inputs"]
    stepper_markup = next(
        item.value for item in app.markdown if item.value.startswith('<div class="agc-stepper">')
    )
    assert "<strong>Project Context</strong><span>Complete</span>" in stepper_markup
    assert "<strong>Draft Solution Intent</strong><span>Complete</span>" in stepper_markup
    assert "<strong>Review Inputs</strong><span>In progress</span>" in stepper_markup
    assert app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).value == generated.strip()
    assert app.text_area(key=TRANSCRIPT_WIDGET_KEY).value == ""
    assert any("Confirmed SI ready" in item.value for item in app.info)


def test_existing_si_can_load_review_companions_and_analyze() -> None:
    app = _review_inputs_app()
    generated = (REPOSITORY_ROOT / "samples" / "solution_intent.md").read_text(encoding="utf-8")
    app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).input(generated).run()

    assert app.button(key="agc_analyze").disabled
    app.button(key="agc_load_review_companions").click().run()

    assert app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).value == generated.strip()
    assert "[10:00] Priya Shah:" in app.text_area(key=TRANSCRIPT_WIDGET_KEY).value
    assert not app.button(key="agc_analyze").disabled

    app.button(key="agc_analyze").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 4 — Human Review"]


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
    assert [item.value for item in app.header] == ["Stage 3 — Review Inputs"]
    assert any(item.value == message for item in app.error)


def test_drafting_deep_link_requires_confirmed_project_context() -> None:
    app = _initial_app()

    app.switch_page("pages/solution_intent_drafting.py").run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 1 — Project Context"]
    assert any(
        item.value == "Confirm a Project Context package before drafting a Solution Intent."
        for item in app.error
    )


def test_sample_load_and_analysis_show_draft_without_automatic_outputs() -> None:
    app = _review_inputs_app()

    app.button(key="agc_load_sample").click().run()

    assert not app.exception
    assert not app.button(key="agc_analyze").disabled
    assert app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).value.startswith("# Solution Intent")
    assert "[10:00] Priya Shah:" in app.text_area(key=TRANSCRIPT_WIDGET_KEY).value
    assert any("Review package loaded" in item.value for item in app.success)

    app.button(key="agc_analyze").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 4 — Human Review"]
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
    assert all("Stage 5" not in item.value for item in app.header)


def test_human_edit_and_exclusion_generate_reviewed_outputs() -> None:
    app = _analyzed_app()

    app.text_input(key="agc_field_action_0_owner").input("Taylor Kim")
    app.checkbox(key="agc_field_question_0_include").uncheck()
    app.button(key="agc_confirm_review").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 5 — Generated Outputs"]
    _assert_completed_workflow(app)
    assert app.button(key="agc_back_to_review")
    assert app.button(key="agc_start_new_review")
    assert any("Governance package ready" in item.value for item in app.markdown)
    assert [(item.label, item.value) for item in app.metric] == [
        ("Workflow", "Complete"),
        ("Review Outcome", "Changes Requested"),
        ("Meeting Minutes", "1"),
        ("Work Item Previews", "2"),
    ]
    assert any(item.value == "Generated Review Record" for item in app.subheader)
    assert any(item.value == "Azure DevOps Work Item Previews" for item in app.subheader)
    assert any(
        item.value == "Preview only · No work items were submitted to Azure DevOps."
        for item in app.warning
    )
    assert any("Taylor Kim" in item.value for item in app.markdown)
    assert not any("Should Redis be used as a cache?" in item.value for item in app.markdown)
    assert sum("Work Item Preview" in item.value for item in app.markdown) == 2


def test_start_new_review_clears_completed_workflow_and_returns_to_drafting() -> None:
    app = _analyzed_app()
    app.button(key="agc_confirm_review").click().run()
    app.switch_page("pages/generated_outputs.py").run()

    app.button(key="agc_start_new_review").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 1 — Project Context"]
    assert not app.text_area
    assert app.session_state[OUTPUTS_KEY] is None


def test_invalid_review_date_shows_error_without_stale_outputs() -> None:
    app = _analyzed_app()
    app.text_input(key="agc_field_action_0_due_date").input("24 July 2026")

    app.button(key="agc_confirm_review").click().run()

    assert not app.exception
    assert any("Use YYYY-MM-DD" in item.value for item in app.error)
    assert all(item.value != "Stage 5 — Generated Outputs" for item in app.header)


def test_changed_inputs_make_analysis_stale_and_hide_previous_outputs() -> None:
    app = _analyzed_app()
    app.button(key="agc_confirm_review").click().run()
    assert any(item.value == "Stage 5 — Generated Outputs" for item in app.header)

    app.button(key="agc_back_to_review").click().run()
    app.switch_page("pages/human_review.py").run()
    app.button(key="agc_back_to_inputs").click().run()
    app.switch_page("pages/review_inputs.py").run()
    solution_intent = app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).value
    app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).input(
        f"{solution_intent}\nEdited after analysis"
    ).run()

    assert not app.exception
    assert any(
        "inputs changed" in item.value.lower() and "analy" in item.value.lower()
        for item in app.warning
    )
    assert all(item.key != "agc_confirm_review" for item in app.button)
    assert app.session_state[OUTPUTS_KEY] is None
    assert all(item.value != "Stage 5 — Generated Outputs" for item in app.header)


def test_routed_back_navigation_preserves_current_analysis() -> None:
    app = _analyzed_app()
    app.text_input(key="agc_field_action_0_owner").input("Taylor Kim").run()

    app.button(key="agc_back_to_inputs").click().run()

    assert [item.value for item in app.header] == ["Stage 3 — Review Inputs"]
    app.switch_page("pages/review_inputs.py").run()
    assert app.button(key="agc_return_to_review")

    app.button(key="agc_return_to_review").click().run()

    assert [item.value for item in app.header] == ["Stage 4 — Human Review"]
    app.switch_page("pages/human_review.py").run()
    assert app.text_input(key="agc_field_action_0_owner").value == "Taylor Kim"
    assert [(item.label, item.value) for item in app.metric][0] == (
        "Outcome",
        "Changes Requested",
    )


def test_incomplete_analysis_is_disabled_and_reset_restores_initial_screen() -> None:
    app = _review_inputs_app()
    assert app.button(key="agc_analyze").disabled
    app.button(key="agc_load_sample").click().run()
    app.button(key="agc_analyze").click().run()
    app.switch_page("pages/human_review.py").run()
    app.button(key="agc_confirm_review").click().run()
    app.switch_page("pages/generated_outputs.py").run()
    app.button(key="agc_reset_from_outputs").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 1 — Project Context"]
    assert not app.text_area
    assert all(item.value != "Stage 5 — Generated Outputs" for item in app.header)
