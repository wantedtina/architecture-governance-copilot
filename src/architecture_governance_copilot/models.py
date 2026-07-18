"""Structured data models for architecture governance analysis."""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ReviewOutcome(StrEnum):
    """Possible outcomes of an architecture governance review."""

    APPROVED = "approved"
    CONDITIONALLY_APPROVED = "conditionally_approved"
    REJECTED = "rejected"
    PENDING = "pending"
    NOT_STATED = "not_stated"


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


class _GovernanceModel(BaseModel):
    """Common strict configuration for governance models."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SourceEvidence(_GovernanceModel):
    """Evidence quoted from or referenced within a meeting transcript."""

    quote: NonEmptyString
    speaker: NonEmptyString | None = None
    timestamp: NonEmptyString | None = None
    reference: NonEmptyString | None = None


class Decision(_GovernanceModel):
    """A confirmed architecture decision supported by transcript evidence."""

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
    """The complete structured result of a governance transcript analysis."""

    review_outcome: ReviewOutcome
    outcome_evidence: list[SourceEvidence] = Field(default_factory=list)
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
