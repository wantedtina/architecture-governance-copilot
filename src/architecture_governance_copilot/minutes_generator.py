"""Standardized architecture governance meeting-minutes generation."""

from __future__ import annotations

from datetime import date

from architecture_governance_copilot.models import (
    EvidenceSource,
    GovernanceResult,
    SourceEvidence,
)

_NOT_PROVIDED = "Not provided"
_NONE_RECORDED = "None recorded."


def generate_review_minutes(result: GovernanceResult) -> str:
    """Generate deterministic Markdown minutes from a validated review result."""
    context = result.context
    lines = [
        "# Solution Intent Review Record",
        "",
        "## Review Context",
        "",
        f"- **Project:** {context.project_name}",
        f"- **Solution Intent:** {context.si_title}",
        f"- **SI Version:** {context.si_version}",
        f"- **SI Status Before Review:** {_humanize(context.current_si_status)}",
        f"- **Review Round:** {context.review_round}",
        f"- **Review Date:** {_format_optional_date(context.review_date, _NOT_PROVIDED)}",
        f"- **Domain Architect:** {context.domain_architect or _NOT_PROVIDED}",
        f"- **ADO Governance Ticket:** {context.ado_ticket_id or _NOT_PROVIDED}",
        "",
        "## Review Outcome",
        "",
        f"**Outcome:** {_humanize(result.review_outcome)}",
        "",
        "**Supporting Evidence:**",
    ]
    _append_evidence(lines, result.outcome_evidence)

    lines.extend(["", "## Confirmed Decisions", ""])
    if not result.decisions:
        lines.append(_NONE_RECORDED)
    for index, decision in enumerate(result.decisions, start=1):
        lines.append(f"{index}. **{decision.statement}**")
        if decision.rationale is not None:
            lines.append(f"   - **Rationale:** {decision.rationale}")
        _append_item_evidence(lines, decision.evidence)

    lines.extend(["", "## Review Findings", ""])
    if not result.findings:
        lines.append(_NONE_RECORDED)
    for index, finding in enumerate(result.findings, start=1):
        lines.extend(
            [
                f"{index}. **{finding.title}**",
                f"   - **Description:** {finding.description}",
            ]
        )
        _append_optional_field(lines, "Category", finding.category)
        _append_optional_field(lines, "SI Section", finding.si_section)
        lines.extend(
            [
                f"   - **Severity:** {_humanize(finding.severity)}",
                f"   - **Status:** {_humanize(finding.status)}",
            ]
        )
        _append_optional_field(lines, "Recommended Change", finding.recommended_change)
        _append_optional_field(lines, "Owner", finding.owner)
        if finding.due_date is not None:
            lines.append(f"   - **Due Date:** {finding.due_date.isoformat()}")
        _append_item_evidence(lines, finding.evidence)

    lines.extend(["", "## Risks", ""])
    if not result.risks:
        lines.append(_NONE_RECORDED)
    for index, risk in enumerate(result.risks, start=1):
        lines.extend(
            [
                f"{index}. **{risk.description}**",
                f"   - **Severity:** {_humanize(risk.severity)}",
            ]
        )
        _append_optional_field(lines, "Owner", risk.owner)
        _append_item_evidence(lines, risk.evidence)

    lines.extend(["", "## Action Items", ""])
    if not result.action_items:
        lines.append(_NONE_RECORDED)
    for index, action in enumerate(result.action_items, start=1):
        lines.extend(
            [
                f"{index}. **{action.title}**",
                f"   - **Owner:** {action.owner or 'Unassigned'}",
                f"   - **Due Date:** {_format_optional_date(action.due_date, 'Not specified')}",
                f"   - **Priority:** {_humanize(action.priority)}",
            ]
        )
        _append_item_evidence(lines, action.evidence)

    lines.extend(["", "## Open Questions", ""])
    if not result.open_questions:
        lines.append(_NONE_RECORDED)
    for index, question in enumerate(result.open_questions, start=1):
        lines.append(f"{index}. **{question.question}**")
        _append_optional_field(lines, "Owner", question.owner)
        _append_item_evidence(lines, question.evidence)

    lines.extend(["", "## Missing Governance Information", ""])
    if not result.missing_evidence:
        lines.append(_NONE_RECORDED)
    for index, missing in enumerate(result.missing_evidence, start=1):
        lines.append(f"{index}. **{missing.item}**")
        _append_optional_field(lines, "Reason", missing.reason)
        if missing.evidence:
            _append_item_evidence(lines, missing.evidence)

    lines.extend(
        [
            "",
            "## Governance Note",
            "",
            (
                "This record was generated from structured review information. "
                "The Domain Architect remains responsible for the formal governance decision. "
                "Review this generated record before publication."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _humanize(value: str) -> str:
    return value.replace("_", " ").title()


def _format_optional_date(value: date | None, fallback: str) -> str:
    return value.isoformat() if value is not None else fallback


def _append_optional_field(lines: list[str], label: str, value: str | None) -> None:
    if value is not None:
        lines.append(f"   - **{label}:** {value}")


def _append_evidence(lines: list[str], evidence_items: list[SourceEvidence]) -> None:
    if not evidence_items:
        lines.append(_NONE_RECORDED)
        return
    lines.extend(f"- {_format_evidence(evidence)}" for evidence in evidence_items)


def _append_item_evidence(lines: list[str], evidence_items: list[SourceEvidence]) -> None:
    lines.append("   - **Supporting Evidence:**")
    lines.extend(f"     - {_format_evidence(evidence)}" for evidence in evidence_items)


def _format_evidence(evidence: SourceEvidence) -> str:
    source_label = _humanize(evidence.source_type)
    metadata = [source_label]
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


def _escape_evidence_metadata(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("]", "\\]")
