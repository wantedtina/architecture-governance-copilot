"""Literal finding/action grouping for edited synthetic transcripts, never semantic AI."""

from __future__ import annotations

import re

from architecture_governance_copilot.models import EvidenceSource
from architecture_governance_copilot.review_candidates import ReviewCandidatePayload
from architecture_governance_copilot.review_sources import build_review_source_index

DEMO_REVIEW_GUIDANCE = (
    "Offline demo: edited transcripts use literal finding/action keyword grouping, "
    "not semantic AI analysis. Review classifications against the complete source. "
    "Unmatched text remains available in the source; other categories are not extracted. "
    "All structured business fields and the outcome require human completion."
)


def group_transcript_candidates(solution_intent: str, transcript: str) -> ReviewCandidatePayload:
    """Group explicit literal cues without business defaults or inferred follow-up work."""
    index = build_review_source_index(solution_intent, transcript)
    items = []
    for entry in index.entries:
        if entry.source_type is not EvidenceSource.MEETING_TRANSCRIPT or not entry.text.strip():
            continue
        content = re.sub(r"^\[[^\]]+\]\s+[^:]+:\s*", "", entry.text.strip())
        lower = content.lower()
        # These are literal demo cues, not a semantic correction layer for live responses.
        if lower.startswith("i accept ownership") or re.match(
            r"(?:decision|risk|question|missing evidence)\s*:", lower
        ):
            continue
        if re.search(r"\b(action|i will|please add|please update)\b", lower) and not re.search(
            r"\b(no|not|never)\b", lower
        ):
            kind = "action"
        elif re.search(r"\b(finding|not defined|not stated|does not explain)\b", lower):
            kind = "finding"
        else:
            continue
        items.append({"kind": kind, "text": content, "evidence_source_ids": [entry.source_id]})
    return ReviewCandidatePayload.model_validate({"items": items})
