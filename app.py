"""Routed Streamlit interface for the Architecture Governance Copilot."""

from __future__ import annotations

import json
import os
import time
from base64 import b64encode
from collections.abc import Sequence
from datetime import date
from enum import StrEnum
from html import escape
from pathlib import Path

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
    SolutionIntentDraft,
    SolutionIntentDraftRequest,
    SolutionIntentReviewContext,
    SourceEvidence,
)
from architecture_governance_copilot.si_drafting import (
    DeterministicDemoDrafter,
    DeterministicDraftingFixtureError,
    SolutionIntentDraftingService,
)
from architecture_governance_copilot.ui_support import (
    ANALYZED_FINGERPRINT_KEY,
    ANALYZED_RESULT_KEY,
    CONTEXT_KEY,
    DRAFT_CONFIRMED_KEY,
    DRAFT_CONTENT_WIDGET_KEY,
    DRAFT_FINGERPRINT_KEY,
    DRAFT_PROJECT_KEY,
    DRAFT_PROJECT_WIDGET_KEY,
    DRAFT_RESULT_KEY,
    DRAFT_SOURCE_CODE_KEY,
    DRAFT_SOURCE_CODE_WIDGET_KEY,
    DRAFT_STAGE,
    DRAFT_SUPPORTING_DOCS_KEY,
    DRAFT_SUPPORTING_DOCS_WIDGET_KEY,
    DRAFT_TEMPLATE_KEY,
    DRAFT_TEMPLATE_WIDGET_KEY,
    ERROR_KEY,
    INPUT_STAGE,
    OUTPUT_STAGE,
    OUTPUT_SUCCESS_KEY,
    OUTPUTS_KEY,
    REVIEW_STAGE,
    REVIEWED_RESULT_KEY,
    SOLUTION_INTENT_KEY,
    SOLUTION_INTENT_WIDGET_KEY,
    TRANSCRIPT_KEY,
    TRANSCRIPT_WIDGET_KEY,
    ReviewFormData,
    analysis_is_stale,
    build_reviewed_result,
    clear_analysis_state,
    clear_outputs,
    clear_stale_si_draft,
    confirm_si_draft_for_review,
    drafting_input_fingerprint,
    drafting_result_is_stale,
    humanize,
    initialize_session_state,
    input_fingerprint,
    load_drafting_context_into_state,
    load_sample_drafting_context,
    load_sample_into_state,
    load_sample_review,
    load_sample_review_companions_into_state,
    preserve_review_widget_state,
    reset_application_state,
    restore_review_widget_state,
    set_active_stage,
    store_analysis,
    store_outputs,
    store_si_draft,
)

_BRAND_LOGO_DATA_URI = "data:image/png;base64," + b64encode(
    (Path(__file__).parent / "assets" / "standard_chartered_logo.png").read_bytes()
).decode("ascii")

_ROUTE_FILES = {
    DRAFT_STAGE: "pages/solution_intent_drafting.py",
    INPUT_STAGE: "pages/review_inputs.py",
    REVIEW_STAGE: "pages/human_review.py",
    OUTPUT_STAGE: "pages/generated_outputs.py",
}
_DEMO_DELAY_ENV = "AGC_DEMO_STEP_DELAY_SECONDS"
_DEFAULT_DEMO_STEP_DELAY_SECONDS = 0.4
_MAX_DEMO_STEP_DELAY_SECONDS = 1.5


def main() -> None:
    """Configure and run the deterministic routed review workflow."""
    st.set_page_config(
        page_title="Architecture Governance Copilot",
        page_icon="🏛️",
        layout="wide",
    )
    _apply_visual_theme()
    initialize_session_state(st.session_state)

    drafting_page = st.Page(
        _ROUTE_FILES[DRAFT_STAGE],
        title="Draft Solution Intent",
        icon=":material/edit_document:",
        url_path="draft-solution-intent",
        default=True,
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
    selected_page = st.navigation(
        [drafting_page, input_page, review_page, output_page],
        position="hidden",
    )
    selected_page.run()


def _render_drafting_page() -> None:
    _render_page_shell(DRAFT_STAGE)
    _render_drafting_stage()
    _render_error()


def _render_input_page() -> None:
    _render_page_shell(INPUT_STAGE)
    _render_input_stage()
    _render_error()


def _render_review_page() -> None:
    analyzed_result = st.session_state[ANALYZED_RESULT_KEY]
    if not isinstance(analyzed_result, GovernanceResult):
        _switch_stage(
            INPUT_STAGE,
            error="Complete review analysis before opening the Human Review page.",
        )

    restore_review_widget_state(st.session_state)
    context = _current_context()
    stale = analysis_is_stale(
        st.session_state[SOLUTION_INTENT_KEY],
        st.session_state[TRANSCRIPT_KEY],
        context,
        st.session_state[ANALYZED_FINGERPRINT_KEY],
    )
    if stale and st.session_state[OUTPUTS_KEY] is not None:
        clear_outputs(st.session_state)

    _render_page_shell(REVIEW_STAGE)
    if stale:
        st.warning(
            "The review inputs changed after analysis. Run Analyze Review again before "
            "generating outputs."
        )

    st.header("Stage 3 — Human Review")
    _render_review_navigation(stale=stale)
    _render_analyzed_input_summary(analyzed_result)
    form_data, submitted = _render_human_review_stage(analyzed_result, stale=stale)
    if submitted and _generate_reviewed_outputs(
        analyzed_result,
        form_data,
        stale=stale,
    ):
        _switch_stage(OUTPUT_STAGE)
    _render_error()


def _render_output_page() -> None:
    analyzed_result = st.session_state[ANALYZED_RESULT_KEY]
    if not isinstance(analyzed_result, GovernanceResult):
        _switch_stage(
            INPUT_STAGE,
            error="Complete review analysis before opening the Generated Outputs page.",
        )

    context = _current_context()
    stale = analysis_is_stale(
        st.session_state[SOLUTION_INTENT_KEY],
        st.session_state[TRANSCRIPT_KEY],
        context,
        st.session_state[ANALYZED_FINGERPRINT_KEY],
    )
    outputs = st.session_state[OUTPUTS_KEY]
    if stale or not isinstance(outputs, GovernanceOutputs):
        if stale:
            clear_outputs(st.session_state)
        _switch_stage(
            REVIEW_STAGE,
            error="Confirm the current reviewed record before opening Generated Outputs.",
        )

    _render_page_shell(OUTPUT_STAGE)
    st.header("Stage 4 — Generated Outputs")
    _render_output_navigation()
    _render_output_stage(outputs)


def _render_page_shell(stage: str) -> None:
    set_active_stage(st.session_state, stage)
    _render_sidebar(stage)
    _render_header()
    _render_step_progress(stage)


def _switch_stage(stage: str, *, error: str | None = None) -> None:
    # Multipage navigation removes widget-owned keys from pages that are no
    # longer rendered. Reassign review fields immediately before switching so
    # in-progress human edits remain durable across routed pages.
    preserve_review_widget_state(st.session_state)
    set_active_stage(st.session_state, stage)
    if error is not None:
        st.session_state[ERROR_KEY] = error
    st.switch_page(_ROUTE_FILES[stage])


def _render_header() -> None:
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
                    <div class="agc-service-status">● Offline demo ready</div>
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
            --agc-background: #f7f8fa;
            --agc-blue-tint: #e7f1fd;
            --agc-green-tint: #ebfae5;
        }
        .stApp {
            background:
                radial-gradient(circle at 92% 2%, rgba(4, 115, 234, 0.07), transparent 30rem),
                var(--agc-background);
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
            color: var(--agc-navy);
            letter-spacing: -0.02em;
        }
        h1 {
            font-weight: 500 !important;
        }
        p, li, label {
            color: var(--agc-slate);
        }
        [data-testid="stHeader"] {
            background: rgba(247, 248, 250, 0.9);
            backdrop-filter: blur(10px);
        }
        [data-testid="stSidebar"] {
            border-right: 0;
            background:
                radial-gradient(circle at 0% 100%, rgba(4, 115, 234, 0.32), transparent 17rem),
                linear-gradient(180deg, var(--agc-navy) 0%, #00172e 100%);
            box-shadow: 8px 0 30px rgba(0, 23, 46, 0.08);
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 1.6rem;
        }
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] strong,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: #ffffff;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            opacity: 0.72;
        }
        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.14);
        }
        [data-testid="stSidebar"] [data-testid="stAlert"] {
            border-color: rgba(56, 210, 0, 0.32);
            background: rgba(56, 210, 0, 0.1);
        }
        [data-testid="stSidebar"] [data-testid="stAlert"] p {
            color: #e9ffe2;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--agc-surface);
            border-color: var(--agc-border);
            border-radius: 14px;
            box-shadow: 0 3px 14px rgba(0, 23, 46, 0.045);
        }
        [data-testid="stMetric"] {
            position: relative;
            overflow: hidden;
            background: var(--agc-surface);
            border: 1px solid var(--agc-border);
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
        [data-testid="stMetricLabel"] {
            color: var(--agc-muted);
        }
        [data-testid="stMetricValue"] {
            color: var(--agc-navy);
            font-size: 1.35rem;
        }
        [data-testid="stAlert"] {
            border-radius: 10px;
            padding-block: 0.55rem;
        }
        .stButton > button, .stDownloadButton > button {
            border-color: #c8d1da;
            border-radius: 6px;
            min-height: 2.6rem;
            font-weight: 500;
            transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            border-color: var(--agc-blue);
            color: var(--agc-blue-dark);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(4, 115, 234, 0.12);
        }
        .stButton > button[kind="primary"] {
            border-color: var(--agc-blue);
            background: var(--agc-blue);
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(4, 115, 234, 0.2);
        }
        .stButton > button[kind="primary"]:hover {
            border-color: var(--agc-blue-dark);
            background: var(--agc-blue-dark);
            color: #ffffff;
        }
        .stTextInput input:focus,
        .stTextArea textarea:focus,
        [data-baseweb="select"] > div:focus-within {
            border-color: var(--agc-blue) !important;
            box-shadow: 0 0 0 2px rgba(4, 115, 234, 0.12) !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            border-bottom: 1px solid var(--agc-border);
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 0;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .stTabs [aria-selected="true"] {
            color: var(--agc-blue) !important;
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
            grid-template-columns: repeat(4, minmax(0, 1fr));
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
        [data-testid="stFormSubmitButton"] {
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
        [data-testid="stForm"] {
            padding-bottom: 5.5rem;
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
            [data-testid="stFormSubmitButton"] {
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
        DRAFT_STAGE: "Draft Solution Intent",
        INPUT_STAGE: "Review Inputs",
        REVIEW_STAGE: "Human Review",
        OUTPUT_STAGE: "Generated Outputs",
    }
    with st.sidebar:
        st.markdown("### Architecture Governance")
        st.caption("INTERNAL CONTROL WORKSPACE")
        st.markdown(f"**Current step**  \n{stage_labels[stage]}")
        st.divider()

        context = _current_context()
        if stage == DRAFT_STAGE:
            st.markdown("**Drafting context**")
            project_name = st.session_state[DRAFT_PROJECT_KEY]
            if isinstance(project_name, str) and project_name:
                st.write(project_name)
                st.caption("SI template · source excerpts · supporting notes")
            else:
                st.caption("Load the sample drafting context to begin.")
        else:
            st.markdown("**Review context**")
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
        st.success("Offline demo services ready")
        st.caption("● Synthetic data")
        st.caption("● Local processing")
        st.caption("● Azure DevOps payload previews")
        st.caption("○ No external connections")


def _render_step_progress(stage: str) -> None:
    stages = [
        (DRAFT_STAGE, "Draft Solution Intent"),
        (INPUT_STAGE, "Review Inputs"),
        (REVIEW_STAGE, "Human Review"),
        (OUTPUT_STAGE, "Generated Outputs"),
    ]
    current_index = next(
        index for index, (stage_name, _) in enumerate(stages) if stage_name == stage
    )
    workflow_complete = stage == OUTPUT_STAGE and st.session_state[OUTPUT_SUCCESS_KEY] is True
    step_cards: list[str] = []
    for index, (_, label) in enumerate(stages):
        draft_skipped = (
            index == 0 and current_index > 0 and st.session_state[DRAFT_CONFIRMED_KEY] is not True
        )
        draft_complete = index == 0 and st.session_state[DRAFT_CONFIRMED_KEY] is True
        if draft_skipped:
            status_class = "agc-step--skipped"
            status = "Skipped"
        elif (
            draft_complete
            or index < current_index
            or (workflow_complete and index == current_index)
        ):
            status_class = "agc-step--complete"
            status = "Complete"
        elif index == current_index:
            status_class = "agc-step--active"
            status = "In progress"
        else:
            status_class = ""
            status = "Upcoming"
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


def _render_drafting_stage() -> None:
    st.header("Stage 1 — Draft Solution Intent")
    st.caption(
        "Create an SI draft from a template, selected source-code context, and supporting "
        "notes. Demo mode supports the bundled review package."
    )
    drafting_context_ready = all(
        isinstance(value, str) and value.strip()
        for value in (
            st.session_state.get(
                DRAFT_PROJECT_WIDGET_KEY,
                st.session_state[DRAFT_PROJECT_KEY],
            ),
            st.session_state.get(
                DRAFT_TEMPLATE_WIDGET_KEY,
                st.session_state[DRAFT_TEMPLATE_KEY],
            ),
            st.session_state.get(
                DRAFT_SOURCE_CODE_WIDGET_KEY,
                st.session_state[DRAFT_SOURCE_CODE_KEY],
            ),
        )
    )

    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">DRAFTING ACTIONS</p>',
            unsafe_allow_html=True,
        )
        load_column, generate_column, existing_column, reset_column = st.columns(
            [1.35, 1.2, 1.25, 1],
        )
        load_clicked = load_column.button(
            "Load Sample Drafting Context",
            key="agc_load_drafting_context",
            use_container_width=True,
        )
        generate_clicked = generate_column.button(
            "Generate SI Draft",
            key="agc_generate_si_draft",
            type="primary",
            disabled=not drafting_context_ready,
            help=(
                "Provide a project name, SI template, and source-code context before "
                "generating a draft."
            ),
            use_container_width=True,
        )
        use_existing_clicked = existing_column.button(
            "Use Existing Solution Intent",
            key="agc_use_existing_si",
            use_container_width=True,
        )
        reset_clicked = reset_column.button(
            "Reset Workspace",
            key="agc_reset_drafting",
            use_container_width=True,
        )

    if use_existing_clicked:
        _switch_stage(INPUT_STAGE)
    if reset_clicked:
        reset_application_state(st.session_state)
        _switch_stage(DRAFT_STAGE)
    if load_clicked:
        try:
            load_drafting_context_into_state(
                st.session_state,
                load_sample_drafting_context(),
            )
        except (OSError, UnicodeError, ValueError) as exc:
            st.session_state[ERROR_KEY] = f"Unable to load drafting context: {exc}"
        else:
            st.rerun()

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

    project_name = st.text_input(
        "Project name",
        key=DRAFT_PROJECT_WIDGET_KEY,
        placeholder="Load the bundled demo context to begin.",
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
        template = st.text_area(
            "SI template",
            key=DRAFT_TEMPLATE_WIDGET_KEY,
            height=280,
            placeholder="Paste the approved SI template structure.",
        )
    with source_tab:
        source_code_context = st.text_area(
            "Selected source-code context",
            key=DRAFT_SOURCE_CODE_WIDGET_KEY,
            height=280,
            placeholder=(
                "Paste a repository summary or selected source excerpts. "
                "The PoC does not scan or execute a repository."
            ),
        )
    with documents_tab:
        supporting_documents = st.text_area(
            "Supporting-document context",
            key=DRAFT_SUPPORTING_DOCS_WIDGET_KEY,
            height=280,
            placeholder="Paste relevant requirements, constraints, and architecture notes.",
        )

    st.session_state[DRAFT_PROJECT_KEY] = project_name
    st.session_state[DRAFT_TEMPLATE_KEY] = template
    st.session_state[DRAFT_SOURCE_CODE_KEY] = source_code_context
    st.session_state[DRAFT_SUPPORTING_DOCS_KEY] = supporting_documents

    if isinstance(st.session_state[DRAFT_RESULT_KEY], SolutionIntentDraft):
        try:
            current_request = SolutionIntentDraftRequest(
                project_name=project_name,
                template=template,
                source_code_context=source_code_context,
                supporting_documents=supporting_documents or None,
            )
            stale_draft = drafting_result_is_stale(
                current_request,
                st.session_state[DRAFT_FINGERPRINT_KEY],
            )
        except ValidationError:
            stale_draft = True
        if stale_draft:
            clear_stale_si_draft(st.session_state)
            st.warning(
                "Drafting context changed after generation. Generate a new SI draft before "
                "human confirmation."
            )

    if generate_clicked and _generate_si_draft():
        st.rerun()

    draft = st.session_state[DRAFT_RESULT_KEY]
    if not isinstance(draft, SolutionIntentDraft):
        st.info(
            "No SI draft has been generated. Load the bundled demonstration context, inspect all "
            "three inputs, then select Generate SI Draft."
        )
        return

    st.success(
        "Solution Intent draft generated. Review and edit it before handing it to governance."
    )
    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">HUMAN REVIEW</p>',
            unsafe_allow_html=True,
        )
        st.markdown("### Proposed Solution Intent")
        st.caption(
            f"Provider: {draft.provider_name}. Generation is a drafting aid, not architecture "
            "approval or publication."
        )
        with st.form("agc_si_draft_review_form", clear_on_submit=False):
            submitted = st.form_submit_button(
                "Confirm SI Draft & Continue to Review",
                key="agc_confirm_si_draft",
                type="primary",
                use_container_width=True,
            )
            st.warning(
                "You may edit this draft and the handoff will preserve your changes. For this "
                "demo, keep the generated content unchanged: the offline review analyzer "
                "supports the bundled SI only."
            )
            reviewed_content = st.text_area(
                "Human-reviewed SI draft",
                key=DRAFT_CONTENT_WIDGET_KEY,
                height=500,
            )
            with st.expander("Draft assumptions and safeguards"):
                for assumption in draft.assumptions:
                    st.write(f"- {assumption}")
        if submitted and _confirm_si_draft(reviewed_content):
            _switch_stage(INPUT_STAGE)


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


def _confirm_si_draft(reviewed_content: str) -> bool:
    processing_overlay = st.empty()
    try:
        processing_overlay.markdown(
            _processing_overlay_markup(
                "CONFIRM SOLUTION INTENT",
                "Validating reviewed draft",
                "Checking the human-reviewed Solution Intent before handoff.",
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
                    "Preparing governance review",
                    "Preserving the confirmed SI and initializing Review Inputs.",
                    step=2,
                    total_steps=2,
                ),
                unsafe_allow_html=True,
            )
            confirm_si_draft_for_review(st.session_state, reviewed_content)
            st.write("Confirmed SI preserved for the governance review")
            status.update(
                label="SI confirmed — opening Review Inputs",
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
                    "Mapping known design context into the required SI sections.",
                    step=2,
                    total_steps=3,
                ),
                unsafe_allow_html=True,
            )
            service = SolutionIntentDraftingService(DeterministicDemoDrafter())
            draft = service.generate_draft(request)
            st.write("Known context and explicit gaps mapped into the SI structure")
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
                drafting_input_fingerprint(request),
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


def _render_input_stage() -> None:
    st.header("Stage 2 — Review Inputs")
    context = _current_context()
    current_solution_intent = st.session_state.get(
        SOLUTION_INTENT_WIDGET_KEY,
        st.session_state[SOLUTION_INTENT_KEY],
    )
    current_transcript = st.session_state.get(
        TRANSCRIPT_WIDGET_KEY,
        st.session_state[TRANSCRIPT_KEY],
    )
    review_inputs_ready = (
        isinstance(current_solution_intent, str)
        and bool(current_solution_intent.strip())
        and isinstance(current_transcript, str)
        and bool(current_transcript.strip())
        and isinstance(context, SolutionIntentReviewContext)
    )

    with st.container(border=True):
        st.markdown(
            '<p class="agc-section-label">REVIEW ACTIONS</p>',
            unsafe_allow_html=True,
        )
        load_column, companion_column = st.columns(
            [1.3, 1.7],
        )
        load_clicked = load_column.button(
            "Load Sample Review",
            key="agc_load_sample",
            use_container_width=True,
        )
        companions_clicked = companion_column.button(
            "Load Sample Transcript & Metadata",
            key="agc_load_review_companions",
            use_container_width=True,
        )
        analyze_column, reset_column, status_column = st.columns(
            [1.2, 1, 2],
            vertical_alignment="center",
        )
        analyze_clicked = analyze_column.button(
            "Analyze Review",
            key="agc_analyze",
            type="primary",
            disabled=not review_inputs_ready,
            help=(
                "Provide a Solution Intent, review transcript, and review metadata before analysis."
            ),
            use_container_width=True,
        )
        reset_clicked = reset_column.button(
            "Reset Demo",
            key="agc_reset",
            use_container_width=True,
        )

        if review_inputs_ready and st.session_state[DRAFT_CONFIRMED_KEY]:
            status_column.success("Confirmed SI + review companions ready")
        elif review_inputs_ready:
            status_column.success("Review package loaded · Inputs are editable")
        elif st.session_state[DRAFT_CONFIRMED_KEY]:
            status_column.info("Confirmed SI ready · Add transcript and metadata")
        elif context is not None:
            status_column.info("Review package incomplete · Add SI and transcript")
        else:
            status_column.info("Waiting for a review package")

    processing_placeholder = st.empty()

    if reset_clicked:
        reset_application_state(st.session_state)
        _switch_stage(DRAFT_STAGE)

    if load_clicked:
        try:
            load_sample_into_state(st.session_state, load_sample_review())
        except (OSError, UnicodeError, ValueError) as exc:
            st.session_state[ERROR_KEY] = f"Unable to load the bundled sample: {exc}"
        else:
            st.rerun()

    if companions_clicked:
        try:
            load_sample_review_companions_into_state(
                st.session_state,
                load_sample_review(),
            )
        except (OSError, UnicodeError, ValueError) as exc:
            st.session_state[ERROR_KEY] = f"Unable to load review companions: {exc}"
        else:
            st.rerun()

    context_column, sources_column = st.columns(
        [1, 2.35],
        gap="medium",
        vertical_alignment="top",
    )
    with context_column:
        if context is not None:
            _render_context(context)
        else:
            with st.container(border=True):
                st.markdown(
                    '<p class="agc-section-label">REVIEW CONTEXT</p>',
                    unsafe_allow_html=True,
                )
                st.caption("Load the sample to initialize review metadata.")

    with sources_column:
        si_tab, transcript_tab = st.tabs(["Solution Intent", "Review Transcript"])
        st.session_state.setdefault(
            SOLUTION_INTENT_WIDGET_KEY,
            st.session_state[SOLUTION_INTENT_KEY],
        )
        st.session_state.setdefault(
            TRANSCRIPT_WIDGET_KEY,
            st.session_state[TRANSCRIPT_KEY],
        )
        with si_tab:
            solution_intent = st.text_area(
                "Solution Intent",
                key=SOLUTION_INTENT_WIDGET_KEY,
                height=315,
                placeholder="Load the bundled review package to begin.",
            )
        with transcript_tab:
            transcript = st.text_area(
                "Teams-style Review Transcript",
                key=TRANSCRIPT_WIDGET_KEY,
                height=315,
                placeholder="Load the bundled review package to begin.",
            )
    st.session_state[SOLUTION_INTENT_KEY] = solution_intent
    st.session_state[TRANSCRIPT_KEY] = transcript

    if analyze_clicked:
        with processing_placeholder.container():
            if _analyze_current_inputs():
                _switch_stage(REVIEW_STAGE)

    analyzed_result = st.session_state[ANALYZED_RESULT_KEY]
    if isinstance(analyzed_result, GovernanceResult):
        stale = analysis_is_stale(
            st.session_state[SOLUTION_INTENT_KEY],
            st.session_state[TRANSCRIPT_KEY],
            context,
            st.session_state[ANALYZED_FINGERPRINT_KEY],
        )
        if stale:
            clear_outputs(st.session_state)
            st.warning(
                "The inputs changed after the previous analysis. Select Analyze Review "
                "to process the current version."
            )
        elif st.button(
            "Return to Human Review",
            key="agc_return_to_review",
            use_container_width=True,
        ):
            _switch_stage(REVIEW_STAGE)


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


def _render_review_navigation(*, stale: bool) -> None:
    back_column, output_column, reset_column = st.columns([1.4, 1.4, 1])
    if back_column.button(
        "← Back to Review Inputs",
        key="agc_back_to_inputs",
        use_container_width=True,
    ):
        _switch_stage(INPUT_STAGE)

    outputs_available = isinstance(st.session_state[OUTPUTS_KEY], GovernanceOutputs) and not stale
    if output_column.button(
        "View Generated Outputs →",
        key="agc_view_outputs",
        disabled=not outputs_available,
        use_container_width=True,
    ):
        _switch_stage(OUTPUT_STAGE)

    if reset_column.button(
        "Reset Demo",
        key="agc_reset_from_review",
        use_container_width=True,
    ):
        reset_application_state(st.session_state)
        _switch_stage(DRAFT_STAGE)


def _render_output_navigation() -> None:
    back_column, reset_column = st.columns([2, 1])
    if back_column.button(
        "← Back to Human Review",
        key="agc_back_to_review",
        use_container_width=True,
    ):
        _switch_stage(REVIEW_STAGE)

    if reset_column.button(
        "Reset Demo",
        key="agc_reset_from_outputs",
        use_container_width=True,
    ):
        reset_application_state(st.session_state)
        _switch_stage(DRAFT_STAGE)


def _render_analyzed_input_summary(result: GovernanceResult) -> None:
    st.success("Review analysis completed. No outputs were generated automatically.")
    with st.container(border=True):
        st.markdown("#### Analyzed Review Inputs")
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
        st.caption(
            "The bundled Solution Intent, review transcript, and metadata were analyzed "
            "together. Return to Review Inputs to inspect or change the sources."
        )


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
    clear_analysis_state(st.session_state)
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
            service = GovernanceReviewService(DeterministicDemoExtractor())
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
                input_fingerprint(solution_intent, transcript, context),
            )
            st.write("Human-review workspace prepared with source evidence")
            processing_status.update(
                label="Analysis complete — opening Human Review",
                state="complete",
                expanded=True,
            )
            _demo_pause()
    except (DeterministicFixtureError, ValidationError, ValueError) as exc:
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
    *,
    stale: bool,
) -> tuple[ReviewFormData, bool]:
    st.subheader("Draft Structured Review")
    st.caption(
        "Edit or exclude proposed items. Supporting evidence is read-only. "
        "This stage does not formally approve the Solution Intent."
    )
    _render_analysis_summary(analyzed_result)

    with st.form("agc_review_form", clear_on_submit=False):
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

        submitted = st.form_submit_button(
            "Confirm Reviewed Record & Generate Outputs",
            key="agc_confirm_review",
            type="primary",
            disabled=stale,
            use_container_width=True,
        )

        review_tabs = st.tabs(
            [
                f"Decisions · {len(analyzed_result.decisions)}",
                f"Findings · {len(analyzed_result.findings)}",
                f"Risks · {len(analyzed_result.risks)}",
                f"Actions · {len(analyzed_result.action_items)}",
                f"Questions · {len(analyzed_result.open_questions)}",
                f"Missing Info · {len(analyzed_result.missing_evidence)}",
            ]
        )
        with review_tabs[0]:
            decisions = _render_decision_edits(analyzed_result)
        with review_tabs[1]:
            findings = _render_finding_edits(analyzed_result)
        with review_tabs[2]:
            risks = _render_risk_edits(analyzed_result)
        with review_tabs[3]:
            actions = _render_action_edits(analyzed_result)
        with review_tabs[4]:
            questions = _render_question_edits(analyzed_result)
        with review_tabs[5]:
            missing = _render_missing_evidence_edits(analyzed_result)

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
    *,
    stale: bool,
) -> bool:
    clear_outputs(st.session_state)
    st.session_state[ERROR_KEY] = None
    processing_overlay = st.empty()
    try:
        if stale:
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
            service = GovernanceReviewService(DeterministicDemoExtractor())
            outputs = service.generate_outputs(reviewed_result)
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
            store_outputs(st.session_state, reviewed_result, outputs)
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


def _render_output_stage(outputs: GovernanceOutputs) -> None:
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
            use_container_width=True,
        ):
            reset_application_state(st.session_state)
            _switch_stage(DRAFT_STAGE)

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

    _render_minutes_output(outputs.review_minutes)
    _render_ado_outputs(outputs)


def _render_minutes_output(review_minutes: str) -> None:
    st.subheader("Generated Review Record")
    st.info(
        "Review before publication. The Domain Architect remains responsible for "
        "the formal governance decision."
    )
    rendered_tab, raw_tab = st.tabs(["Rendered Markdown", "Raw Markdown"])
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


def _current_context() -> SolutionIntentReviewContext | None:
    context = st.session_state[CONTEXT_KEY]
    return context if isinstance(context, SolutionIntentReviewContext) else None


if __name__ == "__main__":
    main()
