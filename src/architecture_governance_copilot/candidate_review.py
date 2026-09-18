"""Explicit human completion of source-bound finding/action candidates."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from architecture_governance_copilot.models import (
    ActionItem,
    ActionPriority,
    DemoReviewedGovernanceResult,
    EvidenceSource,
    FindingSeverity,
    FindingStatus,
    GovernanceResult,
    ReviewExtractionScope,
    ReviewFinding,
    ReviewOutcome,
    SourceEvidence,
)
from architecture_governance_copilot.review_candidates import (
    CandidateKind,
    ReviewCandidateAnalysis,
    validate_candidate_analysis_binding,
)
from architecture_governance_copilot.review_sources import build_review_source_index


class CandidateReviewItemDraft(BaseModel):
    """Editable fields; absence stays absent until human confirmation."""

    model_config = ConfigDict(extra="forbid")
    candidate_id: str
    kind: CandidateKind
    included: bool = True
    title: str = ""
    description: str = ""
    severity: FindingSeverity | None = None
    status: FindingStatus | None = None
    priority: ActionPriority | None = None
    owner: str = ""
    due_date: str = ""
    category: str = ""
    recommended_change: str = ""


class CandidateReviewDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[CandidateReviewItemDraft]
    review_outcome: ReviewOutcome | None = None
    outcome_evidence_source_ids: list[str] = Field(default_factory=list)


@dataclass(frozen=True, slots=True)
class CompletedCandidateReview:
    result: GovernanceResult
    action_original_indices: tuple[int, ...]
    action_candidate_ids: tuple[str, ...]


def create_candidate_review_draft(analysis: ReviewCandidateAnalysis) -> CandidateReviewDraft:
    return CandidateReviewDraft(
        items=[
            CandidateReviewItemDraft(
                candidate_id=item.candidate_id,
                kind=item.kind,
                description=item.text if item.kind == "finding" else "",
                title=item.text if item.kind == "action" else "",
            )
            for item in analysis.items
        ]
    )


def _optional(value: str) -> str | None:
    return value.strip() or None


def _due_date(value: str) -> date | None:
    if not value.strip():
        return None
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value.strip()):
            raise ValueError("Invalid date shape")
        return date.fromisoformat(value.strip())
    except ValueError as error:
        raise ValueError("Due date must be a valid ISO date (YYYY-MM-DD)") from error


def complete_candidate_review(
    analysis: ReviewCandidateAnalysis,
    draft: CandidateReviewDraft,
    *,
    allow_reviewer_selected_outcome: bool,
) -> CompletedCandidateReview:
    """Build a domain result only after deliberate, valid human completion."""
    # Imported here to keep the provider-neutral contract free of provider import cycles.
    from architecture_governance_copilot.evidence_validation import validate_governance_evidence

    validate_candidate_analysis_binding(
        analysis, analysis.solution_intent, analysis.review_transcript, analysis.context
    )
    # Drafts are intentionally editable; validate again after any direct field assignment.
    draft = CandidateReviewDraft.model_validate(draft.model_dump(warnings=False))
    original = {item.candidate_id: item for item in analysis.items}
    submitted_ids = [item.candidate_id for item in draft.items]
    if len(submitted_ids) != len(set(submitted_ids)) or set(submitted_ids) != set(original):
        raise ValueError("The review draft must retain exactly the analyzed candidate identities")
    if draft.review_outcome is None:
        raise ValueError("Select the review outcome explicitly")
    findings = []
    actions = []
    action_indices = []
    action_ids = []
    # Draft order may change visually; identities always refer to original mixed candidates.
    for item in draft.items:
        if not item.included:
            continue
        candidate = original[item.candidate_id]
        evidence = [
            SourceEvidence.model_validate(value.model_dump()) for value in candidate.evidence
        ]
        if item.kind == "finding":
            if item.severity is None or item.status is None:
                raise ValueError("Select severity and status explicitly for every included finding")
            findings.append(
                ReviewFinding(
                    title=item.title,
                    description=item.description,
                    severity=item.severity,
                    status=item.status,
                    owner=_optional(item.owner),
                    due_date=_due_date(item.due_date),
                    category=_optional(item.category),
                    recommended_change=_optional(item.recommended_change),
                    si_section=_unique_si_section(evidence),
                    evidence=evidence,
                )
            )
        else:
            if item.priority is None:
                raise ValueError("Select priority explicitly for every included action")
            actions.append(
                ActionItem(
                    title=item.title,
                    priority=item.priority,
                    owner=_optional(item.owner),
                    due_date=_due_date(item.due_date),
                    evidence=evidence,
                )
            )
            action_indices.append(candidate.original_index)
            action_ids.append(candidate.candidate_id)
    source_index = build_review_source_index(analysis.solution_intent, analysis.review_transcript)
    outcome_evidence = (
        list(source_index.resolve(draft.outcome_evidence_source_ids))
        if draft.outcome_evidence_source_ids
        else []
    )
    values = {
        "context": analysis.context.model_dump(),
        "review_outcome": draft.review_outcome,
        "outcome_evidence": outcome_evidence,
        "findings": findings,
        "action_items": actions,
        "extraction_scope": ReviewExtractionScope(
            analysis_fingerprint=hashlib.sha256(
                json.dumps(analysis.model_dump(mode="json"), sort_keys=True).encode("utf-8")
            ).hexdigest()
        ),
    }
    if allow_reviewer_selected_outcome:
        result = DemoReviewedGovernanceResult(**values, outcome_origin="reviewer_selected")
    else:
        result = GovernanceResult(**values)
    validate_governance_evidence(result, analysis.solution_intent, analysis.review_transcript)
    return CompletedCandidateReview(result, tuple(action_indices), tuple(action_ids))


def _unique_si_section(evidence: list[SourceEvidence]) -> str | None:
    """Retain an unambiguous source locator without inventing a finding classification."""
    sections = {
        item.section
        for item in evidence
        if item.source_type is EvidenceSource.SOLUTION_INTENT and item.section is not None
    }
    return next(iter(sections)) if len(sections) == 1 else None
