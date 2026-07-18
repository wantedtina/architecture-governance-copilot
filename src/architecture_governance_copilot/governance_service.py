"""Application orchestration for human-reviewed governance records."""

from __future__ import annotations

from dataclasses import dataclass

from architecture_governance_copilot.ado_generator import generate_mock_ado_work_items
from architecture_governance_copilot.extractors import GovernanceExtractor
from architecture_governance_copilot.minutes_generator import generate_review_minutes
from architecture_governance_copilot.models import (
    GovernanceResult,
    MockAdoWorkItem,
    SolutionIntentReviewContext,
)


@dataclass(frozen=True, slots=True)
class GovernanceOutputs:
    """Generated review minutes and mock work items for a reviewed result."""

    review_minutes: str
    ado_work_items: tuple[MockAdoWorkItem, ...]


class GovernanceReviewService:
    """Coordinate governance analysis and reviewed-result output generation."""

    def __init__(self, extractor: GovernanceExtractor) -> None:
        self._extractor = extractor

    def analyze_review(
        self,
        solution_intent: str,
        review_transcript: str,
        context: SolutionIntentReviewContext,
    ) -> GovernanceResult:
        """Delegate review analysis to the configured extractor."""
        return self._extractor.extract(solution_intent, review_transcript, context)

    def generate_outputs(
        self,
        reviewed_result: GovernanceResult,
    ) -> GovernanceOutputs:
        """Generate deterministic outputs from a caller-supplied reviewed result."""
        review_minutes = generate_review_minutes(reviewed_result)
        ado_work_items = tuple(generate_mock_ado_work_items(reviewed_result))
        return GovernanceOutputs(
            review_minutes=review_minutes,
            ado_work_items=ado_work_items,
        )
