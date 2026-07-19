"""Streamlit application smoke and workflow tests."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import architecture_governance_copilot.ui_support as ui_support
from architecture_governance_copilot.ui_support import (
    OUTPUTS_KEY,
    SOLUTION_INTENT_WIDGET_KEY,
    TRANSCRIPT_WIDGET_KEY,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = REPOSITORY_ROOT / "app.py"


def _initial_app() -> AppTest:
    return AppTest.from_file(str(APP_PATH), default_timeout=10).run()


def _analyzed_app() -> AppTest:
    app = _initial_app()
    app.button(key="agc_load_sample").click().run()
    app.button(key="agc_analyze").click().run()
    # AppTest does not persist a programmatic route selection between later
    # interactions, so explicitly select the routed page after asserting the
    # navigation triggered by Analyze Review.
    assert [item.value for item in app.header] == ["Stage 2 — Human Review"]
    app.switch_page("pages/human_review.py").run()
    return app


def _assert_active_step(app: AppTest, label: str) -> None:
    stepper_markup = next(
        item.value for item in app.markdown if item.value.startswith('<div class="agc-stepper">')
    )
    assert "\n" not in stepper_markup
    assert stepper_markup.count('<div class="agc-step ') == 3
    assert "agc-step--active" in stepper_markup
    assert f"<strong>{label}</strong><span>In progress</span>" in stepper_markup


def _assert_completed_workflow(app: AppTest) -> None:
    stepper_markup = next(
        item.value for item in app.markdown if item.value.startswith('<div class="agc-stepper">')
    )
    assert "agc-step--active" not in stepper_markup
    assert stepper_markup.count("agc-step--complete") == 3
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
    assert any("synthetic data" in item.value for item in app.info)
    assert any("Domain Architect" in item.value for item in app.info)
    assert {button.label for button in app.button} >= {
        "Load Sample Review",
        "Analyze Review",
        "Reset Demo",
    }
    assert [item.value for item in app.header] == ["Stage 1 — Review Inputs"]
    _assert_active_step(app, "Review Inputs")
    assert all("Generated Outputs" not in item.value for item in app.header)
    assert len(app.text_area) == 2
    assert all(item.value == "" for item in app.text_area)


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
    assert [item.value for item in app.header] == ["Stage 1 — Review Inputs"]
    assert any(item.value == message for item in app.error)


def test_sample_load_and_analysis_show_draft_without_automatic_outputs() -> None:
    app = _initial_app()

    app.button(key="agc_load_sample").click().run()

    assert not app.exception
    assert app.text_area(key=SOLUTION_INTENT_WIDGET_KEY).value.startswith("# Solution Intent")
    assert "[10:00] Priya Shah:" in app.text_area(key=TRANSCRIPT_WIDGET_KEY).value
    assert any("Synthetic sample loaded" in item.value for item in app.success)

    app.button(key="agc_analyze").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 2 — Human Review"]
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
    assert all("Stage 3" not in item.value for item in app.header)


def test_human_edit_and_exclusion_generate_reviewed_outputs() -> None:
    app = _analyzed_app()

    app.text_input(key="agc_field_action_0_owner").input("Taylor Kim")
    app.checkbox(key="agc_field_question_0_include").uncheck()
    app.button(key="agc_confirm_review").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 3 — Generated Outputs"]
    _assert_completed_workflow(app)
    assert app.button(key="agc_back_to_review")
    assert app.button(key="agc_start_new_review")
    assert any("Governance package ready" in item.value for item in app.markdown)
    assert [(item.label, item.value) for item in app.metric] == [
        ("Workflow", "Complete"),
        ("Review Outcome", "Changes Requested"),
        ("Meeting Minutes", "1"),
        ("Mock Work Items", "2"),
    ]
    assert any(item.value == "Generated Review Record" for item in app.subheader)
    assert any(item.value == "Mock Azure DevOps Work Items" for item in app.subheader)
    assert any(
        item.value == "No real Azure DevOps work item has been created." for item in app.warning
    )
    assert any("Taylor Kim" in item.value for item in app.markdown)
    assert not any("Should Redis be used as a cache?" in item.value for item in app.markdown)
    assert sum("Mock Work Item" in item.value for item in app.markdown) == 2


def test_start_new_review_clears_completed_workflow_and_returns_to_inputs() -> None:
    app = _analyzed_app()
    app.button(key="agc_confirm_review").click().run()
    app.switch_page("pages/generated_outputs.py").run()

    app.button(key="agc_start_new_review").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 1 — Review Inputs"]
    assert all(item.value == "" for item in app.text_area)
    assert app.session_state[OUTPUTS_KEY] is None


def test_invalid_review_date_shows_error_without_stale_outputs() -> None:
    app = _analyzed_app()
    app.text_input(key="agc_field_action_0_due_date").input("24 July 2026")

    app.button(key="agc_confirm_review").click().run()

    assert not app.exception
    assert any("Use YYYY-MM-DD" in item.value for item in app.error)
    assert all(item.value != "Stage 3 — Generated Outputs" for item in app.header)


def test_changed_inputs_make_analysis_stale_and_hide_previous_outputs() -> None:
    app = _analyzed_app()
    app.button(key="agc_confirm_review").click().run()
    assert any(item.value == "Stage 3 — Generated Outputs" for item in app.header)

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
    assert all(item.value != "Stage 3 — Generated Outputs" for item in app.header)


def test_routed_back_navigation_preserves_current_analysis() -> None:
    app = _analyzed_app()
    app.text_input(key="agc_field_action_0_owner").input("Taylor Kim").run()

    app.button(key="agc_back_to_inputs").click().run()

    assert [item.value for item in app.header] == ["Stage 1 — Review Inputs"]
    app.switch_page("pages/review_inputs.py").run()
    assert app.button(key="agc_return_to_review")

    app.button(key="agc_return_to_review").click().run()

    assert [item.value for item in app.header] == ["Stage 2 — Human Review"]
    app.switch_page("pages/human_review.py").run()
    assert app.text_input(key="agc_field_action_0_owner").value == "Taylor Kim"
    assert [(item.label, item.value) for item in app.metric][0] == (
        "Outcome",
        "Changes Requested",
    )


def test_blank_analysis_is_rejected_and_reset_restores_initial_screen() -> None:
    app = _initial_app()

    app.button(key="agc_analyze").click().run()

    assert not app.exception
    assert any("Solution Intent must not be blank" in item.value for item in app.error)
    assert [item.value for item in app.header] == ["Stage 1 — Review Inputs"]

    app.button(key="agc_load_sample").click().run()
    app.button(key="agc_analyze").click().run()
    app.switch_page("pages/human_review.py").run()
    app.button(key="agc_confirm_review").click().run()
    app.switch_page("pages/generated_outputs.py").run()
    app.button(key="agc_reset_from_outputs").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 1 — Review Inputs"]
    assert all(item.value == "" for item in app.text_area)
    assert all(item.value != "Stage 3 — Generated Outputs" for item in app.header)
