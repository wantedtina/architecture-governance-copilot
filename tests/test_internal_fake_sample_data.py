"""Consistency tests for the realistic Internal fake review package."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from pathlib import Path

from architecture_governance_copilot.evidence_validation import validate_governance_evidence
from architecture_governance_copilot.integrations.confluence import canonicalize_confluence_body
from architecture_governance_copilot.models import (
    EvidenceSource,
    GovernanceResult,
    SolutionIntentReviewContext,
    SourceEvidence,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SAMPLES = REPOSITORY_ROOT / "samples"
SOLUTION_INTENT_PATH = SAMPLES / "internal_fake_solution_intent.md"
TRANSCRIPT_PATH = SAMPLES / "internal_fake_review_transcript.txt"
METADATA_PATH = SAMPLES / "internal_fake_review_metadata.json"
RESULT_PATH = SAMPLES / "internal_fake_aif_result.json"
CONFLUENCE_PATH = SAMPLES / "internal_fake_confluence_page.json"
PRIMARY_PATHS = (
    SOLUTION_INTENT_PATH,
    TRANSCRIPT_PATH,
    METADATA_PATH,
    RESULT_PATH,
    CONFLUENCE_PATH,
)


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _load_context() -> SolutionIntentReviewContext:
    return SolutionIntentReviewContext.model_validate(_load_json(METADATA_PATH))


def _load_result() -> GovernanceResult:
    return GovernanceResult.model_validate(_load_json(RESULT_PATH))


def _iter_evidence(result: GovernanceResult) -> Iterator[SourceEvidence]:
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


def test_primary_internal_fake_files_exist_and_parse() -> None:
    assert all(
        path.is_file() and path.read_text(encoding="utf-8").strip() for path in PRIMARY_PATHS
    )
    assert _load_json(METADATA_PATH)
    assert _load_json(RESULT_PATH)
    assert _load_json(CONFLUENCE_PATH)


def test_primary_internal_fake_scenario_has_approved_depth_and_roles() -> None:
    solution_intent = SOLUTION_INTENT_PATH.read_text(encoding="utf-8")
    transcript_lines = TRANSCRIPT_PATH.read_text(encoding="utf-8").splitlines()
    speakers = {
        match.group(1)
        for line in transcript_lines
        if (match := re.fullmatch(r"\[\d{2}:\d{2}\] ([^:]+): .+", line))
    }

    assert 900 <= len(solution_intent.split()) <= 1_300
    assert 24 <= len(transcript_lines) <= 32
    assert speakers == {"Morgan Lee", "Casey Wong", "Avery Patel", "Riley Chen"}
    assert all(re.fullmatch(r"\[\d{2}:\d{2}\] [^:]+: .+", line) for line in transcript_lines)


def test_primary_internal_fake_identity_versions_and_counts_are_synchronized() -> None:
    context = _load_context()
    result = _load_result()
    page = _load_json(CONFLUENCE_PATH)

    assert result.context == context
    assert context.project_name == "Synthetic Order Routing Service"
    assert context.si_version == "0.8"
    assert page["id"] == "synthetic-page-204"
    assert page["title"] == context.si_title
    assert page["version"] == {
        "number": 8,
        "message": "Expanded synthetic architecture review snapshot",
        "by": {"displayName": "Synthetic User"},
    }
    assert len(result.findings) == 3
    assert len(result.decisions) == 1
    assert len(result.risks) == 1
    assert len(result.action_items) == 2
    assert len(result.open_questions) == 1
    assert len(result.missing_evidence) == 2


def test_fake_confluence_storage_canonicalizes_to_exact_markdown_snapshot() -> None:
    page = _load_json(CONFLUENCE_PATH)
    body = page["body"]
    assert isinstance(body, dict)
    storage = body["storage"]
    assert isinstance(storage, dict)
    raw_body = storage["value"]
    assert isinstance(raw_body, str)

    canonical = canonicalize_confluence_body(raw_body, "storage")

    assert canonical == SOLUTION_INTENT_PATH.read_text(encoding="utf-8").strip()


def test_primary_internal_fake_evidence_and_assignments_are_grounded() -> None:
    solution_intent = SOLUTION_INTENT_PATH.read_text(encoding="utf-8")
    transcript = TRANSCRIPT_PATH.read_text(encoding="utf-8")
    result = _load_result()

    validate_governance_evidence(result, solution_intent, transcript)
    for evidence in _iter_evidence(result):
        if evidence.source_type is EvidenceSource.SOLUTION_INTENT:
            assert evidence.quote in solution_intent
            assert evidence.section is not None
        else:
            matching_lines = [line for line in transcript.splitlines() if evidence.quote in line]
            assert len(matching_lines) == 1
            assert evidence.speaker is not None
            assert evidence.timestamp is not None
            assert f"[{evidence.timestamp}] {evidence.speaker}:" in matching_lines[0]

    for action in result.action_items:
        assert action.owner is not None
        assert action.due_date is not None
        date_text = f"{action.due_date.day} {action.due_date.strftime('%B %Y')}"
        assert any(
            evidence.source_type is EvidenceSource.MEETING_TRANSCRIPT
            and evidence.speaker == action.owner
            and date_text in evidence.quote
            for evidence in action.evidence
        )


def test_ordinary_discussion_is_not_promoted_to_primary_governance_items() -> None:
    result_text = RESULT_PATH.read_text(encoding="utf-8").lower()

    assert "dashboard color" not in result_text
    assert "90-day aggregate trend" not in result_text


def test_primary_internal_fake_package_is_explicitly_synthetic_and_safe() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in PRIMARY_PATHS)
    page = _load_json(CONFLUENCE_PATH)
    links = page["_links"]
    assert isinstance(links, dict)

    assert "synthetic" in combined.lower()
    assert "no network requests" in combined.lower()
    absolute_urls = [str(value) for value in links.values() if str(value).startswith("http")]
    assert absolute_urls
    assert all("example.invalid" in value for value in absolute_urls)
    assert re.search(r"\b(?:sk|ghp|pat)_[A-Za-z0-9]{12,}\b", combined) is None
    assert "-----BEGIN" not in combined
