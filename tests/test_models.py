"""Tests for structured governance data models."""

from datetime import date

import pytest
from pydantic import ValidationError

from architecture_governance_copilot.models import (
    ActionItem,
    ActionPriority,
    Decision,
    EvidenceSource,
    FindingSeverity,
    FindingStatus,
    GovernanceResult,
    MissingEvidence,
    MockAdoWorkItem,
    OpenQuestion,
    ReviewFinding,
    ReviewOutcome,
    Risk,
    RiskSeverity,
    SolutionIntentReviewContext,
    SolutionIntentStatus,
    SourceEvidence,
)


def evidence_payload(**overrides: object) -> dict[str, object]:
    """Build a valid source-evidence payload with optional overrides."""
    payload: dict[str, object] = {
        "source_type": "meeting_transcript",
        "quote": "Ted will provide the updated deployment diagram by 24 July.",
        "speaker": "Steve",
        "timestamp": "10:14",
        "reference": "transcript-line-12",
    }
    payload.update(overrides)
    return payload


def context_payload(**overrides: object) -> dict[str, object]:
    """Build valid metadata for one Solution Intent review round."""
    payload: dict[str, object] = {
        "project_name": "Project Northstar",
        "si_title": "Northstar Customer Portal Solution Intent",
        "si_version": "0.4",
        "current_si_status": "under_review",
        "review_round": 1,
    }
    payload.update(overrides)
    return payload


def review_context() -> SolutionIntentReviewContext:
    """Build a valid review context model."""
    return SolutionIntentReviewContext.model_validate(context_payload())


def test_source_evidence_accepts_quote_only() -> None:
    evidence = SourceEvidence(
        source_type=EvidenceSource.MEETING_TRANSCRIPT,
        quote="The design is approved.",
    )

    assert evidence.quote == "The design is approved."
    assert evidence.speaker is None
    assert evidence.timestamp is None
    assert evidence.section is None
    assert evidence.reference is None


def test_source_evidence_accepts_solution_intent_section() -> None:
    evidence = SourceEvidence(
        source_type=EvidenceSource.SOLUTION_INTENT,
        quote="Traffic enters through Azure API Management.",
        section="Conceptual Design",
        reference="SI-4.2",
    )

    assert evidence.source_type is EvidenceSource.SOLUTION_INTENT
    assert evidence.section == "Conceptual Design"
    assert evidence.reference == "SI-4.2"


def test_source_evidence_accepts_transcript_speaker_and_timestamp() -> None:
    evidence = SourceEvidence.model_validate(evidence_payload())

    assert evidence.source_type is EvidenceSource.MEETING_TRANSCRIPT
    assert evidence.speaker == "Steve"
    assert evidence.timestamp == "10:14"
    assert evidence.reference == "transcript-line-12"


def test_source_evidence_enum_serializes_to_json_value() -> None:
    evidence = SourceEvidence(
        source_type=EvidenceSource.SOLUTION_INTENT,
        quote="The portal uses Azure API Management.",
        section="Conceptual Design",
    )

    assert evidence.model_dump(mode="json")["source_type"] == "solution_intent"


def test_source_evidence_strips_surrounding_whitespace() -> None:
    evidence = SourceEvidence(
        source_type=EvidenceSource.SOLUTION_INTENT,
        quote="  The design is approved.  ",
        speaker="  Steve ",
        timestamp=" 10:14 ",
        section=" Conceptual Design ",
        reference=" transcript-line-12 ",
    )

    assert evidence.model_dump() == {
        "source_type": EvidenceSource.SOLUTION_INTENT,
        "quote": "The design is approved.",
        "speaker": "Steve",
        "timestamp": "10:14",
        "section": "Conceptual Design",
        "reference": "transcript-line-12",
    }


def test_source_evidence_rejects_blank_quote() -> None:
    with pytest.raises(ValidationError):
        SourceEvidence(source_type=EvidenceSource.MEETING_TRANSCRIPT, quote="   ")


@pytest.mark.parametrize("field", ["speaker", "timestamp", "section", "reference"])
def test_source_evidence_rejects_blank_optional_strings(field: str) -> None:
    with pytest.raises(ValidationError):
        SourceEvidence.model_validate(
            {"source_type": "meeting_transcript", "quote": "A valid quote.", field: "   "}
        )


def test_source_evidence_rejects_unexpected_fields() -> None:
    with pytest.raises(ValidationError):
        SourceEvidence.model_validate(
            {"source_type": "meeting_transcript", "quote": "A valid quote.", "line": 12}
        )


def test_solution_intent_review_context_accepts_valid_data() -> None:
    context = SolutionIntentReviewContext.model_validate(context_payload())

    assert context.project_name == "Project Northstar"
    assert context.current_si_status is SolutionIntentStatus.UNDER_REVIEW
    assert context.review_round == 1


def test_solution_intent_review_context_accepts_optional_metadata() -> None:
    context = SolutionIntentReviewContext.model_validate(
        context_payload(
            ado_ticket_id="ADO-1042",
            domain_architect="Morgan Lee",
            review_date="2026-07-18",
        )
    )

    assert context.ado_ticket_id == "ADO-1042"
    assert context.domain_architect == "Morgan Lee"
    assert context.review_date == date(2026, 7, 18)


def test_solution_intent_review_context_accepts_round_one() -> None:
    context = SolutionIntentReviewContext.model_validate(context_payload(review_round=1))

    assert context.review_round == 1


@pytest.mark.parametrize("review_round", [0, -1])
def test_solution_intent_review_context_rejects_non_positive_round(review_round: int) -> None:
    with pytest.raises(ValidationError):
        SolutionIntentReviewContext.model_validate(context_payload(review_round=review_round))


@pytest.mark.parametrize("field", ["project_name", "si_title", "si_version"])
def test_solution_intent_review_context_rejects_blank_required_strings(field: str) -> None:
    with pytest.raises(ValidationError):
        SolutionIntentReviewContext.model_validate(context_payload(**{field: "   "}))


def test_solution_intent_review_context_serializes_date() -> None:
    context = SolutionIntentReviewContext.model_validate(
        context_payload(review_date=date(2026, 7, 18))
    )

    dumped = context.model_dump(mode="json")

    assert dumped["current_si_status"] == "under_review"
    assert dumped["review_date"] == "2026-07-18"


def test_review_finding_accepts_solution_intent_evidence() -> None:
    finding = ReviewFinding(
        title="Failover design is incomplete.",
        description="The resilience section does not define regional recovery.",
        category="Resilience",
        si_section="Resilience and Recovery",
        severity=FindingSeverity.HIGH,
        recommended_change="Document the regional failover sequence.",
        evidence=[
            SourceEvidence(
                source_type=EvidenceSource.SOLUTION_INTENT,
                quote="Regional recovery design: TBD.",
                section="Resilience and Recovery",
                reference="SI-7.3",
            )
        ],
    )

    assert finding.si_section == "Resilience and Recovery"
    assert finding.evidence[0].source_type is EvidenceSource.SOLUTION_INTENT


def test_review_finding_accepts_transcript_evidence() -> None:
    finding = ReviewFinding(
        title="Recovery objective remains unresolved.",
        description="The review did not confirm the required recovery-time objective.",
        severity=FindingSeverity.MEDIUM,
        evidence=[
            SourceEvidence(
                source_type=EvidenceSource.MEETING_TRANSCRIPT,
                quote="We still need the business to confirm the RTO.",
                speaker="Morgan",
                timestamp="10:22",
            )
        ],
    )

    assert finding.evidence[0].speaker == "Morgan"
    assert finding.evidence[0].timestamp == "10:22"


def test_review_finding_accepts_both_evidence_sources() -> None:
    finding = ReviewFinding(
        title="Authentication design needs clarification.",
        description="The SI and review discussion leave the authentication flow ambiguous.",
        severity=FindingSeverity.HIGH,
        evidence=[
            SourceEvidence(
                source_type=EvidenceSource.SOLUTION_INTENT,
                quote="Authentication flow to be confirmed.",
                section="Security",
            ),
            SourceEvidence(
                source_type=EvidenceSource.MEETING_TRANSCRIPT,
                quote="Please update the security section with the agreed flow.",
                speaker="Morgan",
                timestamp="10:31",
            ),
        ],
    )

    assert [item.source_type for item in finding.evidence] == [
        EvidenceSource.SOLUTION_INTENT,
        EvidenceSource.MEETING_TRANSCRIPT,
    ]


def test_review_finding_defaults_to_open_status() -> None:
    finding = ReviewFinding(
        title="Observability detail is missing.",
        description="Alert ownership is not specified.",
        severity=FindingSeverity.LOW,
        evidence=[SourceEvidence.model_validate(evidence_payload())],
    )

    assert finding.status is FindingStatus.OPEN


def test_review_finding_allows_missing_owner_and_due_date() -> None:
    finding = ReviewFinding(
        title="Observability detail is missing.",
        description="Alert ownership is not specified.",
        severity=FindingSeverity.LOW,
        evidence=[SourceEvidence.model_validate(evidence_payload())],
    )

    assert finding.owner is None
    assert finding.due_date is None


def test_review_finding_rejects_empty_evidence() -> None:
    with pytest.raises(ValidationError):
        ReviewFinding(
            title="Observability detail is missing.",
            description="Alert ownership is not specified.",
            severity=FindingSeverity.LOW,
            evidence=[],
        )


def test_review_finding_rejects_invalid_severity() -> None:
    with pytest.raises(ValidationError):
        ReviewFinding.model_validate(
            {
                "title": "Observability detail is missing.",
                "description": "Alert ownership is not specified.",
                "severity": "urgent",
                "evidence": [evidence_payload()],
            }
        )


def test_review_finding_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        ReviewFinding.model_validate(
            {
                "title": "Observability detail is missing.",
                "description": "Alert ownership is not specified.",
                "severity": "low",
                "status": "in_progress",
                "evidence": [evidence_payload()],
            }
        )


def test_review_finding_rejects_blank_si_section() -> None:
    with pytest.raises(ValidationError):
        ReviewFinding(
            title="Observability detail is missing.",
            description="Alert ownership is not specified.",
            si_section=" ",
            severity=FindingSeverity.LOW,
            evidence=[SourceEvidence.model_validate(evidence_payload())],
        )


def test_review_finding_serializes_enums_and_date() -> None:
    finding = ReviewFinding(
        title="Failover design is incomplete.",
        description="The resilience section does not define regional recovery.",
        severity=FindingSeverity.CRITICAL,
        status=FindingStatus.DEFERRED,
        due_date=date(2026, 7, 24),
        evidence=[
            SourceEvidence(
                source_type=EvidenceSource.SOLUTION_INTENT,
                quote="Regional recovery design: TBD.",
                section="Resilience",
            )
        ],
    )

    dumped = finding.model_dump(mode="json")

    assert dumped["severity"] == "critical"
    assert dumped["status"] == "deferred"
    assert dumped["due_date"] == "2026-07-24"
    assert dumped["evidence"][0]["source_type"] == "solution_intent"


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
        Decision(
            statement=" ",
            evidence=[
                SourceEvidence(
                    source_type=EvidenceSource.MEETING_TRANSCRIPT,
                    quote="A valid quote.",
                )
            ],
        )


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
        evidence=[
            SourceEvidence(
                source_type=EvidenceSource.MEETING_TRANSCRIPT,
                quote="Failover evidence is missing.",
            )
        ],
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
        evidence=[
            SourceEvidence(
                source_type=EvidenceSource.MEETING_TRANSCRIPT,
                quote="The recovery objective remains open.",
            )
        ],
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
        evidence=[
            SourceEvidence(
                source_type=EvidenceSource.MEETING_TRANSCRIPT,
                quote="We still need to agree the RTO.",
            )
        ],
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
        evidence=[
            SourceEvidence(
                source_type=EvidenceSource.MEETING_TRANSCRIPT,
                quote="The threat model was not attached.",
            )
        ],
    )

    assert missing.reason == "Required before production approval."
    assert len(missing.evidence) == 1


def test_missing_evidence_rejects_blank_item() -> None:
    with pytest.raises(ValidationError):
        MissingEvidence(item=" ")


def test_governance_result_accepts_not_stated_without_outcome_evidence() -> None:
    result = GovernanceResult(
        context=review_context(),
        review_outcome=ReviewOutcome.NOT_STATED,
    )

    assert result.review_outcome is ReviewOutcome.NOT_STATED
    assert result.outcome_evidence == []
    assert result.findings == []


def test_governance_result_accepts_context_and_findings() -> None:
    result = GovernanceResult(
        context=review_context(),
        review_outcome=ReviewOutcome.CHANGES_REQUESTED,
        outcome_evidence=[SourceEvidence.model_validate(evidence_payload())],
        findings=[
            ReviewFinding(
                title="Failover design is incomplete.",
                description="Regional recovery is not defined.",
                si_section="Resilience",
                severity=FindingSeverity.HIGH,
                evidence=[
                    SourceEvidence(
                        source_type=EvidenceSource.SOLUTION_INTENT,
                        quote="Regional recovery design: TBD.",
                        section="Resilience",
                    )
                ],
            )
        ],
    )

    assert result.context.review_round == 1
    assert len(result.findings) == 1
    assert result.findings[0].status is FindingStatus.OPEN


def test_governance_result_accepts_approved_with_outcome_evidence() -> None:
    result = GovernanceResult(
        context=review_context(),
        review_outcome=ReviewOutcome.APPROVED,
        outcome_evidence=[
            SourceEvidence(
                source_type=EvidenceSource.MEETING_TRANSCRIPT,
                quote="The architecture is approved.",
            )
        ],
    )

    assert result.review_outcome is ReviewOutcome.APPROVED
    assert len(result.outcome_evidence) == 1


def test_governance_result_rejects_approved_without_outcome_evidence() -> None:
    with pytest.raises(ValidationError, match="outcome_evidence is required"):
        GovernanceResult(
            context=review_context(),
            review_outcome=ReviewOutcome.APPROVED,
        )


def test_governance_result_rejects_conditional_approval_without_evidence() -> None:
    with pytest.raises(ValidationError, match="outcome_evidence is required"):
        GovernanceResult(
            context=review_context(),
            review_outcome=ReviewOutcome.CONDITIONALLY_APPROVED,
        )


def test_governance_result_rejects_changes_requested_without_evidence() -> None:
    with pytest.raises(ValidationError, match="outcome_evidence is required"):
        GovernanceResult(
            context=review_context(),
            review_outcome=ReviewOutcome.CHANGES_REQUESTED,
        )


def test_governance_result_collection_defaults_are_independent() -> None:
    first = GovernanceResult(
        context=review_context(),
        review_outcome=ReviewOutcome.NOT_STATED,
    )
    second = GovernanceResult(
        context=review_context(),
        review_outcome=ReviewOutcome.NOT_STATED,
    )

    first.decisions.append(
        Decision(
            statement="Use managed identities.",
            evidence=[
                SourceEvidence(
                    source_type=EvidenceSource.MEETING_TRANSCRIPT,
                    quote="Use managed identities.",
                )
            ],
        )
    )

    assert len(first.decisions) == 1
    assert second.decisions == []
    assert first.findings is not second.findings


def test_governance_result_nested_models_serialize_to_json_values() -> None:
    result = GovernanceResult(
        context=review_context(),
        review_outcome=ReviewOutcome.CONDITIONALLY_APPROVED,
        outcome_evidence=[
            SourceEvidence(
                source_type=EvidenceSource.MEETING_TRANSCRIPT,
                quote="Approved when evidence is supplied.",
            )
        ],
        findings=[
            ReviewFinding(
                title="Failover design is incomplete.",
                description="Regional recovery is not defined.",
                si_section="Resilience",
                severity=FindingSeverity.HIGH,
                evidence=[
                    SourceEvidence(
                        source_type=EvidenceSource.SOLUTION_INTENT,
                        quote="Regional recovery design: TBD.",
                        section="Resilience",
                    )
                ],
            )
        ],
        risks=[
            Risk(
                description="Failover evidence is missing.",
                severity=RiskSeverity.HIGH,
                evidence=[
                    SourceEvidence(
                        source_type=EvidenceSource.SOLUTION_INTENT,
                        quote="No failover test has been supplied.",
                        section="Resilience",
                    )
                ],
            )
        ],
        action_items=[
            ActionItem(
                title="Provide failover evidence.",
                due_date=date(2026, 7, 24),
                priority=ActionPriority.HIGH,
                evidence=[
                    SourceEvidence(
                        source_type=EvidenceSource.MEETING_TRANSCRIPT,
                        quote="Provide it by 24 July.",
                    )
                ],
            )
        ],
    )

    dumped = result.model_dump(mode="json")

    assert dumped["context"]["current_si_status"] == "under_review"
    assert dumped["review_outcome"] == "conditionally_approved"
    assert dumped["findings"][0]["status"] == "open"
    assert dumped["findings"][0]["evidence"][0]["source_type"] == "solution_intent"
    assert dumped["risks"][0]["severity"] == "high"
    assert dumped["action_items"][0]["due_date"] == "2026-07-24"
    assert dumped["action_items"][0]["priority"] == "high"


def test_governance_result_rejects_top_level_extra_field() -> None:
    with pytest.raises(ValidationError):
        GovernanceResult.model_validate(
            {
                "context": context_payload(),
                "review_outcome": "not_stated",
                "generated_minutes": "Not allowed.",
            }
        )


def test_governance_result_rejects_nested_extra_field() -> None:
    with pytest.raises(ValidationError):
        GovernanceResult.model_validate(
            {
                "context": context_payload(),
                "review_outcome": "not_stated",
                "decisions": [
                    {
                        "statement": "Use managed identities.",
                        "evidence": [
                            {
                                "source_type": "meeting_transcript",
                                "quote": "Use managed identities.",
                                "confidence": 0.99,
                            }
                        ],
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


def test_mock_ado_work_item_accepts_parent_and_si_section() -> None:
    work_item = MockAdoWorkItem(
        title="Provide failover evidence.",
        priority=ActionPriority.HIGH,
        description="Attach the regional failover test results.",
        source_action_index=1,
        parent_work_item_id="ADO-1042",
        si_section="Resilience and Recovery",
    )

    assert work_item.parent_work_item_id == "ADO-1042"
    assert work_item.si_section == "Resilience and Recovery"


def test_mock_ado_work_item_accepts_acceptance_criteria() -> None:
    work_item = MockAdoWorkItem(
        title="Provide failover evidence.",
        priority=ActionPriority.HIGH,
        description="Attach the regional failover test results.",
        source_action_index=1,
        acceptance_criteria=[
            "Failover steps are documented.",
            "Test results are linked from the SI.",
        ],
    )

    assert work_item.acceptance_criteria == [
        "Failover steps are documented.",
        "Test results are linked from the SI.",
    ]


def test_mock_ado_work_item_allows_empty_acceptance_criteria() -> None:
    first = MockAdoWorkItem(
        title="Provide failover evidence.",
        priority=ActionPriority.HIGH,
        description="Attach the regional failover test results.",
        source_action_index=1,
    )
    second = MockAdoWorkItem(
        title="Clarify the recovery objective.",
        priority=ActionPriority.MEDIUM,
        description="Record the agreed recovery-time objective.",
        source_action_index=2,
    )

    assert first.acceptance_criteria == []
    assert second.acceptance_criteria == []
    assert first.acceptance_criteria is not second.acceptance_criteria


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


def test_mock_ado_work_item_rejects_blank_acceptance_criterion() -> None:
    with pytest.raises(ValidationError):
        MockAdoWorkItem(
            title="Provide failover evidence.",
            priority=ActionPriority.HIGH,
            description="Attach the regional failover test results.",
            acceptance_criteria=["Failover steps are documented.", " "],
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

    dumped = work_item.model_dump(mode="json")

    assert dumped["due_date"] == "2026-07-24"
    assert dumped["priority"] == "high"


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
            SolutionIntentReviewContext,
            context_payload(ado_ticket_id=" "),
        ),
        (
            ReviewFinding,
            {
                "title": "Failover design is incomplete.",
                "description": "Regional recovery is not defined.",
                "category": " ",
                "severity": "high",
                "evidence": [evidence_payload()],
            },
        ),
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
        (
            MockAdoWorkItem,
            {
                "title": "Provide failover evidence.",
                "priority": "high",
                "description": "Attach the test results.",
                "parent_work_item_id": " ",
                "source_action_index": 0,
            },
        ),
    ],
)
def test_models_reject_blank_optional_strings(
    model: type[
        Decision
        | Risk
        | ActionItem
        | OpenQuestion
        | MissingEvidence
        | SolutionIntentReviewContext
        | ReviewFinding
        | MockAdoWorkItem
    ],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload)
