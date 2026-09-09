"""AIF governance-analysis contract, validation boundary, and offline fake."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Annotated, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, StringConstraints, ValidationError, model_validator

from architecture_governance_copilot.evidence_validation import (
    EvidenceValidationError,
    validate_governance_evidence,
)
from architecture_governance_copilot.models import (
    EvidenceSource,
    GovernanceResult,
    SolutionIntentReviewContext,
    SourceEvidence,
)

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
SourceText = Annotated[str, StringConstraints(min_length=1)]

_HEADING_PATTERN = re.compile(r"^#{1,6}\s+(?:\d+\.\s+)?(?P<title>.+?)\s*$", re.MULTILINE)
_TRANSCRIPT_PATTERN = re.compile(
    r"^\[(?P<timestamp>[^\]\r\n]+)\]\s+(?P<speaker>[^:\r\n]+):",
    re.MULTILINE,
)


class AifErrorCategory(StrEnum):
    """Recoverable categories exposed without provider response bodies."""

    REFUSAL = "refusal"
    TIMEOUT = "timeout"
    INVALID_RESPONSE = "invalid_response"
    CONTEXT_MISMATCH = "context_mismatch"
    INVALID_EVIDENCE = "invalid_evidence"
    PROVIDER_FAILURE = "provider_failure"


_SAFE_ERROR_MESSAGES = {
    AifErrorCategory.REFUSAL: "The analysis provider refused the request.",
    AifErrorCategory.TIMEOUT: "The analysis provider timed out.",
    AifErrorCategory.INVALID_RESPONSE: "The analysis provider returned an invalid response.",
    AifErrorCategory.CONTEXT_MISMATCH: (
        "The analysis response did not match the confirmed review context."
    ),
    AifErrorCategory.INVALID_EVIDENCE: (
        "The analysis response contained evidence that did not match the supplied sources."
    ),
    AifErrorCategory.PROVIDER_FAILURE: "The analysis provider could not complete the request.",
}


class _BoundaryModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AifGovernanceRequest(_BoundaryModel):
    """Complete, explicit governance-analysis request sent to an AIF transport."""

    solution_intent: SourceText
    review_transcript: SourceText
    context: SolutionIntentReviewContext
    schema_constraints: dict[str, object]
    provider_configuration_identity: NonEmptyString
    solution_intent_source_fingerprint: NonEmptyString
    transcript_source_fingerprint: NonEmptyString

    @model_validator(mode="after")
    def validate_sources(self) -> AifGovernanceRequest:
        """Reject blank sources without changing the exact supplied text."""
        if not self.solution_intent.strip() or not self.review_transcript.strip():
            raise ValueError("Analysis sources must not be blank.")
        return self


class AifAnalysisError(RuntimeError):
    """Safe application-facing AIF error with a recoverable category."""

    def __init__(self, category: AifErrorCategory) -> None:
        self.category = category
        super().__init__(_SAFE_ERROR_MESSAGES[category])


class AifTransportFailure(RuntimeError):
    """Synthetic transport failure used without retaining a response body."""

    def __init__(self, category: AifErrorCategory) -> None:
        if category not in {AifErrorCategory.REFUSAL, AifErrorCategory.TIMEOUT}:
            raise ValueError("Transport failures must be refusal or timeout categories.")
        self.category = category
        super().__init__(_SAFE_ERROR_MESSAGES[category])


@runtime_checkable
class AifTransport(Protocol):
    """Submit one structured governance-analysis request."""

    def analyze(self, request: AifGovernanceRequest) -> str | Mapping[str, object]:
        """Return one JSON-compatible structured provider response."""
        ...


class FakeAifTransport:
    """Return configured synthetic responses and record explicit calls."""

    def __init__(
        self,
        responses: Sequence[str | Mapping[str, object] | Exception],
    ) -> None:
        if not responses:
            raise ValueError("At least one fake AIF response is required.")
        self._responses = list(responses)
        self.calls: list[AifGovernanceRequest] = []

    def analyze(self, request: AifGovernanceRequest) -> str | Mapping[str, object]:
        """Consume one configured response for each explicit analysis call."""
        self.calls.append(request)
        if not self._responses:
            raise AifTransportFailure(AifErrorCategory.TIMEOUT)
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return copy.deepcopy(response)


class AifGovernanceExtractor:
    """Parse, validate, and reference one AIF governance response."""

    def __init__(
        self,
        transport: AifTransport,
        *,
        provider_configuration_identity: str,
    ) -> None:
        normalized_identity = provider_configuration_identity.strip()
        if not normalized_identity:
            raise ValueError("A provider configuration identity is required.")
        self._transport = transport
        self._provider_configuration_identity = normalized_identity

    def extract(
        self,
        solution_intent: str,
        review_transcript: str,
        context: SolutionIntentReviewContext,
    ) -> GovernanceResult:
        """Call AIF once, enforce the request context, and assign trusted references."""
        request = AifGovernanceRequest(
            solution_intent=solution_intent,
            review_transcript=review_transcript,
            context=context,
            schema_constraints=GovernanceResult.model_json_schema(),
            provider_configuration_identity=self._provider_configuration_identity,
            solution_intent_source_fingerprint=_source_fingerprint(solution_intent),
            transcript_source_fingerprint=_source_fingerprint(review_transcript),
        )
        try:
            response = self._transport.analyze(request)
        except AifTransportFailure as exc:
            raise AifAnalysisError(exc.category) from exc
        except TimeoutError as exc:
            raise AifAnalysisError(AifErrorCategory.TIMEOUT) from exc
        except Exception as exc:
            raise AifAnalysisError(AifErrorCategory.PROVIDER_FAILURE) from exc

        try:
            result = _parse_response(response)
        except (json.JSONDecodeError, TypeError, ValidationError, ValueError) as exc:
            raise AifAnalysisError(AifErrorCategory.INVALID_RESPONSE) from exc
        if result.context != context:
            raise AifAnalysisError(AifErrorCategory.CONTEXT_MISMATCH)

        trusted_result = result.model_copy(deep=True)
        for evidence in _iter_evidence(trusted_result):
            evidence.reference = None
        try:
            validate_governance_evidence(
                trusted_result,
                solution_intent,
                review_transcript,
            )
        except EvidenceValidationError as exc:
            raise AifAnalysisError(AifErrorCategory.INVALID_EVIDENCE) from exc
        _assign_source_references(trusted_result, solution_intent, review_transcript)
        return trusted_result


def _parse_response(response: str | Mapping[str, object]) -> GovernanceResult:
    if isinstance(response, str):
        return GovernanceResult.model_validate_json(response)
    if isinstance(response, Mapping):
        return GovernanceResult.model_validate(dict(response))
    raise TypeError("Unsupported response type")


def _iter_evidence(result: GovernanceResult) -> list[SourceEvidence]:
    evidence_items = list(result.outcome_evidence)
    for collection_name in (
        "findings",
        "decisions",
        "risks",
        "action_items",
        "open_questions",
        "missing_evidence",
    ):
        for item in getattr(result, collection_name):
            evidence_items.extend(item.evidence)
    return evidence_items


def _assign_source_references(
    result: GovernanceResult,
    solution_intent: str,
    review_transcript: str,
) -> None:
    normalized_sources = {
        EvidenceSource.SOLUTION_INTENT: _normalize_source(solution_intent),
        EvidenceSource.MEETING_TRANSCRIPT: _normalize_source(review_transcript),
    }
    for evidence in _iter_evidence(result):
        source = normalized_sources[evidence.source_type]
        span = _resolve_unique_span(source, evidence)
        if span is None:
            continue
        source_namespace = (
            "si" if evidence.source_type is EvidenceSource.SOLUTION_INTENT else "transcript"
        )
        source_digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]
        evidence.reference = f"{source_namespace}-{source_digest}-{span[0]}-{span[1]}"


def _resolve_unique_span(source: str, evidence: SourceEvidence) -> tuple[int, int] | None:
    quote = _normalize_source(evidence.quote)
    spans = _quote_spans(source, quote)
    if evidence.source_type is EvidenceSource.SOLUTION_INTENT and evidence.section is not None:
        spans = _filter_si_section_spans(source, spans, evidence.section)
    if evidence.source_type is EvidenceSource.MEETING_TRANSCRIPT and (
        evidence.speaker is not None or evidence.timestamp is not None
    ):
        spans = _filter_transcript_spans(source, spans, evidence)
    return spans[0] if len(spans) == 1 else None


def _quote_spans(source: str, quote: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start = 0
    while True:
        index = source.find(quote, start)
        if index < 0:
            return spans
        spans.append((index, index + len(quote)))
        start = index + 1


def _filter_si_section_spans(
    source: str,
    spans: list[tuple[int, int]],
    section: str,
) -> list[tuple[int, int]]:
    headings = list(_HEADING_PATTERN.finditer(source))
    normalized_section = " ".join(section.split())
    section_ranges: list[tuple[int, int]] = []
    for index, heading in enumerate(headings):
        if " ".join(heading.group("title").split()) != normalized_section:
            continue
        level = len(heading.group(0)) - len(heading.group(0).lstrip("#"))
        end = len(source)
        for later in headings[index + 1 :]:
            later_level = len(later.group(0)) - len(later.group(0).lstrip("#"))
            if later_level <= level:
                end = later.start()
                break
        section_ranges.append((heading.start(), end))
    return [
        span
        for span in spans
        if any(start <= span[0] and span[1] <= end for start, end in section_ranges)
    ]


def _filter_transcript_spans(
    source: str,
    spans: list[tuple[int, int]],
    evidence: SourceEvidence,
) -> list[tuple[int, int]]:
    utterances = list(_TRANSCRIPT_PATTERN.finditer(source))
    matched: list[tuple[int, int]] = []
    for span in spans:
        for index, utterance in enumerate(utterances):
            end = utterances[index + 1].start() if index + 1 < len(utterances) else len(source)
            if not (utterance.start() <= span[0] and span[1] <= end):
                continue
            if (
                evidence.speaker is not None
                and utterance.group("speaker").strip() != evidence.speaker
            ):
                continue
            if (
                evidence.timestamp is not None
                and utterance.group("timestamp").strip() != evidence.timestamp
            ):
                continue
            matched.append(span)
            break
    return matched


def _normalize_source(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def _source_fingerprint(value: str) -> str:
    return hashlib.sha256(_normalize_source(value).encode("utf-8")).hexdigest()
