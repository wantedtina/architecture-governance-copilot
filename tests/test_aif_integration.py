"""Tests for the fake AIF analysis and evidence-trust boundary."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from architecture_governance_copilot.integrations.aif import (
    AifAnalysisError,
    AifErrorCategory,
    AifGovernanceExtractor,
    AifGovernanceRequest,
    AifTransport,
    AifTransportFailure,
    FakeAifTransport,
)
from architecture_governance_copilot.models import SolutionIntentReviewContext

SAMPLES = Path(__file__).resolve().parents[1] / "samples"


@pytest.fixture
def source_package() -> tuple[str, str, SolutionIntentReviewContext, dict[str, object]]:
    return (
        (SAMPLES / "internal_fake_solution_intent.md").read_text(encoding="utf-8"),
        (SAMPLES / "internal_fake_review_transcript.txt").read_text(encoding="utf-8"),
        SolutionIntentReviewContext.model_validate_json(
            (SAMPLES / "internal_fake_review_metadata.json").read_text(encoding="utf-8")
        ),
        json.loads((SAMPLES / "internal_fake_aif_result.json").read_text(encoding="utf-8")),
    )


def _extract(
    source_package: tuple[str, str, SolutionIntentReviewContext, dict[str, object]],
    response: object,
) -> tuple[object, FakeAifTransport]:
    solution_intent, transcript, context, _ = source_package
    transport = FakeAifTransport([response])  # type: ignore[list-item]
    extractor = AifGovernanceExtractor(
        transport,
        provider_configuration_identity="fake-aif-config-v3",
    )
    return extractor.extract(solution_intent, transcript, context), transport


def test_nonbundled_fake_response_is_context_checked_and_referenced_locally(
    source_package: tuple[str, str, SolutionIntentReviewContext, dict[str, object]],
) -> None:
    solution_intent, transcript, context, response = source_package

    result, transport = _extract(source_package, response)

    assert len(transport.calls) == 1
    request = transport.calls[0]
    assert request.solution_intent == solution_intent
    assert request.review_transcript == transcript
    assert request.context == context
    assert request.provider_configuration_identity == "fake-aif-config-v3"
    assert request.schema_constraints["title"] == "GovernanceResult"
    assert len(request.solution_intent_source_fingerprint) == 64
    assert len(request.transcript_source_fingerprint) == 64
    evidence = [
        *result.outcome_evidence,
        *result.findings[0].evidence,
        *result.action_items[0].evidence,
        *result.missing_evidence[0].evidence,
    ]
    references = [item.reference for item in evidence]
    assert all(reference and "provider-reference" not in reference for reference in references)
    assert references[0].startswith("transcript-")
    assert references[1].startswith("si-")
    assert references[-1].startswith("si-")


def test_json_string_and_zero_item_response_are_supported(
    source_package: tuple[str, str, SolutionIntentReviewContext, dict[str, object]],
) -> None:
    _, _, context, _ = source_package
    response = {
        "context": context.model_dump(mode="json"),
        "review_outcome": "not_stated",
        "outcome_evidence": [],
        "findings": [],
        "decisions": [],
        "risks": [],
        "action_items": [],
        "open_questions": [],
        "missing_evidence": [],
    }

    result, _ = _extract(source_package, json.dumps(response))

    assert result.review_outcome.value == "not_stated"
    assert result.findings == []


@pytest.mark.parametrize(
    ("mutate", "category"),
    [
        (lambda value: value.update({"unexpected": "field"}), AifErrorCategory.INVALID_RESPONSE),
        (
            lambda value: value["context"].update({"review_round": 2}),
            AifErrorCategory.CONTEXT_MISMATCH,
        ),
        (
            lambda value: value["findings"][0]["evidence"][0].update(
                {"quote": "A provider-only unsupported quote."}
            ),
            AifErrorCategory.INVALID_EVIDENCE,
        ),
    ],
)
def test_invalid_provider_responses_fail_with_safe_categories(
    source_package: tuple[str, str, SolutionIntentReviewContext, dict[str, object]],
    mutate: object,
    category: AifErrorCategory,
) -> None:
    response = copy.deepcopy(source_package[3])
    mutate(response)  # type: ignore[operator]

    with pytest.raises(AifAnalysisError) as captured:
        _extract(source_package, response)

    assert captured.value.category is category
    assert "provider-only" not in str(captured.value)
    assert len(str(captured.value)) < 100


@pytest.mark.parametrize(
    ("failure", "category"),
    [
        (AifTransportFailure(AifErrorCategory.REFUSAL), AifErrorCategory.REFUSAL),
        (TimeoutError("secret timeout body"), AifErrorCategory.TIMEOUT),
        (RuntimeError("secret provider body"), AifErrorCategory.PROVIDER_FAILURE),
    ],
)
def test_transport_failures_do_not_expose_provider_bodies(
    source_package: tuple[str, str, SolutionIntentReviewContext, dict[str, object]],
    failure: Exception,
    category: AifErrorCategory,
) -> None:
    with pytest.raises(AifAnalysisError) as captured:
        _extract(source_package, failure)

    assert captured.value.category is category
    assert "secret" not in str(captured.value)


def test_reference_assignment_reuses_one_span_and_avoids_ambiguous_quotes(
    source_package: tuple[str, str, SolutionIntentReviewContext, dict[str, object]],
) -> None:
    solution_intent, transcript, context, response = source_package
    duplicated = copy.deepcopy(response["findings"][0]["evidence"][0])
    response["missing_evidence"][0]["evidence"] = [duplicated, copy.deepcopy(duplicated)]
    transport = FakeAifTransport([response])
    result = AifGovernanceExtractor(
        transport,
        provider_configuration_identity="fake-aif-config-v3",
    ).extract(solution_intent, transcript, context)

    first, second = result.missing_evidence[0].evidence
    assert first.reference == second.reference
    assert first.reference is not None

    ambiguous_si = "# A\nRepeated quote.\n\n# B\nRepeated quote."
    ambiguous_response = {
        "context": context.model_dump(mode="json"),
        "review_outcome": "not_stated",
        "outcome_evidence": [],
        "findings": [],
        "decisions": [],
        "risks": [],
        "action_items": [],
        "open_questions": [],
        "missing_evidence": [
            {
                "item": "Synthetic ambiguity",
                "evidence": [{"source_type": "solution_intent", "quote": "Repeated quote."}],
            }
        ],
    }
    ambiguous_result = AifGovernanceExtractor(
        FakeAifTransport([ambiguous_response]),
        provider_configuration_identity="fake-aif-config-v3",
    ).extract(ambiguous_si, transcript, context)
    assert ambiguous_result.missing_evidence[0].evidence[0].reference is None


def test_repeated_transcript_quotes_use_locators_for_distinct_references(
    source_package: tuple[str, str, SolutionIntentReviewContext, dict[str, object]],
) -> None:
    solution_intent, _, context, _ = source_package
    transcript = (
        "[09:00] Morgan Lee: Same synthetic statement.\n"
        "[09:05] Casey Wong: Same synthetic statement."
    )
    response = {
        "context": context.model_dump(mode="json"),
        "review_outcome": "not_stated",
        "outcome_evidence": [],
        "findings": [],
        "decisions": [],
        "risks": [],
        "action_items": [],
        "open_questions": [],
        "missing_evidence": [
            {
                "item": "First synthetic item",
                "evidence": [
                    {
                        "source_type": "meeting_transcript",
                        "quote": "Same synthetic statement.",
                        "speaker": "Morgan Lee",
                        "timestamp": "09:00",
                    }
                ],
            },
            {
                "item": "Second synthetic item",
                "evidence": [
                    {
                        "source_type": "meeting_transcript",
                        "quote": "Same synthetic statement.",
                        "speaker": "Casey Wong",
                        "timestamp": "09:05",
                    }
                ],
            },
        ],
    }
    result = AifGovernanceExtractor(
        FakeAifTransport([response]),
        provider_configuration_identity="fake-aif-config-v3",
    ).extract(solution_intent, transcript, context)

    references = [item.evidence[0].reference for item in result.missing_evidence]
    assert all(reference and reference.startswith("transcript-") for reference in references)
    assert references[0] != references[1]


def test_boundary_protocol_and_models_are_strict() -> None:
    assert isinstance(FakeAifTransport([{}]), AifTransport)
    with pytest.raises(ValidationError, match="extra_forbidden"):
        AifGovernanceRequest.model_validate(
            {
                "solution_intent": "SI",
                "review_transcript": "Transcript",
                "context": {
                    "project_name": "Synthetic",
                    "si_title": "Synthetic SI",
                    "si_version": "1",
                    "current_si_status": "under_review",
                    "review_round": 1,
                },
                "schema_constraints": {},
                "provider_configuration_identity": "fake",
                "solution_intent_source_fingerprint": "si-hash",
                "transcript_source_fingerprint": "transcript-hash",
                "unexpected": "not accepted",
            }
        )
