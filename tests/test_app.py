"""Streamlit application smoke and workflow tests."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import architecture_governance_copilot.ui_support as ui_support
from architecture_governance_copilot.ui_support import (
    SOLUTION_INTENT_KEY,
    TRANSCRIPT_KEY,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = REPOSITORY_ROOT / "app.py"


def _initial_app() -> AppTest:
    return AppTest.from_file(str(APP_PATH), default_timeout=10).run()


def _analyzed_app() -> AppTest:
    app = _initial_app()
    app.button(key="agc_load_sample").click().run()
    app.button(key="agc_analyze").click().run()
    return app


def test_importing_app_does_not_load_sample_files(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_loaded() -> object:
        raise AssertionError("app import must not load sample files")

    monkeypatch.setattr(ui_support, "load_sample_review", fail_if_loaded)

    namespace = runpy.run_path(str(APP_PATH), run_name="app_import_smoke")

    assert "main" in namespace


def test_initial_page_has_required_controls_and_no_generated_outputs() -> None:
    app = _initial_app()

    assert not app.exception
    assert [item.value for item in app.title] == ["Architecture Governance Copilot"]
    assert any("synthetic data" in item.value for item in app.info)
    assert any("Domain Architect" in item.value for item in app.info)
    assert {button.label for button in app.button} >= {
        "Load Sample Review",
        "Analyze Review",
        "Reset Demo",
    }
    assert [item.value for item in app.header] == ["Stage 1 — Review Inputs"]
    assert all("Generated Outputs" not in item.value for item in app.header)
    assert len(app.text_area) == 2
    assert all(item.value == "" for item in app.text_area)


def test_sample_load_and_analysis_show_draft_without_automatic_outputs() -> None:
    app = _initial_app()

    app.button(key="agc_load_sample").click().run()

    assert not app.exception
    assert app.text_area(key=SOLUTION_INTENT_KEY).value.startswith("# Solution Intent")
    assert "[10:00] Priya Shah:" in app.text_area(key=TRANSCRIPT_KEY).value
    assert any("Synthetic sample loaded" in item.value for item in app.success)

    app.button(key="agc_analyze").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == [
        "Stage 1 — Review Inputs",
        "Stage 2 — Human Review",
    ]
    assert [(item.label, item.value) for item in app.metric] == [
        ("Outcome", "Changes Requested"),
        ("Decisions", "1"),
        ("Findings", "3"),
        ("Risks", "1"),
        ("Actions", "2"),
        ("Open Questions", "1"),
        ("Missing Information", "2"),
    ]
    assert any("no outputs were generated automatically" in item.value for item in app.success)
    assert all("Stage 3" not in item.value for item in app.header)


def test_human_edit_and_exclusion_generate_reviewed_outputs() -> None:
    app = _analyzed_app()

    app.text_input(key="agc_field_action_0_owner").input("Taylor Kim")
    app.checkbox(key="agc_field_question_0_include").uncheck()
    app.button(key="agc_confirm_review").click().run()

    assert not app.exception
    assert [item.value for item in app.header][-1] == "Stage 3 — Generated Outputs"
    assert any(item.value == "Generated Review Record" for item in app.subheader)
    assert any(item.value == "Mock Azure DevOps Work Items" for item in app.subheader)
    assert any(
        item.value == "No real Azure DevOps work item has been created." for item in app.warning
    )
    assert any("Taylor Kim" in item.value for item in app.markdown)
    assert not any("Should Redis be used as a cache?" in item.value for item in app.markdown)
    assert sum("Mock Work Item" in item.value for item in app.markdown) == 2


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

    solution_intent = app.text_area(key=SOLUTION_INTENT_KEY).value
    app.text_area(key=SOLUTION_INTENT_KEY).input(f"{solution_intent}\nEdited after analysis").run()

    assert not app.exception
    assert any("inputs changed after analysis" in item.value.lower() for item in app.warning)
    assert app.button(key="agc_confirm_review").disabled is True
    assert all(item.value != "Stage 3 — Generated Outputs" for item in app.header)


def test_blank_analysis_is_rejected_and_reset_restores_initial_screen() -> None:
    app = _initial_app()

    app.button(key="agc_analyze").click().run()

    assert not app.exception
    assert any("Solution Intent must not be blank" in item.value for item in app.error)
    assert [item.value for item in app.header] == ["Stage 1 — Review Inputs"]

    app.button(key="agc_load_sample").click().run()
    app.button(key="agc_analyze").click().run()
    app.button(key="agc_confirm_review").click().run()
    app.button(key="agc_reset").click().run()

    assert not app.exception
    assert [item.value for item in app.header] == ["Stage 1 — Review Inputs"]
    assert all(item.value == "" for item in app.text_area)
    assert all(item.value != "Stage 3 — Generated Outputs" for item in app.header)
