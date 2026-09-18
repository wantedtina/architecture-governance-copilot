"""The exact two-category provider contract and immutable analyzed candidates."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from architecture_governance_copilot.models import SolutionIntentReviewContext, SourceEvidence
from architecture_governance_copilot.review_sources import (
    SOURCE_INDEX_VERSION,
    build_review_source_index,
    review_source_fingerprint,
)

CANDIDATE_CONTRACT_VERSION = "review-candidates-v1"
CandidateKind = Literal["finding", "action"]
_WireText = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1)]
_SourceId = Annotated[str, StringConstraints(strict=True, min_length=1)]


class CandidateEvidenceError(ValueError):
    """A candidate does not belong to its application-owned source binding."""


class ReviewCandidate(BaseModel):
    """One model proposal: no business completion values or invented locators."""

    model_config = ConfigDict(extra="forbid", strict=True)
    kind: CandidateKind
    text: _WireText
    evidence_source_ids: list[_SourceId] = Field(min_length=1)

    @field_validator("evidence_source_ids")
    @classmethod
    def unique_evidence_ids(cls, value: list[str]) -> list[str]:
        if any(not source_id.strip() for source_id in value):
            raise ValueError("Evidence IDs must be nonblank")
        if len(value) != len(set(value)):
            raise ValueError("Evidence IDs must be unique within an item")
        return value


class ReviewCandidatePayload(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    items: list[ReviewCandidate]


class _FrozenContext(SolutionIntentReviewContext):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)


class _FrozenEvidence(SourceEvidence):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)


class ResolvedReviewCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    candidate_id: str
    original_index: int = Field(ge=0)
    kind: CandidateKind
    text: _WireText
    evidence_source_ids: tuple[str, ...]
    evidence: tuple[_FrozenEvidence, ...]


class ReviewCandidateAnalysis(BaseModel):
    """An immutable proposal snapshot, deliberately not a GovernanceResult."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    context: _FrozenContext
    items: tuple[ResolvedReviewCandidate, ...]
    solution_intent: str
    review_transcript: str
    si_content_fingerprint: str
    transcript_content_fingerprint: str
    provider_configuration_identity: str
    contract_version: Literal["review-candidates-v1"] = CANDIDATE_CONTRACT_VERSION
    source_index_version: Literal["normalized-physical-lines-v1"] = SOURCE_INDEX_VERSION
    analysis_id: str


def candidate_json_schema() -> dict[str, Any]:
    """Small inline provider schema; stricter value checks remain local."""
    return {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string", "enum": ["finding", "action"]},
                        "text": {"type": "string"},
                        "evidence_source_ids": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["kind", "text", "evidence_source_ids"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["items"],
        "additionalProperties": False,
    }


def parse_candidate_payload(
    value: str | Mapping[str, Any] | ReviewCandidatePayload,
) -> ReviewCandidatePayload:
    """Decode at most one JSON serialization and reject legacy/coerced shapes."""
    if isinstance(value, ReviewCandidatePayload):
        value = value.model_dump()
    if isinstance(value, str):
        value = json.loads(value, object_pairs_hook=_unique_object_keys)
    if not isinstance(value, Mapping):
        raise ValueError("Candidate response must be a JSON object")
    return ReviewCandidatePayload.model_validate(dict(value))


def _unique_object_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Candidate JSON must not contain duplicate object keys")
        result[key] = value
    return result


def _analysis_identity(
    context: SolutionIntentReviewContext,
    si_fingerprint: str,
    transcript_fingerprint: str,
    provider_configuration_identity: str,
) -> str:
    binding = {
        "context": context.model_dump(mode="json"),
        "solution_intent": si_fingerprint,
        "review_transcript": transcript_fingerprint,
        "provider": provider_configuration_identity,
        "contract": CANDIDATE_CONTRACT_VERSION,
        "index": SOURCE_INDEX_VERSION,
    }
    return hashlib.sha256(json.dumps(binding, sort_keys=True).encode("utf-8")).hexdigest()


def build_candidate_analysis(
    payload: str | Mapping[str, Any] | ReviewCandidatePayload,
    solution_intent: str,
    review_transcript: str,
    context: SolutionIntentReviewContext,
    *,
    provider_configuration_identity: str,
) -> ReviewCandidateAnalysis:
    parsed = parse_candidate_payload(payload)
    if not provider_configuration_identity.strip():
        raise ValueError("Provider configuration identity must be nonblank")
    source_index = build_review_source_index(solution_intent, review_transcript)
    trusted_context = _FrozenContext.model_validate(context.model_dump())
    identity = _analysis_identity(
        trusted_context,
        source_index.si_content_fingerprint,
        source_index.transcript_content_fingerprint,
        provider_configuration_identity,
    )
    items = []
    for position, candidate in enumerate(parsed.items):
        try:
            evidence = source_index.resolve(candidate.evidence_source_ids)
        except ValueError as error:
            raise CandidateEvidenceError(str(error)) from error
        items.append(
            ResolvedReviewCandidate(
                candidate_id=f"candidate-{identity[:16]}-{position:03d}",
                original_index=position,
                kind=candidate.kind,
                text=candidate.text,
                evidence_source_ids=tuple(candidate.evidence_source_ids),
                evidence=tuple(
                    _FrozenEvidence.model_validate(item.model_dump()) for item in evidence
                ),
            )
        )
    return ReviewCandidateAnalysis(
        context=trusted_context,
        items=tuple(items),
        solution_intent=solution_intent,
        review_transcript=review_transcript,
        si_content_fingerprint=source_index.si_content_fingerprint,
        transcript_content_fingerprint=source_index.transcript_content_fingerprint,
        provider_configuration_identity=provider_configuration_identity,
        analysis_id=identity,
    )


def validate_candidate_analysis_binding(
    analysis: ReviewCandidateAnalysis,
    solution_intent: str,
    review_transcript: str,
    context: SolutionIntentReviewContext,
    *,
    provider_configuration_identity: str | None = None,
) -> None:
    """Rebuild evidence and identity, including after bypassing Pydantic with model_copy."""
    if not isinstance(analysis, ReviewCandidateAnalysis):
        raise CandidateEvidenceError("Provider must return a candidate analysis")
    if (
        review_source_fingerprint(solution_intent) != analysis.si_content_fingerprint
        or review_source_fingerprint(review_transcript) != analysis.transcript_content_fingerprint
        or context.model_dump(mode="json") != analysis.context.model_dump(mode="json")
        or (
            provider_configuration_identity is not None
            and provider_configuration_identity != analysis.provider_configuration_identity
        )
    ):
        raise CandidateEvidenceError("Candidate analysis does not match the confirmed inputs")
    expected = build_candidate_analysis(
        {
            "items": [
                {
                    "kind": item.kind,
                    "text": item.text,
                    "evidence_source_ids": list(item.evidence_source_ids),
                }
                for item in analysis.items
            ]
        },
        analysis.solution_intent,
        analysis.review_transcript,
        analysis.context,
        provider_configuration_identity=analysis.provider_configuration_identity,
    )
    if expected.model_dump() != analysis.model_dump():
        raise CandidateEvidenceError("Candidate evidence or snapshot identity was modified")
