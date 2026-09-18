"""Human completion and original candidate identity through category correction."""

import pytest
from pydantic import ValidationError

from architecture_governance_copilot.candidate_review import (
    complete_candidate_review,
    create_candidate_review_draft,
)
from architecture_governance_copilot.models import (
    DemoReviewedGovernanceResult,
    GovernanceResult,
    SolutionIntentReviewContext,
)
from architecture_governance_copilot.review_candidates import build_candidate_analysis
from architecture_governance_copilot.review_sources import build_review_source_index


def analysis(kinds=("finding", "action")):
    si = "# SI\nRecovery design"
    transcript = "[09:00] Lee: Recovery issue raised.\n[09:01] Lee: Document retry by 2026-09-21."
    ids = [entry.source_id for entry in build_review_source_index(si, transcript).entries[-2:]]
    return build_candidate_analysis(
        {
            "items": [
                {
                    "kind": kind,
                    "text": f"Candidate {index}",
                    "evidence_source_ids": [ids[index % 2]],
                }
                for index, kind in enumerate(kinds)
            ]
        },
        si,
        transcript,
        SolutionIntentReviewContext(
            project_name="Synthetic",
            si_title="SI",
            si_version="1",
            current_si_status="draft",
            review_round=1,
        ),
        provider_configuration_identity="synthetic-v1",
    )


def complete(analysis, draft, *, allow=True):
    return complete_candidate_review(analysis, draft, allow_reviewer_selected_outcome=allow)


def test_draft_seeds_only_candidate_text_and_requires_all_business_selections() -> None:
    source = analysis()
    draft = create_candidate_review_draft(source)
    assert draft.review_outcome is None
    assert draft.items[0].description == "Candidate 0" and draft.items[0].title == ""
    assert draft.items[1].title == "Candidate 1"
    assert all(item.owner == "" and item.due_date == "" for item in draft.items)
    assert draft.items[0].severity is None and draft.items[0].status is None
    assert draft.items[1].priority is None
    with pytest.raises(ValueError, match="outcome"):
        complete(source, draft)
    draft.review_outcome = "not_stated"
    with pytest.raises(ValueError, match="severity and status"):
        complete(source, draft)
    draft.items[0].severity = "high"
    draft.items[0].status = "open"
    with pytest.raises(ValidationError):
        complete(source, draft)
    draft.items[0].title = "Recovery review"
    with pytest.raises(ValueError, match="priority"):
        complete(source, draft)
    draft.items[1].priority = "medium"
    result = complete(source, draft)
    assert result.action_original_indices == (1,)
    assert result.result.action_items[0].owner is None
    assert result.result.action_items[0].due_date is None
    assert result.result.extraction_scope.analysis_fingerprint


def test_exclusion_reclassification_and_reordering_preserve_original_action_identity() -> None:
    source = analysis(("finding", "action", "finding"))
    draft = create_candidate_review_draft(source)
    draft.review_outcome = "not_stated"
    draft.items[0].included = False
    draft.items[0].due_date = "invalid excluded value"
    draft.items[1].kind = "finding"
    draft.items[1].title = "Corrected finding"
    draft.items[1].description = "Reviewer corrected classification"
    draft.items[1].severity = "low"
    draft.items[1].status = "deferred"
    draft.items[1].priority = "high"
    draft.items[2].kind = "action"
    draft.items[2].title = "Corrected action"
    draft.items[2].priority = "medium"
    draft.items[2].category = "Ignored finding field"
    draft.items.reverse()
    completed = complete(source, draft)
    assert completed.action_original_indices == (2,)
    assert completed.action_candidate_ids == (source.items[2].candidate_id,)
    assert "category" not in completed.result.action_items[0].model_dump()
    assert "priority" not in completed.result.findings[0].model_dump()
    assert [item.model_dump() for item in completed.result.action_items[0].evidence] == [
        item.model_dump() for item in source.items[2].evidence
    ]


def test_mutated_draft_is_revalidated_at_completion_boundary() -> None:
    source = analysis(("action",))
    draft = create_candidate_review_draft(source)
    draft.review_outcome = "not_stated"
    draft.items[0].priority = "high"
    draft.items[0].kind = "risk"
    with pytest.raises(ValidationError):
        complete(source, draft)


def test_empty_or_all_excluded_still_require_explicit_outcome_and_scope() -> None:
    for source in (analysis(()), analysis()):
        draft = create_candidate_review_draft(source)
        for item in draft.items:
            item.included = False
        with pytest.raises(ValueError, match="outcome"):
            complete(source, draft)
        draft.review_outcome = "not_stated"
        result = complete(source, draft).result
        assert not result.findings and not result.action_items
        assert result.extraction_scope.not_extracted_categories == (
            "decisions",
            "risks",
            "open_questions",
            "missing_evidence",
        )


def test_invalid_dates_and_missing_or_duplicate_identities_cannot_complete() -> None:
    source = analysis(("action",))
    draft = create_candidate_review_draft(source)
    draft.review_outcome = "not_stated"
    draft.items[0].priority = "high"
    draft.items[0].due_date = "2026-02-30"
    with pytest.raises(ValueError, match="valid ISO date"):
        complete(source, draft)
    draft.items[0].due_date = ""
    draft.items.append(draft.items[0].model_copy())
    with pytest.raises(ValueError, match="identities"):
        complete(source, draft)
    draft.items = []
    with pytest.raises(ValueError, match="identities"):
        complete(source, draft)


def test_demo_outcome_policy_does_not_expand_standard_domain_allowance() -> None:
    source = analysis(())
    draft = create_candidate_review_draft(source)
    draft.review_outcome = "approved"
    assert isinstance(complete(source, draft).result, DemoReviewedGovernanceResult)
    with pytest.raises(ValidationError, match="outcome_evidence"):
        complete(source, draft, allow=False)
    draft.review_outcome = "not_stated"
    assert type(complete(source, draft, allow=False).result) is GovernanceResult


def test_completion_runs_fresh_original_source_evidence_gate(monkeypatch) -> None:
    source = analysis(())
    draft = create_candidate_review_draft(source)
    draft.review_outcome = "not_stated"
    observed = []

    def validate(result, si, transcript):
        observed.append((result, si, transcript))

    monkeypatch.setattr(
        "architecture_governance_copilot.evidence_validation.validate_governance_evidence", validate
    )
    result = complete(source, draft).result
    assert observed == [(result, source.solution_intent, source.review_transcript)]


@pytest.mark.parametrize("section_count", [1, 2])
def test_finding_section_uses_only_an_unambiguous_cited_source_locator(section_count) -> None:
    si = "## Recovery\nRecovery evidence\n## Operations\nOperations evidence"
    transcript = "Explicit finding"
    index = build_review_source_index(si, transcript)
    ids = [index.entries[1].source_id, index.entries[3].source_id][:section_count]
    source = build_candidate_analysis(
        {"items": [{"kind": "finding", "text": "Issue", "evidence_source_ids": ids}]},
        si,
        transcript,
        analysis().context,
        provider_configuration_identity="section-test",
    )
    draft = create_candidate_review_draft(source)
    draft.review_outcome = "not_stated"
    draft.items[0].title = "Reviewed issue"
    draft.items[0].severity = "high"
    draft.items[0].status = "open"
    completed = complete(source, draft).result
    assert completed.findings[0].si_section == ("Recovery" if section_count == 1 else None)
    assert len(completed.findings[0].evidence) == section_count
