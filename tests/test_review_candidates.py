"""Strict wire values and application-owned analysis identity."""

import json

import pytest
from pydantic import ValidationError

from architecture_governance_copilot.models import SolutionIntentReviewContext
from architecture_governance_copilot.review_candidates import (
    CandidateEvidenceError,
    build_candidate_analysis,
    parse_candidate_payload,
    validate_candidate_analysis_binding,
)
from architecture_governance_copilot.review_sources import build_review_source_index


def context() -> SolutionIntentReviewContext:
    return SolutionIntentReviewContext(
        project_name="Synthetic",
        si_title="SI",
        si_version="1",
        current_si_status="draft",
        review_round=1,
    )


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"items": "[]"},
        {"items": {}},
        {"items": ()},
        {"findings": [], "action_items": []},
        {"items": [], "review_outcome": "approved"},
        {"items": [{"kind": "risk", "text": "x", "evidence_source_ids": ["id"]}]},
        {"items": [{"kind": "finding", "text": " ", "evidence_source_ids": ["id"]}]},
        {"items": [{"kind": "finding", "text": 1, "evidence_source_ids": ["id"]}]},
        {"items": [{"kind": "finding", "text": "x", "evidence_source_ids": []}]},
        {"items": [{"kind": "finding", "text": "x", "evidence_source_ids": [" "]}]},
        {"items": [{"kind": "finding", "text": "x", "evidence_source_ids": [1]}]},
        {"items": [{"kind": "finding", "text": "x", "evidence_source_ids": ["id", "id"]}]},
        {"items": [{"kind": "finding", "text": "x", "evidence_source_ids": '["id"]'}]},
        {
            "items": [
                {"kind": "finding", "text": "x", "evidence_source_ids": ["id"], "owner": "Lee"}
            ]
        },
        json.dumps(json.dumps({"items": []})),
        '{"items": [], "items": []}',
    ],
)
def test_reject_noncontract_shapes_without_coercion(payload: object) -> None:
    with pytest.raises((ValueError, TypeError)):
        parse_candidate_payload(payload)


def test_empty_batch_valid_and_one_invalid_item_rejects_whole_batch() -> None:
    assert parse_candidate_payload('{"items": []}').items == []
    index = build_review_source_index("SI", "Explicit finding")
    valid = {
        "kind": "finding",
        "text": "Issue",
        "evidence_source_ids": [index.entries[-1].source_id],
    }
    with pytest.raises(CandidateEvidenceError):
        build_candidate_analysis(
            {"items": [valid, {**valid, "evidence_source_ids": ["unknown"]}]},
            "SI",
            "Explicit finding",
            context(),
            provider_configuration_identity="synthetic-v1",
        )


def test_analysis_copies_context_and_rejects_source_context_provider_or_evidence_tampering() -> (
    None
):
    supplied_context = context()
    source_id = build_review_source_index("SI", "Explicit finding").entries[-1].source_id
    analysis = build_candidate_analysis(
        {"items": [{"kind": "finding", "text": "Issue", "evidence_source_ids": [source_id]}]},
        "SI",
        "Explicit finding",
        supplied_context,
        provider_configuration_identity="synthetic-v1",
    )
    validate_candidate_analysis_binding(analysis, "SI", "Explicit finding", context())
    supplied_context.si_title = "Changed caller context"
    assert analysis.context.si_title == "SI"
    with pytest.raises(ValidationError):
        analysis.context.si_title = "Changed frozen context"
    with pytest.raises(ValidationError):
        analysis.items[0].evidence[0].quote = "Changed frozen evidence"
    for kwargs in (
        {"solution_intent": "Changed SI"},
        {"review_transcript": "Changed transcript"},
        {"context": supplied_context},
        {"provider_configuration_identity": "changed-provider"},
    ):
        values = {
            "solution_intent": "SI",
            "review_transcript": "Explicit finding",
            "context": context(),
        }
        values.update(kwargs)
        with pytest.raises(CandidateEvidenceError):
            validate_candidate_analysis_binding(analysis, **values)
    tampered_evidence = analysis.items[0].evidence[0].model_copy(update={"quote": "not in source"})
    tampered_item = analysis.items[0].model_copy(update={"evidence": (tampered_evidence,)})
    with pytest.raises(CandidateEvidenceError, match="modified"):
        validate_candidate_analysis_binding(
            analysis.model_copy(update={"items": (tampered_item,)}),
            "SI",
            "Explicit finding",
            context(),
        )
