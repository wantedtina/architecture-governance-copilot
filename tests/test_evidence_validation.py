"""Tests for provider-neutral governance evidence validation."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import get_type_hints

import pytest

from architecture_governance_copilot.evidence_validation import (
    EvidenceValidatingExtractor,
    EvidenceValidationError,
    validate_governance_evidence,
)
from architecture_governance_copilot.extractors import GovernanceExtractor
from architecture_governance_copilot.models import (
    EvidenceSource,
    GovernanceResult,
    MissingEvidence,
    ReviewOutcome,
    SolutionIntentReviewContext,
    SourceEvidence,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = REPOSITORY_ROOT / "samples"


class RecordingExtractor:
    """Return one configured result and record exact extraction arguments."""

    def __init__(self, result: GovernanceResult) -> None:
        self.result = result
        self.calls: list[tuple[str, str, SolutionIntentReviewContext]] = []

    def extract(
        self,
        solution_intent: str,
        review_transcript: str,
        context: SolutionIntentReviewContext,
    ) -> GovernanceResult:
        self.calls.append((solution_intent, review_transcript, context))
        return self.result


@pytest.fixture
def solution_intent() -> str:
    return (SAMPLES_DIR / "solution_intent.md").read_text(encoding="utf-8")


@pytest.fixture
def transcript() -> str:
    return (SAMPLES_DIR / "review_transcript.txt").read_text(encoding="utf-8")


@pytest.fixture
def context() -> SolutionIntentReviewContext:
    return SolutionIntentReviewContext.model_validate_json(
        (SAMPLES_DIR / "review_metadata.json").read_text(encoding="utf-8")
    )


@pytest.fixture
def result() -> GovernanceResult:
    return GovernanceResult.model_validate_json(
        (SAMPLES_DIR / "expected_result.json").read_text(encoding="utf-8")
    )


def _first_si_evidence(result: GovernanceResult) -> SourceEvidence:
    return next(
        evidence
        for finding in result.findings
        for evidence in finding.evidence
        if evidence.source_type is EvidenceSource.SOLUTION_INTENT
    )


def _first_transcript_evidence(result: GovernanceResult) -> SourceEvidence:
    return result.outcome_evidence[0]


def test_validating_extractor_preserves_protocol_signature_and_delegation(
    result: GovernanceResult,
    solution_intent: str,
    transcript: str,
    context: SolutionIntentReviewContext,
) -> None:
    delegate = RecordingExtractor(result)
    extractor = EvidenceValidatingExtractor(delegate)

    returned = extractor.extract(solution_intent, transcript, context)

    assert isinstance(extractor, GovernanceExtractor)
    assert returned is result
    assert delegate.calls == [(solution_intent, transcript, context)]
    assert list(inspect.signature(EvidenceValidatingExtractor.extract).parameters) == [
        "self",
        "solution_intent",
        "review_transcript",
        "context",
    ]
    assert get_type_hints(EvidenceValidatingExtractor.extract) == {
        "solution_intent": str,
        "review_transcript": str,
        "context": SolutionIntentReviewContext,
        "return": GovernanceResult,
    }


def test_complete_bundled_result_and_reused_references_are_valid(
    result: GovernanceResult,
    solution_intent: str,
    transcript: str,
) -> None:
    validate_governance_evidence(result, solution_intent, transcript)


@pytest.mark.parametrize("source_type", list(EvidenceSource))
def test_quote_must_exist_in_declared_source(
    source_type: EvidenceSource,
    result: GovernanceResult,
    solution_intent: str,
    transcript: str,
) -> None:
    evidence = (
        _first_si_evidence(result)
        if source_type is EvidenceSource.SOLUTION_INTENT
        else _first_transcript_evidence(result)
    )
    evidence.quote = "This quote does not exist in the analyzed source."

    with pytest.raises(EvidenceValidationError, match="quote was not found"):
        validate_governance_evidence(result, solution_intent, transcript)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("section", "Security", "does not occur in section"),
        ("speaker", "Jordan Lee", "cannot use speaker or timestamp"),
        ("timestamp", "10:11", "cannot use speaker or timestamp"),
    ],
)
def test_solution_intent_locators_must_match_the_quote_span(
    field: str,
    value: str,
    message: str,
    result: GovernanceResult,
    solution_intent: str,
    transcript: str,
) -> None:
    evidence = _first_si_evidence(result)
    setattr(evidence, field, value)

    with pytest.raises(EvidenceValidationError, match=message):
        validate_governance_evidence(result, solution_intent, transcript)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("speaker", "Alex Chen", "speaker locator"),
        ("timestamp", "10:27", "timestamp locator"),
        ("section", "Data Design", "cannot use a section locator"),
    ],
)
def test_transcript_locators_must_match_the_quote_span(
    field: str,
    value: str,
    message: str,
    result: GovernanceResult,
    solution_intent: str,
    transcript: str,
) -> None:
    evidence = _first_transcript_evidence(result)
    setattr(evidence, field, value)

    with pytest.raises(EvidenceValidationError, match=message):
        validate_governance_evidence(result, solution_intent, transcript)


def test_parsable_si_reference_must_resolve_to_numbered_section(
    result: GovernanceResult,
    solution_intent: str,
    transcript: str,
) -> None:
    _first_si_evidence(result).reference = "SI-8-FAILOVER"

    with pytest.raises(EvidenceValidationError, match="does not resolve to the quote span"):
        validate_governance_evidence(result, solution_intent, transcript)


def test_si_section_and_reference_must_resolve_to_the_same_repeated_quote_span(
    context: SolutionIntentReviewContext,
) -> None:
    result = GovernanceResult(
        context=context,
        review_outcome=ReviewOutcome.NOT_STATED,
        missing_evidence=[
            MissingEvidence(
                item="Synthetic repeated SI reference",
                evidence=[
                    SourceEvidence(
                        source_type=EvidenceSource.SOLUTION_INTENT,
                        quote="Repeated statement.",
                        section="First Section",
                        reference="SI-2-REPEATED",
                    )
                ],
            )
        ],
    )
    solution_intent = "\n".join(
        (
            "## 1. First Section",
            "Repeated statement.",
            "## 2. Second Section",
            "Repeated statement.",
        )
    )

    with pytest.raises(EvidenceValidationError, match="does not resolve to the quote span"):
        validate_governance_evidence(result, solution_intent, "")


def test_parsable_transcript_reference_must_resolve_to_physical_line(
    result: GovernanceResult,
    solution_intent: str,
    transcript: str,
) -> None:
    _first_transcript_evidence(result).reference = "transcript-line-28"

    with pytest.raises(EvidenceValidationError, match="does not resolve to the quote span"):
        validate_governance_evidence(result, solution_intent, transcript)


def test_same_reference_cannot_describe_conflicting_evidence(
    result: GovernanceResult,
    solution_intent: str,
    transcript: str,
) -> None:
    result.outcome_evidence[0].reference = "shared-reference"
    result.decisions[0].evidence[0].reference = "shared-reference"

    with pytest.raises(EvidenceValidationError, match="conflicts with earlier evidence"):
        validate_governance_evidence(result, solution_intent, transcript)


def test_optional_locators_are_not_invented_or_required(
    result: GovernanceResult,
    solution_intent: str,
    transcript: str,
) -> None:
    si_evidence = _first_si_evidence(result)
    si_evidence.section = None
    si_evidence.reference = None
    transcript_evidence = _first_transcript_evidence(result)
    transcript_evidence.speaker = None
    transcript_evidence.timestamp = None
    transcript_evidence.reference = None

    validate_governance_evidence(result, solution_intent, transcript)


def test_repeated_quote_without_locator_is_allowed(
    context: SolutionIntentReviewContext,
) -> None:
    result = GovernanceResult(
        context=context,
        review_outcome=ReviewOutcome.NOT_STATED,
        missing_evidence=[
            MissingEvidence(
                item="Synthetic repeated statement",
                evidence=[
                    SourceEvidence(
                        source_type=EvidenceSource.SOLUTION_INTENT,
                        quote="Repeated statement.",
                    )
                ],
            )
        ],
    )

    validate_governance_evidence(
        result,
        "# Synthetic\n\nRepeated statement.\n\nRepeated statement.",
        "",
    )


def test_missing_information_may_have_no_evidence(
    context: SolutionIntentReviewContext,
) -> None:
    result = GovernanceResult(
        context=context,
        review_outcome=ReviewOutcome.NOT_STATED,
        missing_evidence=[MissingEvidence(item="Evidence still required")],
    )

    validate_governance_evidence(result, "", "")


def test_opaque_optional_reference_is_allowed_when_quote_resolves(
    context: SolutionIntentReviewContext,
) -> None:
    result = GovernanceResult(
        context=context,
        review_outcome=ReviewOutcome.NOT_STATED,
        missing_evidence=[
            MissingEvidence(
                item="Synthetic reference",
                evidence=[
                    SourceEvidence(
                        source_type=EvidenceSource.SOLUTION_INTENT,
                        quote="Supported statement.",
                        reference="provider-opaque-reference",
                    )
                ],
            )
        ],
    )

    validate_governance_evidence(result, "Supported statement.", "")


def test_speaker_and_timestamp_must_resolve_to_the_same_repeated_quote_span(
    context: SolutionIntentReviewContext,
) -> None:
    result = GovernanceResult(
        context=context,
        review_outcome=ReviewOutcome.NOT_STATED,
        missing_evidence=[
            MissingEvidence(
                item="Synthetic repeated transcript statement",
                evidence=[
                    SourceEvidence(
                        source_type=EvidenceSource.MEETING_TRANSCRIPT,
                        quote="Repeated statement.",
                        speaker="First Speaker",
                        timestamp="10:01",
                    )
                ],
            )
        ],
    )
    transcript = "\n".join(
        (
            "[10:00] First Speaker: Repeated statement.",
            "[10:01] Second Speaker: Repeated statement.",
        )
    )

    with pytest.raises(EvidenceValidationError, match="do not match the same quote span"):
        validate_governance_evidence(result, "", transcript)


def test_line_reference_and_speaker_must_resolve_to_the_same_quote_span(
    context: SolutionIntentReviewContext,
) -> None:
    result = GovernanceResult(
        context=context,
        review_outcome=ReviewOutcome.NOT_STATED,
        missing_evidence=[
            MissingEvidence(
                item="Synthetic repeated transcript reference",
                evidence=[
                    SourceEvidence(
                        source_type=EvidenceSource.MEETING_TRANSCRIPT,
                        quote="Repeated statement.",
                        speaker="First Speaker",
                        timestamp="10:00",
                        reference="transcript-line-2",
                    )
                ],
            )
        ],
    )
    transcript = "\n".join(
        (
            "[10:00] First Speaker: Repeated statement.",
            "[10:01] Second Speaker: Repeated statement.",
        )
    )

    with pytest.raises(EvidenceValidationError, match="does not resolve to the quote span"):
        validate_governance_evidence(result, "", transcript)


def test_multiline_transcript_reference_resolves_to_quote_start_line(
    context: SolutionIntentReviewContext,
) -> None:
    result = GovernanceResult(
        context=context,
        review_outcome=ReviewOutcome.NOT_STATED,
        missing_evidence=[
            MissingEvidence(
                item="Synthetic multiline evidence",
                evidence=[
                    SourceEvidence(
                        source_type=EvidenceSource.MEETING_TRANSCRIPT,
                        quote="Continuation evidence.",
                        speaker="First Speaker",
                        timestamp="10:00",
                        reference="transcript-line-2",
                    )
                ],
            )
        ],
    )

    validate_governance_evidence(
        result,
        "",
        "[10:00] First Speaker: Opening statement.\nContinuation evidence.",
    )


def test_line_endings_and_outer_whitespace_do_not_break_valid_evidence(
    result: GovernanceResult,
    solution_intent: str,
    transcript: str,
) -> None:
    validate_governance_evidence(
        result,
        f"\r\n{solution_intent.replace(chr(10), chr(13) + chr(10))}\r\n",
        f"\r\n{transcript.replace(chr(10), chr(13) + chr(10))}\r\n",
    )
