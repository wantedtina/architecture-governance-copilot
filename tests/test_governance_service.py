"""Tests for governance-service orchestration and human-review boundaries."""

from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError, fields
from datetime import date
from pathlib import Path
from typing import get_type_hints

import pytest

import architecture_governance_copilot.governance_service as governance_service_module
from architecture_governance_copilot import GovernanceOutputs, GovernanceReviewService
from architecture_governance_copilot.ado_generator import generate_mock_ado_work_items
from architecture_governance_copilot.extractors import (
    DeterministicDemoExtractor,
    DeterministicFixtureError,
    GovernanceExtractor,
)
from architecture_governance_copilot.minutes_generator import generate_review_minutes
from architecture_governance_copilot.models import (
    FindingSeverity,
    GovernanceResult,
    MockAdoWorkItem,
    SolutionIntentReviewContext,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = REPOSITORY_ROOT / "samples"
SOLUTION_INTENT_PATH = SAMPLES_DIR / "solution_intent.md"
TRANSCRIPT_PATH = SAMPLES_DIR / "review_transcript.txt"
METADATA_PATH = SAMPLES_DIR / "review_metadata.json"
EXPECTED_RESULT_PATH = SAMPLES_DIR / "expected_result.json"


class FocusedExtractorError(RuntimeError):
    """Represent a focused test-double extraction failure."""


class RecordingExtractor:
    """Record extraction arguments and return or raise a configured value."""

    def __init__(
        self,
        result: GovernanceResult,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.calls: list[tuple[str, str, SolutionIntentReviewContext]] = []

    def extract(
        self,
        solution_intent: str,
        review_transcript: str,
        context: SolutionIntentReviewContext,
    ) -> GovernanceResult:
        self.calls.append((solution_intent, review_transcript, context))
        if self.error is not None:
            raise self.error
        return self.result


@pytest.fixture
def sample_result() -> GovernanceResult:
    """Load the validated synthetic governance result."""
    return GovernanceResult.model_validate_json(EXPECTED_RESULT_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def sample_context() -> SolutionIntentReviewContext:
    """Load the validated synthetic review context."""
    return SolutionIntentReviewContext.model_validate_json(
        METADATA_PATH.read_text(encoding="utf-8")
    )


def test_service_accepts_structural_extractor_and_has_synchronous_public_api(
    sample_result: GovernanceResult,
    sample_context: SolutionIntentReviewContext,
) -> None:
    extractor = RecordingExtractor(sample_result)
    service = GovernanceReviewService(extractor)

    assert isinstance(extractor, GovernanceExtractor)
    assert not inspect.iscoroutinefunction(service.analyze_review)
    assert not inspect.iscoroutinefunction(service.generate_outputs)
    analysis = service.analyze_review("SI", "transcript", sample_context)
    outputs = service.generate_outputs(sample_result)
    assert not inspect.isawaitable(analysis)
    assert not inspect.isawaitable(outputs)


def test_public_method_annotations_match_the_service_contract() -> None:
    assert get_type_hints(GovernanceOutputs) == {
        "review_minutes": str,
        "ado_work_items": tuple[MockAdoWorkItem, ...],
    }
    assert get_type_hints(GovernanceReviewService.analyze_review) == {
        "solution_intent": str,
        "review_transcript": str,
        "context": SolutionIntentReviewContext,
        "return": GovernanceResult,
    }
    assert get_type_hints(GovernanceReviewService.generate_outputs) == {
        "reviewed_result": GovernanceResult,
        "return": GovernanceOutputs,
    }


def test_governance_outputs_is_frozen_slotted_and_uses_tuple() -> None:
    outputs = GovernanceOutputs(review_minutes="Reviewed minutes", ado_work_items=())

    assert [field.name for field in fields(GovernanceOutputs)] == [
        "review_minutes",
        "ado_work_items",
    ]
    assert isinstance(outputs.ado_work_items, tuple)
    assert not hasattr(outputs, "__dict__")
    with pytest.raises(FrozenInstanceError):
        outputs.review_minutes = "Replacement minutes"
    with pytest.raises(FrozenInstanceError):
        outputs.ado_work_items = ()


def test_analyze_review_delegates_exact_arguments_once_without_rewriting(
    sample_result: GovernanceResult,
    sample_context: SolutionIntentReviewContext,
) -> None:
    solution_intent = "".join(["  Synthetic SI", "\r\n", "with final spaces  "])
    transcript = "".join(["\n", "  [10:00] Synthetic transcript", "\r\n"])
    context_before = sample_context.model_dump(mode="json")
    extractor = RecordingExtractor(sample_result)
    service = GovernanceReviewService(extractor)

    returned = service.analyze_review(solution_intent, transcript, sample_context)

    assert returned is sample_result
    assert len(extractor.calls) == 1
    supplied_si, supplied_transcript, supplied_context = extractor.calls[0]
    assert supplied_si is solution_intent
    assert supplied_transcript is transcript
    assert supplied_context is sample_context
    assert supplied_si.startswith("  ")
    assert supplied_si.endswith("  ")
    assert "\r\n" in supplied_si
    assert supplied_transcript.startswith("\n")
    assert sample_context.model_dump(mode="json") == context_before


def test_analyze_review_does_not_call_output_generators(
    monkeypatch: pytest.MonkeyPatch,
    sample_result: GovernanceResult,
    sample_context: SolutionIntentReviewContext,
) -> None:
    def fail_if_called(_: GovernanceResult) -> str:
        raise AssertionError("output generator must not run during analysis")

    monkeypatch.setattr(governance_service_module, "generate_review_minutes", fail_if_called)
    monkeypatch.setattr(governance_service_module, "generate_mock_ado_work_items", fail_if_called)
    service = GovernanceReviewService(RecordingExtractor(sample_result))

    assert service.analyze_review("SI", "transcript", sample_context) is sample_result


@pytest.mark.parametrize(
    "error",
    [
        ValueError("Solution Intent does not match the deterministic demo fixture."),
        DeterministicFixtureError("Deterministic expected result is invalid."),
        FocusedExtractorError("Focused test-double extraction failure."),
    ],
)
def test_analyze_review_propagates_extractor_exceptions_unchanged(
    error: Exception,
    sample_result: GovernanceResult,
    sample_context: SolutionIntentReviewContext,
) -> None:
    complete_document = "COMPLETE-SYNTHETIC-DOCUMENT-CONTENT"
    extractor = RecordingExtractor(sample_result, error=error)
    service = GovernanceReviewService(extractor)

    with pytest.raises(type(error), match=str(error)) as captured:
        service.analyze_review(complete_document, "complete transcript", sample_context)

    assert captured.value is error
    assert complete_document not in str(captured.value)
    assert len(extractor.calls) == 1


def test_generate_outputs_matches_direct_generators_without_using_extractor(
    sample_result: GovernanceResult,
) -> None:
    extractor = RecordingExtractor(
        sample_result,
        error=AssertionError("extractor must not run during output generation"),
    )
    service = GovernanceReviewService(extractor)
    before = sample_result.model_dump(mode="json")

    outputs = service.generate_outputs(sample_result)

    assert isinstance(outputs, GovernanceOutputs)
    assert outputs.review_minutes == generate_review_minutes(sample_result)
    assert outputs.ado_work_items == tuple(generate_mock_ado_work_items(sample_result))
    assert isinstance(outputs.ado_work_items, tuple)
    assert [item.source_action_index for item in outputs.ado_work_items] == [0, 1]
    assert extractor.calls == []
    assert sample_result.model_dump(mode="json") == before
    assert not hasattr(outputs, "approved")


def test_generate_outputs_preserves_validated_human_review_edits(
    sample_result: GovernanceResult,
) -> None:
    edited = sample_result.model_copy(deep=True)
    edited.findings[0].title = "Human-reviewed failover finding"
    edited.findings[0].severity = FindingSeverity.CRITICAL
    edited.findings[0].recommended_change = "Use the human-reviewed failure-path wording."
    edited.action_items[0].owner = "Morgan Rivera"
    edited.action_items[1].due_date = date(2026, 7, 30)
    removed_question = edited.open_questions.pop().question
    reviewed_result = GovernanceResult.model_validate(edited.model_dump(mode="json"))
    extractor = RecordingExtractor(
        sample_result,
        error=AssertionError("reviewed output generation must not rerun extraction"),
    )
    service = GovernanceReviewService(extractor)

    outputs = service.generate_outputs(reviewed_result)

    assert "Human-reviewed failover finding" in outputs.review_minutes
    assert "**Severity:** Critical" in outputs.review_minutes
    assert "Use the human-reviewed failure-path wording." in outputs.review_minutes
    assert outputs.ado_work_items[0].assigned_to == "Morgan Rivera"
    assert "Owner: Morgan Rivera" in outputs.ado_work_items[0].description
    assert outputs.ado_work_items[1].due_date == date(2026, 7, 30)
    assert removed_question not in outputs.review_minutes
    assert sample_result.findings[0].title != "Human-reviewed failover finding"
    assert sample_result.findings[0].severity is FindingSeverity.HIGH
    assert sample_result.action_items[0].owner == "Alex Chen"
    assert sample_result.action_items[1].due_date == date(2026, 7, 25)
    assert len(sample_result.open_questions) == 1
    assert extractor.calls == []


def test_analysis_and_output_generation_remain_separate_public_stages(
    sample_result: GovernanceResult,
    sample_context: SolutionIntentReviewContext,
) -> None:
    service = GovernanceReviewService(RecordingExtractor(sample_result))

    analysis = service.analyze_review("SI", "transcript", sample_context)

    assert isinstance(analysis, GovernanceResult)
    assert not isinstance(analysis, GovernanceOutputs)
    assert list(inspect.signature(service.generate_outputs).parameters) == ["reviewed_result"]
    assert not hasattr(service, "analyze_and_generate")
    assert not hasattr(service, "process_review")
    assert not hasattr(service, "approve")
    assert not hasattr(service, "approve_review")
    assert not hasattr(service, "auto_approve")
    assert not hasattr(service, "finalize_approval")
    assert not hasattr(service, "authorize")
    assert not hasattr(service, "publish")
    assert not hasattr(service, "publish_review")


def test_generate_outputs_calls_generators_in_required_order(
    monkeypatch: pytest.MonkeyPatch,
    sample_result: GovernanceResult,
) -> None:
    calls: list[str] = []
    expected_items = generate_mock_ado_work_items(sample_result)

    def record_minutes(reviewed_result: GovernanceResult) -> str:
        assert reviewed_result is sample_result
        calls.append("minutes")
        return "Exact generated minutes"

    def record_ado(reviewed_result: GovernanceResult) -> list[MockAdoWorkItem]:
        assert reviewed_result is sample_result
        calls.append("ado")
        return expected_items

    monkeypatch.setattr(governance_service_module, "generate_review_minutes", record_minutes)
    monkeypatch.setattr(governance_service_module, "generate_mock_ado_work_items", record_ado)
    service = GovernanceReviewService(RecordingExtractor(sample_result))

    outputs = service.generate_outputs(sample_result)

    assert calls == ["minutes", "ado"]
    assert outputs == GovernanceOutputs(
        review_minutes="Exact generated minutes",
        ado_work_items=tuple(expected_items),
    )


def test_repeated_output_generation_is_deterministic_and_independent(
    sample_result: GovernanceResult,
) -> None:
    service = GovernanceReviewService(RecordingExtractor(sample_result))
    source_before = sample_result.model_dump(mode="json")

    first = service.generate_outputs(sample_result)
    second = service.generate_outputs(sample_result)

    assert first == second
    assert first is not second
    assert first.ado_work_items is not second.ado_work_items
    assert first.ado_work_items[0] is not second.ado_work_items[0]
    assert first.ado_work_items[0].tags is not second.ado_work_items[0].tags
    assert (
        first.ado_work_items[0].acceptance_criteria
        is not second.ado_work_items[0].acceptance_criteria
    )

    first.ado_work_items[0].title = "Mutated generated title"
    first.ado_work_items[0].tags.append("Mutated generated tag")
    first.ado_work_items[0].acceptance_criteria.append("Mutated generated criterion")
    later = service.generate_outputs(sample_result)

    assert later == second
    assert "Mutated generated tag" not in later.ado_work_items[0].tags
    assert later.ado_work_items[0].acceptance_criteria == []
    assert sample_result.model_dump(mode="json") == source_before


def test_generate_outputs_supports_reviewed_result_without_actions(
    sample_result: GovernanceResult,
) -> None:
    payload = sample_result.model_dump(mode="json")
    payload["action_items"] = []
    reviewed_result = GovernanceResult.model_validate(payload)
    service = GovernanceReviewService(RecordingExtractor(sample_result))

    outputs = service.generate_outputs(reviewed_result)

    assert "# Solution Intent Review Record" in outputs.review_minutes
    assert "## Action Items\n\nNone recorded." in outputs.review_minutes
    assert outputs.ado_work_items == ()


def test_realistic_deterministic_service_flow_requires_no_external_integration() -> None:
    solution_intent = SOLUTION_INTENT_PATH.read_text(encoding="utf-8")
    transcript = TRANSCRIPT_PATH.read_text(encoding="utf-8")
    context = SolutionIntentReviewContext.model_validate_json(
        METADATA_PATH.read_text(encoding="utf-8")
    )
    service = GovernanceReviewService(DeterministicDemoExtractor())

    result = service.analyze_review(solution_intent, transcript, context)
    outputs = service.generate_outputs(result)

    assert result.review_outcome.value == "changes_requested"
    assert len(result.decisions) == 1
    assert len(result.findings) == 3
    assert len(result.risks) == 1
    assert len(result.action_items) == 2
    assert len(result.open_questions) == 1
    assert "**Outcome:** Changes Requested" in outputs.review_minutes
    assert len(outputs.ado_work_items) == 2


def test_minutes_generator_exception_propagates_and_stops_output_generation(
    monkeypatch: pytest.MonkeyPatch,
    sample_result: GovernanceResult,
) -> None:
    error = RuntimeError("Focused minutes generation failure")
    ado_called = False

    def raise_minutes(_: GovernanceResult) -> str:
        raise error

    def record_ado_call(_: GovernanceResult) -> list[object]:
        nonlocal ado_called
        ado_called = True
        return []

    monkeypatch.setattr(governance_service_module, "generate_review_minutes", raise_minutes)
    monkeypatch.setattr(
        governance_service_module,
        "generate_mock_ado_work_items",
        record_ado_call,
    )
    service = GovernanceReviewService(RecordingExtractor(sample_result))

    with pytest.raises(RuntimeError, match=str(error)) as captured:
        service.generate_outputs(sample_result)

    assert captured.value is error
    assert ado_called is False


def test_ado_generator_exception_propagates_without_partial_output(
    monkeypatch: pytest.MonkeyPatch,
    sample_result: GovernanceResult,
) -> None:
    error = RuntimeError("Focused mock ADO generation failure")

    def raise_ado(_: GovernanceResult) -> list[object]:
        raise error

    monkeypatch.setattr(governance_service_module, "generate_mock_ado_work_items", raise_ado)
    service = GovernanceReviewService(RecordingExtractor(sample_result))

    with pytest.raises(RuntimeError, match=str(error)) as captured:
        service.generate_outputs(sample_result)

    assert captured.value is error
