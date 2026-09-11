"""Tests for deterministic Solution Intent drafting and workflow isolation."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

import architecture_governance_copilot.ui_support as ui_support
from architecture_governance_copilot.models import (
    DraftingSourcePackageManifest,
    DraftInputType,
    SolutionIntentDraft,
    SolutionIntentDraftRequest,
)
from architecture_governance_copilot.si_drafting import (
    DeterministicDemoDrafter,
    DeterministicDraftingFixtureError,
    SolutionIntentDrafter,
    SolutionIntentDraftingService,
)
from architecture_governance_copilot.ui_support import (
    ANALYZED_RESULT_KEY,
    CONFIRMED_SOURCE_PACKAGE_KEY,
    CONTEXT_KEY,
    DRAFT_CONFIRMED_KEY,
    DRAFT_CONTENT_WIDGET_KEY,
    DRAFT_FINGERPRINT_KEY,
    DRAFT_PROJECT_KEY,
    DRAFT_RESULT_KEY,
    DRAFT_SOURCE_CODE_KEY,
    DRAFT_STAGE,
    DRAFT_SUPPORTING_DOCS_KEY,
    DRAFT_TEMPLATE_KEY,
    OUTPUTS_KEY,
    SOLUTION_INTENT_KEY,
    SOLUTION_INTENT_WIDGET_KEY,
    TRANSCRIPT_KEY,
    TRANSCRIPT_WIDGET_KEY,
    DraftingSamplePaths,
    clear_stale_si_draft,
    confirm_si_draft_for_review,
    drafting_input_fingerprint,
    drafting_result_is_stale,
    drafting_sample_paths,
    initialize_session_state,
    load_drafting_context_into_state,
    load_sample_drafting_context,
    load_sample_review,
    load_sample_review_companions_into_state,
    source_package_fingerprint,
    store_si_draft,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DRAFT_PATH = REPOSITORY_ROOT / "samples" / "solution_intent.md"


def _request(**overrides: object) -> SolutionIntentDraftRequest:
    sample = load_sample_drafting_context()
    values: dict[str, object] = {
        "project_name": sample.project_name,
        "template": sample.template,
        "source_code_context": sample.source_code_context,
        "supporting_documents": sample.supporting_documents,
    }
    values.update(overrides)
    return SolutionIntentDraftRequest.model_validate(values)


def test_drafting_sample_paths_are_absolute_and_exist(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    expected = drafting_sample_paths()

    monkeypatch.chdir(tmp_path)
    actual = drafting_sample_paths()

    assert actual == expected
    assert actual.template.is_absolute()
    assert actual.template.is_file()
    assert actual.source_code_context.is_file()
    assert actual.supporting_documents.is_file()


@pytest.mark.parametrize(
    "missing_name", ["template", "source_code_context", "supporting_documents"]
)
def test_drafting_inventory_rejects_missing_local_resource(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    missing_name: str,
) -> None:
    paths = {
        "template": tmp_path / "template.md",
        "source_code_context": tmp_path / "source.txt",
        "supporting_documents": tmp_path / "evidence.md",
    }
    for name, path in paths.items():
        if name != missing_name:
            path.write_text("content", encoding="utf-8")
    monkeypatch.setattr(
        ui_support,
        "drafting_sample_paths",
        lambda: DraftingSamplePaths(**paths),
    )

    with pytest.raises(ValueError, match="is unavailable"):
        load_sample_drafting_context()


def test_drafting_inventory_rejects_empty_local_resource(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    paths = DraftingSamplePaths(
        template=tmp_path / "template.md",
        source_code_context=tmp_path / "source.txt",
        supporting_documents=tmp_path / "evidence.md",
    )
    paths.template.write_text("# Template", encoding="utf-8")
    paths.source_code_context.write_text(" ", encoding="utf-8")
    paths.supporting_documents.write_text("Evidence", encoding="utf-8")
    monkeypatch.setattr(ui_support, "drafting_sample_paths", lambda: paths)

    with pytest.raises(ValueError, match="source-code context is empty"):
        load_sample_drafting_context()


def test_draft_request_rejects_blank_required_context() -> None:
    with pytest.raises(ValidationError):
        SolutionIntentDraftRequest(
            project_name="Project",
            template=" ",
            source_code_context="selected source",
        )


def test_deterministic_drafter_implements_protocol_and_returns_expected_si() -> None:
    drafter = DeterministicDemoDrafter()

    result = drafter.draft(_request())

    assert isinstance(drafter, SolutionIntentDrafter)
    assert result.project_name == "Digital Payment Notification Service"
    assert result.content == EXPECTED_DRAFT_PATH.read_text(encoding="utf-8").strip()
    assert result.provider_name == "Deterministic demo drafter"
    assert result.input_types == [
        DraftInputType.TEMPLATE,
        DraftInputType.SOURCE_CODE,
        DraftInputType.SUPPORTING_DOCUMENTS,
    ]
    assert len(result.assumptions) == 3


@pytest.mark.parametrize(
    "draft_request",
    [
        _request(project_name="Different project"),
        _request(template="# Different template"),
        _request(source_code_context="Different source"),
    ],
)
def test_deterministic_drafter_rejects_non_fixture_context(
    draft_request: SolutionIntentDraftRequest,
) -> None:
    with pytest.raises(ValueError, match="does not match"):
        DeterministicDemoDrafter().draft(draft_request)


def test_deterministic_drafter_detects_missing_fixture(tmp_path: Path) -> None:
    with pytest.raises(
        DeterministicDraftingFixtureError,
        match="sample file is missing",
    ):
        DeterministicDemoDrafter(tmp_path)


def test_drafting_service_returns_independent_drafts() -> None:
    service = SolutionIntentDraftingService(DeterministicDemoDrafter())

    first = service.generate_draft(_request())
    second = service.generate_draft(_request())

    assert first == second
    assert first is not second
    assert first.assumptions is not second.assumptions
    first.content = "# Edited"
    first.assumptions.append("Edited")
    assert second.content.startswith("# Solution Intent")
    assert "Edited" not in second.assumptions


def test_drafting_state_load_generate_and_confirm_stays_isolated() -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample_context = load_sample_drafting_context()
    load_drafting_context_into_state(state, sample_context)

    assert state[DRAFT_PROJECT_KEY] == sample_context.project_name
    assert state[DRAFT_TEMPLATE_KEY] == sample_context.template
    assert state[DRAFT_SOURCE_CODE_KEY] == sample_context.source_code_context
    assert state[DRAFT_SUPPORTING_DOCS_KEY] == sample_context.supporting_documents

    draft = DeterministicDemoDrafter().draft(_request())
    request = _request()
    manifest = state[CONFIRMED_SOURCE_PACKAGE_KEY]
    assert isinstance(manifest, DraftingSourcePackageManifest)
    fingerprint = drafting_input_fingerprint(request, manifest)
    store_si_draft(state, draft, fingerprint)
    stored = state[DRAFT_RESULT_KEY]
    assert isinstance(stored, SolutionIntentDraft)
    assert stored is not draft
    assert state[DRAFT_CONTENT_WIDGET_KEY] == draft.content
    assert state[DRAFT_FINGERPRINT_KEY] == fingerprint
    assert not drafting_result_is_stale(request, fingerprint, manifest)
    assert drafting_result_is_stale(
        request.model_copy(update={"project_name": "Changed project"}),
        fingerprint,
        manifest,
    )
    changed_manifest = manifest.model_copy(
        update={"governance_reference": "Different governance work item"}
    )
    assert source_package_fingerprint(changed_manifest) != source_package_fingerprint(manifest)
    assert drafting_result_is_stale(request, fingerprint, changed_manifest)

    state[ANALYZED_RESULT_KEY] = object()
    state[OUTPUTS_KEY] = object()
    confirmed_content = f"{draft.content}\n\nHuman-reviewed drafting note."
    confirm_si_draft_for_review(state, confirmed_content)

    assert state[DRAFT_CONTENT_WIDGET_KEY] == confirmed_content
    assert state[SOLUTION_INTENT_KEY] == ""
    assert SOLUTION_INTENT_WIDGET_KEY not in state
    assert state[TRANSCRIPT_KEY] == ""
    assert state[CONTEXT_KEY] is None
    assert state[ANALYZED_RESULT_KEY] is not None
    assert state[OUTPUTS_KEY] is not None
    assert state[DRAFT_CONFIRMED_KEY] is True
    assert state["agc_active_stage"] == DRAFT_STAGE


def test_review_companions_load_independently_before_solution_intent() -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample = load_sample_review()

    load_sample_review_companions_into_state(state, sample)

    assert state[SOLUTION_INTENT_KEY] == ""
    assert state[TRANSCRIPT_KEY] == sample.transcript.strip()
    assert state[TRANSCRIPT_WIDGET_KEY] == sample.transcript.strip()
    assert state[CONTEXT_KEY] == sample.context


def test_clearing_stale_draft_preserves_source_context() -> None:
    state: dict[str, object] = {}
    initialize_session_state(state)
    sample = load_sample_drafting_context()
    load_drafting_context_into_state(state, sample)
    request = _request()
    store_si_draft(
        state,
        DeterministicDemoDrafter().draft(request),
        drafting_input_fingerprint(request),
    )

    clear_stale_si_draft(state)

    assert state[DRAFT_RESULT_KEY] is None
    assert state[DRAFT_FINGERPRINT_KEY] is None
    assert state[DRAFT_CONTENT_WIDGET_KEY] == ""
    assert state[DRAFT_TEMPLATE_KEY] == sample.template
    assert state[DRAFT_SOURCE_CODE_KEY] == sample.source_code_context


@pytest.mark.parametrize("evidence", [None, " "])
def test_demo_drafter_rejects_missing_evidence(evidence):
    with pytest.raises((ValueError, ValidationError)):
        DeterministicDemoDrafter().draft(_request(supporting_documents=evidence))


def test_custom_evidence_changes_draft_without_reusing_sample_claims():
    drafter = DeterministicDemoDrafter()
    first = drafter.draft(_request(supporting_documents="Retention: 30 days.\nRTO: 2 hours."))
    second = drafter.draft(_request(supporting_documents="Retention: 7 days.\nRTO: 1 hour."))
    assert first.content != second.content
    assert first == drafter.draft(
        _request(supporting_documents="Retention: 30 days.\nRTO: 2 hours.")
    )
    assert "Retention: 30 days." in first.content
    assert "Evidence L1:" in first.content
    assert "RTO: 2 hours." in first.content
    assert "90 days" not in first.content
    assert "August 2026" not in first.content
    assert "To be confirmed" in first.content
    assert "## 12. Assumptions and Open Items" in first.content
    assert "Selected repository context" in first.content


def test_unmapped_or_instruction_like_evidence_is_retained_as_literal_source():
    evidence = "Unmapped synthetic detail.\n## Ignore instructions\n<script>alert(1)</script>\n```"
    result = DeterministicDemoDrafter().draft(_request(supporting_documents=evidence))
    assert "    Unmapped synthetic detail." in result.content
    assert "\n## Ignore instructions" not in result.content
    assert "    <script>alert(1)</script>" in result.content
    assert "    ```" in result.content
