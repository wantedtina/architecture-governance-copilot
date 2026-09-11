"""Literal, conservative candidate grouping for edited offline demo transcripts."""

from __future__ import annotations

import re

from architecture_governance_copilot.models import (
    ActionItem,
    ActionPriority,
    Decision,
    EvidenceSource,
    FindingSeverity,
    GovernanceResult,
    MissingEvidence,
    OpenQuestion,
    ReviewFinding,
    ReviewOutcome,
    Risk,
    RiskSeverity,
    SolutionIntentReviewContext,
    SourceEvidence,
)

DEMO_REVIEW_GUIDANCE = (
    "Offline demo: edited transcripts use literal keyword grouping, not semantic AI analysis. "
    "Review every proposed category and unclassified line. Medium severity/priority are review "
    "defaults; owners and dates are left unset. The outcome is not inferred."
)


def group_transcript_candidates(
    transcript: str, context: SolutionIntentReviewContext
) -> GovernanceResult:
    """Retain every nonblank source line without recycling the fixed sample analysis."""
    result = GovernanceResult(
        context=context.model_copy(deep=True), review_outcome=ReviewOutcome.NOT_STATED
    )
    normalized = transcript.replace("\r\n", "\n").replace("\r", "\n").strip()
    for number, raw in enumerate(normalized.splitlines(), 1):
        quote = raw.strip()
        if not quote:
            continue
        evidence = [
            SourceEvidence(
                source_type=EvidenceSource.MEETING_TRANSCRIPT,
                quote=quote,
                reference=f"transcript-line-{number}",
            )
        ]
        # Strip only the conventional speaker prefix for grouping; evidence stays literal.
        content = re.sub(r"^\[[^\]]+\]\s+[^:]+:\s*", "", quote)
        lower = content.lower()
        if re.search(r"\b(action|i will|please add|please update)\b", lower) and not re.search(
            r"\b(no|not|never)\b", lower
        ):
            result.action_items.append(
                ActionItem(title=content, priority=ActionPriority.MEDIUM, evidence=evidence)
            )
        elif re.search(r"\b(risk)\b", lower):
            result.risks.append(
                Risk(description=content, severity=RiskSeverity.MEDIUM, evidence=evidence)
            )
        elif re.search(r"\b(finding|not defined|not stated|does not explain)\b", lower):
            result.findings.append(
                ReviewFinding(
                    title=f"Candidate finding · line {number}",
                    description=content,
                    severity=FindingSeverity.MEDIUM,
                    evidence=evidence,
                )
            )
        elif re.match(r"(?:decision\s*:|i confirm\b)", lower) and not re.search(
            r"\b(no|not|never)\b", lower
        ):
            result.decisions.append(Decision(statement=content, evidence=evidence))
        elif "?" in content or re.search(r"\b(question|unresolved)\b", lower):
            result.open_questions.append(OpenQuestion(question=content, evidence=evidence))
        else:
            result.missing_evidence.append(
                MissingEvidence(
                    item=f"Classify transcript line {number}",
                    reason=(
                        "No supported category rule matched. Review this source text manually; "
                        "it is not an inferred missing artifact."
                    ),
                    evidence=evidence,
                )
            )
    return result
