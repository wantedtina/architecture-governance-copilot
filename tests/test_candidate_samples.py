"""Active candidate fixtures, explicit human inputs and scope form one synthetic contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from architecture_governance_copilot.ado_generator import generate_mock_ado_work_items
from architecture_governance_copilot.candidate_review import (
    CandidateReviewDraft,
    complete_candidate_review,
    create_candidate_review_draft,
)
from architecture_governance_copilot.evidence_validation import validate_governance_evidence
from architecture_governance_copilot.minutes_generator import generate_review_minutes
from architecture_governance_copilot.models import (
    NOT_EXTRACTED_NOTICE,
    SolutionIntentReviewContext,
)
from architecture_governance_copilot.review_candidates import (
    ReviewCandidateAnalysis,
    build_candidate_analysis,
    parse_candidate_payload,
)
from architecture_governance_copilot.review_sources import build_review_source_index

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
FIXTURES = ROOT / "tests" / "fixtures"


def _package(mode: str, *, candidate_path: Path | None = None) -> ReviewCandidateAnalysis:
    prefix = "internal_fake_" if mode == "internal_fake" else ""
    candidate_path = candidate_path or SAMPLES / (
        "internal_fake_review_candidates.json"
        if mode == "internal_fake"
        else "expected_candidates.json"
    )
    return build_candidate_analysis(
        candidate_path.read_text(encoding="utf-8"),
        (SAMPLES / f"{prefix}solution_intent.md").read_text(encoding="utf-8"),
        (SAMPLES / f"{prefix}review_transcript.txt").read_text(encoding="utf-8"),
        SolutionIntentReviewContext.model_validate_json(
            (SAMPLES / f"{prefix}review_metadata.json").read_text(encoding="utf-8")
        ),
        provider_configuration_identity=(
            "internal-fake-candidates" if mode == "internal_fake" else "offline-candidates-v1"
        ),
    )


def _enter_human_values(mode: str, draft: CandidateReviewDraft) -> CandidateReviewDraft:
    overlay = json.loads((FIXTURES / f"{mode}_human_completion.json").read_text(encoding="utf-8"))
    assert overlay["provenance"] == "Synthetic explicit human inputs; never provider defaults."
    values = draft.model_dump(mode="json")
    values["review_outcome"] = overlay["review_outcome"]
    for completed in overlay["items"]:
        item = values["items"][completed["original_index"]]
        for field, value in completed.items():
            if field in item:
                item[field] = value
    return CandidateReviewDraft.model_validate(values)


@pytest.mark.parametrize("mode", ["offline", "internal_fake"])
def test_active_fixture_has_only_candidates_with_original_source_evidence(mode: str) -> None:
    analysis = _package(mode)
    assert [item.kind for item in analysis.items].count("finding") == 3
    assert [item.kind for item in analysis.items].count("action") == 2
    index = build_review_source_index(analysis.solution_intent, analysis.review_transcript)
    for item in analysis.items:
        assert item.evidence
        assert [value.model_dump() for value in item.evidence] == [
            value.model_dump() for value in index.resolve(item.evidence_source_ids)
        ]
        for evidence in item.evidence:
            original = (
                analysis.solution_intent
                if evidence.source_type == "solution_intent"
                else analysis.review_transcript
            )
            assert evidence.quote in original
            assert evidence.reference in item.evidence_source_ids
    filename = (
        "internal_fake_review_candidates.json"
        if mode == "internal_fake"
        else "expected_candidates.json"
    )
    payload = parse_candidate_payload((SAMPLES / filename).read_text(encoding="utf-8"))
    assert set(payload.model_dump()) == {"items"}
    assert all(
        set(item) == {"kind", "text", "evidence_source_ids"}
        for item in payload.model_dump()["items"]
    )


@pytest.mark.parametrize("mode", ["offline", "internal_fake"])
def test_fixture_business_values_are_only_explicit_human_test_inputs(mode: str) -> None:
    analysis = _package(mode)
    draft = create_candidate_review_draft(analysis)
    assert draft.review_outcome is None
    assert all(item.owner == item.due_date == "" for item in draft.items)
    assert all(item.severity is item.status is item.priority is None for item in draft.items)
    assert all(item.title == "" for item in draft.items if item.kind == "finding")
    with pytest.raises(ValueError, match="outcome"):
        complete_candidate_review(analysis, draft, allow_reviewer_selected_outcome=True)

    completed = complete_candidate_review(
        analysis,
        _enter_human_values(mode, draft),
        allow_reviewer_selected_outcome=True,
    )
    result = completed.result
    assert completed.action_original_indices == (3, 4)
    assert completed.action_candidate_ids == tuple(item.candidate_id for item in analysis.items[3:])
    expected = json.loads(
        (FIXTURES / f"{mode}_reviewed_candidates_result.json").read_text(encoding="utf-8")
    )
    assert result.model_dump(mode="json") == expected
    assert len(result.findings) == 3
    assert len(result.action_items) == 2
    assert not result.decisions and not result.risks
    assert not result.open_questions and not result.missing_evidence
    assert result.extraction_scope is not None
    assert result.extraction_scope.review_outcome_origin == "human_completed"
    assert result.model_dump(mode="json")["extraction_scope"]["automated_categories"] == [
        "finding",
        "action",
    ]
    validate_governance_evidence(result, analysis.solution_intent, analysis.review_transcript)
    minutes = generate_review_minutes(result)
    work_items = generate_mock_ado_work_items(result)
    assert minutes.count(NOT_EXTRACTED_NOTICE) == 4
    for action, work_item in zip(result.action_items, work_items, strict=True):
        assert action.owner and action.owner in minutes
        assert action.due_date and action.due_date.isoformat() in minutes
        assert work_item.assigned_to == action.owner
        assert work_item.due_date == action.due_date
        assert NOT_EXTRACTED_NOTICE in work_item.description


def test_synthetic_category_mistakes_reach_human_review_and_can_be_excluded() -> None:
    analysis = _package(
        "internal_fake", candidate_path=FIXTURES / "synthetic_misclassified_candidates.json"
    )
    assert len(analysis.items) == 7
    assert sum(item.kind == "finding" for item in analysis.items) == 5
    assert "Record both alert thresholds and the support escalation roster as missing evidence" in (
        analysis.review_transcript
    )
    draft = _enter_human_values("internal_fake", create_candidate_review_draft(analysis))
    for item in draft.items[5:]:
        assert item.severity is None and item.status is None
        item.included = False
    completed = complete_candidate_review(analysis, draft, allow_reviewer_selected_outcome=True)
    assert len(completed.result.findings) == 3
    assert len(completed.result.action_items) == 2
    assert completed.action_original_indices == (3, 4)
    assert completed.result.action_items[0].owner == "Riley Chen"
    assert completed.result.action_items[1].owner == "Avery Patel"
    assert len(analysis.items) == 7
