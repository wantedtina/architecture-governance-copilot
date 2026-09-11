"""Request-aware synthetic responses, never a live AIF transport or Offline fallback."""

from architecture_governance_copilot.demo_review import group_transcript_candidates
from architecture_governance_copilot.integrations.aif import AifGovernanceRequest
from architecture_governance_copilot.models import GovernanceResult


class SyntheticReviewResponder:
    """Keep canonical fake output while deriving edited requests from their current inputs."""

    def __init__(self, solution_intent: str, transcript: str, response: str) -> None:
        self._si = self._normalize(solution_intent)
        self._transcript = self._normalize(transcript)
        self._result = GovernanceResult.model_validate_json(response)

    @staticmethod
    def _normalize(text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n").strip()

    def __call__(self, request: AifGovernanceRequest) -> dict[str, object]:
        if self._normalize(request.solution_intent) != self._si:
            raise ValueError("Reload the configured synthetic SI snapshot.")
        if not request.review_transcript.strip():
            raise ValueError("Provide a nonblank review transcript.")
        if any(
            getattr(request.context, field) != getattr(self._result.context, field)
            for field in ("project_name", "si_title", "si_version", "current_si_status")
        ):
            raise ValueError("Review metadata must retain the synthetic SI identity.")
        if self._normalize(request.review_transcript) == self._transcript:
            result = self._result.model_copy(deep=True)
            result.context = request.context.model_copy(deep=True)
        else:
            result = group_transcript_candidates(request.review_transcript, request.context)
        return result.model_dump(mode="json")
