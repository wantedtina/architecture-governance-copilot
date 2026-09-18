"""One-call AIF candidate extraction, safe failures, and original-source binding."""

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from architecture_governance_copilot.candidate_review import (
    CandidateReviewDraft,
    CandidateReviewItemDraft,
    complete_candidate_review,
    create_candidate_review_draft,
)
from architecture_governance_copilot.governance_service import GovernanceReviewService
from architecture_governance_copilot.integrations.aif import (
    AifAnalysisError,
    AifErrorCategory,
    AifGovernanceExtractor,
    AifGovernanceRequest,
    AifTransport,
    AifTransportFailure,
    FakeAifTransport,
)
from architecture_governance_copilot.integrations.aif_candidate_protocol import (
    CANDIDATE_TOOL_NAME,
    build_candidate_request_body,
    decode_candidate_tool_response,
)
from architecture_governance_copilot.models import NOT_EXTRACTED_NOTICE, SolutionIntentReviewContext
from architecture_governance_copilot.review_candidates import candidate_json_schema
from architecture_governance_copilot.review_sources import build_review_source_index

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def source_package():
    samples = ROOT / "samples"
    return (
        (samples / "internal_fake_solution_intent.md").read_text(),
        (samples / "internal_fake_review_transcript.txt").read_text(),
        SolutionIntentReviewContext.model_validate_json(
            (samples / "internal_fake_review_metadata.json").read_text()
        ),
        json.loads((samples / "internal_fake_review_candidates.json").read_text()),
    )


def extractor(response):
    transport = FakeAifTransport([response])
    return AifGovernanceExtractor(
        transport, provider_configuration_identity="fake-candidates"
    ), transport


def test_one_call_preserves_full_inputs_context_schema_and_resolves_original_ids(source_package):
    si, transcript, context, payload = source_package
    provider, transport = extractor(payload)
    result = provider.extract(si, transcript, context)
    assert len(transport.calls) == 1
    request = transport.calls[0]
    assert (request.solution_intent, request.review_transcript) == (si, transcript)
    assert request.context.model_dump() == context.model_dump()
    assert request.context is not context
    assert request.schema_constraints == candidate_json_schema()
    assert (
        len(request.solution_intent_source_fingerprint)
        == len(request.transcript_source_fingerprint)
        == 64
    )
    assert len(result.items) == 5
    assert result.context.model_dump() == context.model_dump() and result.context is not context
    index = build_review_source_index(si, transcript)
    for item in result.items:
        assert [e.model_dump() for e in item.evidence] == [
            e.model_dump() for e in index.resolve(item.evidence_source_ids)
        ]
    assert not hasattr(result, "review_outcome")


def test_minimal_candidate_fixture_remains_supported():
    base = ROOT / "tests/fixtures"
    si = (base / "internal_fake_minimal_solution_intent.md").read_text()
    transcript = (base / "internal_fake_minimal_review_transcript.txt").read_text()
    context = SolutionIntentReviewContext.model_validate_json(
        (base / "internal_fake_minimal_review_metadata.json").read_text()
    )
    provider, transport = extractor(
        (base / "internal_fake_minimal_review_candidates.json").read_text()
    )
    result = provider.extract(si, transcript, context)
    assert [i.kind for i in result.items] == ["finding", "action"]
    assert len(transport.calls) == 1


@pytest.mark.parametrize("response", [{"items": []}, '{"items": []}'])
def test_empty_and_single_json_serialization_are_valid(source_package, response):
    provider, transport = extractor(response)
    result = provider.extract(*source_package[:3])
    assert not result.items
    assert len(transport.calls) == 1


@pytest.mark.parametrize(
    "mutation,category",
    [
        (lambda p: p.update(unexpected="secret"), AifErrorCategory.INVALID_RESPONSE),
        (lambda p: p.update(context={}), AifErrorCategory.INVALID_RESPONSE),
        (lambda p: p["items"][0].update(severity="high"), AifErrorCategory.INVALID_RESPONSE),
        (lambda p: p["items"][0].update(kind="risk"), AifErrorCategory.INVALID_RESPONSE),
        (
            lambda p: p["items"][0].update(evidence_source_ids=["unknown-secret-id"]),
            AifErrorCategory.INVALID_EVIDENCE,
        ),
        (lambda p: p["items"].append({"kind": "action"}), AifErrorCategory.INVALID_RESPONSE),
    ],
)
def test_whole_response_rejects_atomically_after_one_call(source_package, mutation, category):
    payload = copy.deepcopy(source_package[3])
    mutation(payload)
    provider, transport = extractor(payload)
    with pytest.raises(AifAnalysisError) as error:
        provider.extract(*source_package[:3])
    assert error.value.category == category
    assert "secret" not in str(error.value)
    assert len(transport.calls) == 1


@pytest.mark.parametrize("payload", ["{", '"{\\"items\\":[]}"', {"items": "[]"}, [], None])
def test_malformed_and_nested_payloads_are_never_repaired(source_package, payload):
    provider, transport = extractor(payload)
    with pytest.raises(AifAnalysisError) as error:
        provider.extract(*source_package[:3])
    assert error.value.category == AifErrorCategory.INVALID_RESPONSE
    assert len(transport.calls) == 1


@pytest.mark.parametrize(
    "failure,category",
    [
        (AifTransportFailure(AifErrorCategory.REFUSAL), AifErrorCategory.REFUSAL),
        (TimeoutError("secret"), AifErrorCategory.TIMEOUT),
        (RuntimeError("secret"), AifErrorCategory.PROVIDER_FAILURE),
    ],
)
def test_failures_are_safe_without_retry(source_package, failure, category):
    provider, transport = extractor(failure)
    with pytest.raises(AifAnalysisError) as error:
        provider.extract(*source_package[:3])
    assert error.value.category == category
    assert "secret" not in str(error.value)
    assert len(transport.calls) == 1


def test_repeated_text_has_distinct_position_ids(source_package):
    si, _, context, _ = source_package
    transcript = "[09:00] Morgan: Same statement.\n[09:05] Casey: Same statement."
    entries = [
        e
        for e in build_review_source_index(si, transcript).entries
        if e.source_id.startswith("transcript-")
    ]
    payload = {
        "items": [
            {"kind": "finding", "text": "Same statement.", "evidence_source_ids": [e.source_id]}
            for e in entries
        ]
    }
    provider, _ = extractor(payload)
    result = provider.extract(si, transcript, context)
    assert result.items[0].evidence[0].reference != result.items[1].evidence[0].reference
    assert [i.evidence[0].speaker for i in result.items] == ["Morgan", "Casey"]


def test_legacy_full_domain_is_rejected(source_package):
    provider, _ = extractor((ROOT / "samples/internal_fake_aif_result.json").read_text())
    with pytest.raises(AifAnalysisError):
        provider.extract(*source_package[:3])


def test_invalid_local_request_makes_no_call(source_package):
    provider, transport = extractor(source_package[3])
    with pytest.raises(ValidationError):
        provider.extract(" ", *source_package[1:3])
    assert transport.calls == []
    assert isinstance(transport, AifTransport)
    with pytest.raises(ValidationError, match="extra_forbidden"):
        request = AifGovernanceRequest(
            solution_intent="SI",
            review_transcript="Transcript",
            context=source_package[2],
            schema_constraints={},
            provider_configuration_identity="fake",
            solution_intent_source_fingerprint="si",
            transcript_source_fingerprint="tr",
            unexpected=True,
        )
        assert request


def _synthetic_tool_envelope(payload):
    """Constructed test data, never a replay of the user photographs."""
    return {
        "choices": [
            {
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "type": "function",
                            "function": {
                                "name": CANDIDATE_TOOL_NAME,
                                "arguments": json.dumps(payload),
                            },
                        }
                    ],
                },
            }
        ],
        "custom_outputs": {},
    }


@pytest.mark.parametrize("failure", [None, "refusal", "truncation", "multiple_outputs"])
def test_pure_protocol_adapter_seam_matches_extractor_request_without_http(source_package, failure):
    si, transcript, context, payload = source_package
    built_bodies = []

    def respond(request):
        body = build_candidate_request_body(
            model="synthetic-configured-model",
            solution_intent=request.solution_intent,
            review_transcript=request.review_transcript,
            context=request.context,
        )
        built_bodies.append(body)
        assert body["tools"][0]["function"]["parameters"] == request.schema_constraints
        response = _synthetic_tool_envelope(payload)
        if failure == "refusal":
            response["choices"][0]["message"]["refusal"] = "synthetic refusal"
        elif failure == "truncation":
            response["choices"][0]["finish_reason"] = "length"
        elif failure == "multiple_outputs":
            response["choices"].append(copy.deepcopy(response["choices"][0]))
        return decode_candidate_tool_response(response)

    transport = FakeAifTransport([payload], response_factory=respond)
    provider = AifGovernanceExtractor(transport, provider_configuration_identity="codec-seam")
    if failure:
        with pytest.raises(AifAnalysisError) as error:
            provider.extract(si, transcript, context)
        expected = (
            AifErrorCategory.REFUSAL if failure == "refusal" else AifErrorCategory.INVALID_RESPONSE
        )
        assert error.value.category == expected
    else:
        result = provider.extract(si, transcript, context)
        assert len(result.items) == len(payload["items"])
    assert len(transport.calls) == len(built_bodies) == 1
    request = transport.calls[0]
    index = build_review_source_index(si, transcript)
    assert request.solution_intent_source_fingerprint == index.si_content_fingerprint
    assert request.transcript_source_fingerprint == index.transcript_content_fingerprint
    assert request.source_index_version == index.version
    rendered_sources = built_bodies[0]["messages"][1]["content"]
    for entry in index.entries:
        assert rendered_sources.count(f"[{entry.source_id}]") == 1
        assert f"[{entry.source_id}] {entry.text}" in rendered_sources


def test_analysis_uses_the_immutable_pre_call_context_snapshot(source_package):
    si, transcript, context, payload = source_package
    expected_context = context.model_dump()

    def respond(request):
        with pytest.raises(ValidationError, match="frozen"):
            request.context.review_round = 100
        context.review_round = 101
        return payload

    transport = FakeAifTransport([payload], response_factory=respond)
    provider = AifGovernanceExtractor(transport, provider_configuration_identity="context-test")
    result = provider.extract(si, transcript, context)
    assert result.context.model_dump() == expected_context
    assert len(transport.calls) == 1


def test_valid_but_misclassified_synthetic_response_reaches_human_correction(source_package):
    si, transcript, context, _ = source_package
    payload = json.loads(
        (ROOT / "tests/fixtures/synthetic_misclassified_candidates.json").read_text()
    )
    provider, transport = extractor(payload)
    service = GovernanceReviewService(provider)
    analysis = service.analyze_review(si, transcript, context)
    assert [item.kind for item in analysis.items].count("finding") == 5
    assert [item.kind for item in analysis.items].count("action") == 2
    assert "missing evidence" in analysis.review_transcript.lower()
    original_ids = [item.candidate_id for item in analysis.items]
    draft = create_candidate_review_draft(analysis)
    with pytest.raises(ValueError, match="outcome"):
        complete_candidate_review(analysis, draft, allow_reviewer_selected_outcome=True)
    overlay = json.loads((ROOT / "tests/fixtures/internal_fake_human_completion.json").read_text())
    for human in overlay["items"]:
        position = human["original_index"]
        values = draft.items[position].model_dump()
        values.update(
            {
                key: value
                for key, value in human.items()
                if key in CandidateReviewItemDraft.model_fields
            }
        )
        draft.items[position] = CandidateReviewItemDraft.model_validate(values)
    draft.items[5].included = False
    draft.items[6].included = False
    draft = CandidateReviewDraft.model_validate(
        {
            **draft.model_dump(),
            "review_outcome": overlay["review_outcome"],
        }
    )
    completed = complete_candidate_review(analysis, draft, allow_reviewer_selected_outcome=True)
    assert len(completed.result.findings) == 3
    assert len(completed.result.action_items) == 2
    assert completed.action_original_indices == (3, 4)
    assert completed.action_candidate_ids == tuple(original_ids[3:5])
    assert [item.candidate_id for item in analysis.items] == original_ids
    outputs = service.generate_outputs(completed.result)
    assert outputs.review_minutes.count(NOT_EXTRACTED_NOTICE) == 4
    assert len(outputs.ado_work_items) == 2
    assert len(transport.calls) == 1
