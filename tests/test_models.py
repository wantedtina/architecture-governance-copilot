"""Tests for structured governance data models."""

from datetime import date

import pytest
from pydantic import ValidationError

from architecture_governance_copilot.models import (
    ActionItem,
    ActionPriority,
    Decision,
    GovernanceResult,
    MissingEvidence,
    MockAdoWorkItem,
    OpenQuestion,
    ReviewOutcome,
    Risk,
    RiskSeverity,
    SourceEvidence,
)


def evidence_payload(**overrides: object) -> dict[str, object]:
    """Build a valid source-evidence payload with optional overrides."""
    payload: dict[str, object] = {
        "quote": "Ted will provide the updated deployment diagram by 24 July.",
        "speaker": "Steve",
        "timestamp": "10:14",
        "reference": "transcript-line-12",
    }
    payload.update(overrides)
    return payload


def test_source_evidence_accepts_quote_only() -> None:
    evidence = SourceEvidence(quote="The design is approved.")

    assert evidence.quote == "The design is approved."
    assert evidence.speaker is None
    assert evidence.timestamp is None
    assert evidence.reference is None


def test_source_evidence_accepts_all_source_details() -> None:
    evidence = SourceEvidence.model_validate(evidence_payload())

    assert evidence.speaker == "Steve"
    assert evidence.timestamp == "10:14"
    assert evidence.reference == "transcript-line-12"


def test_source_evidence_strips_surrounding_whitespace() -> None:
    evidence = SourceEvidence(
        quote="  The design is approved.  ",
        speaker="  Steve ",
        timestamp=" 10:14 ",
        reference=" transcript-line-12 ",
    )

    assert evidence.model_dump() == {
        "quote": "The design is approved.",
        "speaker": "Steve",
        "timestamp": "10:14",
        "reference": "transcript-line-12",
    }


def test_source_evidence_rejects_blank_quote() -> None:
    with pytest.raises(ValidationError):
        SourceEvidence(quote="   ")


@pytest.mark.parametrize("field", ["speaker", "timestamp", "reference"])
def test_source_evidence_rejects_blank_optional_strings(field: str) -> None:
    with pytest.raises(ValidationError):
        SourceEvidence.model_validate({"quote": "A valid quote.", field: "   "})


def test_source_evidence_rejects_unexpected_fields() -> None:
    with pytest.raises(ValidationError):
        SourceEvidence.model_validate({"quote": "A valid quote.", "line": 12})


def test_decision_accepts_valid_data() -> None:
    decision = Decision(
        statement="Use managed identities.",
        rationale="Avoid stored service credentials.",
        evidence=[SourceEvidence.model_validate(evidence_payload())],
    )

    assert decision.statement == "Use managed identities."
    assert decision.rationale == "Avoid stored service credentials."
    assert len(decision.evidence) == 1


def test_decision_rejects_empty_evidence() -> None:
    with pytest.raises(ValidationError):
        Decision(statement="Use managed identities.", evidence=[])


def test_decision_rejects_blank_statement() -> None:
    with pytest.raises(ValidationError):
        Decision(statement=" ", evidence=[SourceEvidence(quote="A valid quote.")])


def test_risk_accepts_valid_data() -> None:
    risk = Risk(
        description="Regional failover has not been demonstrated.",
        severity=RiskSeverity.HIGH,
        owner="Ted",
        evidence=[SourceEvidence.model_validate(evidence_payload())],
    )

    assert risk.severity is RiskSeverity.HIGH
    assert risk.owner == "Ted"


def test_risk_enum_serializes_to_string_value() -> None:
    risk = Risk(
        description="Regional failover has not been demonstrated.",
        severity=RiskSeverity.CRITICAL,
        evidence=[SourceEvidence(quote="Failover evidence is missing.")],
    )

    assert risk.model_dump(mode="json")["severity"] == "critical"


def test_risk_rejects_invalid_severity() -> None:
    with pytest.raises(ValidationError):
        Risk.model_validate(
            {
                "description": "Regional failover has not been demonstrated.",
                "severity": "urgent",
                "evidence": [evidence_payload()],
            }
        )


def test_risk_rejects_empty_evidence() -> None:
    with pytest.raises(ValidationError):
        Risk(
            description="Regional failover has not been demonstrated.",
            severity=RiskSeverity.HIGH,
            evidence=[],
        )


def test_action_item_accepts_owner_and_due_date() -> None:
    action = ActionItem(
        title="Provide the updated deployment diagram.",
        owner="Ted",
        due_date=date(2026, 7, 24),
        priority=ActionPriority.HIGH,
        evidence=[SourceEvidence.model_validate(evidence_payload())],
    )

    assert action.owner == "Ted"
    assert action.due_date == date(2026, 7, 24)
    assert action.priority is ActionPriority.HIGH


def test_action_item_accepts_missing_owner_and_due_date() -> None:
    action = ActionItem(
        title="Clarify the recovery objective.",
        priority=ActionPriority.MEDIUM,
        evidence=[SourceEvidence(quote="The recovery objective remains open.")],
    )

    assert action.owner is None
    assert action.due_date is None


def test_action_item_parses_iso_date_string() -> None:
    action = ActionItem.model_validate(
        {
            "title": "Provide the updated deployment diagram.",
            "due_date": "2026-07-24",
            "priority": "high",
            "evidence": [evidence_payload()],
        }
    )

    assert action.due_date == date(2026, 7, 24)


def test_action_item_rejects_invalid_date() -> None:
    with pytest.raises(ValidationError):
        ActionItem.model_validate(
            {
                "title": "Provide the updated deployment diagram.",
                "due_date": "24 July 2026",
                "priority": "high",
                "evidence": [evidence_payload()],
            }
        )


def test_action_item_rejects_invalid_priority() -> None:
    with pytest.raises(ValidationError):
        ActionItem.model_validate(
            {
                "title": "Provide the updated deployment diagram.",
                "priority": "urgent",
                "evidence": [evidence_payload()],
            }
        )


def test_action_item_rejects_empty_evidence() -> None:
    with pytest.raises(ValidationError):
        ActionItem(
            title="Provide the updated deployment diagram.",
            priority=ActionPriority.HIGH,
            evidence=[],
        )


def test_open_question_accepts_valid_data() -> None:
    question = OpenQuestion(
        question="What recovery-time objective is required?",
        owner="Ava",
        evidence=[SourceEvidence(quote="We still need to agree the RTO.")],
    )

    assert question.question == "What recovery-time objective is required?"
    assert question.owner == "Ava"


def test_open_question_rejects_empty_evidence() -> None:
    with pytest.raises(ValidationError):
        OpenQuestion(question="What recovery-time objective is required?", evidence=[])


def test_missing_evidence_accepts_item_without_evidence() -> None:
    missing = MissingEvidence(item="Threat model")

    assert missing.reason is None
    assert missing.evidence == []


def test_missing_evidence_accepts_item_with_evidence() -> None:
    missing = MissingEvidence(
        item="Threat model",
        reason="Required before production approval.",
        evidence=[SourceEvidence(quote="The threat model was not attached.")],
    )

    assert missing.reason == "Required before production approval."
    assert len(missing.evidence) == 1


def test_missing_evidence_rejects_blank_item() -> None:
    with pytest.raises(ValidationError):
        MissingEvidence(item=" ")


def test_governance_result_accepts_not_stated_without_outcome_evidence() -> None:
    result = GovernanceResult(review_outcome=ReviewOutcome.NOT_STATED)

    assert result.review_outcome is ReviewOutcome.NOT_STATED
    assert result.outcome_evidence == []


def test_governance_result_accepts_approved_with_outcome_evidence() -> None:
    result = GovernanceResult(
        review_outcome=ReviewOutcome.APPROVED,
        outcome_evidence=[SourceEvidence(quote="The architecture is approved.")],
    )

    assert result.review_outcome is ReviewOutcome.APPROVED
    assert len(result.outcome_evidence) == 1


def test_governance_result_rejects_approved_without_outcome_evidence() -> None:
    with pytest.raises(ValidationError, match="outcome_evidence is required"):
        GovernanceResult(review_outcome=ReviewOutcome.APPROVED)


def test_governance_result_rejects_conditional_approval_without_evidence() -> None:
    with pytest.raises(ValidationError, match="outcome_evidence is required"):
        GovernanceResult(review_outcome=ReviewOutcome.CONDITIONALLY_APPROVED)


def test_governance_result_collection_defaults_are_independent() -> None:
    first = GovernanceResult(review_outcome=ReviewOutcome.NOT_STATED)
    second = GovernanceResult(review_outcome=ReviewOutcome.NOT_STATED)

    first.decisions.append(
        Decision(
            statement="Use managed identities.",
            evidence=[SourceEvidence(quote="Use managed identities.")],
        )
    )

    assert len(first.decisions) == 1
    assert second.decisions == []


def test_governance_result_nested_models_serialize_to_json_values() -> None:
    result = GovernanceResult(
        review_outcome=ReviewOutcome.CONDITIONALLY_APPROVED,
        outcome_evidence=[SourceEvidence(quote="Approved when evidence is supplied.")],
        risks=[
            Risk(
                description="Failover evidence is missing.",
                severity=RiskSeverity.HIGH,
                evidence=[SourceEvidence(quote="No failover test has been supplied.")],
            )
        ],
        action_items=[
            ActionItem(
                title="Provide failover evidence.",
                due_date=date(2026, 7, 24),
                priority=ActionPriority.HIGH,
                evidence=[SourceEvidence(quote="Provide it by 24 July.")],
            )
        ],
    )

    dumped = result.model_dump(mode="json")

    assert dumped["review_outcome"] == "conditionally_approved"
    assert dumped["risks"][0]["severity"] == "high"
    assert dumped["action_items"][0]["due_date"] == "2026-07-24"
    assert dumped["action_items"][0]["priority"] == "high"


def test_governance_result_rejects_top_level_extra_field() -> None:
    with pytest.raises(ValidationError):
        GovernanceResult.model_validate(
            {"review_outcome": "not_stated", "generated_minutes": "Not allowed."}
        )


def test_governance_result_rejects_nested_extra_field() -> None:
    with pytest.raises(ValidationError):
        GovernanceResult.model_validate(
            {
                "review_outcome": "not_stated",
                "decisions": [
                    {
                        "statement": "Use managed identities.",
                        "evidence": [{"quote": "Use managed identities.", "confidence": 0.99}],
                    }
                ],
            }
        )


def test_mock_ado_work_item_accepts_valid_data() -> None:
    work_item = MockAdoWorkItem(
        title="Provide failover evidence.",
        priority=ActionPriority.HIGH,
        description="Attach the regional failover test results.",
        tags=["Architecture Governance", "Hackathon PoC"],
        source_action_index=0,
    )

    assert work_item.title == "Provide failover evidence."
    assert work_item.source_action_index == 0


def test_mock_ado_work_item_accepts_assignee_and_due_date() -> None:
    work_item = MockAdoWorkItem(
        title="Provide failover evidence.",
        assigned_to="Ted",
        due_date=date(2026, 7, 24),
        priority=ActionPriority.HIGH,
        description="Attach the regional failover test results.",
        source_action_index=1,
    )

    assert work_item.assigned_to == "Ted"
    assert work_item.due_date == date(2026, 7, 24)


def test_mock_ado_work_item_rejects_negative_source_action_index() -> None:
    with pytest.raises(ValidationError):
        MockAdoWorkItem(
            title="Provide failover evidence.",
            priority=ActionPriority.HIGH,
            description="Attach the regional failover test results.",
            source_action_index=-1,
        )


def test_mock_ado_work_item_rejects_blank_description() -> None:
    with pytest.raises(ValidationError):
        MockAdoWorkItem(
            title="Provide failover evidence.",
            priority=ActionPriority.HIGH,
            description=" ",
            source_action_index=0,
        )


def test_mock_ado_work_item_rejects_blank_tag() -> None:
    with pytest.raises(ValidationError):
        MockAdoWorkItem(
            title="Provide failover evidence.",
            priority=ActionPriority.HIGH,
            description="Attach the regional failover test results.",
            tags=["Architecture Governance", " "],
            source_action_index=0,
        )


def test_mock_ado_work_item_serializes_date_to_iso_string() -> None:
    work_item = MockAdoWorkItem(
        title="Provide failover evidence.",
        due_date=date(2026, 7, 24),
        priority=ActionPriority.HIGH,
        description="Attach the regional failover test results.",
        source_action_index=0,
    )

    assert work_item.model_dump(mode="json")["due_date"] == "2026-07-24"


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (
            Decision,
            {
                "statement": "Use managed identities.",
                "rationale": " ",
                "evidence": [evidence_payload()],
            },
        ),
        (
            Risk,
            {
                "description": "Failover evidence is missing.",
                "severity": "high",
                "owner": " ",
                "evidence": [evidence_payload()],
            },
        ),
        (
            ActionItem,
            {
                "title": "Provide failover evidence.",
                "owner": " ",
                "priority": "high",
                "evidence": [evidence_payload()],
            },
        ),
        (
            OpenQuestion,
            {
                "question": "What is the recovery objective?",
                "owner": " ",
                "evidence": [evidence_payload()],
            },
        ),
        (MissingEvidence, {"item": "Threat model", "reason": " "}),
        (
            MockAdoWorkItem,
            {
                "title": "Provide failover evidence.",
                "assigned_to": " ",
                "priority": "high",
                "description": "Attach the test results.",
                "source_action_index": 0,
            },
        ),
    ],
)
def test_models_reject_blank_optional_strings(
    model: type[Decision | Risk | ActionItem | OpenQuestion | MissingEvidence | MockAdoWorkItem],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload)
