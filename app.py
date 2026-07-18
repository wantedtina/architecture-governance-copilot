"""Single-page Streamlit interface for the Architecture Governance Copilot."""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import date
from enum import StrEnum

import streamlit as st
from pydantic import ValidationError

from architecture_governance_copilot.extractors import (
    DeterministicDemoExtractor,
    DeterministicFixtureError,
)
from architecture_governance_copilot.governance_service import (
    GovernanceOutputs,
    GovernanceReviewService,
)
from architecture_governance_copilot.models import (
    ActionPriority,
    EvidenceSource,
    FindingSeverity,
    FindingStatus,
    GovernanceResult,
    ReviewOutcome,
    RiskSeverity,
    SolutionIntentReviewContext,
    SourceEvidence,
)
from architecture_governance_copilot.ui_support import (
    ANALYSIS_SUCCESS_KEY,
    ANALYZED_FINGERPRINT_KEY,
    ANALYZED_RESULT_KEY,
    CONTEXT_KEY,
    ERROR_KEY,
    LOADED_KEY,
    OUTPUT_SUCCESS_KEY,
    OUTPUTS_KEY,
    SOLUTION_INTENT_KEY,
    TRANSCRIPT_KEY,
    ReviewFormData,
    analysis_is_stale,
    build_reviewed_result,
    clear_analysis_state,
    clear_outputs,
    humanize,
    initialize_session_state,
    input_fingerprint,
    load_sample_into_state,
    load_sample_review,
    reset_application_state,
    store_analysis,
    store_outputs,
)


def main() -> None:
    """Render the complete deterministic single-page review workflow."""
    st.set_page_config(
        page_title="Architecture Governance Copilot",
        page_icon="🏛️",
        layout="wide",
    )
    initialize_session_state(st.session_state)
    _render_header()
    _render_input_stage()
    _render_error()

    analyzed_result = st.session_state[ANALYZED_RESULT_KEY]
    if not isinstance(analyzed_result, GovernanceResult):
        return

    context = _current_context()
    stale = analysis_is_stale(
        st.session_state[SOLUTION_INTENT_KEY],
        st.session_state[TRANSCRIPT_KEY],
        context,
        st.session_state[ANALYZED_FINGERPRINT_KEY],
    )
    if stale:
        if st.session_state[OUTPUTS_KEY] is not None:
            clear_outputs(st.session_state)
        st.warning(
            "The review inputs changed after analysis. Run Analyze Review again before "
            "generating outputs."
        )

    form_data, submitted = _render_human_review_stage(analyzed_result, stale=stale)
    if submitted:
        _generate_reviewed_outputs(analyzed_result, form_data, stale=stale)

    outputs = st.session_state[OUTPUTS_KEY]
    if isinstance(outputs, GovernanceOutputs) and not stale:
        _render_output_stage(outputs)


def _render_header() -> None:
    st.title("Architecture Governance Copilot")
    st.subheader("A human-controlled proof of concept for Solution Intent review")
    st.info(
        "This PoC uses synthetic data and a deterministic demo extractor. "
        "Formal governance decisions remain with the Domain Architect."
    )
    st.caption(
        "The deterministic extractor supports only the bundled sample. "
        "No real Teams, Confluence, LLM, or Azure DevOps integration is used."
    )


def _render_input_stage() -> None:
    st.header("Stage 1 — Review Inputs")
    st.write(
        "Load the bundled synthetic Solution Intent, review transcript, and metadata, "
        "then analyze them together."
    )

    load_column, analyze_column, reset_column, status_column = st.columns([1.2, 1.2, 1, 2])
    load_clicked = load_column.button(
        "Load Sample Review",
        key="agc_load_sample",
        use_container_width=True,
    )
    analyze_clicked = analyze_column.button(
        "Analyze Review",
        key="agc_analyze",
        use_container_width=True,
    )
    reset_clicked = reset_column.button(
        "Reset Demo",
        key="agc_reset",
        use_container_width=True,
    )

    if reset_clicked:
        reset_application_state(st.session_state)
        st.rerun()

    if load_clicked:
        try:
            load_sample_into_state(st.session_state, load_sample_review())
        except (OSError, UnicodeError, ValueError) as exc:
            st.session_state[ERROR_KEY] = f"Unable to load the bundled sample: {exc}"
        else:
            st.rerun()

    if st.session_state[LOADED_KEY]:
        status_column.success("Synthetic sample loaded into editable inputs.")
    else:
        status_column.info("Start with Load Sample Review.")

    context = _current_context()
    if context is not None:
        _render_context(context)
    else:
        st.caption("Review metadata will appear after the bundled sample is loaded.")

    si_tab, transcript_tab = st.tabs(["Solution Intent", "Review Transcript"])
    with si_tab:
        st.text_area(
            "Synthetic Solution Intent",
            key=SOLUTION_INTENT_KEY,
            height=360,
            placeholder="Load the bundled synthetic review to begin.",
        )
    with transcript_tab:
        st.text_area(
            "Synthetic Teams-style Review Transcript",
            key=TRANSCRIPT_KEY,
            height=360,
            placeholder="Load the bundled synthetic review to begin.",
        )

    if analyze_clicked:
        _analyze_current_inputs()

    if st.session_state[ANALYSIS_SUCCESS_KEY]:
        st.success(
            "Deterministic analysis completed. Review and edit the draft below; "
            "no outputs were generated automatically."
        )


def _render_context(context: SolutionIntentReviewContext) -> None:
    st.markdown("#### Solution Intent Review Metadata")
    values = [
        ("Project", context.project_name),
        ("SI Title", context.si_title),
        ("SI Version", context.si_version),
        ("Current SI Status", humanize(context.current_si_status.value)),
        ("Review Round", str(context.review_round)),
        ("Review Date", context.review_date.isoformat() if context.review_date else "Not provided"),
        ("Domain Architect", context.domain_architect or "Not provided"),
        ("ADO Governance Ticket", context.ado_ticket_id or "Not provided"),
    ]
    first_row = st.columns(4)
    second_row = st.columns(4)
    for column, (label, value) in zip([*first_row, *second_row], values, strict=True):
        column.markdown(f"**{label}**")
        column.write(value)


def _analyze_current_inputs() -> None:
    clear_analysis_state(st.session_state)
    solution_intent = st.session_state[SOLUTION_INTENT_KEY]
    transcript = st.session_state[TRANSCRIPT_KEY]
    context = _current_context()
    try:
        if not solution_intent.strip():
            raise ValueError("Solution Intent must not be blank.")
        if not transcript.strip():
            raise ValueError("Review transcript must not be blank.")
        if context is None:
            raise ValueError("Review metadata is missing. Load the sample review first.")
        service = GovernanceReviewService(DeterministicDemoExtractor())
        result = service.analyze_review(solution_intent, transcript, context)
        store_analysis(
            st.session_state,
            result,
            input_fingerprint(solution_intent, transcript, context),
        )
    except (DeterministicFixtureError, ValidationError, ValueError) as exc:
        st.session_state[ERROR_KEY] = f"Analysis failed: {exc}"


def _render_error() -> None:
    error = st.session_state[ERROR_KEY]
    if isinstance(error, str) and error:
        st.error(error)


def _render_human_review_stage(
    analyzed_result: GovernanceResult,
    *,
    stale: bool,
) -> tuple[ReviewFormData, bool]:
    st.header("Stage 2 — Human Review")
    st.subheader("Draft Structured Review")
    st.caption(
        "Edit or exclude proposed items. Supporting evidence is read-only. "
        "This stage does not formally approve the Solution Intent."
    )
    _render_analysis_summary(analyzed_result)

    with st.form("agc_review_form", clear_on_submit=False):
        st.markdown("### Review Outcome")
        review_outcome = _enum_selectbox(
            "Review outcome",
            ReviewOutcome,
            analyzed_result.review_outcome.value,
            key="agc_field_outcome",
        )
        _render_evidence(analyzed_result.outcome_evidence, "Outcome supporting evidence")

        decisions = _render_decision_edits(analyzed_result)
        findings = _render_finding_edits(analyzed_result)
        risks = _render_risk_edits(analyzed_result)
        actions = _render_action_edits(analyzed_result)
        questions = _render_question_edits(analyzed_result)
        missing = _render_missing_evidence_edits(analyzed_result)

        submitted = st.form_submit_button(
            "Confirm Reviewed Record & Generate Outputs",
            key="agc_confirm_review",
            type="primary",
            disabled=stale,
            use_container_width=True,
        )

    return (
        ReviewFormData(
            review_outcome=review_outcome,
            decisions=tuple(decisions),
            findings=tuple(findings),
            risks=tuple(risks),
            action_items=tuple(actions),
            open_questions=tuple(questions),
            missing_evidence=tuple(missing),
        ),
        submitted,
    )


def _render_analysis_summary(result: GovernanceResult) -> None:
    labels_and_values = [
        ("Outcome", humanize(result.review_outcome.value)),
        ("Decisions", len(result.decisions)),
        ("Findings", len(result.findings)),
        ("Risks", len(result.risks)),
        ("Actions", len(result.action_items)),
        ("Open Questions", len(result.open_questions)),
        ("Missing Information", len(result.missing_evidence)),
    ]
    for column, (label, value) in zip(
        st.columns(len(labels_and_values)),
        labels_and_values,
        strict=True,
    ):
        column.metric(label, value)


def _render_decision_edits(result: GovernanceResult) -> list[dict[str, object]]:
    st.markdown("### Confirmed Decisions")
    if not result.decisions:
        st.caption("None recorded.")
    edits: list[dict[str, object]] = []
    for index, decision in enumerate(result.decisions):
        with st.container(border=True):
            st.markdown(f"**Decision {index + 1}**")
            include = st.checkbox(
                "Include in reviewed record",
                value=True,
                key=f"agc_field_decision_{index}_include",
            )
            statement = st.text_area(
                "Statement",
                value=decision.statement,
                key=f"agc_field_decision_{index}_statement",
                height=80,
            )
            rationale = st.text_area(
                "Rationale (optional)",
                value=decision.rationale or "",
                key=f"agc_field_decision_{index}_rationale",
                height=70,
            )
            _render_evidence(decision.evidence, "Supporting evidence")
            edits.append(
                {
                    "include": include,
                    "statement": statement,
                    "rationale": rationale,
                }
            )
    return edits


def _render_finding_edits(result: GovernanceResult) -> list[dict[str, object]]:
    st.markdown("### Review Findings")
    if not result.findings:
        st.caption("None recorded.")
    edits: list[dict[str, object]] = []
    for index, finding in enumerate(result.findings):
        with st.container(border=True):
            st.markdown(f"**Review Finding {index + 1}**")
            include = st.checkbox(
                "Include in reviewed record",
                value=True,
                key=f"agc_field_finding_{index}_include",
            )
            title = st.text_input(
                "Title",
                value=finding.title,
                key=f"agc_field_finding_{index}_title",
            )
            description = st.text_area(
                "Description",
                value=finding.description,
                key=f"agc_field_finding_{index}_description",
                height=80,
            )
            category_column, section_column = st.columns(2)
            category = category_column.text_input(
                "Category (optional)",
                value=finding.category or "",
                key=f"agc_field_finding_{index}_category",
            )
            si_section = section_column.text_input(
                "SI section (optional)",
                value=finding.si_section or "",
                key=f"agc_field_finding_{index}_si_section",
            )
            severity_column, status_column = st.columns(2)
            with severity_column:
                severity = _enum_selectbox(
                    "Severity",
                    FindingSeverity,
                    finding.severity.value,
                    key=f"agc_field_finding_{index}_severity",
                )
            with status_column:
                status = _enum_selectbox(
                    "Status",
                    FindingStatus,
                    finding.status.value,
                    key=f"agc_field_finding_{index}_status",
                )
            recommended_change = st.text_area(
                "Recommended change (optional)",
                value=finding.recommended_change or "",
                key=f"agc_field_finding_{index}_recommended_change",
                height=80,
            )
            owner_column, date_column = st.columns(2)
            owner = owner_column.text_input(
                "Owner (optional)",
                value=finding.owner or "",
                key=f"agc_field_finding_{index}_owner",
            )
            due_date = date_column.text_input(
                "Due date (optional, YYYY-MM-DD)",
                value=_date_text(finding.due_date),
                key=f"agc_field_finding_{index}_due_date",
            )
            _render_evidence(finding.evidence, "Supporting evidence")
            edits.append(
                {
                    "include": include,
                    "title": title,
                    "description": description,
                    "category": category,
                    "si_section": si_section,
                    "severity": severity,
                    "status": status,
                    "recommended_change": recommended_change,
                    "owner": owner,
                    "due_date": due_date,
                }
            )
    return edits


def _render_risk_edits(result: GovernanceResult) -> list[dict[str, object]]:
    st.markdown("### Risks")
    if not result.risks:
        st.caption("None recorded.")
    edits: list[dict[str, object]] = []
    for index, risk in enumerate(result.risks):
        with st.container(border=True):
            st.markdown(f"**Risk {index + 1}**")
            include = st.checkbox(
                "Include in reviewed record",
                value=True,
                key=f"agc_field_risk_{index}_include",
            )
            description = st.text_area(
                "Description",
                value=risk.description,
                key=f"agc_field_risk_{index}_description",
                height=80,
            )
            severity_column, owner_column = st.columns(2)
            with severity_column:
                severity = _enum_selectbox(
                    "Severity",
                    RiskSeverity,
                    risk.severity.value,
                    key=f"agc_field_risk_{index}_severity",
                )
            owner = owner_column.text_input(
                "Owner (optional)",
                value=risk.owner or "",
                key=f"agc_field_risk_{index}_owner",
            )
            _render_evidence(risk.evidence, "Supporting evidence")
            edits.append(
                {
                    "include": include,
                    "description": description,
                    "severity": severity,
                    "owner": owner,
                }
            )
    return edits


def _render_action_edits(result: GovernanceResult) -> list[dict[str, object]]:
    st.markdown("### Action Items")
    if not result.action_items:
        st.caption("None recorded.")
    edits: list[dict[str, object]] = []
    for index, action in enumerate(result.action_items):
        with st.container(border=True):
            st.markdown(f"**Action Item {index + 1}**")
            include = st.checkbox(
                "Include in reviewed record",
                value=True,
                key=f"agc_field_action_{index}_include",
            )
            title = st.text_input(
                "Title",
                value=action.title,
                key=f"agc_field_action_{index}_title",
            )
            owner_column, date_column, priority_column = st.columns(3)
            owner = owner_column.text_input(
                "Owner (optional)",
                value=action.owner or "",
                key=f"agc_field_action_{index}_owner",
            )
            due_date = date_column.text_input(
                "Due date (optional, YYYY-MM-DD)",
                value=_date_text(action.due_date),
                key=f"agc_field_action_{index}_due_date",
            )
            with priority_column:
                priority = _enum_selectbox(
                    "Priority",
                    ActionPriority,
                    action.priority.value,
                    key=f"agc_field_action_{index}_priority",
                )
            _render_evidence(action.evidence, "Supporting evidence")
            edits.append(
                {
                    "include": include,
                    "title": title,
                    "owner": owner,
                    "due_date": due_date,
                    "priority": priority,
                }
            )
    return edits


def _render_question_edits(result: GovernanceResult) -> list[dict[str, object]]:
    st.markdown("### Open Questions")
    if not result.open_questions:
        st.caption("None recorded.")
    edits: list[dict[str, object]] = []
    for index, question in enumerate(result.open_questions):
        with st.container(border=True):
            st.markdown(f"**Open Question {index + 1}**")
            include = st.checkbox(
                "Include in reviewed record",
                value=True,
                key=f"agc_field_question_{index}_include",
            )
            question_text = st.text_area(
                "Question",
                value=question.question,
                key=f"agc_field_question_{index}_question",
                height=70,
            )
            owner = st.text_input(
                "Owner (optional)",
                value=question.owner or "",
                key=f"agc_field_question_{index}_owner",
            )
            _render_evidence(question.evidence, "Supporting evidence")
            edits.append(
                {
                    "include": include,
                    "question": question_text,
                    "owner": owner,
                }
            )
    return edits


def _render_missing_evidence_edits(result: GovernanceResult) -> list[dict[str, object]]:
    st.markdown("### Missing Governance Information")
    if not result.missing_evidence:
        st.caption("None recorded.")
    edits: list[dict[str, object]] = []
    for index, missing in enumerate(result.missing_evidence):
        with st.container(border=True):
            st.markdown(f"**Missing Information {index + 1}**")
            include = st.checkbox(
                "Include in reviewed record",
                value=True,
                key=f"agc_field_missing_{index}_include",
            )
            item = st.text_input(
                "Item",
                value=missing.item,
                key=f"agc_field_missing_{index}_item",
            )
            reason = st.text_area(
                "Reason (optional)",
                value=missing.reason or "",
                key=f"agc_field_missing_{index}_reason",
                height=70,
            )
            _render_evidence(missing.evidence, "Supporting evidence")
            edits.append(
                {
                    "include": include,
                    "item": item,
                    "reason": reason,
                }
            )
    return edits


def _render_evidence(evidence_items: Sequence[SourceEvidence], label: str) -> None:
    with st.expander(f"{label} ({len(evidence_items)})", expanded=False):
        if not evidence_items:
            st.caption("No direct quote recorded.")
            return
        for index, evidence in enumerate(evidence_items, start=1):
            st.markdown(f"**Evidence {index}: {_evidence_source_label(evidence)}**")
            metadata = _evidence_metadata(evidence)
            if metadata:
                st.caption(" · ".join(metadata))
            st.code(evidence.quote, language=None, wrap_lines=True)


def _evidence_source_label(evidence: SourceEvidence) -> str:
    return (
        "Solution Intent"
        if evidence.source_type is EvidenceSource.SOLUTION_INTENT
        else "Meeting Transcript"
    )


def _evidence_metadata(evidence: SourceEvidence) -> list[str]:
    metadata: list[str] = []
    if evidence.section is not None:
        metadata.append(f"SI section: {evidence.section}")
    if evidence.timestamp is not None:
        metadata.append(f"Timestamp: {evidence.timestamp}")
    if evidence.speaker is not None:
        metadata.append(f"Speaker: {evidence.speaker}")
    if evidence.reference is not None:
        metadata.append(f"Reference: {evidence.reference}")
    return metadata


def _enum_selectbox(
    label: str,
    enum_type: type[StrEnum],
    current_value: str,
    *,
    key: str,
) -> str:
    options = [item.value for item in enum_type]
    return st.selectbox(
        label,
        options=options,
        index=options.index(current_value),
        format_func=humanize,
        key=key,
    )


def _date_text(value: date | None) -> str:
    return value.isoformat() if value is not None else ""


def _generate_reviewed_outputs(
    analyzed_result: GovernanceResult,
    form_data: ReviewFormData,
    *,
    stale: bool,
) -> None:
    clear_outputs(st.session_state)
    st.session_state[ERROR_KEY] = None
    try:
        if stale:
            raise ValueError("Inputs changed after analysis. Run Analyze Review again.")
        reviewed_result = build_reviewed_result(analyzed_result, form_data)
        service = GovernanceReviewService(DeterministicDemoExtractor())
        outputs = service.generate_outputs(reviewed_result)
        store_outputs(st.session_state, reviewed_result, outputs)
    except (DeterministicFixtureError, ValidationError, ValueError, RuntimeError) as exc:
        st.session_state[ERROR_KEY] = f"Unable to generate reviewed outputs: {exc}"
        st.error(st.session_state[ERROR_KEY])
    else:
        st.success(
            "Reviewed record validated and outputs generated. "
            "The Domain Architect remains responsible for the formal decision."
        )


def _render_output_stage(outputs: GovernanceOutputs) -> None:
    st.header("Stage 3 — Generated Outputs")
    if st.session_state[OUTPUT_SUCCESS_KEY]:
        st.success("Reviewed outputs generated from the human-reviewed structured record.")

    st.subheader("Generated Review Record")
    st.info(
        "This generated record must be reviewed before publication. "
        "The Domain Architect remains responsible for the formal governance decision."
    )
    rendered_tab, raw_tab = st.tabs(["Rendered Markdown", "Raw Markdown"])
    with rendered_tab:
        st.markdown(outputs.review_minutes)
    with raw_tab:
        st.code(outputs.review_minutes, language="markdown", wrap_lines=True)
    st.download_button(
        "Download Markdown Review Record",
        data=outputs.review_minutes,
        file_name="solution-intent-review-record.md",
        mime="text/markdown",
        key="agc_download_minutes",
    )

    st.subheader("Mock Azure DevOps Work Items")
    st.warning("No real Azure DevOps work item has been created.")
    if not outputs.ado_work_items:
        st.caption("No action items were included in the reviewed record.")
    for index, item in enumerate(outputs.ado_work_items, start=1):
        with st.container(border=True):
            st.markdown(f"#### Mock Work Item {index}: {item.title}")
            first_row = st.columns(4)
            first_row[0].markdown("**Assigned to**")
            first_row[0].write(item.assigned_to or "Unassigned")
            first_row[1].markdown("**Due date**")
            first_row[1].write(item.due_date.isoformat() if item.due_date else "Not specified")
            first_row[2].markdown("**Priority**")
            first_row[2].write(humanize(item.priority.value))
            first_row[3].markdown("**Source action index**")
            first_row[3].write(item.source_action_index)

            second_row = st.columns(3)
            second_row[0].markdown("**Parent work-item ID**")
            second_row[0].write(item.parent_work_item_id or "Not provided")
            second_row[1].markdown("**SI section**")
            second_row[1].write(item.si_section or "Not provided")
            second_row[2].markdown("**Tags**")
            second_row[2].write(", ".join(item.tags))

            st.markdown("**Description**")
            st.markdown(item.description)
            if item.acceptance_criteria:
                st.markdown("**Acceptance criteria**")
                for criterion in item.acceptance_criteria:
                    st.markdown(f"- {criterion}")
            with st.expander("JSON representation"):
                st.json(item.model_dump(mode="json"))

    if outputs.ado_work_items:
        work_items_json = json.dumps(
            [item.model_dump(mode="json") for item in outputs.ado_work_items],
            indent=2,
        )
        st.download_button(
            "Download Mock Work Items JSON",
            data=work_items_json,
            file_name="mock-ado-work-items.json",
            mime="application/json",
            key="agc_download_ado",
        )


def _current_context() -> SolutionIntentReviewContext | None:
    context = st.session_state[CONTEXT_KEY]
    return context if isinstance(context, SolutionIntentReviewContext) else None


if __name__ == "__main__":
    main()
