"""AIF governance-analysis contract, validation boundary, and offline fake."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from enum import StrEnum
from typing import Annotated, Protocol, runtime_checkable

from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

from architecture_governance_copilot.integrations.aif_candidate_protocol import (
    CandidateProtocolError,
)
from architecture_governance_copilot.models import SolutionIntentReviewContext
from architecture_governance_copilot.review_candidates import (
    CANDIDATE_CONTRACT_VERSION,
    CandidateEvidenceError,
    ReviewCandidateAnalysis,
    build_candidate_analysis,
    candidate_json_schema,
    parse_candidate_payload,
)
from architecture_governance_copilot.review_sources import SOURCE_INDEX_VERSION

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
SourceText = Annotated[str, StringConstraints(min_length=1)]


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


class _RequestContext(SolutionIntentReviewContext):
    """The confirmed metadata cannot change while the transport handles a request."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)


class AifGovernanceRequest(_BoundaryModel):
    """Complete, explicit governance-analysis request sent to an AIF transport."""

    solution_intent: SourceText
    review_transcript: SourceText
    context: SolutionIntentReviewContext
    schema_constraints: dict[str, object]
    provider_configuration_identity: NonEmptyString
    solution_intent_source_fingerprint: NonEmptyString
    transcript_source_fingerprint: NonEmptyString
    candidate_contract_version: str = CANDIDATE_CONTRACT_VERSION
    source_index_version: str = SOURCE_INDEX_VERSION

    @field_validator("context")
    @classmethod
    def freeze_confirmed_context(cls, value: SolutionIntentReviewContext) -> _RequestContext:
        return _RequestContext.model_validate(value.model_dump())

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

    # TODO(INTERNAL-AIF): Implement the approved company transport described in
    # docs/INTERNAL_INTEGRATION_HANDOFF.md without changing this validated boundary.

    def analyze(self, request: AifGovernanceRequest) -> str | Mapping[str, object]:
        """Return one candidate object after transport envelope decoding."""
        ...


class FakeAifTransport:
    """Return configured synthetic responses and record explicit calls."""

    def __init__(
        self,
        responses: Sequence[str | Mapping[str, object] | Exception],
        *,
        response_factory: Callable[[AifGovernanceRequest], Mapping[str, object]] | None = None,
    ) -> None:
        if not responses:
            raise ValueError("At least one fake AIF response is required.")
        self._responses = list(responses)
        self._response_factory = response_factory
        self.calls: list[AifGovernanceRequest] = []

    def analyze(self, request: AifGovernanceRequest) -> str | Mapping[str, object]:
        """Consume one configured response for each explicit analysis call."""
        self.calls.append(request)
        if self._response_factory is not None:
            return copy.deepcopy(self._response_factory(request))
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
    ) -> ReviewCandidateAnalysis:
        """Call AIF once and resolve its candidate IDs against the exact original sources."""
        request = AifGovernanceRequest(
            solution_intent=solution_intent,
            review_transcript=review_transcript,
            context=_RequestContext.model_validate(context.model_dump()),
            schema_constraints=candidate_json_schema(),
            provider_configuration_identity=self._provider_configuration_identity,
            solution_intent_source_fingerprint=_source_fingerprint(solution_intent),
            transcript_source_fingerprint=_source_fingerprint(review_transcript),
        )
        try:
            response = self._transport.analyze(request)
        except AifTransportFailure as exc:
            raise AifAnalysisError(exc.category) from exc
        except CandidateProtocolError as exc:
            raise AifAnalysisError(AifErrorCategory(exc.category)) from exc
        except TimeoutError as exc:
            raise AifAnalysisError(AifErrorCategory.TIMEOUT) from exc
        except Exception as exc:
            raise AifAnalysisError(AifErrorCategory.PROVIDER_FAILURE) from exc

        try:
            payload = parse_candidate_payload(response)
        except (json.JSONDecodeError, TypeError, ValidationError, ValueError) as exc:
            raise AifAnalysisError(AifErrorCategory.INVALID_RESPONSE) from exc
        try:
            return build_candidate_analysis(
                payload,
                solution_intent,
                review_transcript,
                request.context,
                provider_configuration_identity=self._provider_configuration_identity,
            )
        except CandidateEvidenceError as exc:
            raise AifAnalysisError(AifErrorCategory.INVALID_EVIDENCE) from exc


def _normalize_source(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def _source_fingerprint(value: str) -> str:
    return hashlib.sha256(_normalize_source(value).encode("utf-8")).hexdigest()
