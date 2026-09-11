"""Structured data models for architecture governance analysis."""

from __future__ import annotations

import hashlib
from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Sha256Fingerprint = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[0-9a-f]{64}$"),
]


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


class DraftingSourceRole(StrEnum):
    """Roles available in an authorized drafting-source inventory."""

    TEMPLATE = "template"
    REPOSITORY = "repository"
    SUPPORTING_EVIDENCE = "supporting_evidence"


class DraftingRevisionKind(StrEnum):
    """Revision selectors supported by the production-shaped source contract."""

    VERSION = "version"
    BRANCH = "branch"
    TAG = "tag"
    COMMIT = "commit"


class DraftingValidationStatus(StrEnum):
    """Truthful local validation states for bundled drafting resources."""

    VALIDATED = "validated"


class DraftingSourceProvenance(StrEnum):
    """Origins supported by the deterministic drafting inventory."""

    SYNTHETIC_LOCAL_FIXTURE = "synthetic_local_fixture"


class ReviewInputProvenance(StrEnum):
    """Truthful origins supported by the review-input manifest."""

    SYNTHETIC_SAMPLE = "synthetic_sample"
    USER_ENTERED = "user_entered"
    INTERNAL_FAKE = "internal_fake"


class _GovernanceModel(BaseModel):
    """Common strict configuration for governance models."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class _FrozenGovernanceModel(_GovernanceModel):
    """Strict immutable model used for confirmed source identities."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)


class DraftingSourceResource(_FrozenGovernanceModel):
    """One exact resource in the authorized synthetic drafting inventory."""

    resource_id: NonEmptyString
    role: DraftingSourceRole
    display_name: NonEmptyString
    source_reference: NonEmptyString
    revision_kind: DraftingRevisionKind
    revision: NonEmptyString
    content_fingerprint: Sha256Fingerprint
    validation_status: DraftingValidationStatus
    provenance: DraftingSourceProvenance
    authorized: Literal[True]
    content: NonEmptyString

    @model_validator(mode="after")
    def fingerprint_matches_content(self) -> Self:
        """Reject resource metadata that does not identify its exact content."""
        actual = hashlib.sha256(self.content.encode("utf-8")).hexdigest()
        if actual != self.content_fingerprint:
            raise ValueError("Drafting resource fingerprint does not match its content")
        return self


class DraftingSourceInventory(_FrozenGovernanceModel):
    """Authorized local project and its deterministic drafting resources."""

    project_id: NonEmptyString
    project_name: NonEmptyString
    governance_reference: NonEmptyString
    provider_configuration_identity: NonEmptyString
    resources: tuple[DraftingSourceResource, ...]

    def resource_for_role(self, role: DraftingSourceRole) -> DraftingSourceResource:
        """Return the sole resource for a required deterministic role."""
        matches = [resource for resource in self.resources if resource.role is role]
        if len(matches) != 1:
            raise ValueError(f"Drafting inventory requires exactly one {role.value} resource")
        return matches[0]

    @property
    def template(self) -> str:
        return self.resource_for_role(DraftingSourceRole.TEMPLATE).content

    @property
    def source_code_context(self) -> str:
        return self.resource_for_role(DraftingSourceRole.REPOSITORY).content

    @property
    def supporting_documents(self) -> str:
        return self.resource_for_role(DraftingSourceRole.SUPPORTING_EVIDENCE).content

    @model_validator(mode="after")
    def resource_ids_are_unique(self) -> Self:
        """Reject ambiguous inventories before they reach selection controls."""
        resource_ids = [resource.resource_id for resource in self.resources]
        if len(resource_ids) != len(set(resource_ids)):
            raise ValueError("Drafting inventory resource IDs must be unique")
        if not self.resources:
            raise ValueError("Drafting inventory must contain at least one resource")
        self.resource_for_role(DraftingSourceRole.TEMPLATE)
        self.resource_for_role(DraftingSourceRole.REPOSITORY)
        if not any(
            resource.role is DraftingSourceRole.SUPPORTING_EVIDENCE for resource in self.resources
        ):
            raise ValueError("Drafting inventory requires supporting evidence")
        return self


class SelectedDraftingSource(_FrozenGovernanceModel):
    """Content-independent identity retained in a source-package manifest."""

    resource_id: NonEmptyString
    role: DraftingSourceRole
    display_name: NonEmptyString
    source_reference: NonEmptyString
    revision_kind: DraftingRevisionKind
    revision: NonEmptyString
    content_fingerprint: Sha256Fingerprint
    validation_status: DraftingValidationStatus
    provenance: DraftingSourceProvenance
    authorized: Literal[True]


class DraftingSourcePackageManifest(_FrozenGovernanceModel):
    """Exact source package requiring human confirmation before drafting."""

    project_id: NonEmptyString
    project_name: NonEmptyString
    governance_reference: NonEmptyString
    provider_configuration_identity: NonEmptyString
    offline: Literal[True]
    resources: tuple[SelectedDraftingSource, ...] = Field(min_length=3)

    @model_validator(mode="after")
    def require_unambiguous_provider_package(self) -> Self:
        """Require one template, one repository, and supporting evidence."""
        resource_ids = [resource.resource_id for resource in self.resources]
        if len(resource_ids) != len(set(resource_ids)):
            raise ValueError("Selected source resource IDs must be unique")
        role_counts = {
            role: sum(resource.role is role for resource in self.resources)
            for role in DraftingSourceRole
        }
        if role_counts[DraftingSourceRole.TEMPLATE] != 1:
            raise ValueError("Selected source package requires exactly one template")
        if role_counts[DraftingSourceRole.REPOSITORY] != 1:
            raise ValueError("Selected source package requires exactly one repository revision")
        if role_counts[DraftingSourceRole.SUPPORTING_EVIDENCE] < 1:
            raise ValueError("Selected source package requires supporting evidence")
        return self


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


class ReviewInputManifest(_GovernanceModel):
    """Exact confirmed source package eligible for one governance analysis."""

    source_page_id: NonEmptyString
    source_space: NonEmptyString
    source_url: NonEmptyString
    source_version: int = Field(ge=1)
    source_retrieved_at: datetime
    source_canonicalizer_version: NonEmptyString
    source_content_fingerprint: NonEmptyString
    transcript_fingerprint: NonEmptyString
    transcript_provenance: ReviewInputProvenance
    transcript_edited: bool
    metadata_fingerprint: NonEmptyString
    metadata_provenance: ReviewInputProvenance
    metadata_edited: bool
    review_mode: NonEmptyString
    provider_configuration_identity: NonEmptyString

    @field_validator("source_retrieved_at")
    @classmethod
    def require_aware_retrieval_time(cls, value: datetime) -> datetime:
        """Keep source freshness evidence unambiguous across environments."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("source_retrieved_at must include a timezone")
        return value


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
