"""Consistency tests for the frozen synthetic Solution Intent review dataset."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from architecture_governance_copilot.models import (
    EvidenceSource,
    FindingStatus,
    GovernanceResult,
    ReviewOutcome,
    SolutionIntentReviewContext,
    SolutionIntentStatus,
    SourceEvidence,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = REPOSITORY_ROOT / "samples"
SOLUTION_INTENT_PATH = SAMPLES_DIR / "solution_intent.md"
METADATA_PATH = SAMPLES_DIR / "review_metadata.json"
TRANSCRIPT_PATH = SAMPLES_DIR / "review_transcript.txt"
EXPECTED_RESULT_PATH = SAMPLES_DIR / "expected_result.json"
DRAFT_TEMPLATE_PATH = SAMPLES_DIR / "si_template.md"
SOURCE_CONTEXT_PATH = SAMPLES_DIR / "source_context.txt"
SUPPORTING_CONTEXT_PATH = SAMPLES_DIR / "supporting_context.md"
SAMPLE_PATHS = (
    SOLUTION_INTENT_PATH,
    METADATA_PATH,
    TRANSCRIPT_PATH,
    EXPECTED_RESULT_PATH,
    DRAFT_TEMPLATE_PATH,
    SOURCE_CONTEXT_PATH,
    SUPPORTING_CONTEXT_PATH,
)


def load_json(path: Path) -> dict[str, Any]:
    """Load a sample JSON object using UTF-8."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def load_metadata() -> SolutionIntentReviewContext:
    """Load and validate the frozen review metadata."""
    return SolutionIntentReviewContext.model_validate(load_json(METADATA_PATH))


def load_result() -> GovernanceResult:
    """Load and validate the frozen expected governance result."""
    return GovernanceResult.model_validate(load_json(EXPECTED_RESULT_PATH))


def iter_evidence(result: GovernanceResult) -> Iterator[SourceEvidence]:
    """Yield every evidence item nested directly within the governance result."""
    yield from result.outcome_evidence
    for collection in (
        result.findings,
        result.decisions,
        result.risks,
        result.action_items,
        result.open_questions,
        result.missing_evidence,
    ):
        for item in collection:
            yield from item.evidence


def solution_intent_headings(solution_intent: str) -> set[str]:
    """Return normalized second-level section headings from the sample SI."""
    headings = set()
    for match in re.finditer(r"^##\s+(?:\d+\.\s+)?(.+?)\s*$", solution_intent, re.MULTILINE):
        headings.add(match.group(1))
    return headings


@pytest.mark.parametrize("path", SAMPLE_PATHS)
def test_required_sample_file_exists(path: Path) -> None:
    assert path.is_file()


@pytest.mark.parametrize("path", [METADATA_PATH, EXPECTED_RESULT_PATH])
def test_sample_json_is_parseable(path: Path) -> None:
    assert load_json(path)


@pytest.mark.parametrize(
    "path",
    [
        SOLUTION_INTENT_PATH,
        TRANSCRIPT_PATH,
        DRAFT_TEMPLATE_PATH,
        SOURCE_CONTEXT_PATH,
        SUPPORTING_CONTEXT_PATH,
    ],
)
def test_sample_text_file_is_non_empty(path: Path) -> None:
    assert path.read_text(encoding="utf-8").strip()


def test_sample_documents_fit_demo_size_bounds() -> None:
    solution_intent_words = SOLUTION_INTENT_PATH.read_text(encoding="utf-8").split()
    transcript_lines = TRANSCRIPT_PATH.read_text(encoding="utf-8").splitlines()

    assert 1_000 <= len(solution_intent_words) <= 1_800
    assert 25 <= len(transcript_lines) <= 40


def test_drafting_template_covers_generated_si_sections() -> None:
    template_headings = solution_intent_headings(DRAFT_TEMPLATE_PATH.read_text(encoding="utf-8"))
    generated_headings = solution_intent_headings(SOLUTION_INTENT_PATH.read_text(encoding="utf-8"))

    assert template_headings == generated_headings


def test_drafting_context_is_explicitly_synthetic() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (SOURCE_CONTEXT_PATH, SUPPORTING_CONTEXT_PATH)
    )

    assert "synthetic" in combined.lower()
    assert "not evidenced" in combined.lower()


def test_review_metadata_validates() -> None:
    metadata = load_metadata()

    assert metadata.project_name == "Digital Payment Notification Service"
    assert metadata.si_title == "Solution Intent - Digital Payment Notification Service"
    assert metadata.si_version == "1.2"
    assert metadata.current_si_status is SolutionIntentStatus.UNDER_REVIEW
    assert metadata.review_round == 2
    assert metadata.ado_ticket_id == "ARCH-POC-1024"
    assert metadata.domain_architect == "Jordan Lee"
    assert metadata.review_date == date(2026, 7, 18)


def test_review_metadata_serializes_enum_and_date_values() -> None:
    dumped = load_metadata().model_dump(mode="json")

    assert dumped["current_si_status"] == "under_review"
    assert dumped["review_date"] == "2026-07-18"


def test_expected_result_validates_and_matches_metadata() -> None:
    result = load_result()

    assert result.context == load_metadata()
    assert result.review_outcome is ReviewOutcome.CHANGES_REQUESTED


def test_expected_result_has_required_scenario_counts() -> None:
    result = load_result()

    assert len(result.decisions) == 1
    assert len(result.findings) == 3
    assert len(result.risks) == 1
    assert len(result.action_items) == 2
    assert len(result.open_questions) == 1
    assert all(finding.status is FindingStatus.OPEN for finding in result.findings)
    assert {item.item for item in result.missing_evidence} >= {
        "Defined RTO and RPO values",
        "Confirmed production support ownership",
    }


def test_action_assignments_match_the_transcript() -> None:
    result = load_result()
    expected_assignments = {
        "Update the resilience design and deployment diagram": (
            "Alex Chen",
            date(2026, 7, 24),
            "24 July 2026",
        ),
        "Confirm the RTO and RPO values": (
            "Priya Shah",
            date(2026, 7, 25),
            "25 July 2026",
        ),
    }

    assert {item.title for item in result.action_items} == set(expected_assignments)
    for action in result.action_items:
        owner, due_date, transcript_date = expected_assignments[action.title]
        transcript_evidence = [
            item
            for item in action.evidence
            if item.source_type is EvidenceSource.MEETING_TRANSCRIPT
        ]
        assert action.owner == owner
        assert action.due_date == due_date
        assert any(
            item.speaker == owner and transcript_date in item.quote for item in transcript_evidence
        )


def test_all_assigned_owners_and_due_dates_have_transcript_support() -> None:
    result = load_result()
    review_items = [
        *result.findings,
        *result.risks,
        *result.action_items,
        *result.open_questions,
    ]

    for item in review_items:
        owner = getattr(item, "owner", None)
        due_date = getattr(item, "due_date", None)
        transcript_evidence = [
            evidence
            for evidence in item.evidence
            if evidence.source_type is EvidenceSource.MEETING_TRANSCRIPT
        ]
        if owner is not None:
            assert any(evidence.speaker == owner for evidence in transcript_evidence)
        if due_date is not None:
            transcript_date = f"{due_date.day} {due_date.strftime('%B %Y')}"
            assert any(transcript_date in evidence.quote for evidence in transcript_evidence)


def test_expected_result_json_round_trips_cleanly() -> None:
    dumped = load_result().model_dump(mode="json")
    encoded = json.dumps(dumped)
    round_tripped = GovernanceResult.model_validate(json.loads(encoded))

    assert round_tripped.model_dump(mode="json") == dumped


def test_all_evidence_quotes_and_locators_match_their_sources() -> None:
    result = load_result()
    solution_intent = SOLUTION_INTENT_PATH.read_text(encoding="utf-8")
    transcript_lines = TRANSCRIPT_PATH.read_text(encoding="utf-8").splitlines()
    headings = solution_intent_headings(solution_intent)

    for evidence in iter_evidence(result):
        if evidence.source_type is EvidenceSource.SOLUTION_INTENT:
            assert evidence.quote in solution_intent
            assert evidence.section is not None
            assert evidence.section in headings
            assert evidence.speaker is None
            assert evidence.timestamp is None
        else:
            matching_lines = [line for line in transcript_lines if evidence.quote in line]
            assert len(matching_lines) == 1
            matching_line = matching_lines[0]
            assert evidence.speaker is not None
            assert evidence.timestamp is not None
            assert f"{evidence.speaker}:" in matching_line
            assert f"[{evidence.timestamp}]" in matching_line
            assert evidence.section is None


def test_postgresql_is_a_decision_and_redis_is_only_an_open_question() -> None:
    result = load_result()
    decision_text = " ".join(item.statement.lower() for item in result.decisions)
    question_text = " ".join(item.question.lower() for item in result.open_questions)

    assert "postgresql" in decision_text
    assert "redis" not in decision_text
    assert "redis" in question_text


def test_changes_requested_is_supported_by_transcript_evidence() -> None:
    result = load_result()

    assert result.review_outcome is ReviewOutcome.CHANGES_REQUESTED
    assert any(
        item.source_type is EvidenceSource.MEETING_TRANSCRIPT
        and "changes requested" in item.quote.lower()
        for item in result.outcome_evidence
    )


def test_database_sizing_is_represented_only_as_a_risk() -> None:
    result = load_result()
    risks = " ".join(item.description.lower() for item in result.risks)
    actions = " ".join(item.title.lower() for item in result.action_items)

    assert "database sizing" in risks
    assert "august release" in risks
    assert "database sizing" not in actions


def test_ordinary_discussion_is_not_promoted_to_a_governance_item() -> None:
    result_text = json.dumps(load_result().model_dump(mode="json")).lower()

    assert "90-day retention" not in result_text
    assert "email and sms provider details" not in result_text


def test_sample_files_contain_no_obvious_sensitive_values() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in SAMPLE_PATHS)
    forbidden_patterns = {
        "URL": r"https?://|www\.",
        "email address": r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "access token": r"\b(?:sk|ghp|pat)_[A-Za-z0-9]{12,}\b",
        "assigned credential": (
            r"(?i)\b(?:api[_ -]?key|access[_ -]?token|password|client[_ -]?secret)"
            r"\b\s*[:=]"
        ),
        "private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        "cloud resource identifier": r"(?i)\barn:aws:|/subscriptions/[0-9a-f-]{36}",
    }

    for label, pattern in forbidden_patterns.items():
        assert re.search(pattern, combined, re.IGNORECASE) is None, label

    assert "ARCH-POC-1024" in combined
    assert "synthetic" in combined.lower()
