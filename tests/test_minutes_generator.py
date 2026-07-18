"""Tests for standardized Solution Intent review-minutes generation."""

from __future__ import annotations

from pathlib import Path

import pytest

from architecture_governance_copilot.minutes_generator import generate_review_minutes
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
    SolutionIntentStatus,
    SourceEvidence,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RESULT_PATH = REPOSITORY_ROOT / "samples" / "expected_result.json"
SECTION_HEADINGS = [
    "# Solution Intent Review Record",
    "## Review Context",
    "## Review Outcome",
    "## Confirmed Decisions",
    "## Review Findings",
    "## Risks",
    "## Action Items",
    "## Open Questions",
    "## Missing Governance Information",
    "## Governance Note",
]
_NONE_RECORDED_LINE = "None recorded."


@pytest.fixture
def sample_result() -> GovernanceResult:
    """Load the validated synthetic review result."""
    return GovernanceResult.model_validate_json(EXPECTED_RESULT_PATH.read_text(encoding="utf-8"))


def _context(**overrides: object) -> SolutionIntentReviewContext:
    values: dict[str, object] = {
        "project_name": "Project Northstar",
        "si_title": "Northstar Solution Intent",
        "si_version": "0.4",
        "current_si_status": SolutionIntentStatus.UNDER_REVIEW,
        "review_round": 1,
    }
    values.update(overrides)
    return SolutionIntentReviewContext.model_validate(values)


def _evidence(
    quote: str = "The review outcome is changes requested.",
    **overrides: object,
) -> SourceEvidence:
    values: dict[str, object] = {
        "source_type": EvidenceSource.MEETING_TRANSCRIPT,
        "quote": quote,
        "speaker": "Morgan Lee",
        "timestamp": "11:00",
        "reference": "transcript-line-1",
    }
    values.update(overrides)
    return SourceEvidence.model_validate(values)


def _minimal_result(**overrides: object) -> GovernanceResult:
    values: dict[str, object] = {
        "context": _context(),
        "review_outcome": ReviewOutcome.CHANGES_REQUESTED,
        "outcome_evidence": [_evidence()],
    }
    values.update(overrides)
    return GovernanceResult.model_validate(values)


def _section(markdown: str, heading: str, next_heading: str) -> str:
    return markdown.split(heading, maxsplit=1)[1].split(next_heading, maxsplit=1)[0]


def test_sample_minutes_have_required_sections_in_exact_order(
    sample_result: GovernanceResult,
) -> None:
    minutes = generate_review_minutes(sample_result)

    assert minutes.startswith("# Solution Intent Review Record\n")
    assert [minutes.index(heading) for heading in SECTION_HEADINGS] == sorted(
        minutes.index(heading) for heading in SECTION_HEADINGS
    )
    assert [line for line in minutes.splitlines() if line.startswith("#")] == SECTION_HEADINGS


def test_sample_minutes_contain_complete_review_context(
    sample_result: GovernanceResult,
) -> None:
    minutes = generate_review_minutes(sample_result)

    expected_lines = [
        "- **Project:** Digital Payment Notification Service",
        "- **Solution Intent:** Solution Intent - Digital Payment Notification Service",
        "- **SI Version:** 1.2",
        "- **SI Status Before Review:** Under Review",
        "- **Review Round:** 2",
        "- **Review Date:** 2026-07-18",
        "- **Domain Architect:** Jordan Lee",
        "- **ADO Governance Ticket:** ARCH-POC-1024",
    ]
    assert all(line in minutes for line in expected_lines)


def test_sample_minutes_contain_every_governance_item(
    sample_result: GovernanceResult,
) -> None:
    minutes = generate_review_minutes(sample_result)

    assert "**Outcome:** Changes Requested" in minutes
    for decision in sample_result.decisions:
        assert decision.statement in minutes
    for finding in sample_result.findings:
        assert finding.title in minutes
    for risk in sample_result.risks:
        assert risk.description in minutes
    for action in sample_result.action_items:
        assert action.title in minutes
    for question in sample_result.open_questions:
        assert question.question in minutes
    for missing in sample_result.missing_evidence:
        assert missing.item in minutes


def test_sample_minutes_include_fixed_human_accountability_note(
    sample_result: GovernanceResult,
) -> None:
    minutes = generate_review_minutes(sample_result)

    assert "generated from structured review information" in minutes
    assert "Domain Architect remains responsible for the formal governance decision" in minutes
    assert "Review this generated record before publication" in minutes
    assert "application approved" not in minutes.lower()
    assert "ai approved" not in minutes.lower()


def test_enums_are_rendered_as_human_readable_labels(
    sample_result: GovernanceResult,
) -> None:
    minutes = generate_review_minutes(sample_result)

    assert "under_review" not in minutes
    assert "changes_requested" not in minutes
    assert "**SI Status Before Review:** Under Review" in minutes
    assert "**Outcome:** Changes Requested" in minutes
    assert "**Severity:** High" in minutes
    assert "**Severity:** Medium" in minutes
    assert "**Status:** Open" in minutes
    assert "**Priority:** High" in minutes


def test_solution_intent_evidence_is_rendered_exactly(
    sample_result: GovernanceResult,
) -> None:
    minutes = generate_review_minutes(sample_result)
    evidence = sample_result.findings[0].evidence[0]

    assert evidence.quote in minutes
    assert (
        "[Solution Intent | Availability and Resilience | "
        'Reference: SI-7-FAILOVER] "behaviour when one replica becomes unavailable '
        'is not described."'
    ) in minutes


def test_transcript_evidence_is_rendered_exactly(
    sample_result: GovernanceResult,
) -> None:
    minutes = generate_review_minutes(sample_result)
    evidence = sample_result.outcome_evidence[0]

    assert evidence.quote in minutes
    assert (
        "[Meeting Transcript | 10:28 | Jordan Lee | Reference: transcript-line-29] "
        '"The outcome for review round two is changes requested."'
    ) in minutes


def test_all_sample_evidence_quotes_are_preserved(
    sample_result: GovernanceResult,
) -> None:
    minutes = generate_review_minutes(sample_result)
    collections = [
        sample_result.findings,
        sample_result.decisions,
        sample_result.risks,
        sample_result.action_items,
        sample_result.open_questions,
        sample_result.missing_evidence,
    ]

    for evidence in sample_result.outcome_evidence:
        assert evidence.quote in minutes
    for collection in collections:
        for item in collection:
            for evidence in item.evidence:
                assert evidence.quote in minutes


def test_absent_optional_context_fields_use_explicit_fallbacks(
    sample_result: GovernanceResult,
) -> None:
    result = sample_result.model_copy(update={"context": _context()})

    minutes = generate_review_minutes(result)

    assert "- **Review Date:** Not provided" in minutes
    assert "- **Domain Architect:** Not provided" in minutes
    assert "- **ADO Governance Ticket:** Not provided" in minutes
    assert "None" not in minutes
    assert "null" not in minutes


def test_absent_optional_item_fields_are_omitted_or_use_required_fallbacks() -> None:
    evidence = _evidence()
    result = _minimal_result(
        decisions=[Decision(statement="Use the managed service.", evidence=[evidence])],
        findings=[
            ReviewFinding(
                title="Design detail is missing.",
                description="The detail must be documented.",
                severity=FindingSeverity.HIGH,
                evidence=[evidence],
            )
        ],
        risks=[
            Risk(
                description="The release could be delayed.",
                severity=RiskSeverity.MEDIUM,
                evidence=[evidence],
            )
        ],
        action_items=[
            ActionItem(
                title="Document the detail.",
                priority=ActionPriority.HIGH,
                evidence=[evidence],
            )
        ],
        open_questions=[
            OpenQuestion(question="Which option should be selected?", evidence=[evidence])
        ],
        missing_evidence=[MissingEvidence(item="Recovery test results")],
    )

    minutes = generate_review_minutes(result)
    decisions = _section(minutes, "## Confirmed Decisions", "## Review Findings")
    findings = _section(minutes, "## Review Findings", "## Risks")
    risks = _section(minutes, "## Risks", "## Action Items")
    actions = _section(minutes, "## Action Items", "## Open Questions")
    questions = _section(minutes, "## Open Questions", "## Missing Governance Information")
    missing = _section(minutes, "## Missing Governance Information", "## Governance Note")

    assert "Rationale" not in decisions
    assert "Category" not in findings
    assert "SI Section" not in findings
    assert "Recommended Change" not in findings
    assert "Owner" not in findings
    assert "Due Date" not in findings
    assert "Owner" not in risks
    assert "**Owner:** Unassigned" in actions
    assert "**Due Date:** Not specified" in actions
    assert "Owner" not in questions
    assert "Reason" not in missing
    assert "Supporting Evidence" not in missing
    assert "None" not in minutes
    assert "null" not in minutes


def test_empty_collections_are_rendered_explicitly() -> None:
    minutes = generate_review_minutes(_minimal_result())

    for heading, next_heading in zip(
        SECTION_HEADINGS[3:9],
        SECTION_HEADINGS[4:10],
        strict=True,
    ):
        assert _NONE_RECORDED_LINE in _section(minutes, heading, next_heading)
    assert minutes.count(_NONE_RECORDED_LINE) == 6


def test_minutes_are_deterministic_ordered_and_do_not_mutate_input(
    sample_result: GovernanceResult,
) -> None:
    before = sample_result.model_dump(mode="json")

    first = generate_review_minutes(sample_result)
    second = generate_review_minutes(sample_result)

    assert first == second
    assert sample_result.model_dump(mode="json") == before
    assert first.index(sample_result.findings[0].title) < first.index(
        sample_result.findings[1].title
    )
    assert first.index(sample_result.action_items[0].title) < first.index(
        sample_result.action_items[1].title
    )


def test_minutes_do_not_include_complete_source_documents(
    sample_result: GovernanceResult,
) -> None:
    minutes = generate_review_minutes(sample_result)

    assert "The conceptual flow is event driven." not in minutes
    assert "Thanks for joining review round two" not in minutes
