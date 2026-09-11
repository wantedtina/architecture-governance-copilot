"""Literal, conservative candidate grouping for edited offline demo transcripts."""

from __future__ import annotations

import re
from datetime import date, datetime

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
    "defaults. Explicit speaker commitments and dates become candidates; "
    "ambiguous values remain unset. The outcome is not inferred."
)


def _explicit_date(content: str) -> date | None:
    matches = re.findall(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2} [A-Za-z]+ \d{4})\b", content)
    if len(matches) != 1:
        return None
    literal = re.escape(matches[0])
    if not re.search(
        rf"(?:\bby\s+|\bdue(?:\s+on)?\s+){literal}\b|{literal}\s+due date\b", content, re.I
    ):
        return None
    for fmt in ("%Y-%m-%d", "%d %B %Y"):
        try:
            return datetime.strptime(matches[0], fmt).date()
        except ValueError:
            pass
    return None


def _task_words(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+", text.lower())) - {
        "i",
        "will",
        "the",
        "a",
        "an",
        "and",
        "its",
        "by",
        "of",
        "to",
        "date",
        "due",
        "accept",
        "ownership",
        "action",
        "document",
        "schedule",
    }


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
        speaker_match = re.match(r"^\[[^\]]+\]\s+([^:]+):\s*", quote)
        speaker = speaker_match.group(1).strip() if speaker_match else None
        due = _explicit_date(content)
        acknowledgement = lower.startswith("i accept ownership of ")
        if acknowledgement and speaker and due:
            candidates = [
                action
                for action in result.action_items
                if action.owner == speaker
                and action.due_date == due
                and (_task_words(action.title) & _task_words(content))
                - _task_words(due.strftime("%d %B %Y"))
            ]
            if len(candidates) == 1:
                candidates[0].evidence.extend(evidence)
                continue
        if (
            not acknowledgement
            and re.search(r"\b(action|i will|please add|please update)\b", lower)
            and not re.search(r"\b(no|not|never)\b", lower)
        ):
            result.action_items.append(
                ActionItem(
                    title=content,
                    owner=speaker if lower.startswith("i will ") else None,
                    due_date=due,
                    priority=ActionPriority.MEDIUM,
                    evidence=evidence,
                )
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
