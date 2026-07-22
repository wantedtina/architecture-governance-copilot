"""Tests for deterministic mock Azure DevOps work-item generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from architecture_governance_copilot.ado_generator import generate_mock_ado_work_items
from architecture_governance_copilot.models import (
    ActionItem,
    ActionPriority,
    EvidenceSource,
    FindingSeverity,
    GovernanceResult,
    MissingEvidence,
    MockAdoWorkItem,
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
        "ado_ticket_id": "ARCH-42",
    }
    values.update(overrides)
    return SolutionIntentReviewContext.model_validate(values)


def _transcript_evidence(
    quote: str = "Morgan will document the failover design.",
) -> SourceEvidence:
    return SourceEvidence(
        source_type=EvidenceSource.MEETING_TRANSCRIPT,
        quote=quote,
        speaker="Morgan Lee",
        timestamp="11:05",
        reference="transcript-line-5",
    )


def _solution_intent_evidence(
    section: str | None = "Availability and Resilience",
) -> SourceEvidence:
    return SourceEvidence(
        source_type=EvidenceSource.SOLUTION_INTENT,
        quote="The failover design is pending.",
        section=section,
        reference="SI-7-FAILOVER",
    )


def _result_with_actions(
    actions: list[ActionItem],
    **overrides: object,
) -> GovernanceResult:
    values: dict[str, object] = {
        "context": _context(),
        "review_outcome": ReviewOutcome.CHANGES_REQUESTED,
        "outcome_evidence": [_transcript_evidence("Changes are requested.")],
        "action_items": actions,
    }
    values.update(overrides)
    return GovernanceResult.model_validate(values)


def test_sample_actions_map_to_exactly_two_ordered_work_items(
    sample_result: GovernanceResult,
) -> None:
    items = generate_mock_ado_work_items(sample_result)

    assert len(items) == 2
    assert [item.source_action_index for item in items] == [0, 1]
    assert [item.title for item in items] == [
        "Update the resilience design and deployment diagram",
        "Confirm the RTO and RPO values",
    ]
    assert [item.assigned_to for item in items] == ["Alex Chen", "Priya Shah"]
    assert [item.due_date.isoformat() for item in items if item.due_date] == [
        "2026-07-24",
        "2026-07-25",
    ]
    assert [item.priority for item in items] == [
        sample_result.action_items[0].priority,
        sample_result.action_items[1].priority,
    ]


def test_sample_work_items_have_parent_and_stable_tags(
    sample_result: GovernanceResult,
) -> None:
    items = generate_mock_ado_work_items(sample_result)
    expected_tags = [
        "Architecture Governance",
        "Solution Intent",
        "Review Round 2",
        "Changes Requested",
    ]

    assert all(item.parent_work_item_id == "ARCH-POC-1024" for item in items)
    assert all(item.tags == expected_tags for item in items)
    assert all(item.acceptance_criteria == [] for item in items)
    assert all(item.tags is not expected_tags for item in items)
    assert all(item.tags for item in items)


def test_sample_descriptions_contain_context_and_action_evidence(
    sample_result: GovernanceResult,
) -> None:
    items = generate_mock_ado_work_items(sample_result)

    for action, item in zip(sample_result.action_items, items, strict=True):
        assert "Architecture Governance action" in item.description
        assert "Project: Digital Payment Notification Service" in item.description
        assert (
            "Solution Intent: Solution Intent - Digital Payment Notification Service"
            in item.description
        )
        assert "SI Version: 1.2" in item.description
        assert "Review Round: 2" in item.description
        assert "Review Outcome: Changes Requested" in item.description
        assert f"Action:\n{action.title}" in item.description
        assert f"Owner: {action.owner}" in item.description
        assert f"Due Date: {action.due_date.isoformat()}" in item.description
        assert "Priority: High" in item.description
        for evidence in action.evidence:
            assert evidence.quote in item.description
        assert "No real Azure DevOps work item has been created." in item.description


def test_missing_optional_action_fields_remain_missing() -> None:
    action = ActionItem(
        title="Document the failover design.",
        priority=ActionPriority.MEDIUM,
        evidence=[_transcript_evidence()],
    )
    result = _result_with_actions(
        [action],
        context=_context(ado_ticket_id=None),
    )

    item = generate_mock_ado_work_items(result)[0]

    assert item.assigned_to is None
    assert item.due_date is None
    assert item.parent_work_item_id is None
    assert item.si_section is None
    assert "Owner: Unassigned" in item.description
    assert "Due Date: Not specified" in item.description


def test_direct_solution_intent_evidence_supplies_si_section() -> None:
    action = ActionItem(
        title="Document the failover design.",
        priority=ActionPriority.HIGH,
        evidence=[
            _transcript_evidence(),
            _solution_intent_evidence("Availability and Resilience"),
        ],
    )

    item = generate_mock_ado_work_items(_result_with_actions([action]))[0]

    assert item.si_section == "Availability and Resilience"


def test_first_direct_solution_intent_section_is_used() -> None:
    action = ActionItem(
        title="Document the failover design.",
        priority=ActionPriority.HIGH,
        evidence=[
            _solution_intent_evidence("Availability and Resilience"),
            _solution_intent_evidence("Deployment Design"),
        ],
    )

    item = generate_mock_ado_work_items(_result_with_actions([action]))[0]

    assert item.si_section == "Availability and Resilience"


def test_first_direct_solution_intent_without_section_does_not_use_later_section() -> None:
    action = ActionItem(
        title="Document the failover design.",
        priority=ActionPriority.HIGH,
        evidence=[
            _solution_intent_evidence(None),
            _solution_intent_evidence("Deployment Design"),
        ],
    )

    item = generate_mock_ado_work_items(_result_with_actions([action]))[0]

    assert item.si_section is None


def test_transcript_evidence_does_not_supply_si_section() -> None:
    action = ActionItem(
        title="Document the failover design.",
        priority=ActionPriority.HIGH,
        evidence=[_transcript_evidence()],
    )

    item = generate_mock_ado_work_items(_result_with_actions([action]))[0]

    assert item.si_section is None


def test_related_finding_does_not_infer_action_si_section() -> None:
    evidence = _transcript_evidence()
    action = ActionItem(
        title="Document the failover design.",
        priority=ActionPriority.HIGH,
        evidence=[evidence],
    )
    finding = ReviewFinding(
        title="Failover design is incomplete.",
        description="The failure path is missing.",
        si_section="Availability and Resilience",
        severity=FindingSeverity.HIGH,
        evidence=[evidence],
    )
    result = _result_with_actions([action], findings=[finding])

    item = generate_mock_ado_work_items(result)[0]

    assert item.si_section is None


def test_no_actions_returns_empty_list_even_with_other_review_items() -> None:
    evidence = _transcript_evidence()
    result = _result_with_actions(
        [],
        findings=[
            ReviewFinding(
                title="Failover design is incomplete.",
                description="The failure path is missing.",
                severity=FindingSeverity.HIGH,
                evidence=[evidence],
            )
        ],
        risks=[
            Risk(
                description="The release could be delayed.",
                severity=RiskSeverity.HIGH,
                evidence=[evidence],
            )
        ],
        missing_evidence=[MissingEvidence(item="Recovery test results")],
    )

    assert generate_mock_ado_work_items(result) == []


def test_work_items_serialize_to_json_compatible_values(
    sample_result: GovernanceResult,
) -> None:
    items = generate_mock_ado_work_items(sample_result)
    serialized = [item.model_dump(mode="json") for item in items]

    assert all(isinstance(item, MockAdoWorkItem) for item in items)
    assert serialized[0]["due_date"] == "2026-07-24"
    assert serialized[1]["due_date"] == "2026-07-25"
    assert serialized[0]["priority"] == "high"
    assert json.loads(json.dumps(serialized)) == serialized


def test_repeated_calls_return_independent_work_items_without_mutating_source(
    sample_result: GovernanceResult,
) -> None:
    source_before = sample_result.model_dump(mode="json")
    first = generate_mock_ado_work_items(sample_result)
    second = generate_mock_ado_work_items(sample_result)

    assert first == second
    assert first is not second
    assert first[0] is not second[0]
    assert first[0].tags is not second[0].tags
    assert first[0].acceptance_criteria is not second[0].acceptance_criteria

    first[0].title = "Edited generated title"
    first[0].tags.append("Edited tag")
    first.pop()
    later = generate_mock_ado_work_items(sample_result)

    assert second == later
    assert later[0].title == sample_result.action_items[0].title
    assert "Edited tag" not in later[0].tags
    assert sample_result.model_dump(mode="json") == source_before


def test_acceptance_criteria_are_not_inferred_from_action_text() -> None:
    action = ActionItem(
        title="Document the failover design and prove recovery succeeds.",
        priority=ActionPriority.HIGH,
        evidence=[_transcript_evidence()],
    )

    item = generate_mock_ado_work_items(_result_with_actions([action]))[0]

    assert item.acceptance_criteria == []
