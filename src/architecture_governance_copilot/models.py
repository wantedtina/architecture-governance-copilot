"""Structured data models for architecture governance analysis."""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class EvidenceSource(StrEnum):
    """Sources that can support a structured review item."""

    SOLUTION_INTENT = "solution_intent"
    MEETING_TRANSCRIPT = "meeting_transcript"


class SolutionIntentStatus(StrEnum):
    """Lifecycle status of the Solution Intent under review."""

    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    CHANGES_REQUESTED = "changes_requested"
    CONDITIONALLY_APPROVED = "conditionally_approved"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReviewOutcome(StrEnum):
    """Possible outcomes of the current Solution Intent review round."""

    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    CONDITIONALLY_APPROVED = "conditionally_approved"
    REJECTED = "rejected"
    PENDING = "pending"
    NOT_STATED = "not_stated"


class FindingSeverity(StrEnum):
    """Severity assigned to a Solution Intent review finding."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingStatus(StrEnum):
    """Tracking status of a Solution Intent review finding."""

    OPEN = "open"
    RESOLVED = "resolved"
    DEFERRED = "deferred"
    ACCEPTED = "accepted"


class RiskSeverity(StrEnum):
    """Severity assigned to an identified governance risk."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionPriority(StrEnum):
    """Priority assigned to a governance action."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DraftInputType(StrEnum):
    """Context types used to prepare a Solution Intent draft."""

    TEMPLATE = "template"
    SOURCE_CODE = "source_code"
    SUPPORTING_DOCUMENTS = "supporting_documents"


class _GovernanceModel(BaseModel):
    """Common strict configuration for governance models."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SolutionIntentDraftRequest(_GovernanceModel):
    """Synthetic context supplied to one Solution Intent drafting operation."""

    project_name: NonEmptyString
    template: NonEmptyString
    source_code_context: NonEmptyString
    supporting_documents: NonEmptyString | None = None


class SolutionIntentDraft(_GovernanceModel):
    """A provider-generated Solution Intent draft awaiting human confirmation."""

    project_name: NonEmptyString
    content: NonEmptyString
    provider_name: NonEmptyString
    input_types: list[DraftInputType] = Field(min_length=2)
    assumptions: list[NonEmptyString] = Field(default_factory=list)


class SourceEvidence(_GovernanceModel):
    """Evidence quoted from a Solution Intent or review transcript."""

    source_type: EvidenceSource
    quote: NonEmptyString
    speaker: NonEmptyString | None = None
    timestamp: NonEmptyString | None = None
    section: NonEmptyString | None = None
    reference: NonEmptyString | None = None


class SolutionIntentReviewContext(_GovernanceModel):
    """Metadata identifying one Solution Intent review round."""

    project_name: NonEmptyString
    si_title: NonEmptyString
    si_version: NonEmptyString
    current_si_status: SolutionIntentStatus
    review_round: int = Field(ge=1)
    ado_ticket_id: NonEmptyString | None = None
    domain_architect: NonEmptyString | None = None
    review_date: date | None = None


class ReviewFinding(_GovernanceModel):
    """A source-backed issue identified during Solution Intent review."""

    title: NonEmptyString
    description: NonEmptyString
    category: NonEmptyString | None = None
    si_section: NonEmptyString | None = None
    severity: FindingSeverity
    status: FindingStatus = FindingStatus.OPEN
    recommended_change: NonEmptyString | None = None
    owner: NonEmptyString | None = None
    due_date: date | None = None
    evidence: list[SourceEvidence] = Field(min_length=1)


class Decision(_GovernanceModel):
    """A confirmed architecture decision supported by review evidence."""

    statement: NonEmptyString
    rationale: NonEmptyString | None = None
    evidence: list[SourceEvidence] = Field(min_length=1)


class Risk(_GovernanceModel):
    """An identified architecture or delivery risk."""

    description: NonEmptyString
    severity: RiskSeverity
    owner: NonEmptyString | None = None
    evidence: list[SourceEvidence] = Field(min_length=1)


class ActionItem(_GovernanceModel):
    """Follow-up work agreed during the governance review."""

    title: NonEmptyString
    owner: NonEmptyString | None = None
    due_date: date | None = None
    priority: ActionPriority
    evidence: list[SourceEvidence] = Field(min_length=1)


class OpenQuestion(_GovernanceModel):
    """A governance question that remains unresolved."""

    question: NonEmptyString
    owner: NonEmptyString | None = None
    evidence: list[SourceEvidence] = Field(min_length=1)


class MissingEvidence(_GovernanceModel):
    """A required governance artifact or fact that remains unavailable."""

    item: NonEmptyString
    reason: NonEmptyString | None = None
    evidence: list[SourceEvidence] = Field(default_factory=list)


class GovernanceResult(_GovernanceModel):
    """The structured result of one Solution Intent review round."""

    context: SolutionIntentReviewContext
    review_outcome: ReviewOutcome
    outcome_evidence: list[SourceEvidence] = Field(default_factory=list)
    findings: list[ReviewFinding] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    missing_evidence: list[MissingEvidence] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_stated_outcome_evidence(self) -> Self:
        """Require evidence whenever the meeting states a review outcome."""
        if self.review_outcome is not ReviewOutcome.NOT_STATED and not self.outcome_evidence:
            raise ValueError("outcome_evidence is required when review_outcome is stated")
        return self


class MockAdoWorkItem(_GovernanceModel):
    """A validated preview of a future mock Azure DevOps work item."""

    title: NonEmptyString
    assigned_to: NonEmptyString | None = None
    due_date: date | None = None
    priority: ActionPriority
    description: NonEmptyString
    tags: list[NonEmptyString] = Field(default_factory=list)
    source_action_index: int = Field(ge=0)
    parent_work_item_id: NonEmptyString | None = None
    si_section: NonEmptyString | None = None
    acceptance_criteria: list[NonEmptyString] = Field(default_factory=list)
