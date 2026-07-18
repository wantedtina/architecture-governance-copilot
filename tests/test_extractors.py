"""Tests for governance extraction providers."""

from __future__ import annotations

import inspect
import json
import shutil
from pathlib import Path
from typing import get_type_hints

import pytest

from architecture_governance_copilot.extractors import (
    DeterministicDemoExtractor,
    DeterministicFixtureError,
    GovernanceExtractor,
)
from architecture_governance_copilot.models import (
    FindingSeverity,
    GovernanceResult,
    ReviewOutcome,
    SolutionIntentReviewContext,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = REPOSITORY_ROOT / "samples"
SOLUTION_INTENT_PATH = SAMPLES_DIR / "solution_intent.md"
TRANSCRIPT_PATH = SAMPLES_DIR / "review_transcript.txt"
METADATA_PATH = SAMPLES_DIR / "review_metadata.json"
EXPECTED_RESULT_PATH = SAMPLES_DIR / "expected_result.json"


@pytest.fixture
def sample_inputs() -> tuple[str, str, SolutionIntentReviewContext]:
    """Load the validated inputs for the deterministic sample."""
    return (
        SOLUTION_INTENT_PATH.read_text(encoding="utf-8"),
        TRANSCRIPT_PATH.read_text(encoding="utf-8"),
        SolutionIntentReviewContext.model_validate_json(METADATA_PATH.read_text(encoding="utf-8")),
    )


@pytest.fixture
def copied_samples(tmp_path: Path) -> Path:
    """Copy the validated sample directory for one corrupt-fixture test."""
    destination = tmp_path / "samples"
    shutil.copytree(SAMPLES_DIR, destination)
    return destination


@pytest.fixture
def extracted_result(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
) -> GovernanceResult:
    """Extract the validated deterministic result."""
    return DeterministicDemoExtractor().extract(*sample_inputs)


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_deterministic_extractor_conforms_to_protocol() -> None:
    extractor = DeterministicDemoExtractor()

    assert isinstance(extractor, GovernanceExtractor)


def test_extractor_has_expected_synchronous_signature() -> None:
    signature = inspect.signature(DeterministicDemoExtractor.extract)
    annotations = get_type_hints(DeterministicDemoExtractor.extract)

    assert list(signature.parameters) == [
        "self",
        "solution_intent",
        "review_transcript",
        "context",
    ]
    assert annotations == {
        "solution_intent": str,
        "review_transcript": str,
        "context": SolutionIntentReviewContext,
        "return": GovernanceResult,
    }
    assert not inspect.iscoroutinefunction(DeterministicDemoExtractor.extract)


def test_extraction_does_not_return_a_coroutine(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
) -> None:
    result = DeterministicDemoExtractor().extract(*sample_inputs)

    assert isinstance(result, GovernanceResult)
    assert not inspect.isawaitable(result)


def test_default_sample_directory_produces_expected_result(
    extracted_result: GovernanceResult,
) -> None:
    expected = GovernanceResult.model_validate_json(
        EXPECTED_RESULT_PATH.read_text(encoding="utf-8")
    )

    assert extracted_result == expected


def test_default_sample_directory_is_independent_of_working_directory(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = DeterministicDemoExtractor().extract(*sample_inputs)

    assert result.review_outcome is ReviewOutcome.CHANGES_REQUESTED


def test_returned_context_matches_metadata(extracted_result: GovernanceResult) -> None:
    expected_context = SolutionIntentReviewContext.model_validate_json(
        METADATA_PATH.read_text(encoding="utf-8")
    )

    assert extracted_result.context == expected_context


def test_successful_extraction_preserves_scenario(extracted_result: GovernanceResult) -> None:
    assert extracted_result.review_outcome is ReviewOutcome.CHANGES_REQUESTED
    assert len(extracted_result.decisions) == 1
    assert len(extracted_result.findings) == 3
    assert len(extracted_result.risks) == 1
    assert len(extracted_result.action_items) == 2
    assert len(extracted_result.open_questions) == 1


@pytest.mark.parametrize(
    ("prefix", "suffix"),
    [
        ("\n", ""),
        ("", "\n"),
        ("\n", "\n"),
    ],
)
def test_solution_intent_outer_whitespace_is_accepted(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
    prefix: str,
    suffix: str,
) -> None:
    solution_intent, transcript, context = sample_inputs

    result = DeterministicDemoExtractor().extract(
        f"{prefix}{solution_intent}{suffix}", transcript, context
    )

    assert result.review_outcome is ReviewOutcome.CHANGES_REQUESTED


@pytest.mark.parametrize(
    ("prefix", "suffix"),
    [
        ("\n", ""),
        ("", "\n"),
        ("\n", "\n"),
    ],
)
def test_transcript_outer_whitespace_is_accepted(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
    prefix: str,
    suffix: str,
) -> None:
    solution_intent, transcript, context = sample_inputs

    result = DeterministicDemoExtractor().extract(
        solution_intent, f"{prefix}{transcript}{suffix}", context
    )

    assert result.review_outcome is ReviewOutcome.CHANGES_REQUESTED


@pytest.mark.parametrize("line_ending", ["\r\n", "\r"])
def test_alternate_line_endings_are_accepted(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
    line_ending: str,
) -> None:
    solution_intent, transcript, context = sample_inputs

    result = DeterministicDemoExtractor().extract(
        solution_intent.replace("\n", line_ending),
        transcript.replace("\n", line_ending),
        context,
    )

    assert result.review_outcome is ReviewOutcome.CHANGES_REQUESTED


def test_substantive_solution_intent_change_is_rejected(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
) -> None:
    solution_intent, transcript, context = sample_inputs

    with pytest.raises(ValueError, match="Solution Intent.*does not match"):
        DeterministicDemoExtractor().extract(
            solution_intent.replace(
                "The initial release is planned for August 2026.",
                "The initial release is planned for September 2026.",
            ),
            transcript,
            context,
        )


def test_substantive_transcript_change_is_rejected(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
) -> None:
    solution_intent, transcript, context = sample_inputs

    with pytest.raises(ValueError, match="Review transcript.*does not match"):
        DeterministicDemoExtractor().extract(
            solution_intent,
            transcript.replace("changes requested", "approved"),
            context,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("project_name", "Different Project"),
        ("si_version", "1.3"),
        ("review_round", 3),
    ],
)
def test_changed_context_is_rejected(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
    field: str,
    value: str | int,
) -> None:
    solution_intent, transcript, context = sample_inputs
    changed_context = context.model_copy(update={field: value})

    with pytest.raises(ValueError, match="Review context.*does not match"):
        DeterministicDemoExtractor().extract(solution_intent, transcript, changed_context)


@pytest.mark.parametrize("solution_intent", ["", " ", "\n\t"])
def test_blank_solution_intent_is_rejected(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
    solution_intent: str,
) -> None:
    _, transcript, context = sample_inputs

    with pytest.raises(ValueError, match="Solution Intent input must not be blank"):
        DeterministicDemoExtractor().extract(solution_intent, transcript, context)


@pytest.mark.parametrize("transcript", ["", " ", "\n\t"])
def test_blank_transcript_is_rejected(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
    transcript: str,
) -> None:
    solution_intent, _, context = sample_inputs

    with pytest.raises(ValueError, match="Review transcript input must not be blank"):
        DeterministicDemoExtractor().extract(solution_intent, transcript, context)


def test_successive_results_are_deep_independent_copies(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
) -> None:
    extractor = DeterministicDemoExtractor()
    first = extractor.extract(*sample_inputs)
    second = extractor.extract(*sample_inputs)

    assert first == second
    assert first is not second
    assert first.findings is not second.findings
    assert first.findings[0] is not second.findings[0]
    assert first.findings[0].evidence is not second.findings[0].evidence
    assert first.action_items is not second.action_items
    assert first.action_items[0] is not second.action_items[0]


def test_mutation_does_not_affect_other_or_later_results(
    sample_inputs: tuple[str, str, SolutionIntentReviewContext],
) -> None:
    extractor = DeterministicDemoExtractor()
    first = extractor.extract(*sample_inputs)
    second = extractor.extract(*sample_inputs)

    first.findings[0].severity = FindingSeverity.LOW
    first.action_items[0].title = "Edited title"
    first.decisions.clear()
    later = extractor.extract(*sample_inputs)

    assert second.findings[0].severity is FindingSeverity.HIGH
    assert second.action_items[0].title != "Edited title"
    assert len(second.decisions) == 1
    assert later == second


@pytest.mark.parametrize(
    "filename",
    [
        "solution_intent.md",
        "review_transcript.txt",
        "review_metadata.json",
        "expected_result.json",
    ],
)
def test_missing_fixture_file_is_rejected(
    copied_samples: Path,
    filename: str,
) -> None:
    (copied_samples / filename).unlink()

    with pytest.raises(
        DeterministicFixtureError,
        match=rf"sample file is missing: {filename}",
    ):
        DeterministicDemoExtractor(copied_samples)


@pytest.mark.parametrize(
    "filename",
    [
        "solution_intent.md",
        "review_transcript.txt",
        "review_metadata.json",
        "expected_result.json",
    ],
)
def test_unreadable_utf8_fixture_file_is_rejected(
    copied_samples: Path,
    filename: str,
) -> None:
    (copied_samples / filename).write_bytes(b"\xff")

    with pytest.raises(
        DeterministicFixtureError,
        match=rf"sample file is unreadable: {filename}",
    ):
        DeterministicDemoExtractor(copied_samples)


def test_invalid_metadata_json_is_rejected(copied_samples: Path) -> None:
    (copied_samples / "review_metadata.json").write_text("{", encoding="utf-8")

    with pytest.raises(
        DeterministicFixtureError,
        match="review metadata is not valid JSON",
    ):
        DeterministicDemoExtractor(copied_samples)


def test_invalid_metadata_model_is_rejected(copied_samples: Path) -> None:
    metadata_path = copied_samples / "review_metadata.json"
    metadata = _load_json(metadata_path)
    metadata["review_round"] = 0
    _write_json(metadata_path, metadata)

    with pytest.raises(
        DeterministicFixtureError,
        match="review metadata is invalid",
    ):
        DeterministicDemoExtractor(copied_samples)


def test_invalid_expected_result_json_is_rejected(copied_samples: Path) -> None:
    (copied_samples / "expected_result.json").write_text("{", encoding="utf-8")

    with pytest.raises(
        DeterministicFixtureError,
        match="expected result is not valid JSON",
    ):
        DeterministicDemoExtractor(copied_samples)


def test_invalid_expected_result_model_is_rejected(copied_samples: Path) -> None:
    result_path = copied_samples / "expected_result.json"
    result = _load_json(result_path)
    result["review_outcome"] = "unknown"
    _write_json(result_path, result)

    with pytest.raises(
        DeterministicFixtureError,
        match="expected result is invalid",
    ):
        DeterministicDemoExtractor(copied_samples)


def test_mismatched_fixture_context_is_rejected(copied_samples: Path) -> None:
    result_path = copied_samples / "expected_result.json"
    result = _load_json(result_path)
    context = result["context"]
    assert isinstance(context, dict)
    context["project_name"] = "Different Project"
    _write_json(result_path, result)

    with pytest.raises(
        DeterministicFixtureError,
        match="expected-result context does not match review metadata",
    ):
        DeterministicDemoExtractor(copied_samples)


@pytest.mark.parametrize(
    ("filename", "message"),
    [
        ("solution_intent.md", "Solution Intent fixture is empty"),
        ("review_transcript.txt", "review transcript fixture is empty"),
    ],
)
def test_empty_text_fixture_is_rejected(
    copied_samples: Path,
    filename: str,
    message: str,
) -> None:
    (copied_samples / filename).write_text(" \n\t", encoding="utf-8")

    with pytest.raises(DeterministicFixtureError, match=message):
        DeterministicDemoExtractor(copied_samples)


def test_serialization_matches_expected_fixture(extracted_result: GovernanceResult) -> None:
    serialized = extracted_result.model_dump(mode="json")
    expected = GovernanceResult.model_validate_json(
        EXPECTED_RESULT_PATH.read_text(encoding="utf-8")
    ).model_dump(mode="json")

    assert serialized == expected
    assert serialized["review_outcome"] == "changes_requested"
    context = serialized["context"]
    assert isinstance(context, dict)
    assert context["current_si_status"] == "under_review"
    assert context["review_date"] == "2026-07-18"
    action_items = serialized["action_items"]
    assert isinstance(action_items, list)
    assert action_items[0]["due_date"] == "2026-07-24"
