"""Mock Azure DevOps work-item payload generation."""

from __future__ import annotations

from architecture_governance_copilot.models import (
    ActionItem,
    EvidenceSource,
    GovernanceResult,
    MockAdoWorkItem,
    SourceEvidence,
)


def generate_mock_ado_work_items(
    result: GovernanceResult,
) -> list[MockAdoWorkItem]:
    """Generate typed mock ADO work items for the supplied review actions."""
    outcome_label = _humanize(result.review_outcome)
    tags = [
        "Architecture Governance",
        "Solution Intent",
        f"Review Round {result.context.review_round}",
        outcome_label,
    ]

    return [
        MockAdoWorkItem(
            title=action.title,
            assigned_to=action.owner,
            due_date=action.due_date,
            priority=action.priority,
            description=_build_description(result, action),
            tags=list(tags),
            source_action_index=index,
            parent_work_item_id=result.context.ado_ticket_id,
            si_section=_first_solution_intent_section(action),
            acceptance_criteria=[],
        )
        for index, action in enumerate(result.action_items)
    ]


def _build_description(result: GovernanceResult, action: ActionItem) -> str:
    context = result.context
    lines = [
        "Architecture Governance action generated from a Solution Intent review.",
        "",
        f"Project: {context.project_name}",
        f"Solution Intent: {context.si_title}",
        f"SI Version: {context.si_version}",
        f"Review Round: {context.review_round}",
        f"Review Outcome: {_humanize(result.review_outcome)}",
        "",
        "Action:",
        action.title,
        "",
        f"Owner: {action.owner or 'Unassigned'}",
        f"Due Date: {action.due_date.isoformat() if action.due_date else 'Not specified'}",
        f"Priority: {_humanize(action.priority)}",
        "",
        "Supporting Evidence:",
    ]
    lines.extend(f"- {_format_evidence(evidence)}" for evidence in action.evidence)
    lines.extend(
        [
            "",
            "No real Azure DevOps work item has been created.",
        ]
    )
    return "\n".join(lines)


def _first_solution_intent_section(action: ActionItem) -> str | None:
    first_solution_intent_evidence = next(
        (
            evidence
            for evidence in action.evidence
            if evidence.source_type is EvidenceSource.SOLUTION_INTENT
        ),
        None,
    )
    return (
        first_solution_intent_evidence.section
        if first_solution_intent_evidence is not None
        else None
    )


def _format_evidence(evidence: SourceEvidence) -> str:
    metadata = [_humanize(evidence.source_type)]
    if evidence.source_type is EvidenceSource.SOLUTION_INTENT:
        if evidence.section is not None:
            metadata.append(evidence.section)
    else:
        if evidence.timestamp is not None:
            metadata.append(evidence.timestamp)
        if evidence.speaker is not None:
            metadata.append(evidence.speaker)
    if evidence.reference is not None:
        metadata.append(f"Reference: {evidence.reference}")
    locator = " | ".join(_escape_evidence_metadata(item) for item in metadata)
    return f'[{locator}] "{evidence.quote}"'


def _humanize(value: str) -> str:
    return value.replace("_", " ").title()


def _escape_evidence_metadata(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("]", "\\]")
