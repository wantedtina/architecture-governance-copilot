"""Routed Streamlit interface for the Architecture Governance Copilot."""

from __future__ import annotations

import json
import os
import time
from base64 import b64encode
from collections.abc import Mapping, Sequence
from datetime import date
from enum import StrEnum
from html import escape
from pathlib import Path

import streamlit as st
from pydantic import ValidationError

from architecture_governance_copilot.extractors import DeterministicFixtureError
from architecture_governance_copilot.governance_service import (
    GovernanceOutputs,
    GovernanceReviewService,
    generate_governance_outputs,
)
from architecture_governance_copilot.integrations.aif import AifAnalysisError
from architecture_governance_copilot.integrations.azure_devops import (
    InMemoryFakeAdoGateway,
)
from architecture_governance_copilot.integrations.confluence import (
    ConfluencePageSnapshot,
    ConfluenceReadError,
)
from architecture_governance_copilot.minutes_generator import format_action_item_entry
from architecture_governance_copilot.models import (
    ActionPriority,
    DraftingSourceInventory,
    DraftingSourcePackageManifest,
    DraftingSourceResource,
    DraftingSourceRole,
    EvidenceSource,
    FindingSeverity,
    FindingStatus,
    GovernanceResult,
    ReviewInputProvenance,
    ReviewOutcome,
    RiskSeverity,
    SolutionIntentDraft,
    SolutionIntentDraftRequest,
    SolutionIntentReviewContext,
    SourceEvidence,
)
from architecture_governance_copilot.publication import (
    PROTECTED_PUBLICATION_STATUSES,
    AdoPublicationConfirmation,
    AdoPublicationCoordinator,
    AdoPublicationOperation,
    AdoPublicationPreview,
    PublicationStatus,
    PublicationValidationError,
    assess_delivery_readiness,
    build_ado_publication_preview,
    confirm_ado_publication_preview,
    delivery_action_correlations,
    publication_request_summary,
)
from architecture_governance_copilot.runtime_dependencies import (
    DeploymentConfigurationError,
    DeploymentPolicy,
    DeploymentProfile,
    ReviewMode,
    available_review_modes,
    build_review_runtime,
    configured_delivery_capability,
    resolve_deployment_policy,
)
from architecture_governance_copilot.si_drafting import (
    DeterministicDemoDrafter,
    DeterministicDraftingFixtureError,
    SolutionIntentDraftingService,
)
from architecture_governance_copilot.ui_support import (
    ADO_FAKE_GATEWAY_KEY,
    ADO_PUBLICATION_CONFIRMATION_KEY,
    ADO_PUBLICATION_HISTORY_KEY,
    ADO_PUBLICATION_PREVIEW_KEY,
    ANALYZED_RESULT_KEY,
    CONFIRMED_SOURCE_PACKAGE_KEY,
    CONFLUENCE_SNAPSHOT_KEY,
    CONTEXT_EVIDENCE_IDS_KEY,
    CONTEXT_EVIDENCE_WIDGET_KEY,
    CONTEXT_KEY,
    CONTEXT_REPOSITORY_ID_KEY,
    CONTEXT_REPOSITORY_WIDGET_KEY,
    CONTEXT_STAGE,
    CONTEXT_TEMPLATE_ID_KEY,
    CONTEXT_TEMPLATE_WIDGET_KEY,
    DELIVERY_ACTION_SELECTION_KEY,
    DELIVERY_ACTION_WIDGET_KEY,
    DELIVERY_STAGE,
    DRAFT_CONFIRMED_KEY,
    DRAFT_CONTENT_WIDGET_KEY,
    DRAFT_EVIDENCE_KEY,
    DRAFT_FINGERPRINT_KEY,
    DRAFT_PROJECT_KEY,
    DRAFT_PROJECT_WIDGET_KEY,
    DRAFT_REPOSITORY_NAME_KEY,
    DRAFT_RESULT_KEY,
    DRAFT_SOURCE_CODE_KEY,
    DRAFT_SOURCE_CODE_WIDGET_KEY,
    DRAFT_STAGE,
    DRAFT_SUPPORTING_DOCS_KEY,
    DRAFT_SUPPORTING_DOCS_WIDGET_KEY,
    DRAFT_TEMPLATE_KEY,
    DRAFT_TEMPLATE_WIDGET_KEY,
    ERROR_KEY,
    HOME_STAGE,
    INPUT_STAGE,
    METADATA_ARCHITECT_WIDGET_KEY,
    METADATA_PROVENANCE_KEY,
    METADATA_REVIEW_DATE_WIDGET_KEY,
    METADATA_REVIEW_ROUND_WIDGET_KEY,
    METADATA_TICKET_WIDGET_KEY,
    OUTPUT_ACTION_SELECTION_KEY,
    OUTPUT_STAGE,
    OUTPUT_SUCCESS_KEY,
    OUTPUTS_KEY,
    PROJECT_CONTEXT_CONFIRMED_KEY,
    PROJECT_CONTEXT_KEY,
    PROJECT_CONTEXT_REFRESHED_KEY,
    REVIEW_CHANGE_SUMMARY_KEY,
    REVIEW_INPUT_FEEDBACK_KEY,
    REVIEW_MODE_WIDGET_KEY,
    REVIEW_POLICY_RECOVERY_KEY,
    REVIEW_PROVIDER_CONFIGURATION_ID_KEY,
    REVIEW_STAGE,
    REVIEWED_RESULT_KEY,
    ROUTE_SOURCE_STAGE_KEY,
    SOLUTION_INTENT_KEY,
    SOLUTION_INTENT_WIDGET_KEY,
    TRANSCRIPT_KEY,
    TRANSCRIPT_PROVENANCE_KEY,
    TRANSCRIPT_WIDGET_KEY,
    AnalysisInvalidation,
    PendingReviewChanges,
    ReviewChangeSummary,
    ReviewFormData,
    ReviewInputReadiness,
    Workflow,
    active_stage,
    add_drafting_evidence,
    apply_deployment_policy,
    build_drafting_source_package,
    build_pending_review_changes,
    build_review_change_summary,
    build_reviewed_result,
    build_sample_review_snapshot,
    clear_outputs,
    clear_publication_preview,
    clear_review_action_due_date,
    clear_stale_si_draft,
    confirm_project_context_for_drafting,
    confirm_review_input_manifest,
    confirm_si_draft_for_review,
    current_analysis_invalidation,
    current_input_fingerprint,
    current_review_form_data,
    current_review_input_manifest,
    current_review_mode,
    current_workflow,
    delivery_operation_for_correlations,
    delivery_original_action_index,
    delivery_outputs_available,
    delivery_status,
    drafting_evidence_is_saved,
    drafting_input_fingerprint,
    drafting_result_is_stale,
    edit_drafting_evidence,
    humanize,
    load_drafting_sample_evidence,
    load_internal_review_into_state,
    load_sample_drafting_context,
    load_sample_review,
    open_demonstration_project_into_state,
    prepare_analysis_attempt,
    preserve_review_widget_state,
    project_context_readiness,
    record_internal_source_load_failure,
    record_publication_operation,
    recover_review_policy,
    refresh_project_context,
    remove_drafting_evidence,
    reset_application_state,
    reset_drafting_workflow,
    reset_review_workflow,
    restore_review_widget_state,
    retain_drafting_source_widget_state,
    retain_review_widget_state,
    review_input_readiness,
    save_drafting_evidence,
    select_delivery_action,
    set_active_stage,
    start_workflow,
    store_analysis,
    store_metadata_component,
    store_outputs,
    store_publication_confirmation,
    store_publication_preview,
    store_review_source_snapshot,
    store_si_draft,
    store_transcript_component,
    switch_review_mode,
    update_live_drafting_source_package,
)

_BRAND_LOGO_DATA_URI = "data:image/png;base64," + b64encode(
    (Path(__file__).parent / "assets" / "standard_chartered_logo.png").read_bytes()
).decode("ascii")

_ROUTE_FILES = {
    HOME_STAGE: "pages/workflow_home.py",
    CONTEXT_STAGE: "pages/project_context.py",
    DRAFT_STAGE: "pages/solution_intent_drafting.py",
    INPUT_STAGE: "pages/review_inputs.py",
    REVIEW_STAGE: "pages/human_review.py",
    OUTPUT_STAGE: "pages/generated_outputs.py",
    DELIVERY_STAGE: "pages/work_item_delivery.py",
}
_DEMO_DELAY_ENV = "AGC_DEMO_STEP_DELAY_SECONDS"
_DEFAULT_DEMO_STEP_DELAY_SECONDS = 0.4
_MAX_DEMO_STEP_DELAY_SECONDS = 1.5


def main() -> None:
    """Configure and run the two independent deterministic workflows."""
    st.set_page_config(
        page_title="Architecture Governance Copilot",
        page_icon="🏛️",
        layout="wide",
    )
    _apply_visual_theme()

    home_page = st.Page(
        _ROUTE_FILES[HOME_STAGE],
        title="Choose workflow",
        icon=":material/home:",
        url_path="home",
        default=True,
        visibility="hidden",
    )
    context_page = st.Page(
        _ROUTE_FILES[CONTEXT_STAGE],
        title="Project Context",
        icon=":material/folder_managed:",
        url_path="project-context",
        visibility="hidden",
    )
    drafting_page = st.Page(
        _ROUTE_FILES[DRAFT_STAGE],
        title="Draft Solution Intent",
        icon=":material/edit_document:",
        url_path="draft-solution-intent",
        visibility="hidden",
    )
    input_page = st.Page(
        _ROUTE_FILES[INPUT_STAGE],
        title="Review Inputs",
        icon=":material/description:",
        visibility="hidden",
    )
    review_page = st.Page(
        _ROUTE_FILES[REVIEW_STAGE],
        title="Human Review",
        icon=":material/fact_check:",
        url_path="human-review",
        visibility="hidden",
    )
    output_page = st.Page(
        _ROUTE_FILES[OUTPUT_STAGE],
        title="Generated Outputs",
        icon=":material/task_alt:",
        url_path="generated-outputs",
        visibility="hidden",
    )
    delivery_page = st.Page(
        _ROUTE_FILES[DELIVERY_STAGE],
        title="Work Item Delivery",
        icon=":material/send:",
        url_path="work-item-delivery",
        visibility="hidden",
    )
    selected_page = st.navigation(
        [
            home_page,
            context_page,
            drafting_page,
            input_page,
            review_page,
            output_page,
            delivery_page,
        ],
        position="hidden",
    )
    selected_page.run()


def _enforce_deployment_policy(route: str) -> None:
    """Apply deployment eligibility before any routed workflow reads or renders state."""
    try:
        policy = resolve_deployment_policy()
    except DeploymentConfigurationError as exc:
        apply_deployment_policy(
            st.session_state, DeploymentPolicy(DeploymentProfile.PRODUCTION, ())
        )
        st.header("Deployment configuration error")
        st.error(str(exc))
        st.info(
            "Ask the deployment operator to correct the configuration and restart the application."
        )
        st.stop()
    apply_deployment_policy(st.session_state, policy)
    st.caption(f"Environment: {policy.profile.value}")
    if not policy.drafting_allowed:
        st.header("Production capabilities unavailable")
        st.info(
            "No accepted live capabilities are configured for this deployment. "
            "Synthetic drafting, review, and delivery are disabled."
        )
        st.caption(
            "The deployment operator must complete separately approved live integration and "
            "release acceptance before enabling production workflows. "
            "This profile does not certify readiness."
        )
        st.stop()
    if st.session_state.get(REVIEW_POLICY_RECOVERY_KEY) and route not in {
        HOME_STAGE,
        CONTEXT_STAGE,
        DRAFT_STAGE,
    }:
        st.header("Choose an allowed review mode")
        st.warning(
            "The previous review mode is no longer available. Its inputs and confirmations were "
            "revoked. No fallback analysis was performed; delivery history remains session-local."
        )
        for descriptor in policy.review_modes:
            if st.button(
                f"Start a new {descriptor.label} review", key=f"agc_recover_{descriptor.mode.value}"
            ):
                recover_review_policy(st.session_state, policy, descriptor.mode)
                _switch_stage(INPUT_STAGE)
        st.stop()


def _render_home_page() -> None:
    _enforce_deployment_policy(HOME_STAGE)
    _render_page_shell(HOME_STAGE)
    st.header("Choose a governance workflow")
    st.caption(
        "Drafting and governance review are separate human-controlled activities. "
        "Choose the task you want to perform."
    )
    draft_column, review_column = st.columns(2, gap="large")
    with draft_column.container(border=True, height="stretch"):
        st.subheader("Draft a Solution Intent")
        st.write(
            "Prepare and human-confirm a draft from a deterministic synthetic Project Context "
            "package. The result is not published to Confluence."
        )
        if st.button(
            "Draft a Solution Intent",
            key="agc_start_drafting_workflow",
            type="primary",
            icon=":material/edit_document:",
            width="stretch",
        ):
            start_workflow(st.session_state, Workflow.DRAFT)
            _switch_stage(active_stage(st.session_state))
    with review_column.container(border=True, height="stretch"):
        st.subheader("Review a Solution Intent")
        st.write(
            "Review an explicitly selected authoritative SI snapshot together with a transcript "
            "and review metadata."
        )
        if st.button(
            "Review a Solution Intent",
            key="agc_start_review_workflow",
            type="primary",
            icon=":material/fact_check:",
            width="stretch",
        ):
            start_workflow(st.session_state, Workflow.REVIEW)
            _switch_stage(INPUT_STAGE)
    if st.button(
        "Reset all local demo state",
        key="agc_reset_all_state",
        icon=":material/restart_alt:",
    ):
        reset_application_state(st.session_state)
        _switch_stage(HOME_STAGE)
    st.info(
        "Synthetic data · No external connections · Human confirmation remains mandatory in "
        "both workflows."
    )


def _render_context_page() -> None:
    _enforce_deployment_policy(CONTEXT_STAGE)
    _render_page_shell(CONTEXT_STAGE)
    _render_project_context_stage()
    _render_error()


def _render_drafting_page() -> None:
    _enforce_deployment_policy(DRAFT_STAGE)
    retain_drafting_source_widget_state(st.session_state)
    if st.session_state[PROJECT_CONTEXT_CONFIRMED_KEY] is not True:
        _switch_stage(
            CONTEXT_STAGE,
            error="Confirm a Project Context package before drafting a Solution Intent.",
        )
    _render_page_shell(DRAFT_STAGE)
    _render_drafting_stage()
    _render_error()


def _render_input_page() -> None:
    _enforce_deployment_policy(INPUT_STAGE)
    route_source = st.session_state.pop(ROUTE_SOURCE_STAGE_KEY, None)
    restore_input_widgets = (
        active_stage(st.session_state) != INPUT_STAGE
        or isinstance(route_source, str)
        and route_source != INPUT_STAGE
    )
    _render_page_shell(INPUT_STAGE)
    _render_input_stage(restore_input_widgets=restore_input_widgets)
    _render_error()


def _render_review_page() -> None:
    _enforce_deployment_policy(REVIEW_STAGE)
    analyzed_result = st.session_state[ANALYZED_RESULT_KEY]
    if not isinstance(analyzed_result, GovernanceResult):
        _switch_stage(
            INPUT_STAGE,
            error="Complete review analysis before opening the Human Review page.",
        )

    restore_review_widget_state(st.session_state)
    invalidation = current_analysis_invalidation(st.session_state)

    _render_page_shell(REVIEW_STAGE)
    st.header("Review step 2 — Human Review")
    _render_review_navigation(analysis_invalid=invalidation is not None)
    if invalidation is not None:
        _render_invalidation_notice(invalidation)
    _render_analyzed_input_summary(analyzed_result, valid=invalidation is None)
    if invalidation is not None:
        _render_error()
        return

    form_data, submitted = _render_human_review_stage(analyzed_result)
    if submitted and _generate_reviewed_outputs(analyzed_result, form_data):
        _switch_stage(OUTPUT_STAGE)
    _render_error()


def _render_output_page() -> None:
    _enforce_deployment_policy(OUTPUT_STAGE)
    retain_review_widget_state(st.session_state)
    invalidation = current_analysis_invalidation(st.session_state)
    analyzed_result = st.session_state[ANALYZED_RESULT_KEY]
    if invalidation is not None and isinstance(analyzed_result, GovernanceResult):
        clear_outputs(st.session_state)
        _switch_stage(REVIEW_STAGE)
    if not isinstance(analyzed_result, GovernanceResult):
        _switch_stage(
            INPUT_STAGE,
            error="Complete review analysis before opening the Generated Outputs page.",
        )

    outputs = st.session_state[OUTPUTS_KEY]
    change_summary = st.session_state[REVIEW_CHANGE_SUMMARY_KEY]
    if not isinstance(outputs, GovernanceOutputs) or not isinstance(
        change_summary, ReviewChangeSummary
    ):
        clear_outputs(st.session_state)
        _switch_stage(
            REVIEW_STAGE,
            error="Confirm the current reviewed record before opening Generated Outputs.",
        )

    _render_page_shell(OUTPUT_STAGE)
    st.header("Review step 3 — Generated Outputs")
    _render_output_navigation()
    _render_output_stage(outputs, change_summary)


def _render_delivery_page() -> None:
    _enforce_deployment_policy(DELIVERY_STAGE)
    retain_review_widget_state(st.session_state)
    if current_analysis_invalidation(st.session_state) is not None:
        _switch_stage(REVIEW_STAGE)
    if not delivery_outputs_available(st.session_state):
        _switch_stage(
            OUTPUT_STAGE,
            error="Confirm the reviewed record and generate outputs before Work Item Delivery.",
        )
    _render_page_shell(DELIVERY_STAGE)
    st.header("Review step 4 — Work Item Delivery")
    with st.container(horizontal=True):
        if st.button("Back to Generated Outputs", key="agc_delivery_back_outputs"):
            _switch_stage(OUTPUT_STAGE)
        if st.button("Back to Human Review", key="agc_delivery_back_review"):
            _switch_stage(REVIEW_STAGE)
    st.caption("Local governance artifacts are complete. Delivery is a separate conditional step.")
    _render_fake_ado_publication(st.session_state[REVIEWED_RESULT_KEY])
    _render_error()


def _render_page_shell(stage: str) -> None:
    set_active_stage(st.session_state, stage)
    _render_sidebar(stage)
    _render_header()
    if stage != HOME_STAGE:
        _render_step_progress(stage)


def _switch_stage(stage: str, *, error: str | None = None) -> None:
    # Multipage navigation removes widget-owned keys from pages that are no
    # longer rendered. Reassign review fields immediately before switching so
    # in-progress human edits remain durable across routed pages.
    preserve_review_widget_state(st.session_state)
    st.session_state[ROUTE_SOURCE_STAGE_KEY] = active_stage(st.session_state)
    set_active_stage(st.session_state, stage)
    if error is not None:
        st.session_state[ERROR_KEY] = error
    st.switch_page(_ROUTE_FILES[stage])


def _render_header() -> None:
    review_mode = current_review_mode(st.session_state)
    service_status = (
        "● Internal fake · no network"
        if review_mode is ReviewMode.INTERNAL_FAKE
        else "● Offline demo ready"
    )
    if st.session_state.get(REVIEW_POLICY_RECOVERY_KEY):
        service_status = "Review mode selection required"
    st.markdown(
        f"""
            <div class="agc-brandbar">
                <div class="agc-brand-lockup">
                    <img class="agc-brand-logo" src="{_BRAND_LOGO_DATA_URI}"
                         alt="Standard Chartered">
                    <span class="agc-brand-context">Technology &amp; Operations</span>
                </div>
                <div class="agc-product-copy">
                    <span>ARCHITECTURE &amp; ENGINEERING</span>
                    <strong>Architecture Governance Copilot</strong>
                    <small>Human-controlled Solution Intent drafting and review</small>
                </div>
                <div class="agc-brand-actions">
                    <div class="agc-classification">
                        <span class="agc-classification-dot"></span>
                        INTERNAL · HACKATHON PoC
                    </div>
                    <div class="agc-service-status">{service_status}</div>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "Demo Mode · Synthetic Data · No External Connections. "
        "Formal decisions remain with the Domain Architect."
    )


def _apply_visual_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --agc-indigo: #020b43;
            --agc-navy: #061d33;
            --agc-blue-dark: #0b56a8;
            --agc-blue: #0473ea;
            --agc-green: #38d200;
            --agc-green-dark: #238500;
            --agc-slate: #525355;
            --agc-muted: #666666;
            --agc-border: #e1e5e8;
            --agc-surface: #ffffff;
            --agc-blue-tint: #e7f1fd;
            --agc-green-tint: #ebfae5;
        }
        .stApp {
            background-image:
                radial-gradient(circle at 92% 2%, rgba(4, 115, 234, 0.07), transparent 30rem);
        }
        .stApp::before {
            position: fixed;
            inset: 0 0 auto 0;
            z-index: 999999;
            height: 4px;
            content: "";
            background: linear-gradient(
                90deg,
                var(--agc-blue) 0%,
                var(--agc-blue) 54%,
                var(--agc-green) 78%,
                #9be880 100%
            );
        }
        .block-container {
            max-width: 1380px;
            padding-top: 4.25rem;
            padding-bottom: 1.5rem;
        }
        h1, h2, h3 {
            letter-spacing: -0.02em;
        }
        h1 {
            font-weight: 500 !important;
        }
        [data-testid="stSidebar"] {
            background-image:
                radial-gradient(circle at 0% 100%, rgba(4, 115, 234, 0.32), transparent 17rem);
            box-shadow: 8px 0 30px rgba(0, 23, 46, 0.08);
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 1.6rem;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            opacity: 0.72;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px;
            box-shadow: 0 3px 14px rgba(0, 23, 46, 0.045);
        }
        [data-testid="stMetric"] {
            position: relative;
            overflow: hidden;
            border-radius: 12px;
            padding: 0.5rem 0.75rem;
            box-shadow: 0 2px 8px rgba(0, 23, 46, 0.035);
        }
        [data-testid="stMetric"]::before {
            position: absolute;
            inset: 0 auto 0 0;
            width: 3px;
            content: "";
            background: linear-gradient(180deg, var(--agc-blue), var(--agc-green));
        }
        [data-testid="stMetricValue"] {
            font-size: 1.35rem;
        }
        [data-testid="stAlert"] {
            border-radius: 10px;
            padding-block: 0.55rem;
        }
        .stButton > button, .stDownloadButton > button {
            border-radius: 6px;
            min-height: 2.6rem;
            font-weight: 500;
            transition: transform 120ms ease, box-shadow 120ms ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(4, 115, 234, 0.12);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 0;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .agc-brandbar {
            display: grid;
            grid-template-columns: auto minmax(18rem, 1fr) auto;
            align-items: center;
            gap: 1rem;
            min-height: 3.4rem;
            margin: 0 0 0.65rem;
            padding: 0.5rem 0.75rem;
            border: 1px solid var(--agc-border);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.94);
            box-shadow: 0 3px 16px rgba(0, 23, 46, 0.045);
        }
        .agc-brand-lockup {
            display: flex;
            align-items: flex-start;
            flex-direction: column;
            gap: 0.05rem;
        }
        .agc-brand-logo {
            display: block;
            width: 9.4rem;
            height: 2.65rem;
            object-fit: contain;
        }
        .agc-brand-context {
            padding-left: 0.2rem;
            color: var(--agc-muted);
            font-size: 0.62rem;
            letter-spacing: 0.04em;
        }
        .agc-product-copy {
            display: flex;
            min-width: 0;
            flex-direction: column;
            padding-left: 1rem;
            border-left: 1px solid var(--agc-border);
            line-height: 1.12;
        }
        .agc-product-copy span {
            color: var(--agc-blue-dark);
            font-size: 0.58rem;
            font-weight: 600;
            letter-spacing: 0.1em;
        }
        .agc-product-copy strong {
            overflow: hidden;
            margin-top: 0.14rem;
            color: var(--agc-navy);
            font-size: 1.08rem;
            font-weight: 500;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .agc-product-copy small {
            margin-top: 0.2rem;
            color: var(--agc-muted);
            font-size: 0.7rem;
        }
        .agc-brand-actions {
            display: flex;
            align-items: flex-end;
            flex-direction: column;
            gap: 0.3rem;
        }
        .agc-service-status {
            color: var(--agc-green-dark);
            font-size: 0.68rem;
            font-weight: 600;
        }
        .agc-classification {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.42rem 0.7rem;
            border: 1px solid #c3defa;
            border-radius: 999px;
            color: var(--agc-blue-dark);
            background: var(--agc-blue-tint);
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.08em;
        }
        .agc-classification-dot {
            width: 0.45rem;
            height: 0.45rem;
            border-radius: 50%;
            background: var(--agc-green);
            box-shadow: 0 0 0 3px rgba(56, 210, 0, 0.14);
        }
        .agc-stepper {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.6rem;
            margin: 0.35rem 0 0.75rem;
        }
        .agc-step {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            min-height: 3.15rem;
            padding: 0.5rem 0.75rem;
            background: var(--agc-surface);
            border: 1px solid var(--agc-border);
            border-radius: 12px;
            color: #737477;
        }
        .agc-step strong {
            display: block;
            color: inherit;
            font-weight: 600;
        }
        .agc-step span {
            font-size: 0.75rem;
        }
        .agc-step-number {
            display: grid;
            place-items: center;
            width: 1.75rem;
            height: 1.75rem;
            flex: 0 0 1.75rem;
            border-radius: 999px;
            background: #eef0f2;
            font-weight: 700;
        }
        .agc-step--active {
            border-color: #7bb6f5;
            background: var(--agc-blue-tint);
            color: var(--agc-blue-dark);
            box-shadow: 0 4px 14px rgba(4, 115, 234, 0.1);
        }
        .agc-step--active .agc-step-number {
            color: white;
            background: var(--agc-blue);
        }
        .agc-step--complete {
            color: var(--agc-green-dark);
            background: var(--agc-green-tint);
            border-color: #bcebab;
        }
        .agc-step--complete .agc-step-number {
            color: white;
            background: var(--agc-green-dark);
        }
        .agc-step--skipped {
            border-style: dashed;
            background: #f3f4f5;
            color: var(--agc-muted);
        }
        .agc-section-label {
            margin-bottom: -0.2rem;
            color: var(--agc-blue);
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.12em;
        }
        .agc-section-label::before {
            display: inline-block;
            width: 1.7rem;
            height: 3px;
            margin: 0 0.5rem 0.18rem 0;
            border-radius: 999px;
            content: "";
            background: linear-gradient(90deg, var(--agc-blue), var(--agc-green));
        }
        .agc-context-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.8rem 1rem;
            margin-top: 0.65rem;
        }
        .agc-context-item {
            min-width: 0;
        }
        .agc-context-item span {
            display: block;
            margin-bottom: 0.16rem;
            color: var(--agc-muted);
            font-size: 0.64rem;
            font-weight: 600;
            letter-spacing: 0.07em;
            text-transform: uppercase;
        }
        .agc-context-item strong {
            display: block;
            overflow: hidden;
            color: var(--agc-navy);
            font-size: 0.82rem;
            font-weight: 500;
            line-height: 1.25;
            text-overflow: ellipsis;
        }
        .agc-intake-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.65rem;
            margin: 0.35rem 0 0.15rem;
        }
        .agc-intake-card {
            min-width: 0;
            padding: 0.7rem 0.8rem;
            border: 1px solid var(--agc-border);
            border-radius: 10px;
            background: linear-gradient(180deg, #ffffff, #f7fbff);
        }
        .agc-intake-card span {
            display: block;
            margin-bottom: 0.18rem;
            color: var(--agc-muted);
            font-size: 0.6rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .agc-intake-card strong {
            display: block;
            color: var(--agc-navy);
            font-size: 0.78rem;
            font-weight: 600;
            line-height: 1.25;
        }
        .st-key-agc_primary_action {
            position: fixed;
            right: 2rem;
            bottom: 1.25rem;
            z-index: 999990;
            width: min(34rem, calc(100vw - 24rem));
            padding: 0.65rem;
            border: 1px solid #c3defa;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.96);
            backdrop-filter: blur(8px);
            box-shadow: 0 12px 32px rgba(0, 23, 46, 0.2);
        }
        [data-testid="stMainBlockContainer"] {
            padding-bottom: 9rem;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:has(h4) {
            max-height: 190px;
            overflow-y: auto;
            overscroll-behavior: contain;
        }
        [data-testid="stHeadingWithActionElements"] {
            margin-bottom: 0.15rem;
        }
        .agc-processing-overlay {
            position: fixed;
            inset: 0;
            z-index: 1000001;
            display: grid;
            place-items: center;
            padding: 1rem;
            background: rgba(0, 23, 46, 0.46);
            backdrop-filter: blur(7px);
            animation: agc-overlay-in 180ms ease-out both;
        }
        .agc-processing-card {
            width: min(31rem, calc(100vw - 2rem));
            padding: 1.6rem 1.75rem 1.4rem;
            border: 1px solid rgba(195, 222, 250, 0.9);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.98);
            box-shadow: 0 24px 70px rgba(0, 23, 46, 0.32);
            text-align: center;
        }
        .agc-processing-spinner {
            position: relative;
            width: 3.6rem;
            height: 3.6rem;
            margin: 0 auto 1rem;
        }
        .agc-processing-spinner::before,
        .agc-processing-spinner::after {
            position: absolute;
            border-radius: 50%;
            content: "";
        }
        .agc-processing-spinner::before {
            inset: 0;
            border: 5px solid var(--agc-blue-tint);
            border-top-color: var(--agc-blue);
            animation: agc-spin 900ms linear infinite;
        }
        .agc-processing-spinner::after {
            inset: 0.72rem;
            border: 4px solid var(--agc-green-tint);
            border-bottom-color: var(--agc-green);
            animation: agc-spin-reverse 700ms linear infinite;
        }
        .agc-processing-eyebrow {
            display: block;
            color: var(--agc-blue-dark);
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.12em;
        }
        .agc-processing-card h2 {
            margin: 0.4rem 0 0.45rem;
            color: var(--agc-navy);
            font-size: 1.35rem;
            font-weight: 500;
        }
        .agc-processing-card p {
            min-height: 1.5rem;
            margin: 0;
            color: var(--agc-muted);
            font-size: 0.88rem;
        }
        .agc-processing-progress {
            overflow: hidden;
            height: 0.38rem;
            margin: 1.15rem 0 0.55rem;
            border-radius: 999px;
            background: #e7edf3;
        }
        .agc-processing-progress span {
            position: relative;
            display: block;
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, var(--agc-blue), #008acb, var(--agc-green));
            transition: width 240ms ease;
        }
        .agc-processing-progress span::after {
            position: absolute;
            inset: 0;
            content: "";
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.65),
                transparent
            );
            transform: translateX(-100%);
            animation: agc-progress-shimmer 1.15s ease-in-out infinite;
        }
        .agc-processing-step {
            color: var(--agc-muted);
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.06em;
        }
        @keyframes agc-overlay-in {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        @keyframes agc-spin {
            to {
                transform: rotate(360deg);
            }
        }
        @keyframes agc-spin-reverse {
            to {
                transform: rotate(-360deg);
            }
        }
        @keyframes agc-progress-shimmer {
            to {
                transform: translateX(100%);
            }
        }
        @media (prefers-reduced-motion: reduce) {
            .agc-processing-overlay,
            .agc-processing-spinner::before,
            .agc-processing-spinner::after,
            .agc-processing-progress span::after {
                animation: none;
            }
        }
        @media (max-width: 800px) {
            .agc-stepper {
                grid-template-columns: 1fr;
            }
            .agc-brandbar {
                align-items: flex-start;
                grid-template-columns: 1fr;
                gap: 0.8rem;
            }
            .agc-product-copy {
                padding-top: 0.65rem;
                padding-left: 0;
                border-top: 1px solid var(--agc-border);
                border-left: 0;
            }
            .agc-brand-actions {
                align-items: flex-start;
            }
            .st-key-agc_primary_action {
                right: 1rem;
                bottom: 1rem;
                width: calc(100vw - 2rem);
            }
            .agc-context-grid {
                grid-template-columns: 1fr;
            }
            .agc-intake-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar(stage: str) -> None:
    stage_labels = {
        HOME_STAGE: "Choose workflow",
        CONTEXT_STAGE: "Project Context",
        DRAFT_STAGE: "Draft Solution Intent",
        INPUT_STAGE: "Review Inputs",
        REVIEW_STAGE: "Human Review",
        OUTPUT_STAGE: "Generated Outputs",
        DELIVERY_STAGE: "Work Item Delivery",
    }
    with st.sidebar:
        st.markdown("### Architecture Governance")
        st.caption("INTERNAL CONTROL WORKSPACE")
        st.markdown(f"**Current step**  \n{stage_labels[stage]}")
        st.divider()

        context = _current_context()
        project_context = st.session_state[PROJECT_CONTEXT_KEY]
        workflow = current_workflow(st.session_state)
        if workflow is Workflow.NONE:
            st.markdown("**Workflow**")
            st.caption("Choose drafting or governance review to begin.")
        elif workflow is Workflow.DRAFT:
            st.markdown("**Workflow**")
            st.write("Draft a Solution Intent")
            st.markdown("**Drafting context**")
        else:
            st.markdown("**Workflow**")
            st.write("Review a Solution Intent")
            st.markdown("**Review context**")

        if workflow is Workflow.DRAFT:
            if isinstance(project_context, DraftingSourceInventory):
                st.write(project_context.project_name)
                if st.session_state[PROJECT_CONTEXT_CONFIRMED_KEY] is True:
                    st.caption("Confirmed context package · ready for drafting")
                else:
                    st.caption("Workspace opened · confirmation required")
            else:
                st.caption("Open a demonstration project workspace to begin.")
        elif workflow is Workflow.REVIEW:
            if context is None:
                st.caption("Load or prepare a review package to initialize the review.")
            else:
                st.write(context.project_name)
                st.caption(
                    f"SI {context.si_version} · Round {context.review_round} · "
                    f"{context.ado_ticket_id or 'No governance ticket'}"
                )

        st.divider()
        st.markdown("**System status**")
        if st.session_state.get(REVIEW_POLICY_RECOVERY_KEY):
            st.warning("Review mode selection required")
            st.caption("Synthetic drafting remains available · no network")
        elif current_review_mode(st.session_state) is ReviewMode.INTERNAL_FAKE:
            st.warning("Internal fake mode · no network")
            st.caption("● Synthetic Confluence snapshot")
            st.caption("● Fake AIF analysis")
            st.caption("● Azure DevOps payload previews")
            st.caption("○ No live enterprise connections")
        else:
            st.success("Offline demo services ready")
            st.caption("● Synthetic data")
            st.caption("● Local processing")
            st.caption("● Azure DevOps payload previews")
            st.caption("○ No external connections")


def _render_step_progress(stage: str) -> None:
    workflow = current_workflow(st.session_state)
    stages = (
        [(CONTEXT_STAGE, "Project Context"), (DRAFT_STAGE, "Draft Solution Intent")]
        if workflow is Workflow.DRAFT
        else [
            (INPUT_STAGE, "Review Inputs"),
            (REVIEW_STAGE, "Human Review"),
            (OUTPUT_STAGE, "Generated Outputs"),
            (DELIVERY_STAGE, "Work Item Delivery"),
        ]
    )
    current_index = next(
        index for index, (stage_name, _) in enumerate(stages) if stage_name == stage
    )
    workflow_complete = delivery_outputs_available(st.session_state)
    step_cards: list[str] = []
    for index, (_, label) in enumerate(stages):
        context_complete = (
            workflow is Workflow.DRAFT
            and index == 0
            and st.session_state[PROJECT_CONTEXT_CONFIRMED_KEY] is True
        )
        draft_complete = (
            workflow is Workflow.DRAFT
            and index == 1
            and st.session_state[DRAFT_CONFIRMED_KEY] is True
        )
        if (
            context_complete
            or draft_complete
            or index < current_index
            or (workflow_complete and index < 3 and workflow is Workflow.REVIEW)
        ):
            status_class = "agc-step--complete"
            status = "Complete"
        elif index == current_index:
            status_class = "agc-step--active"
            status = "In progress"
        else:
            status_class = ""
            status = "Upcoming"
        if workflow is Workflow.REVIEW and index == 3:
            status_class = "agc-step--active" if stage == DELIVERY_STAGE else ""
            status = "Unavailable"
            if delivery_outputs_available(st.session_state):
                _, readiness, operations = _delivery_context(st.session_state[REVIEWED_RESULT_KEY])
                status = delivery_status(
                    readiness,
                    operations,
                    has_preview=isinstance(
                        st.session_state.get(ADO_PUBLICATION_PREVIEW_KEY), AdoPublicationPreview
                    ),
                ).value
            status_class = "agc-step--active" if stage == DELIVERY_STAGE else ""
        step_cards.append(
            f'<div class="agc-step {status_class}">'
            f'<div class="agc-step-number">{index + 1}</div>'
            f"<div><strong>{label}</strong><span>{status}</span></div>"
            "</div>"
        )
    st.markdown(
        f'<div class="agc-stepper">{"".join(step_cards)}</div>',
        unsafe_allow_html=True,
    )


def _render_readonly_markdown_document(
    content: str,
    *,
    source_label: str = "Markdown source",
    empty_message: str = "No Markdown document is loaded.",
) -> None:
    """Render a reader view alongside the exact, read-only Markdown source."""
    rendered_tab, source_tab = st.tabs(["Rendered", source_label])
    with rendered_tab, st.container(border=True):
        if content.strip():
            st.markdown(content)
        else:
            st.info(empty_message)
    with source_tab:
        st.code(content, language="markdown", wrap_lines=True)


def _workflow_action_button(
    label: str, *, target=None, floating: bool = True, download: bool = False, **kwargs
) -> bool:
    """Render the existing action once, optionally in the shared persistent action area."""
    target = st if target is None else target
    with target.container(key="agc_primary_action" if floating else None):
        if download:
            return st.download_button(label, **kwargs)
        return st.button(label, **kwargs)


def _render_project_context_stage() -> None:
    st.header("Drafting step 1 — Project Context")
    st.caption(
        "Open a project workspace, inspect the available source package, and explicitly "
        "confirm what may be used for Solution Intent drafting."
    )
    project_context = st.session_state[PROJECT_CONTEXT_KEY]
    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">PROJECT WORKSPACE</p>',
            unsafe_allow_html=True,
        )
        st.selectbox(
            "Demonstration project",
            ("Digital Payment Notification Service",),
            key="agc_project_workspace_selector",
            help="The PoC includes one frozen synthetic workspace for reliable demonstration.",
        )
        open_column, refresh_column, home_column, reset_column = st.columns([1.25, 1, 1.2, 1])
        open_clicked = open_column.button(
            "Open Demonstration Project",
            key="agc_open_demonstration_project",
            type="primary",
            width="stretch",
        )
        refresh_clicked = refresh_column.button(
            "Refresh Context",
            key="agc_refresh_project_context",
            disabled=not isinstance(project_context, DraftingSourceInventory),
            width="stretch",
        )
        home_clicked = home_column.button(
            "Choose another workflow",
            key="agc_choose_workflow_from_context",
            width="stretch",
        )
        reset_clicked = reset_column.button(
            "Reset drafting",
            key="agc_reset_project_context",
            width="stretch",
        )

    if home_clicked:
        _switch_stage(HOME_STAGE)
    if reset_clicked:
        reset_drafting_workflow(st.session_state)
        _switch_stage(CONTEXT_STAGE)
    if open_clicked:
        try:
            reset_drafting_workflow(st.session_state)
            open_demonstration_project_into_state(
                st.session_state,
                load_sample_drafting_context(),
            )
            st.session_state[DRAFT_EVIDENCE_KEY] = ()
        except (OSError, UnicodeError, ValueError) as exc:
            st.session_state[ERROR_KEY] = f"Unable to open project workspace: {exc}"
        else:
            st.rerun()
    if refresh_clicked:
        try:
            context_changed = refresh_project_context(st.session_state)
        except (OSError, UnicodeError, ValueError) as exc:
            st.session_state[ERROR_KEY] = f"Unable to refresh project context: {exc}"
        else:
            if context_changed:
                st.warning(
                    "Local source facts changed. Drafting confirmation and artifacts were "
                    "cleared; no external systems were contacted."
                )
            else:
                st.success(
                    "Local source facts are unchanged and validated. No external systems were "
                    "contacted."
                )

    project_context = st.session_state[PROJECT_CONTEXT_KEY]
    if not isinstance(project_context, DraftingSourceInventory):
        st.info(
            "No project workspace is open. Select Open Demonstration Project to initialize the "
            "synthetic source package."
        )
        return

    _render_project_context_summary(project_context)
    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">SOURCE SELECTION</p>',
            unsafe_allow_html=True,
        )
        resources = {resource.resource_id: resource for resource in project_context.resources}
        template_ids = tuple(
            resource.resource_id
            for resource in project_context.resources
            if resource.role is DraftingSourceRole.TEMPLATE
        )
        repository_ids = tuple(
            resource.resource_id
            for resource in project_context.resources
            if resource.role is DraftingSourceRole.REPOSITORY
        )
        st.session_state.setdefault(
            CONTEXT_TEMPLATE_WIDGET_KEY,
            st.session_state[CONTEXT_TEMPLATE_ID_KEY],
        )
        st.session_state.setdefault(
            CONTEXT_REPOSITORY_WIDGET_KEY,
            st.session_state[CONTEXT_REPOSITORY_ID_KEY],
        )
        st.session_state.setdefault(
            CONTEXT_EVIDENCE_WIDGET_KEY,
            list(st.session_state[CONTEXT_EVIDENCE_IDS_KEY]),
        )

        template_column, repository_column = st.columns(2)
        with template_column:
            st.selectbox(
                "Governed SI template",
                template_ids,
                disabled=True,
                key=CONTEXT_TEMPLATE_WIDGET_KEY,
                format_func=lambda resource_id: (
                    "Select a template"
                    if resource_id is None
                    else f"{resources[resource_id].display_name} · "
                    f"{resources[resource_id].revision}"
                ),
                help="Required and limited to the authorized synthetic inventory.",
            )
        with repository_column:
            st.markdown(
                "**Organization**  \nSynthetic Architecture · authorized synthetic inventory"
            )

        project_column, repository_column, revision_column = st.columns(3)
        with project_column:
            st.markdown(f"**Project**  \n{project_context.project_name}")
        with repository_column:
            repository_names = tuple(
                dict.fromkeys(resources[item].display_name for item in repository_ids)
            )
            current_name = st.session_state.get(DRAFT_REPOSITORY_NAME_KEY, repository_names[0])
            if current_name not in repository_names:
                current_name = repository_names[0]
            name_key = "agc_context_repository_name_widget"
            if st.session_state.get(name_key) not in repository_names:
                st.session_state[name_key] = current_name
            selected_name = st.selectbox(
                "Repository",
                repository_names,
                key=name_key,
                help="Synthetic inventory only; live ADO permission discovery is not connected.",
            )
            if selected_name != current_name:
                st.session_state[CONTEXT_REPOSITORY_WIDGET_KEY] = None
            st.session_state[DRAFT_REPOSITORY_NAME_KEY] = selected_name
        with revision_column:
            revision_ids = tuple(
                item for item in repository_ids if resources[item].display_name == selected_name
            )
            if st.session_state.get(CONTEXT_REPOSITORY_WIDGET_KEY) not in revision_ids:
                st.session_state[CONTEXT_REPOSITORY_WIDGET_KEY] = None
            st.selectbox(
                "Repository revision",
                (None, *revision_ids),
                key=CONTEXT_REPOSITORY_WIDGET_KEY,
                format_func=lambda resource_id: (
                    "Select a revision"
                    if resource_id is None
                    else f"{resources[resource_id].revision_kind.value.title()} · "
                    f"{resources[resource_id].revision}"
                ),
                help="Select a revision. The demo supports its bundled snapshot only.",
            )
        st.session_state[CONTEXT_TEMPLATE_ID_KEY] = st.session_state[CONTEXT_TEMPLATE_WIDGET_KEY]
        st.session_state[CONTEXT_REPOSITORY_ID_KEY] = st.session_state[
            CONTEXT_REPOSITORY_WIDGET_KEY
        ]

        with st.expander("SI Template", expanded=True):
            selected_template = _selected_drafting_resource(
                project_context, st.session_state[CONTEXT_TEMPLATE_ID_KEY]
            )
            if selected_template is None:
                st.info("No governed SI template is selected.")
            else:
                _render_readonly_markdown_document(selected_template.content)
                with st.expander("Template source details"):
                    _render_drafting_resource_identity(selected_template)

        with st.expander("Repository", expanded=True):
            selected_repository = _selected_drafting_resource(
                project_context, st.session_state[CONTEXT_REPOSITORY_ID_KEY]
            )
            if selected_repository is None:
                st.info("No repository revision is selected.")
            else:
                st.text(selected_repository.display_name)
                st.caption(
                    f"{selected_repository.revision_kind.value.title()}: "
                    f"{selected_repository.revision}"
                )
                st.code(selected_repository.content, language="text", wrap_lines=True)
                with st.expander("Repository source details"):
                    _render_drafting_resource_identity(selected_repository)

        _render_drafting_evidence_inputs()

        with st.expander("Governance Metadata", expanded=True):
            st.caption("Source-controlled and read-only · validated synthetic workspace")
            for label, value in (
                ("Project", project_context.project_name),
                ("Project ID", project_context.project_id),
                ("Governance reference", project_context.governance_reference),
            ):
                st.markdown(f"**{label}**")
                st.text(value)

        if update_live_drafting_source_package(st.session_state):
            st.rerun()

    _render_selected_source_package(st.session_state)

    blockers = project_context_readiness(st.session_state)
    if not drafting_evidence_is_saved(st.session_state):
        blockers += ("Save evidence before confirming the context.",)
    if blockers:
        st.warning("Context not ready: " + " ".join(blockers))
    else:
        refresh_status = (
            "Validated in this session"
            if st.session_state[PROJECT_CONTEXT_REFRESHED_KEY] is True
            else "Bundled sources ready for validation"
        )
        st.success(f"Context ready for drafting · {refresh_status}")

    with (
        st.container(key="agc_primary_action"),
        st.form("agc_project_context_confirmation_form", border=False),
    ):
        confirm_context = st.form_submit_button(
            "Confirm Context & Continue",
            key="agc_confirm_project_context",
            type="primary",
            disabled=bool(blockers),
            width="stretch",
        )

    if confirm_context and _confirm_project_context():
        _switch_stage(DRAFT_STAGE)


def _render_drafting_evidence_inputs() -> None:
    """Collect session-local evidence without treating user content as externally verified."""
    st.subheader("Supporting evidence")
    st.caption(
        "Add notes or upload UTF-8 TXT / Markdown documents, then inspect and edit their text. "
        "Use synthetic data only. User-provided content is not externally verified. "
        "Up to 10 items, 1 MiB per item."
    )
    st.session_state.setdefault(DRAFT_EVIDENCE_KEY, ())
    with st.container(horizontal=True):
        if st.button("Add notes", key="agc_evidence_add"):
            try:
                add_drafting_evidence(st.session_state)
            except ValueError as exc:
                st.error(str(exc))
        if st.button("Add sample evidence", key="agc_evidence_sample"):
            try:
                load_drafting_sample_evidence(st.session_state)
            except ValueError as exc:
                st.error(str(exc))
    uploaded = st.file_uploader(
        "Evidence documents",
        type=["txt", "md"],
        accept_multiple_files=True,
        max_upload_size=1,
        key="agc_evidence_upload",
    )
    if st.button("Add uploaded documents", key="agc_evidence_import", disabled=not uploaded):
        try:
            # Validate the complete import in a temporary state before applying any item.
            pending = {
                DRAFT_EVIDENCE_KEY: st.session_state[DRAFT_EVIDENCE_KEY],
                "agc_evidence_counter": st.session_state.get("agc_evidence_counter", 0),
            }
            for document in uploaded:
                add_drafting_evidence(pending, title=document.name, data=document.getvalue())
            st.session_state[DRAFT_EVIDENCE_KEY] = pending[DRAFT_EVIDENCE_KEY]
            st.session_state["agc_evidence_counter"] = pending["agc_evidence_counter"]
            update_live_drafting_source_package(st.session_state)
            st.success(
                "Uploaded text added. Review the content below before confirming the package."
            )
        except ValueError as exc:
            st.error(str(exc))
    for item in st.session_state[DRAFT_EVIDENCE_KEY]:
        with st.container(border=True):
            st.text(item.title)
            st.caption(f"Origin: {item.provenance.value} · {item.source_reference}")
            key = f"agc_evidence_text_{item.evidence_id}"
            if st.button("Remove evidence", key=f"agc_evidence_remove_{item.evidence_id}"):
                remove_drafting_evidence(st.session_state, item.evidence_id)
                st.session_state.pop(key, None)
                st.rerun()
            st.session_state.setdefault(key, item.text)
            text = st.text_area(
                "Evidence text", key=key, height=180, max_chars=1024 * 1024, persist_state="session"
            )
            if (text or "") != item.text:
                edit_drafting_evidence(st.session_state, item.evidence_id, text or "")

    if st.button("Save evidence", key="agc_evidence_save", type="primary"):
        try:
            save_drafting_evidence(st.session_state)
        except ValueError as exc:
            st.error(str(exc))
    if drafting_evidence_is_saved(st.session_state):
        st.success("Evidence saved for this session. You can confirm the context below.")
    else:
        st.info("Evidence not saved. Add or edit the text, then select Save evidence.")


def _render_project_context_summary(project_context: DraftingSourceInventory) -> None:
    """Render production-shaped metadata without implying live integrations."""
    values = (
        ("Project", project_context.project_name),
        ("Governance reference", project_context.governance_reference),
        ("Inventory", f"{len(project_context.resources)} authorized resources"),
        ("Provider", project_context.provider_configuration_identity),
    )
    cards = "".join(
        (
            '<div class="agc-intake-card">'
            f"<span>{escape(label)}</span>"
            f"<strong>{escape(value)}</strong>"
            "</div>"
        )
        for label, value in values
    )
    st.markdown(
        f'<div class="agc-intake-grid">{cards}</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Synthetic demonstration workspace · local fixture-backed sources · deterministic local "
        "validation · no authentication, synchronization, repository scan, or external API calls."
    )


def _selected_drafting_resource(
    inventory: DraftingSourceInventory,
    resource_id: object,
) -> DraftingSourceResource | None:
    """Return an authorized resource selected by its stable identifier."""
    return next(
        (resource for resource in inventory.resources if resource.resource_id == resource_id),
        None,
    )


def _render_drafting_resource_identity(resource: DraftingSourceResource) -> None:
    """Show exact local identity and validation without implying external access."""
    st.caption(
        f"{resource.source_reference} · {resource.revision_kind.value} "
        f"{resource.revision} · validated local fixture"
    )
    st.code(f"SHA-256 {resource.content_fingerprint}", language="text", wrap_lines=True)


def _render_selected_source_package(state: Mapping[str, object]) -> None:
    """Render the exact manifest that the user will confirm."""
    st.subheader("Selected Source Package")
    try:
        manifest = build_drafting_source_package(state)
    except ValueError:
        st.info("Complete the required authorized selections to build the exact manifest.")
        return
    st.caption(
        "Synthetic offline manifest · human confirmation records drafting inputs only; it is "
        "not architecture approval and contacts no external system."
    )
    with st.expander("Inspect exact source-package manifest"):
        st.json(manifest.model_dump(mode="json"))


def _render_drafting_stage() -> None:
    st.header("Drafting step 2 — Draft Solution Intent")
    st.caption("Generate an editable SI draft from the human-confirmed Project Context package.")
    draft_available = isinstance(st.session_state[DRAFT_RESULT_KEY], SolutionIntentDraft)
    drafting_context_ready = all(
        isinstance(value, str) and value.strip()
        for value in (
            st.session_state[DRAFT_PROJECT_KEY],
            st.session_state[DRAFT_TEMPLATE_KEY],
            st.session_state[DRAFT_SOURCE_CODE_KEY],
        )
    ) and isinstance(
        st.session_state[CONFIRMED_SOURCE_PACKAGE_KEY],
        DraftingSourcePackageManifest,
    )

    generation_blockers = project_context_readiness(st.session_state, check_provider=True)
    for blocker in generation_blockers:
        st.warning(blocker)

    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">DRAFTING ACTIONS</p>',
            unsafe_allow_html=True,
        )
        generate_column, home_column, context_column, reset_column = st.columns(
            [1.2, 1.25, 1.15, 1],
        )
        generate_clicked = _workflow_action_button(
            "Regenerate SI Draft" if draft_available else "Generate SI Draft",
            target=generate_column,
            floating=not draft_available,
            key="agc_generate_si_draft",
            type="primary",
            disabled=not drafting_context_ready or bool(generation_blockers),
            help=(
                "Provide a project name, SI template, and source-code context before "
                "generating a draft."
            ),
            width="stretch",
        )
        home_clicked = home_column.button(
            "Choose another workflow",
            key="agc_choose_workflow_from_drafting",
            width="stretch",
        )
        back_clicked = context_column.button(
            "Back to Project Context",
            key="agc_back_to_project_context",
            width="stretch",
        )
        reset_clicked = reset_column.button(
            "Reset drafting",
            key="agc_reset_drafting",
            width="stretch",
        )

    if home_clicked:
        _switch_stage(HOME_STAGE)
    if back_clicked:
        _switch_stage(CONTEXT_STAGE)
    if reset_clicked:
        reset_drafting_workflow(st.session_state)
        _switch_stage(CONTEXT_STAGE)

    st.session_state.setdefault(
        DRAFT_PROJECT_WIDGET_KEY,
        st.session_state[DRAFT_PROJECT_KEY],
    )
    st.session_state.setdefault(
        DRAFT_TEMPLATE_WIDGET_KEY,
        st.session_state[DRAFT_TEMPLATE_KEY],
    )
    st.session_state.setdefault(
        DRAFT_SOURCE_CODE_WIDGET_KEY,
        st.session_state[DRAFT_SOURCE_CODE_KEY],
    )
    st.session_state.setdefault(
        DRAFT_SUPPORTING_DOCS_WIDGET_KEY,
        st.session_state[DRAFT_SUPPORTING_DOCS_KEY],
    )

    draft = st.session_state[DRAFT_RESULT_KEY]
    if isinstance(draft, SolutionIntentDraft):
        try:
            current_request = SolutionIntentDraftRequest(
                project_name=st.session_state[DRAFT_PROJECT_KEY],
                template=st.session_state[DRAFT_TEMPLATE_KEY],
                source_code_context=st.session_state[DRAFT_SOURCE_CODE_KEY],
                supporting_documents=st.session_state[DRAFT_SUPPORTING_DOCS_KEY] or None,
            )
            stale_draft = drafting_result_is_stale(
                current_request,
                st.session_state[DRAFT_FINGERPRINT_KEY],
                st.session_state[CONFIRMED_SOURCE_PACKAGE_KEY],
            )
        except ValidationError:
            stale_draft = True
        if stale_draft:
            clear_stale_si_draft(st.session_state)
            st.warning(
                "Drafting context changed after generation. Generate a new SI draft before "
                "human confirmation."
            )
        else:
            if generate_clicked and _generate_si_draft():
                st.rerun()
            _render_generated_si_draft(draft)
            return

    project_name = st.text_input(
        "Project name",
        key=DRAFT_PROJECT_WIDGET_KEY,
        disabled=True,
    )
    if drafting_context_ready:
        _render_drafting_context_snapshot(
            template=st.session_state[DRAFT_TEMPLATE_WIDGET_KEY],
            source_code_context=st.session_state[DRAFT_SOURCE_CODE_WIDGET_KEY],
            supporting_documents=st.session_state[DRAFT_SUPPORTING_DOCS_WIDGET_KEY],
        )
    template_tab, source_tab, documents_tab = st.tabs(
        ["SI Template Snapshot", "Selected Repository Context", "Supporting Evidence"]
    )
    with template_tab:
        template = str(st.session_state[DRAFT_TEMPLATE_WIDGET_KEY])
        rendered_tab, markdown_tab = st.tabs(["Rendered", "Markdown source"])
        with rendered_tab, st.container(border=True):
            st.markdown(template)
        with markdown_tab:
            template = st.text_area(
                "SI template Markdown source",
                key=DRAFT_TEMPLATE_WIDGET_KEY,
                height=280,
                disabled=True,
            )
    with source_tab:
        source_code_context = st.text_area(
            "Selected source-code context",
            key=DRAFT_SOURCE_CODE_WIDGET_KEY,
            height=280,
            disabled=True,
        )
    with documents_tab:
        supporting_documents = str(st.session_state[DRAFT_SUPPORTING_DOCS_WIDGET_KEY])
        rendered_tab, markdown_tab = st.tabs(["Rendered", "Markdown source"])
        with rendered_tab, st.container(border=True):
            st.markdown(supporting_documents)
        with markdown_tab:
            supporting_documents = st.text_area(
                "Supporting-document Markdown source",
                key=DRAFT_SUPPORTING_DOCS_WIDGET_KEY,
                height=280,
                disabled=True,
            )

    st.session_state[DRAFT_PROJECT_KEY] = project_name
    st.session_state[DRAFT_TEMPLATE_KEY] = template
    st.session_state[DRAFT_SOURCE_CODE_KEY] = source_code_context
    st.session_state[DRAFT_SUPPORTING_DOCS_KEY] = supporting_documents

    if generate_clicked and _generate_si_draft():
        st.rerun()

    st.info(
        "No SI draft has been generated. Inspect the confirmed context package, then select "
        "Generate SI Draft."
    )


def _render_generated_si_draft(draft: SolutionIntentDraft) -> None:
    """Prioritize the generated draft while keeping its sources available on demand."""
    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">HUMAN REVIEW</p>',
            unsafe_allow_html=True,
        )
        st.markdown("### Proposed Solution Intent")
        draft_confirmed = st.session_state[DRAFT_CONFIRMED_KEY] is True
        if not draft_confirmed:
            editor_tab, preview_tab = st.tabs(["Markdown editor", "Rendered preview"])
            with editor_tab:
                reviewed_content = st.text_area(
                    "Human-reviewed SI draft Markdown",
                    key=DRAFT_CONTENT_WIDGET_KEY,
                    height=500,
                )
            with preview_tab, st.container(border=True):
                st.markdown(reviewed_content)
            submitted = _workflow_action_button(
                "Confirm SI draft",
                key="agc_confirm_si_draft",
                type="primary",
                width="stretch",
            )
            if submitted and _confirm_si_draft(reviewed_content):
                st.rerun()
        else:
            reviewed_content = str(st.session_state[DRAFT_CONTENT_WIDGET_KEY])
            rendered_tab, source_tab = st.tabs(["Rendered", "Markdown source"])
            with rendered_tab, st.container(border=True):
                st.markdown(reviewed_content)
            with source_tab:
                reviewed_content = st.text_area(
                    "Confirmed SI draft Markdown source",
                    key=DRAFT_CONTENT_WIDGET_KEY,
                    height=500,
                    disabled=True,
                )
            st.success("Draft confirmed by the user. It has not been published to Confluence.")
            provenance = {
                "project": draft.project_name,
                "provider": draft.provider_name,
                "source_package_fingerprint": st.session_state[DRAFT_FINGERPRINT_KEY],
                "publication_status": "not_published",
            }
            with st.expander("Draft provenance", expanded=True):
                st.json(provenance)
            action_column, review_column = st.columns(2)
            _workflow_action_button(
                "Download confirmed Markdown",
                target=action_column,
                download=True,
                data=reviewed_content,
                file_name="confirmed-solution-intent.md",
                mime="text/markdown",
                key="agc_download_confirmed_si",
                icon=":material/download:",
                width="stretch",
            )
            if review_column.button(
                "Start a separate review",
                key="agc_start_separate_review",
                icon=":material/fact_check:",
                width="stretch",
            ):
                reset_review_workflow(st.session_state)
                _switch_stage(INPUT_STAGE)

        st.caption(
            f"Provider: {draft.provider_name}. Generation is a drafting aid, not architecture "
            "approval or publication."
        )
        if not draft_confirmed:
            st.info(
                "Review and edit the draft before confirming it for manual transfer. Governance "
                "review starts separately from an authoritative SI snapshot."
            )
        with st.expander("Draft assumptions and safeguards"):
            for assumption in draft.assumptions:
                st.write(f"- {assumption}")

    with st.expander("View drafting sources"):
        st.text_input(
            "Project name",
            key=DRAFT_PROJECT_WIDGET_KEY,
            disabled=True,
        )
        _render_drafting_context_snapshot(
            template=st.session_state[DRAFT_TEMPLATE_KEY],
            source_code_context=st.session_state[DRAFT_SOURCE_CODE_KEY],
            supporting_documents=st.session_state[DRAFT_SUPPORTING_DOCS_KEY],
        )
        template_tab, source_tab, documents_tab = st.tabs(
            ["SI Template Snapshot", "Selected Repository Context", "Supporting Evidence"]
        )
        with template_tab:
            template = str(st.session_state[DRAFT_TEMPLATE_KEY])
            rendered_tab, markdown_tab = st.tabs(["Rendered", "Markdown source"])
            with rendered_tab, st.container(border=True):
                st.markdown(template)
            with markdown_tab:
                st.text_area(
                    "SI template Markdown source",
                    key=DRAFT_TEMPLATE_WIDGET_KEY,
                    height=280,
                    disabled=True,
                )
        with source_tab:
            st.text_area(
                "Selected source-code context",
                key=DRAFT_SOURCE_CODE_WIDGET_KEY,
                height=280,
                disabled=True,
            )
        with documents_tab:
            supporting_documents = str(st.session_state[DRAFT_SUPPORTING_DOCS_KEY])
            rendered_tab, markdown_tab = st.tabs(["Rendered", "Markdown source"])
            with rendered_tab, st.container(border=True):
                st.markdown(supporting_documents)
            with markdown_tab:
                st.text_area(
                    "Supporting-document Markdown source",
                    key=DRAFT_SUPPORTING_DOCS_WIDGET_KEY,
                    height=280,
                    disabled=True,
                )


def _render_drafting_context_snapshot(
    *,
    template: str,
    source_code_context: str,
    supporting_documents: str,
) -> None:
    """Render a concise, synthetic inventory of the loaded drafting context."""
    chapter_count = sum(line.startswith("## ") for line in template.splitlines())
    artifact_count = sum(
        line.startswith("- src/") or line.startswith("- deploy/")
        for line in source_code_context.splitlines()
    )
    evidence_domain_count = sum(
        line.startswith("## ") for line in supporting_documents.splitlines()
    )
    values = (
        ("Workspace", "Enterprise SI template snapshot"),
        ("Template coverage", f"{chapter_count} governed chapters detected"),
        ("Engineering context", f"{artifact_count} selected repository artefacts"),
        ("Supporting evidence", f"{evidence_domain_count} context domains supplied"),
    )
    cards = "".join(
        (
            '<div class="agc-intake-card">'
            f"<span>{escape(label)}</span>"
            f"<strong>{escape(value)}</strong>"
            "</div>"
        )
        for label, value in values
    )
    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">CONTEXT PACKAGE</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="agc-intake-grid">{cards}</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Synthetic local snapshot · no Confluence connection, repository scan, or external "
            "document retrieval occurs in demo mode."
        )


def _confirm_project_context() -> bool:
    """Validate and confirm the selected local source package with visible progress."""
    processing_overlay = st.empty()
    try:
        processing_overlay.markdown(
            _processing_overlay_markup(
                "PROJECT CONTEXT",
                "Validating selected sources",
                "Checking required sources and local fixture availability.",
                step=1,
                total_steps=3,
            ),
            unsafe_allow_html=True,
        )
        with st.status("Preparing drafting context...", expanded=True) as status:
            st.write("Required SI template and repository context selected")
            _demo_pause()
            processing_overlay.markdown(
                _processing_overlay_markup(
                    "PROJECT CONTEXT",
                    "Building context manifest",
                    "Recording source selections and provenance for this session.",
                    step=2,
                    total_steps=3,
                ),
                unsafe_allow_html=True,
            )
            st.write("Synthetic source manifest prepared")
            _demo_pause()
            processing_overlay.markdown(
                _processing_overlay_markup(
                    "PROJECT CONTEXT",
                    "Opening drafting workspace",
                    "Handing the confirmed context package to Solution Intent drafting.",
                    step=3,
                    total_steps=3,
                ),
                unsafe_allow_html=True,
            )
            confirm_project_context_for_drafting(st.session_state)
            st.write("Confirmed context package ready for drafting")
            status.update(
                label="Context confirmed — opening Solution Intent drafting",
                state="complete",
                expanded=True,
            )
            _demo_pause()
    except ValueError as exc:
        st.session_state[ERROR_KEY] = f"Unable to confirm project context: {exc}"
        return False
    finally:
        processing_overlay.empty()
    return True


def _confirm_si_draft(reviewed_content: str) -> bool:
    processing_overlay = st.empty()
    try:
        processing_overlay.markdown(
            _processing_overlay_markup(
                "CONFIRM SOLUTION INTENT",
                "Validating reviewed draft",
                "Checking the human-reviewed Solution Intent before manual transfer.",
                step=1,
                total_steps=2,
            ),
            unsafe_allow_html=True,
        )
        with st.status("Confirming Solution Intent...", expanded=True) as status:
            st.write("Human-reviewed draft ready for validation")
            _demo_pause()
            processing_overlay.markdown(
                _processing_overlay_markup(
                    "CONFIRM SOLUTION INTENT",
                    "Preparing confirmed artifact",
                    "Preserving the draft and its local provenance without publishing it.",
                    step=2,
                    total_steps=2,
                ),
                unsafe_allow_html=True,
            )
            confirm_si_draft_for_review(
                st.session_state,
                reviewed_content,
                sync_widget=False,
            )
            st.write("Confirmed draft preserved for manual transfer")
            status.update(
                label="SI draft confirmed — not published",
                state="complete",
                expanded=True,
            )
            _demo_pause()
    except ValueError as exc:
        st.session_state[ERROR_KEY] = f"Unable to confirm SI draft: {exc}"
        return False
    finally:
        processing_overlay.empty()
    return True


def _generate_si_draft() -> bool:
    processing_overlay = st.empty()
    try:
        request = SolutionIntentDraftRequest(
            project_name=st.session_state[DRAFT_PROJECT_KEY],
            template=st.session_state[DRAFT_TEMPLATE_KEY],
            source_code_context=st.session_state[DRAFT_SOURCE_CODE_KEY],
            supporting_documents=st.session_state[DRAFT_SUPPORTING_DOCS_KEY] or None,
        )
        processing_overlay.markdown(
            _processing_overlay_markup(
                "DRAFT SOLUTION INTENT",
                "Validating drafting context",
                "Checking the template, selected code context, and supporting notes.",
                step=1,
                total_steps=3,
            ),
            unsafe_allow_html=True,
        )
        with st.status("Preparing Solution Intent draft...", expanded=True) as status:
            st.write("Drafting inputs validated")
            _demo_pause()
            processing_overlay.markdown(
                _processing_overlay_markup(
                    "DRAFT SOLUTION INTENT",
                    "Structuring architecture content",
                    "Mapping the confirmed inputs into the required SI sections.",
                    step=2,
                    total_steps=3,
                ),
                unsafe_allow_html=True,
            )
            service = SolutionIntentDraftingService(DeterministicDemoDrafter())
            draft = service.generate_draft(request)
            st.write("Confirmed inputs and explicit gaps mapped into the SI structure")
            _demo_pause()
            processing_overlay.markdown(
                _processing_overlay_markup(
                    "DRAFT SOLUTION INTENT",
                    "Preparing human review",
                    "Creating an editable draft without publishing it.",
                    step=3,
                    total_steps=3,
                ),
                unsafe_allow_html=True,
            )
            store_si_draft(
                st.session_state,
                draft,
                drafting_input_fingerprint(
                    request,
                    st.session_state[CONFIRMED_SOURCE_PACKAGE_KEY],
                ),
            )
            st.write("Editable SI draft prepared")
            status.update(
                label="Draft ready — human confirmation required",
                state="complete",
                expanded=True,
            )
            _demo_pause()
    except (
        DeterministicDraftingFixtureError,
        ValidationError,
        ValueError,
    ) as exc:
        st.session_state[ERROR_KEY] = f"Draft generation failed: {exc}"
        return False
    finally:
        processing_overlay.empty()
    return True


def _render_review_mode_control() -> None:
    descriptors = available_review_modes()
    available_values = [descriptor.mode.value for descriptor in descriptors]
    current_mode = current_review_mode(st.session_state)
    current_descriptor = next(
        descriptor for descriptor in descriptors if descriptor.mode is current_mode
    )
    if (
        st.session_state.get(REVIEW_PROVIDER_CONFIGURATION_ID_KEY)
        != current_descriptor.provider_configuration_identity
    ):
        switch_review_mode(
            st.session_state,
            current_mode,
            current_descriptor.provider_configuration_identity,
        )

    widget_value = st.session_state.get(REVIEW_MODE_WIDGET_KEY)
    if widget_value not in available_values:
        st.session_state[REVIEW_MODE_WIDGET_KEY] = current_mode.value

    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">REVIEW MODE</p>',
            unsafe_allow_html=True,
        )
        if len(descriptors) == 1:
            st.text(f"Review capability: {current_descriptor.label}")
        else:
            selected_value = st.segmented_control(
                "Review source and analysis mode",
                options=available_values,
                format_func=lambda value: next(
                    descriptor.label for descriptor in descriptors if descriptor.mode.value == value
                ),
                key=REVIEW_MODE_WIDGET_KEY,
                required=True,
            )
            selected_mode = ReviewMode(selected_value or current_mode.value)
            if selected_mode is not current_mode:
                selected_descriptor = next(
                    descriptor for descriptor in descriptors if descriptor.mode is selected_mode
                )
                switch_review_mode(
                    st.session_state,
                    selected_mode,
                    selected_descriptor.provider_configuration_identity,
                )
                st.rerun()
        if current_mode is ReviewMode.INTERNAL_FAKE:
            st.warning(
                "Configured fake only · Confluence and AIF operations remain local and make no "
                "network requests."
            )
        else:
            st.caption(
                "Zero-configuration deterministic mode · no credentials, network, or enterprise "
                "connections."
            )


def _load_internal_review_source() -> bool:
    """Invoke configured fake source dependencies only for an explicit load or refresh."""
    try:
        runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE)
        if (
            runtime.confluence_reader is None
            or runtime.confluence_page_id is None
            or runtime.review_transcript is None
            or runtime.review_context is None
        ):
            raise ValueError("The fake internal review package is incomplete.")
        snapshot = runtime.confluence_reader.get_page(runtime.confluence_page_id)
        load_internal_review_into_state(
            st.session_state,
            snapshot=snapshot,
            transcript=runtime.review_transcript,
            context=runtime.review_context,
            provider_configuration_identity=(runtime.descriptor.provider_configuration_identity),
        )
    except ConfluenceReadError as exc:
        record_internal_source_load_failure(st.session_state)
        st.session_state[ERROR_KEY] = f"Fake Confluence source load failed: {exc}"
        return False
    except (OSError, UnicodeError, ValidationError, ValueError):
        record_internal_source_load_failure(st.session_state)
        st.session_state[ERROR_KEY] = (
            "Fake internal review configuration is invalid. No previous source remains eligible."
        )
        return False
    return True


def _render_input_stage(*, restore_input_widgets: bool = False) -> None:
    st.header("Review step 1 — Review Inputs")
    st.caption(
        "Prepare an authoritative SI snapshot, a transcript, and review metadata in any order. "
        "Confirm the exact package before analysis."
    )
    _render_review_mode_control()
    review_mode = current_review_mode(st.session_state)
    source_loaded = isinstance(
        st.session_state.get(CONFLUENCE_SNAPSHOT_KEY), ConfluencePageSnapshot
    )
    if restore_input_widgets:
        st.session_state[SOLUTION_INTENT_WIDGET_KEY] = st.session_state[SOLUTION_INTENT_KEY]
        st.session_state[TRANSCRIPT_WIDGET_KEY] = st.session_state[TRANSCRIPT_KEY]

    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">ACQUIRE REVIEW INPUTS</p>',
            unsafe_allow_html=True,
        )
        source_column, transcript_column, metadata_column = st.columns(3)
        source_clicked = source_column.button(
            ("Refresh fake Confluence SI" if source_loaded else "Load fake Confluence SI")
            if review_mode is ReviewMode.INTERNAL_FAKE
            else (
                "Refresh authoritative SI snapshot"
                if source_loaded
                else "Load authoritative SI snapshot"
            ),
            key="agc_load_review_source",
            icon=":material/article:",
            width="stretch",
        )
        transcript_clicked = transcript_column.button(
            "Load synthetic transcript",
            key="agc_load_review_transcript",
            icon=":material/notes:",
            width="stretch",
        )
        metadata_clicked = metadata_column.button(
            "Load synthetic metadata",
            key="agc_load_review_metadata",
            icon=":material/dataset:",
            width="stretch",
        )
        utility_column, reset_column = st.columns(2)
        home_clicked = utility_column.button(
            "Choose another workflow",
            key="agc_choose_workflow_from_review",
            width="stretch",
        )
        reset_clicked = reset_column.button(
            "Reset review",
            key="agc_reset_review",
            width="stretch",
        )

        if source_clicked and _load_review_source_component(review_mode):
            st.rerun()
        if transcript_clicked and _load_review_transcript_component(review_mode):
            st.rerun()
        if metadata_clicked and _load_review_metadata_component(review_mode):
            st.rerun()
        if home_clicked:
            _switch_stage(HOME_STAGE)
        if reset_clicked:
            reset_review_workflow(st.session_state)
            _switch_stage(INPUT_STAGE)
        feedback = st.session_state.get(REVIEW_INPUT_FEEDBACK_KEY)
        if isinstance(feedback, str) and feedback:
            st.success(feedback)

    snapshot = st.session_state.get(CONFLUENCE_SNAPSHOT_KEY)
    context = _current_context()
    st.session_state.setdefault(
        SOLUTION_INTENT_WIDGET_KEY,
        st.session_state[SOLUTION_INTENT_KEY],
    )
    st.session_state.setdefault(
        TRANSCRIPT_WIDGET_KEY,
        st.session_state[TRANSCRIPT_KEY],
    )
    si_tab, transcript_tab, metadata_tab = st.tabs(
        ["Authoritative SI", "Review transcript", "Review metadata"]
    )
    with si_tab:
        st.selectbox(
            "Authorized synthetic SI source",
            (
                "Synthetic Order Routing Service · fake Confluence"
                if review_mode is ReviewMode.INTERNAL_FAKE
                else "Digital Payment Notification Service · authoritative snapshot",
            ),
            disabled=True,
        )
        if isinstance(snapshot, ConfluencePageSnapshot):
            st.caption(
                f"Validated · {snapshot.space} · page {snapshot.page_id} · version "
                f"{snapshot.version} · retrieved {snapshot.retrieved_at.isoformat()}"
            )
            st.caption(
                f"Canonicalizer {snapshot.canonicalizer_version} · content fingerprint "
                f"{snapshot.content_fingerprint}"
            )
        solution_intent = str(st.session_state[SOLUTION_INTENT_WIDGET_KEY])
        rendered_tab, source_tab = st.tabs(["Rendered", "Canonical Markdown source"])
        with rendered_tab, st.container(border=True):
            if solution_intent.strip():
                st.markdown(solution_intent)
            else:
                st.info("Load the authorized synthetic SI snapshot to begin.")
        with source_tab:
            st.text_area(
                "Authoritative SI canonical Markdown source",
                key=SOLUTION_INTENT_WIDGET_KEY,
                height=315,
                placeholder="Load the authorized synthetic SI snapshot to begin.",
                disabled=True,
            )
    with transcript_tab:
        st.caption(
            "Paste user-provided content or load the bundled synthetic transcript. Recommended "
            "format: [timestamp] Speaker: text. Missing locators are never invented."
        )
        transcript = st.text_area(
            "User-provided review transcript",
            key=TRANSCRIPT_WIDGET_KEY,
            height=315,
            placeholder="Paste a review transcript or load the synthetic example.",
        )
    with metadata_tab:
        _render_review_metadata_editor(context)

    stored_transcript = st.session_state.get(TRANSCRIPT_KEY)
    if isinstance(transcript, str) and transcript != stored_transcript:
        existing_provenance = st.session_state.get(TRANSCRIPT_PROVENANCE_KEY)
        establish_baseline = existing_provenance is None and bool(transcript.strip())
        provenance = (
            ReviewInputProvenance.USER_ENTERED
            if existing_provenance is None
            else ReviewInputProvenance(existing_provenance)
        )
        store_transcript_component(
            st.session_state,
            transcript,
            provenance,
            establish_baseline=establish_baseline,
            sync_widget=False,
            feedback=(
                "User-provided transcript stored; review package confirmation is required."
                if establish_baseline
                else "Transcript edited after load; review package confirmation was revoked."
            ),
        )
        st.rerun()

    readiness = review_input_readiness(st.session_state)
    _render_review_input_readiness(readiness)
    action_column, analyze_column = st.columns(2)
    confirm_clicked = _workflow_action_button(
        "Confirm review input manifest",
        target=action_column,
        floating=not readiness.confirmed,
        key="agc_confirm_review_inputs",
        type="primary" if not readiness.confirmed else "secondary",
        disabled=not readiness.ready_to_confirm or readiness.confirmed,
        help="Complete all three review-input components before confirmation.",
        width="stretch",
    )
    analyze_clicked = _workflow_action_button(
        "Analyze with Fake AIF" if review_mode is ReviewMode.INTERNAL_FAKE else "Analyze review",
        target=analyze_column,
        floating=readiness.confirmed,
        key="agc_analyze",
        type="primary",
        disabled=not readiness.ready_to_analyze,
        help=(
            "Confirm the exact complete review input manifest before analysis."
            if not readiness.ready_to_analyze
            else None
        ),
        width="stretch",
    )
    if confirm_clicked:
        try:
            confirm_review_input_manifest(st.session_state)
        except (ValidationError, ValueError) as exc:
            st.session_state[ERROR_KEY] = f"Unable to confirm review inputs: {exc}"
        else:
            st.rerun()

    processing_placeholder = st.empty()
    if analyze_clicked:
        with processing_placeholder.container():
            if _analyze_current_inputs():
                _switch_stage(REVIEW_STAGE)

    analyzed_result = st.session_state[ANALYZED_RESULT_KEY]
    if isinstance(analyzed_result, GovernanceResult):
        invalidation = current_analysis_invalidation(st.session_state)
        if invalidation is not None:
            _render_invalidation_notice(invalidation)
        elif st.button(
            "Return to Human Review",
            key="agc_return_to_review",
            width="stretch",
        ):
            _switch_stage(REVIEW_STAGE)


def _load_review_source_component(mode: ReviewMode) -> bool:
    """Load only the authoritative SI component for the selected review mode."""
    try:
        if mode is ReviewMode.INTERNAL_FAKE:
            runtime = build_review_runtime(mode)
            if runtime.confluence_reader is None or runtime.confluence_page_id is None:
                raise ValueError("The fake Confluence source is not configured.")
            snapshot = runtime.confluence_reader.get_page(runtime.confluence_page_id)
            st.session_state[REVIEW_PROVIDER_CONFIGURATION_ID_KEY] = (
                runtime.descriptor.provider_configuration_identity
            )
            feedback = "Fake Confluence SI snapshot loaded; transcript and metadata are unchanged."
        else:
            sample = load_sample_review()
            snapshot = build_sample_review_snapshot(sample)
            feedback = (
                "Authoritative synthetic SI snapshot loaded; transcript and metadata are unchanged."
            )
        store_review_source_snapshot(st.session_state, snapshot, feedback=feedback)
    except ConfluenceReadError as exc:
        record_internal_source_load_failure(st.session_state)
        st.session_state[ERROR_KEY] = f"Unable to load the authoritative SI source: {exc}"
        return False
    except (OSError, UnicodeError, ValidationError, ValueError) as exc:
        st.session_state[ERROR_KEY] = f"Unable to load the authoritative SI source: {exc}"
        return False
    return True


def _load_review_transcript_component(mode: ReviewMode) -> bool:
    """Load only the synthetic transcript component for the selected mode."""
    try:
        if mode is ReviewMode.INTERNAL_FAKE:
            runtime = build_review_runtime(mode)
            transcript = runtime.review_transcript
            provenance = ReviewInputProvenance.INTERNAL_FAKE
        else:
            transcript = load_sample_review().transcript
            provenance = ReviewInputProvenance.SYNTHETIC_SAMPLE
        if not isinstance(transcript, str) or not transcript.strip():
            raise ValueError("The configured synthetic transcript is empty.")
        store_transcript_component(
            st.session_state,
            transcript,
            provenance,
            establish_baseline=True,
            feedback="Synthetic transcript loaded; SI source and metadata are unchanged.",
        )
    except (OSError, UnicodeError, ValidationError, ValueError) as exc:
        st.session_state[ERROR_KEY] = f"Unable to load the review transcript: {exc}"
        return False
    return True


def _load_review_metadata_component(mode: ReviewMode) -> bool:
    """Load only validated synthetic review metadata for the selected mode."""
    try:
        if mode is ReviewMode.INTERNAL_FAKE:
            runtime = build_review_runtime(mode)
            context = runtime.review_context
            provenance = ReviewInputProvenance.INTERNAL_FAKE
        else:
            context = load_sample_review().context
            provenance = ReviewInputProvenance.SYNTHETIC_SAMPLE
        if not isinstance(context, SolutionIntentReviewContext):
            raise ValueError("The configured review metadata is missing.")
        store_metadata_component(
            st.session_state,
            context,
            provenance,
            establish_baseline=True,
            feedback="Synthetic review metadata loaded; SI source and transcript are unchanged.",
        )
    except (OSError, UnicodeError, ValidationError, ValueError) as exc:
        st.session_state[ERROR_KEY] = f"Unable to load review metadata: {exc}"
        return False
    return True


def _render_review_metadata_editor(
    context: SolutionIntentReviewContext | None,
) -> None:
    """Render source-controlled identity separately from editable round metadata."""
    if context is None:
        st.info("Load synthetic metadata in any order to initialize the review round.")
        return
    st.caption(
        f"Source-controlled · {context.project_name} · {context.si_title} · SI "
        f"{context.si_version} · {humanize(context.current_si_status.value)}"
    )
    st.session_state.setdefault(METADATA_REVIEW_ROUND_WIDGET_KEY, context.review_round)
    st.session_state.setdefault(METADATA_REVIEW_DATE_WIDGET_KEY, context.review_date)
    st.session_state.setdefault(METADATA_ARCHITECT_WIDGET_KEY, context.domain_architect or "")
    st.session_state.setdefault(METADATA_TICKET_WIDGET_KEY, context.ado_ticket_id or "")
    st.number_input(
        "Review round",
        min_value=1,
        step=1,
        key=METADATA_REVIEW_ROUND_WIDGET_KEY,
    )
    st.date_input(
        "Review date",
        key=METADATA_REVIEW_DATE_WIDGET_KEY,
    )
    st.text_input("Domain Architect", key=METADATA_ARCHITECT_WIDGET_KEY)
    st.text_input("Governance ticket", key=METADATA_TICKET_WIDGET_KEY)
    try:
        edited_context = context.model_copy(
            update={
                "review_round": st.session_state[METADATA_REVIEW_ROUND_WIDGET_KEY],
                "review_date": st.session_state[METADATA_REVIEW_DATE_WIDGET_KEY],
                "domain_architect": (
                    st.session_state[METADATA_ARCHITECT_WIDGET_KEY].strip() or None
                ),
                "ado_ticket_id": st.session_state[METADATA_TICKET_WIDGET_KEY].strip() or None,
            }
        )
        edited_context = SolutionIntentReviewContext.model_validate(edited_context.model_dump())
    except (AttributeError, ValidationError, ValueError) as exc:
        st.error(f"Review metadata is invalid: {exc}")
        return
    if edited_context != context:
        existing = st.session_state.get(METADATA_PROVENANCE_KEY)
        provenance = (
            ReviewInputProvenance.USER_ENTERED
            if existing is None
            else ReviewInputProvenance(existing)
        )
        store_metadata_component(
            st.session_state,
            edited_context,
            provenance,
            establish_baseline=existing is None,
            sync_widgets=False,
            feedback="Review metadata edited; review package confirmation was revoked.",
        )
        st.rerun()


def _render_review_input_readiness(readiness: ReviewInputReadiness) -> None:
    """Render component states next to the confirmation and Analyze actions."""
    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">REVIEW INPUT READINESS</p>',
            unsafe_allow_html=True,
        )
        si_column, transcript_column, metadata_column = st.columns(3)
        si_column.metric("Authoritative SI", readiness.solution_intent.value)
        transcript_column.metric("Transcript", readiness.transcript.value)
        metadata_column.metric("Metadata", readiness.metadata.value)
        if readiness.confirmed:
            manifest = current_review_input_manifest(st.session_state)
            st.success(
                "Confirmed exact manifest · "
                f"{manifest.source_page_id} v{manifest.source_version} · "
                f"{manifest.provider_configuration_identity}"
            )
        elif readiness.blockers:
            st.info("Next: " + " ".join(readiness.blockers))


def _render_context(context: SolutionIntentReviewContext) -> None:
    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">REVIEW CONTEXT</p>',
            unsafe_allow_html=True,
        )
        values = [
            ("Project", context.project_name),
            ("SI Title", context.si_title),
            ("SI Version", context.si_version),
            ("Current SI Status", humanize(context.current_si_status.value)),
            ("Review Round", str(context.review_round)),
            (
                "Review Date",
                context.review_date.isoformat() if context.review_date else "Not provided",
            ),
            ("Domain Architect", context.domain_architect or "Not provided"),
            ("ADO Governance Ticket", context.ado_ticket_id or "Not provided"),
        ]
        context_items = "".join(
            (
                '<div class="agc-context-item">'
                f"<span>{escape(label)}</span>"
                f'<strong title="{escape(value)}">{escape(value)}</strong>'
                "</div>"
            )
            for label, value in values
        )
        st.markdown(
            f'<div class="agc-context-grid">{context_items}</div>',
            unsafe_allow_html=True,
        )


def _render_review_navigation(*, analysis_invalid: bool) -> None:
    back_column, output_column, reset_column = st.columns([1.4, 1.4, 1])
    if back_column.button(
        "← Back to Review Inputs",
        key="agc_back_to_inputs",
        width="stretch",
    ):
        _switch_stage(INPUT_STAGE)

    outputs_available = (
        isinstance(st.session_state[OUTPUTS_KEY], GovernanceOutputs) and not analysis_invalid
    )
    if output_column.button(
        "View Generated Outputs →",
        key="agc_view_outputs",
        disabled=not outputs_available,
        width="stretch",
    ):
        _switch_stage(OUTPUT_STAGE)

    if reset_column.button(
        "Reset review",
        key="agc_reset_from_review",
        width="stretch",
    ):
        reset_review_workflow(st.session_state)
        _switch_stage(INPUT_STAGE)


def _render_output_navigation() -> None:
    if _workflow_action_button(
        "Continue to Work Item Delivery", key="agc_continue_delivery", icon=":material/send:"
    ):
        _switch_stage(DELIVERY_STAGE)
    back_column, reset_column = st.columns([2, 1])
    if back_column.button(
        "← Back to Human Review",
        key="agc_back_to_review",
        width="stretch",
    ):
        _switch_stage(REVIEW_STAGE)

    if reset_column.button(
        "Reset review",
        key="agc_reset_from_outputs",
        width="stretch",
    ):
        reset_review_workflow(st.session_state)
        _switch_stage(INPUT_STAGE)


def _render_analyzed_input_summary(result: GovernanceResult, *, valid: bool = True) -> None:
    if valid:
        st.success("Review analysis completed. No outputs were generated automatically.")
    with st.container(border=True):
        st.markdown("#### Analyzed Review Inputs" if valid else "#### Previous Analysis Snapshot")
        columns = st.columns(4)
        values = [
            ("Project", result.context.project_name),
            ("SI Version", result.context.si_version),
            ("Review Round", str(result.context.review_round)),
            (
                "Review Date",
                (
                    result.context.review_date.isoformat()
                    if result.context.review_date
                    else "Not provided"
                ),
            ),
        ]
        for column, (label, value) in zip(columns, values, strict=True):
            column.markdown(f"**{label}**")
            column.write(value)
        if valid:
            if current_review_mode(st.session_state) is ReviewMode.INTERNAL_FAKE:
                st.caption(
                    "Fake AIF analyzed the canonical fake Confluence snapshot together with "
                    "the explicitly supplied synthetic transcript and metadata. No live "
                    "enterprise call occurred."
                )
            else:
                st.caption(
                    "The bundled Solution Intent, review transcript, and metadata were analyzed "
                    "together. Return to Review Inputs to inspect or change the sources."
                )
        else:
            st.caption(
                "This snapshot is retained for reference only and cannot be confirmed. "
                "Return to Review Inputs and run Analyze Review again."
            )


def _render_invalidation_notice(invalidation: AnalysisInvalidation) -> None:
    invalidated_target = "outputs" if invalidation.outputs_invalidated else "analysis"
    st.warning(
        f"Inputs changed → {invalidated_target} invalidated. Run Analyze Review again before "
        "confirming the reviewed record or generating outputs."
    )
    st.caption(f"Reason: {invalidation.reason}")


def _processing_overlay_markup(
    eyebrow: str,
    title: str,
    detail: str,
    *,
    step: int,
    total_steps: int,
) -> str:
    safe_total = max(total_steps, 1)
    safe_step = min(max(step, 1), safe_total)
    progress = round((safe_step / safe_total) * 100)
    return (
        '<div class="agc-processing-overlay" role="status" '
        'aria-live="polite" aria-busy="true">'
        '<div class="agc-processing-card">'
        '<div class="agc-processing-spinner" aria-hidden="true"></div>'
        f'<span class="agc-processing-eyebrow">{escape(eyebrow)}</span>'
        f"<h2>{escape(title)}</h2>"
        f"<p>{escape(detail)}</p>"
        '<div class="agc-processing-progress" aria-hidden="true">'
        f'<span style="width: {progress}%"></span>'
        "</div>"
        f'<span class="agc-processing-step">STEP {safe_step} OF {safe_total}</span>'
        "</div>"
        "</div>"
    )


def _analyze_current_inputs() -> bool:
    prepare_analysis_attempt(st.session_state)
    solution_intent = st.session_state[SOLUTION_INTENT_KEY]
    transcript = st.session_state[TRANSCRIPT_KEY]
    context = _current_context()
    processing_overlay = st.empty()
    try:
        if not solution_intent.strip():
            raise ValueError("Solution Intent must not be blank.")
        if not transcript.strip():
            raise ValueError("Review transcript must not be blank.")
        if context is None:
            raise ValueError("Review metadata is missing. Load the sample review first.")
        mode = current_review_mode(st.session_state)
        if mode is ReviewMode.INTERNAL_FAKE and not isinstance(
            st.session_state.get(CONFLUENCE_SNAPSHOT_KEY),
            ConfluencePageSnapshot,
        ):
            raise ValueError("Load the fake Confluence source before analysis.")
        processing_overlay.markdown(
            _processing_overlay_markup(
                "ANALYZE REVIEW",
                "Validating review package",
                "Checking the Solution Intent, transcript, and governance metadata.",
                step=1,
                total_steps=3,
            ),
            unsafe_allow_html=True,
        )
        with st.status(
            "Processing architecture review package...",
            expanded=True,
        ) as processing_status:
            st.write("Review inputs and governance metadata validated")
            _demo_pause()

            processing_overlay.markdown(
                _processing_overlay_markup(
                    "ANALYZE REVIEW",
                    "Extracting governance signals",
                    "Identifying decisions, findings, risks, actions, and source evidence.",
                    step=2,
                    total_steps=3,
                ),
                unsafe_allow_html=True,
            )
            runtime = build_review_runtime(mode)
            service = GovernanceReviewService(runtime.extractor)
            result = service.analyze_review(solution_intent, transcript, context)
            st.write("Governance decisions, findings, risks, and actions extracted")
            _demo_pause()

            processing_overlay.markdown(
                _processing_overlay_markup(
                    "ANALYZE REVIEW",
                    "Preparing human review",
                    "Building the editable governance record and evidence workspace.",
                    step=3,
                    total_steps=3,
                ),
                unsafe_allow_html=True,
            )
            store_analysis(
                st.session_state,
                result,
                current_input_fingerprint(st.session_state, context),
            )
            st.write("Human-review workspace prepared with source evidence")
            processing_status.update(
                label="Analysis complete — opening Human Review",
                state="complete",
                expanded=True,
            )
            _demo_pause()
    except (
        AifAnalysisError,
        DeterministicFixtureError,
        ValidationError,
        ValueError,
    ) as exc:
        processing_overlay.empty()
        st.session_state[ERROR_KEY] = f"Analysis failed: {exc}"
        return False
    return True


def _render_error() -> None:
    error = st.session_state[ERROR_KEY]
    if isinstance(error, str) and error:
        st.error(error)


def _render_human_review_stage(
    analyzed_result: GovernanceResult,
) -> tuple[ReviewFormData, bool]:
    st.subheader("Draft Structured Review")
    st.caption(
        "Edit or exclude proposed items. Supporting evidence is read-only. "
        "This stage does not formally approve the Solution Intent."
    )
    _render_analysis_summary(analyzed_result)
    pending = build_pending_review_changes(
        analyzed_result,
        current_review_form_data(st.session_state, analyzed_result),
    )
    _render_pending_review_summary(pending)

    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">GOVERNANCE DISPOSITION</p>',
            unsafe_allow_html=True,
        )
        st.markdown("### Review Outcome")
        outcome_column, evidence_column = st.columns([1, 2])
        with outcome_column:
            review_outcome = _enum_selectbox(
                "Review outcome",
                ReviewOutcome,
                analyzed_result.review_outcome.value,
                key="agc_field_outcome",
            )
        with evidence_column:
            _render_evidence(
                analyzed_result.outcome_evidence,
                "Outcome supporting evidence",
            )

    submitted = _workflow_action_button(
        "Confirm Reviewed Record & Generate Outputs",
        key="agc_confirm_review",
        type="primary",
        width="stretch",
    )

    review_tabs = st.tabs(
        [
            _pending_tab_label("Decisions", len(analyzed_result.decisions), "Decision", pending),
            _pending_tab_label("Findings", len(analyzed_result.findings), "Finding", pending),
            _pending_tab_label("Risks", len(analyzed_result.risks), "Risk", pending),
            _pending_tab_label(
                "Actions", len(analyzed_result.action_items), "Action item", pending
            ),
            _pending_tab_label(
                "Questions", len(analyzed_result.open_questions), "Open question", pending
            ),
            _pending_tab_label(
                "Missing Info",
                len(analyzed_result.missing_evidence),
                "Missing information",
                pending,
            ),
        ]
    )
    with review_tabs[0]:
        decisions = _render_decision_edits(analyzed_result, pending)
    with review_tabs[1]:
        findings = _render_finding_edits(analyzed_result, pending)
    with review_tabs[2]:
        risks = _render_risk_edits(analyzed_result, pending)
    with review_tabs[3]:
        actions = _render_action_edits(analyzed_result, pending)
    with review_tabs[4]:
        questions = _render_question_edits(analyzed_result, pending)
    with review_tabs[5]:
        missing = _render_missing_evidence_edits(analyzed_result, pending)

    st.divider()
    st.caption(
        "Confirmation validates the edited record and generates local demo artifacts. "
        "It does not publish or create records in an external system."
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


def _pending_tab_label(
    label: str,
    proposal_count: int,
    collection: str,
    pending: PendingReviewChanges,
) -> str:
    pending_count = pending.pending_item_count(collection)
    suffix = f" · {pending_count} pending" if pending_count else ""
    return f"{label} · {proposal_count}{suffix}"


def _render_pending_review_summary(pending: PendingReviewChanges) -> None:
    st.markdown("### Pending human changes")
    st.caption(
        "Session-local comparison with the analyzed proposal. Pending values are not confirmed, "
        "published, or formal approval."
    )
    if not pending.has_changes and not pending.validation_issues:
        st.info("No pending human changes. All current values match the analyzed proposal.")
        return
    modified_column, excluded_column, sections_column, invalid_column = st.columns(4)
    modified_column.metric("Modified fields", len(pending.field_changes))
    excluded_column.metric("Excluded items", len(pending.excluded_items))
    sections_column.metric("Affected sections", len(pending.affected_collections))
    invalid_column.metric("Validation issues", len(pending.validation_issues))
    affected = ", ".join(pending.affected_collections)
    if affected:
        st.caption(f"Affected: {affected}")
    for issue in pending.validation_issues:
        location = issue.collection
        if issue.item_index is not None:
            location = f"{location} {issue.item_index + 1}"
        st.warning(f"{location} · {issue.field}: {issue.message}")


def _render_pending_item_marker(
    pending: PendingReviewChanges,
    collection: str,
    item_index: int,
) -> None:
    modified, excluded, invalid = pending.item_state(collection, item_index)
    labels: list[str] = []
    if excluded:
        labels.append("Excluded")
    if modified:
        labels.append(f"{modified} modified")
    if invalid:
        labels.append(f"{invalid} needs correction")
    if labels:
        st.caption("Pending · " + " · ".join(labels) + " · Unconfirmed")


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
    first_row = st.columns(4)
    second_row = st.columns(3)
    for column, (label, value) in zip([*first_row, *second_row], labels_and_values, strict=True):
        column.metric(label, value)


def _render_decision_edits(
    result: GovernanceResult, pending: PendingReviewChanges
) -> list[dict[str, object]]:
    st.markdown("### Confirmed Decisions")
    if not result.decisions:
        st.caption("None recorded.")
    edits: list[dict[str, object]] = []
    for index, decision in enumerate(result.decisions):
        with st.container(border=True):
            st.markdown(f"**Decision {index + 1}**")
            _render_pending_item_marker(pending, "Decision", index)
            include = st.checkbox(
                "Include in reviewed record",
                key=f"agc_field_decision_{index}_include",
                **_review_widget_default(
                    f"agc_field_decision_{index}_include",
                    value=True,
                ),
            )
            statement = st.text_area(
                "Statement",
                key=f"agc_field_decision_{index}_statement",
                height=80,
                **_review_widget_default(
                    f"agc_field_decision_{index}_statement",
                    value=decision.statement,
                ),
            )
            rationale = st.text_area(
                "Rationale (optional)",
                key=f"agc_field_decision_{index}_rationale",
                height=70,
                **_review_widget_default(
                    f"agc_field_decision_{index}_rationale",
                    value=decision.rationale or "",
                ),
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


def _render_finding_edits(
    result: GovernanceResult, pending: PendingReviewChanges
) -> list[dict[str, object]]:
    st.markdown("### Review Findings")
    if not result.findings:
        st.caption("None recorded.")
    edits: list[dict[str, object]] = []
    for index, finding in enumerate(result.findings):
        with st.container(border=True):
            st.markdown(f"**Review Finding {index + 1}**")
            _render_pending_item_marker(pending, "Finding", index)
            include = st.checkbox(
                "Include in reviewed record",
                key=f"agc_field_finding_{index}_include",
                **_review_widget_default(
                    f"agc_field_finding_{index}_include",
                    value=True,
                ),
            )
            title = st.text_input(
                "Title",
                key=f"agc_field_finding_{index}_title",
                **_review_widget_default(
                    f"agc_field_finding_{index}_title",
                    value=finding.title,
                ),
            )
            description = st.text_area(
                "Description",
                key=f"agc_field_finding_{index}_description",
                height=80,
                **_review_widget_default(
                    f"agc_field_finding_{index}_description",
                    value=finding.description,
                ),
            )
            category_column, section_column = st.columns(2)
            category = category_column.text_input(
                "Category (optional)",
                key=f"agc_field_finding_{index}_category",
                **_review_widget_default(
                    f"agc_field_finding_{index}_category",
                    value=finding.category or "",
                ),
            )
            si_section = section_column.text_input(
                "SI section (optional)",
                key=f"agc_field_finding_{index}_si_section",
                **_review_widget_default(
                    f"agc_field_finding_{index}_si_section",
                    value=finding.si_section or "",
                ),
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
                key=f"agc_field_finding_{index}_recommended_change",
                height=80,
                **_review_widget_default(
                    f"agc_field_finding_{index}_recommended_change",
                    value=finding.recommended_change or "",
                ),
            )
            owner_column, date_column = st.columns(2)
            owner = owner_column.text_input(
                "Owner (optional)",
                key=f"agc_field_finding_{index}_owner",
                **_review_widget_default(
                    f"agc_field_finding_{index}_owner",
                    value=finding.owner or "",
                ),
            )
            due_date = date_column.text_input(
                "Due date (optional, YYYY-MM-DD)",
                key=f"agc_field_finding_{index}_due_date",
                **_review_widget_default(
                    f"agc_field_finding_{index}_due_date",
                    value=_date_text(finding.due_date),
                ),
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


def _render_risk_edits(
    result: GovernanceResult, pending: PendingReviewChanges
) -> list[dict[str, object]]:
    st.markdown("### Risks")
    if not result.risks:
        st.caption("None recorded.")
    edits: list[dict[str, object]] = []
    for index, risk in enumerate(result.risks):
        with st.container(border=True):
            st.markdown(f"**Risk {index + 1}**")
            _render_pending_item_marker(pending, "Risk", index)
            include = st.checkbox(
                "Include in reviewed record",
                key=f"agc_field_risk_{index}_include",
                **_review_widget_default(
                    f"agc_field_risk_{index}_include",
                    value=True,
                ),
            )
            description = st.text_area(
                "Description",
                key=f"agc_field_risk_{index}_description",
                height=80,
                **_review_widget_default(
                    f"agc_field_risk_{index}_description",
                    value=risk.description,
                ),
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
                key=f"agc_field_risk_{index}_owner",
                **_review_widget_default(
                    f"agc_field_risk_{index}_owner",
                    value=risk.owner or "",
                ),
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


def _render_action_edits(
    result: GovernanceResult, pending: PendingReviewChanges
) -> list[dict[str, object]]:
    st.markdown("### Action Items")
    if not result.action_items:
        st.caption("None recorded.")
    edits: list[dict[str, object]] = []
    for index, action in enumerate(result.action_items):
        with st.container(border=True):
            st.markdown(f"**Action Item {index + 1}**")
            _render_pending_item_marker(pending, "Action item", index)
            include = st.checkbox(
                "Include in reviewed record",
                key=f"agc_field_action_{index}_include",
                **_review_widget_default(
                    f"agc_field_action_{index}_include",
                    value=True,
                ),
            )
            title = st.text_input(
                "Title",
                key=f"agc_field_action_{index}_title",
                **_review_widget_default(
                    f"agc_field_action_{index}_title",
                    value=action.title,
                ),
            )
            owner_column, date_column, priority_column = st.columns(3)
            owner = owner_column.text_input(
                "Owner (optional)",
                key=f"agc_field_action_{index}_owner",
                **_review_widget_default(
                    f"agc_field_action_{index}_owner",
                    value=action.owner or "",
                ),
            )
            due_date = date_column.date_input(
                "Due date (optional)",
                key=f"agc_field_action_{index}_due_date",
                format="YYYY-MM-DD",
                min_value=date.min,
                max_value=date.max,
                persist_state="session",
                **_review_widget_default(
                    f"agc_field_action_{index}_due_date",
                    value=action.due_date,
                ),
            )
            date_column.button(
                "Clear due date",
                key=f"agc_clear_action_{index}_due_date",
                on_click=clear_review_action_due_date,
                args=(st.session_state, index),
                disabled=due_date is None,
                help="Leave this optional review date genuinely unset.",
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


def _render_question_edits(
    result: GovernanceResult, pending: PendingReviewChanges
) -> list[dict[str, object]]:
    st.markdown("### Open Questions")
    if not result.open_questions:
        st.caption("None recorded.")
    edits: list[dict[str, object]] = []
    for index, question in enumerate(result.open_questions):
        with st.container(border=True):
            st.markdown(f"**Open Question {index + 1}**")
            _render_pending_item_marker(pending, "Open question", index)
            include = st.checkbox(
                "Include in reviewed record",
                key=f"agc_field_question_{index}_include",
                **_review_widget_default(
                    f"agc_field_question_{index}_include",
                    value=True,
                ),
            )
            question_text = st.text_area(
                "Question",
                key=f"agc_field_question_{index}_question",
                height=70,
                **_review_widget_default(
                    f"agc_field_question_{index}_question",
                    value=question.question,
                ),
            )
            owner = st.text_input(
                "Owner (optional)",
                key=f"agc_field_question_{index}_owner",
                **_review_widget_default(
                    f"agc_field_question_{index}_owner",
                    value=question.owner or "",
                ),
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


def _render_missing_evidence_edits(
    result: GovernanceResult, pending: PendingReviewChanges
) -> list[dict[str, object]]:
    st.markdown("### Missing Governance Information")
    if not result.missing_evidence:
        st.caption("None recorded.")
    edits: list[dict[str, object]] = []
    for index, missing in enumerate(result.missing_evidence):
        with st.container(border=True):
            st.markdown(f"**Missing Information {index + 1}**")
            _render_pending_item_marker(pending, "Missing information", index)
            include = st.checkbox(
                "Include in reviewed record",
                key=f"agc_field_missing_{index}_include",
                **_review_widget_default(
                    f"agc_field_missing_{index}_include",
                    value=True,
                ),
            )
            item = st.text_input(
                "Item",
                key=f"agc_field_missing_{index}_item",
                **_review_widget_default(
                    f"agc_field_missing_{index}_item",
                    value=missing.item,
                ),
            )
            reason = st.text_area(
                "Reason (optional)",
                key=f"agc_field_missing_{index}_reason",
                height=70,
                **_review_widget_default(
                    f"agc_field_missing_{index}_reason",
                    value=missing.reason or "",
                ),
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


def _render_evidence(
    evidence_items: Sequence[SourceEvidence],
    label: str,
    *,
    expanded: bool = True,
) -> None:
    with st.expander(f"{label} ({len(evidence_items)})", expanded=expanded):
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
        format_func=humanize,
        key=key,
        **_review_widget_default(key, index=options.index(current_value)),
    )


def _review_widget_default(key: str, **default: object) -> dict[str, object]:
    """Supply a widget default only before routed state has restored its key."""
    return {} if key in st.session_state else default


def _date_text(value: date | None) -> str:
    return value.isoformat() if value is not None else ""


def _demo_step_delay_seconds() -> float:
    raw_value = os.getenv(
        _DEMO_DELAY_ENV,
        str(_DEFAULT_DEMO_STEP_DELAY_SECONDS),
    )
    try:
        configured_delay = float(raw_value)
    except ValueError:
        return _DEFAULT_DEMO_STEP_DELAY_SECONDS
    return min(max(configured_delay, 0.0), _MAX_DEMO_STEP_DELAY_SECONDS)


def _demo_pause() -> None:
    delay = _demo_step_delay_seconds()
    if delay > 0:
        time.sleep(delay)


def _generate_reviewed_outputs(
    analyzed_result: GovernanceResult,
    form_data: ReviewFormData,
) -> bool:
    clear_outputs(st.session_state)
    st.session_state[ERROR_KEY] = None
    processing_overlay = st.empty()
    try:
        if current_analysis_invalidation(st.session_state) is not None:
            raise ValueError("Inputs changed after analysis. Run Analyze Review again.")
        processing_overlay.markdown(
            _processing_overlay_markup(
                "GENERATE OUTPUTS",
                "Validating reviewed record",
                "Checking human edits, exclusions, owners, priorities, and due dates.",
                step=1,
                total_steps=3,
            ),
            unsafe_allow_html=True,
        )
        reviewed_result = build_reviewed_result(analyzed_result, form_data)
        change_summary = build_review_change_summary(
            analyzed_result,
            reviewed_result,
            form_data,
        )
        with st.status(
            "Preparing reviewed governance artifacts...",
            expanded=True,
        ) as processing_status:
            st.write("Human-reviewed governance record validated")
            _demo_pause()

            processing_overlay.markdown(
                _processing_overlay_markup(
                    "GENERATE OUTPUTS",
                    "Generating governance artifacts",
                    "Creating standardized meeting minutes from the approved record.",
                    step=2,
                    total_steps=3,
                ),
                unsafe_allow_html=True,
            )
            st.write("Generating standardized meeting minutes")
            outputs = generate_governance_outputs(reviewed_result)
            _demo_pause()

            processing_overlay.markdown(
                _processing_overlay_markup(
                    "GENERATE OUTPUTS",
                    "Preparing delivery package",
                    "Formatting Azure DevOps work-item previews and downloadable outputs.",
                    step=3,
                    total_steps=3,
                ),
                unsafe_allow_html=True,
            )
            st.write(f"Prepared {len(outputs.ado_work_items)} Azure DevOps work-item previews")
            store_outputs(st.session_state, reviewed_result, change_summary, outputs)
            processing_status.update(
                label="Artifacts ready — opening Generated Outputs",
                state="complete",
                expanded=True,
            )
            _demo_pause()
    except (DeterministicFixtureError, ValidationError, ValueError, RuntimeError) as exc:
        processing_overlay.empty()
        st.session_state[ERROR_KEY] = f"Unable to generate reviewed outputs: {exc}"
        return False
    return True


def _render_output_stage(
    outputs: GovernanceOutputs,
    change_summary: ReviewChangeSummary,
) -> None:
    reviewed_result = st.session_state[REVIEWED_RESULT_KEY]
    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">WORKFLOW COMPLETE</p>',
            unsafe_allow_html=True,
        )
        message_column, action_column = st.columns(
            [3, 1],
            vertical_alignment="center",
        )
        with message_column:
            st.markdown("### Governance package ready")
            st.caption("Human-reviewed local artifacts are ready for inspection or download.")
        if action_column.button(
            "Start New Review",
            key="agc_start_new_review",
            type="primary",
            width="stretch",
        ):
            reset_review_workflow(st.session_state)
            _switch_stage(INPUT_STAGE)

        if st.session_state[OUTPUT_SUCCESS_KEY]:
            st.caption(
                "✓ Demo workflow complete · No artifact was published to an external system."
            )

        if isinstance(reviewed_result, GovernanceResult):
            summary_columns = st.columns(4)
            summary_columns[0].metric("Workflow", "Complete")
            summary_columns[1].metric(
                "Review Outcome",
                humanize(reviewed_result.review_outcome.value),
            )
            summary_columns[2].metric("Meeting Minutes", "1")
            summary_columns[3].metric(
                "Work Item Previews",
                len(outputs.ado_work_items),
            )
        _render_review_change_summary(change_summary)

    if isinstance(reviewed_result, GovernanceResult):
        _render_evidence_to_output_comparison(reviewed_result, outputs)
    _render_minutes_output(outputs.review_minutes)
    _render_ado_outputs(outputs)


def _render_evidence_to_output_comparison(
    reviewed_result: GovernanceResult,
    outputs: GovernanceOutputs,
) -> None:
    st.subheader("Evidence-to-Output Comparison")
    st.caption(
        "Trace one human-confirmed action from its direct source evidence to the exact "
        "minutes entry and Azure DevOps preview generated from the reviewed record."
    )
    if not reviewed_result.action_items:
        st.info(
            "No action items were included in the reviewed record, so no action work-item "
            "comparison is available."
        )
        return

    selected_value = st.session_state.get(OUTPUT_ACTION_SELECTION_KEY)
    if not isinstance(selected_value, int) or not (
        0 <= selected_value < len(reviewed_result.action_items)
    ):
        st.session_state[OUTPUT_ACTION_SELECTION_KEY] = 0

    selected_index = st.selectbox(
        "Confirmed action",
        options=range(len(reviewed_result.action_items)),
        format_func=lambda index: (
            f"Action {index + 1} · {reviewed_result.action_items[index].title}"
        ),
        key=OUTPUT_ACTION_SELECTION_KEY,
        help="Actions are matched to generated previews by their reviewed collection index.",
    )
    action = reviewed_result.action_items[selected_index]
    minutes_entry = format_action_item_entry(action, selected_index + 1)
    matching_items = [
        item for item in outputs.ado_work_items if item.source_action_index == selected_index
    ]

    evidence_column, output_column = st.columns(2)
    with evidence_column.container(border=True):
        st.markdown("**Direct source evidence**")
        st.caption("Read-only quotes and locators retained from the validated source snapshot.")
        _render_evidence(action.evidence, "Action supporting evidence", expanded=True)

    with output_column.container(border=True):
        st.markdown("**Confirmed action and generated output**")
        st.markdown(f"**Title:** {action.title}")
        details = st.columns(3)
        details[0].markdown("**Owner**")
        details[0].write(action.owner or "Unassigned")
        details[1].markdown("**Due date**")
        details[1].write(action.due_date.isoformat() if action.due_date else "Not specified")
        details[2].markdown("**Priority**")
        details[2].write(humanize(action.priority.value))

        st.markdown("##### Actual minutes entry")
        st.markdown(minutes_entry)

        st.markdown("##### Azure DevOps preview")
        if len(matching_items) != 1:
            st.warning(
                "No unique work-item preview maps to this confirmed action. "
                "No substitute preview was inferred."
            )
            return
        item = matching_items[0]
        st.markdown(f"**{item.title}**")
        st.caption(
            f"Assigned to: {item.assigned_to or 'Unassigned'} · "
            f"Due: {item.due_date.isoformat() if item.due_date else 'Not specified'} · "
            f"Priority: {humanize(item.priority.value)} · "
            f"Source action index: {item.source_action_index}"
        )
        with st.expander("Full work-item description"):
            st.markdown(item.description)


def _render_review_change_summary(change_summary: ReviewChangeSummary) -> None:
    st.subheader("Human Review Changes")
    st.caption(
        "Compared with the validated provider analysis. Supporting evidence remains read-only "
        "and is not part of this editable comparison."
    )
    if not change_summary.has_changes:
        st.info("No changes were made during human review. All proposed items were retained.")
        return

    if change_summary.field_changes:
        st.markdown("#### Confirmed field changes")
        for change in change_summary.field_changes:
            location = change.collection
            if change.item_index is not None:
                location = f"{location} {change.item_index + 1}: {change.item_name}"
            with st.container(border=True):
                st.markdown(f"**{location} · {change.field}**")
                st.caption(f"Before — {_display_review_change_value(change.before, change.field)}")
                st.caption(f"After — {_display_review_change_value(change.after, change.field)}")

    if change_summary.excluded_items:
        st.markdown("#### Excluded items")
        for item in change_summary.excluded_items:
            st.markdown(f"- **{item.collection} {item.item_index + 1}:** {item.item_name}")


def _display_review_change_value(value: str | None, field: str) -> str:
    if value is None:
        return "Not set"
    if field in {"Outcome", "Priority", "Severity", "Status"}:
        return humanize(value)
    return value


def _render_minutes_output(review_minutes: str) -> None:
    st.subheader("Generated Review Record")
    st.info(
        "Review before publication. The Domain Architect remains responsible for "
        "the formal governance decision."
    )
    rendered_tab, raw_tab = st.tabs(["Rendered", "Markdown source"])
    with rendered_tab:
        st.markdown(review_minutes)
    with raw_tab:
        st.code(review_minutes, language="markdown", wrap_lines=True)
    st.download_button(
        "Download Markdown Review Record",
        data=review_minutes,
        file_name="solution-intent-review-record.md",
        mime="text/markdown",
        key="agc_download_minutes",
    )


def _render_ado_outputs(outputs: GovernanceOutputs) -> None:
    st.subheader("Azure DevOps Work Item Previews")
    st.warning("Preview only · No work items were submitted to Azure DevOps.")
    if not outputs.ado_work_items:
        st.caption("No action items were included in the reviewed record.")
    for index, item in enumerate(outputs.ado_work_items, start=1):
        with st.container(border=True):
            st.markdown(f"#### Work Item Preview {index}: {item.title}")
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
            "Download Work Item Preview JSON",
            data=work_items_json,
            file_name="ado-work-item-previews.json",
            mime="application/json",
            key="agc_download_ado",
        )


def _delivery_context(reviewed_result: GovernanceResult):
    capability = configured_delivery_capability()
    snapshot = st.session_state.get(CONFLUENCE_SNAPSHOT_KEY)
    manifest = current_review_input_manifest(st.session_state)
    readiness = assess_delivery_readiness(reviewed_result, snapshot, manifest, capability)
    operations = tuple(
        delivery_operation_for_correlations(
            st.session_state,
            delivery_action_correlations(
                reviewed_result,
                snapshot,
                row.action_index,
                delivery_original_action_index(st.session_state, row.action_index),
                capability.target,
            ),
        )
        if capability is not None and isinstance(snapshot, ConfluencePageSnapshot)
        else None
        for row in readiness.actions
    )
    preview = st.session_state.get(ADO_PUBLICATION_PREVIEW_KEY)
    selected_index = st.session_state.get(DELIVERY_ACTION_SELECTION_KEY)
    if isinstance(preview, AdoPublicationPreview):
        try:
            if (
                capability is None
                or selected_index is None
                or not readiness.actions[selected_index].ready
            ):
                raise PublicationValidationError("Delivery is no longer ready.")
            rebuilt = build_ado_publication_preview(
                reviewed_result,
                snapshot,
                selected_index,
                capability.target,
                original_action_index=delivery_original_action_index(
                    st.session_state, selected_index
                ),
            )
            if rebuilt != preview:
                raise PublicationValidationError("The request binding changed.")
        except (ValueError, IndexError):
            clear_publication_preview(st.session_state)
            preview = None

    return capability, readiness, operations


def _render_fake_ado_publication(reviewed_result: GovernanceResult) -> None:
    """Show all reviewed actions and one independently selected, exact fake request."""
    capability, readiness, operations = _delivery_context(reviewed_result)
    snapshot = st.session_state.get(CONFLUENCE_SNAPSHOT_KEY)
    preview = st.session_state.get(ADO_PUBLICATION_PREVIEW_KEY)
    selected_index = st.session_state.get(DELIVERY_ACTION_SELECTION_KEY)
    status = delivery_status(
        readiness, operations, has_preview=isinstance(preview, AdoPublicationPreview)
    )
    st.subheader(f"Delivery status · {status.value}")
    st.caption(
        "Delivery does not approve the Solution Intent. History is session-local, not a durable "
        "audit record. Restarting cannot establish that a prior Create did not occur."
    )
    if not readiness.actions:
        st.info("Not applicable · No actions were included in the confirmed reviewed record.")
    elif not readiness.capability_available:
        clear_publication_preview(st.session_state)
        st.info(
            "Unavailable · No delivery provider is configured for this exact review package. "
            "Use Back to Generated Outputs to inspect or download the local artifacts."
        )
        for blocker in readiness.blockers:
            st.caption(blocker)
    else:
        st.warning(
            "Synthetic target · no network. Create work item uses only an in-memory fake gateway."
        )
        target = capability.target
        with st.expander("Configured target and field mappings", expanded=False):
            st.json(target.model_dump(mode="json"))
        st.caption(
            f"Target: {target.project} · Type: {target.work_item_type} · "
            f"API version: {target.api_version}"
        )

    for row, operation in zip(readiness.actions, operations, strict=True):
        with st.container(border=True):
            st.subheader(f"Action {row.action_index + 1}")
            st.text(row.title)
            row_status = "Ready" if row.ready else "Unavailable"
            if operation is not None:
                row_status = _publication_status_label(operation.status)
            st.markdown(f"**{row_status}**")
            st.text(
                f"Reviewed owner: {row.reviewed_owner or 'Unset'}\n"
                f"Resolved assignee: {row.resolved_assignee or 'Unresolved'}\n"
                f"Due date: {row.due_date.isoformat() if row.due_date else 'Unset'}\n"
                f"Priority: {row.reviewed_priority} → {row.mapped_priority or 'Unmapped'}\n"
                f"Parent: {row.parent_reference or 'Unset'} → {row.mapped_parent or 'Unmapped'}"
            )
            for blocker in row.blockers:
                st.warning(blocker)
            if operation is not None:
                _render_publication_operation(operation)

    if readiness.actions and readiness.capability_available:
        options = list(range(len(readiness.actions)))
        selected_index = st.selectbox(
            "Action to deliver",
            options,
            index=selected_index if selected_index in options else 0,
            key=DELIVERY_ACTION_WIDGET_KEY,
            format_func=lambda index: f"Action {index + 1} · {readiness.actions[index].title}",
            persist_state="session",
        )
        select_delivery_action(st.session_state, selected_index)
        preview = st.session_state.get(ADO_PUBLICATION_PREVIEW_KEY)
        row = readiness.actions[selected_index]
        operation = operations[selected_index]
        protected = operation is not None and operation.status in PROTECTED_PUBLICATION_STATUSES
        if protected:
            st.info(
                "This action has a protected result. Another ready action may be selected; "
                "do not retry a succeeded, submitting, or unknown operation."
            )
        if not row.ready:
            st.info(
                "Use Back to Human Review to correct the named action, "
                "then confirm the record again. "
                "Source-controlled parent and target mappings cannot be edited here."
            )
        if _workflow_action_button(
            "Preview Azure DevOps request",
            floating=not isinstance(preview, AdoPublicationPreview) and not protected,
            key="agc_prepare_ado_publication",
            icon=":material/preview:",
            disabled=not row.ready or protected,
        ):
            preview = build_ado_publication_preview(
                reviewed_result,
                snapshot,
                selected_index,
                capability.target,
                original_action_index=delivery_original_action_index(
                    st.session_state, selected_index
                ),
            )
            store_publication_preview(st.session_state, preview)
            st.rerun()
        if isinstance(preview, AdoPublicationPreview):
            summary_tab, json_tab = st.tabs(["Work item summary", "Request JSON"])
            with summary_tab:
                st.caption(
                    "Read-only summary derived from this exact prepared request. "
                    "The reviewed owner is preserved; the resolved assignee is "
                    "its configured target identity."
                )
                for label, value in publication_request_summary(preview, capability.target).items():
                    st.markdown(f"**{escape(label)}**")
                    if isinstance(value, dict):
                        st.json(value)
                    else:
                        st.text(str(value))
            with json_tab:
                st.caption("Exact Create · POST endpoint · JSON Patch request")
                st.code(preview.request.url, language=None)
                st.text(preview.request.content_type)
                st.json(
                    [operation.model_dump(mode="json") for operation in preview.request.operations]
                )
                st.json(
                    {
                        "correlation": preview.request.correlation_id,
                        "request_binding_fingerprint": preview.request.binding_fingerprint,
                        "preview_fingerprint": preview.preview_fingerprint,
                        "reviewed_result_fingerprint": preview.reviewed_result_fingerprint,
                        "source_snapshot_fingerprint": preview.source_snapshot_fingerprint,
                        "target_fingerprint": preview.target_fingerprint,
                        "mapping_fingerprint": preview.mapping_fingerprint,
                        "original_action_index": preview.original_action_index,
                    }
                )
            confirmation = st.session_state.get(ADO_PUBLICATION_CONFIRMATION_KEY)
            if not protected:
                if not isinstance(confirmation, AdoPublicationConfirmation):
                    st.info("Prepared · Inspect both views before confirming this exact request.")
                    if _workflow_action_button(
                        "Confirm request",
                        key="agc_confirm_ado_publication",
                        icon=":material/check_circle:",
                    ):
                        store_publication_confirmation(
                            st.session_state, confirm_ado_publication_preview(preview)
                        )
                        st.rerun()
                else:
                    st.success(
                        "Confirmed · No request has been sent yet. "
                        "Create work item submits once to the fake gateway."
                    )
                    if _workflow_action_button(
                        "Create work item",
                        key="agc_submit_ado_publication",
                        type="primary",
                        icon=":material/send:",
                    ):
                        _submit_fake_ado_publication(
                            preview, confirmation, reviewed_result, snapshot
                        )
                        st.session_state[ADO_PUBLICATION_CONFIRMATION_KEY] = None
                        st.rerun()
        else:
            st.info("Not prepared · No exact Create request is currently prepared.")
    history = st.session_state.get(ADO_PUBLICATION_HISTORY_KEY)
    if isinstance(history, Mapping) and history:
        with st.expander("Session delivery history and reconciliation", expanded=False):
            for operation in history.values():
                if isinstance(operation, AdoPublicationOperation):
                    _render_publication_operation(operation)


def _submit_fake_ado_publication(
    preview: AdoPublicationPreview,
    confirmation: AdoPublicationConfirmation,
    reviewed_result: GovernanceResult,
    snapshot: ConfluencePageSnapshot,
) -> None:
    """Revalidate package capability and exact source immediately before guarded submission."""
    try:
        if current_analysis_invalidation(st.session_state) is not None:
            raise PublicationValidationError("The confirmed review package changed.")
        capability, readiness, _ = _delivery_context(reviewed_result)
        if capability is None or not readiness.actions[preview.action_index].ready:
            raise PublicationValidationError("Delivery capability or action readiness changed.")
        if preview.action_index != st.session_state.get(DELIVERY_ACTION_SELECTION_KEY):
            raise PublicationValidationError("The selected delivery action changed.")
        runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE)
        current_snapshot = runtime.confluence_reader.get_page(runtime.confluence_page_id)
        if not _same_source_snapshot(current_snapshot, snapshot):
            raise PublicationValidationError(
                "The Confluence source changed; analyze and confirm it again."
            )
        gateway = st.session_state.get(ADO_FAKE_GATEWAY_KEY)
        if gateway is None:
            gateway = InMemoryFakeAdoGateway()
            st.session_state[ADO_FAKE_GATEWAY_KEY] = gateway
        coordinator = AdoPublicationCoordinator(
            gateway,
            transition=lambda operation: record_publication_operation(st.session_state, operation),
        )
        with st.status(
            "Submitting · Reconciling correlation and verifying read-back", expanded=True
        ):
            coordinator.publish(
                preview=preview,
                confirmation=confirmation,
                reviewed_result=reviewed_result,
                source_snapshot=current_snapshot,
                target=capability.target,
                prior_operations=st.session_state.get(ADO_PUBLICATION_HISTORY_KEY),
                original_action_index=delivery_original_action_index(
                    st.session_state, preview.action_index
                ),
            )
    except (ValueError, RuntimeError) as exc:
        clear_publication_preview(st.session_state)
        st.session_state[ERROR_KEY] = str(exc)


def _publication_status_label(status: PublicationStatus) -> str:
    return {
        PublicationStatus.NOT_SUBMITTED: "Not prepared",
        PublicationStatus.SUBMITTING: "Submitting",
        PublicationStatus.SUCCEEDED: "Succeeded",
        PublicationStatus.DEFINITELY_FAILED: "Definitely failed",
        PublicationStatus.UNKNOWN_RESULT: "Needs reconciliation · Unknown result",
    }[status]


def _same_source_snapshot(
    current: ConfluencePageSnapshot,
    expected: ConfluencePageSnapshot,
) -> bool:
    """Compare publication-relevant source identity without retrieval timestamps."""
    return (
        current.page_id,
        current.version,
        current.canonicalizer_version,
        current.content_fingerprint,
    ) == (
        expected.page_id,
        expected.version,
        expected.canonicalizer_version,
        expected.content_fingerprint,
    )


def _render_publication_operation(operation: AdoPublicationOperation) -> None:
    st.text(f"Correlation: {operation.correlation_id}")
    st.caption(_publication_status_label(operation.status))
    if operation.status is PublicationStatus.SUCCEEDED:
        st.success(operation.message)
    elif operation.status is PublicationStatus.DEFINITELY_FAILED:
        st.error(operation.message)
    elif operation.status is PublicationStatus.UNKNOWN_RESULT:
        st.warning(operation.message)
    else:
        st.info(operation.message)
    if operation.receipt is not None:
        receipt = operation.receipt
        st.markdown(f"**Receipt ID:** {receipt.work_item_id}")
        st.caption(
            f"Revision: {receipt.revision or 'Unknown'} · Verified: "
            f"{'Yes' if receipt.verified else 'No'} · Correlation: {receipt.correlation_id}"
        )


def _current_context() -> SolutionIntentReviewContext | None:
    context = st.session_state[CONTEXT_KEY]
    return context if isinstance(context, SolutionIntentReviewContext) else None


if __name__ == "__main__":
    main()
