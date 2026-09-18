"""Versioned physical-line evidence indexing with exact original snapshots."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from dataclasses import dataclass

from architecture_governance_copilot.models import EvidenceSource, SourceEvidence

SOURCE_INDEX_VERSION = "normalized-physical-lines-v1"
_HEADING = re.compile(r"^#{1,6}\s+(?:\d+\.\s+)?(?P<title>.+?)\s*$")
_UTTERANCE = re.compile(r"^\[(?P<timestamp>[^\]\r\n]+)\]\s+(?P<speaker>[^:\r\n]+):")


def normalize_review_source(value: str) -> str:
    """Match the application's newline and outer-whitespace fingerprint convention."""
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def review_source_fingerprint(value: str) -> str:
    return hashlib.sha256(normalize_review_source(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ReviewSourceEntry:
    """One physical line and its original-source character span."""

    source_id: str
    source_type: EvidenceSource
    text: str
    line_number: int
    original_start: int
    original_end: int
    original_text: str
    section: str | None = None
    speaker: str | None = None
    timestamp: str | None = None

    def to_evidence(self) -> SourceEvidence:
        if not self.text.strip():
            raise ValueError("Blank source lines cannot support a candidate")
        return SourceEvidence(
            source_type=self.source_type,
            quote=self.original_text,
            section=self.section,
            speaker=self.speaker,
            timestamp=self.timestamp,
            reference=self.source_id,
        )


@dataclass(frozen=True, slots=True)
class ReviewSourceIndex:
    solution_intent: str
    review_transcript: str
    entries: tuple[ReviewSourceEntry, ...]
    si_content_fingerprint: str
    transcript_content_fingerprint: str
    version: str = SOURCE_INDEX_VERSION

    @property
    def by_id(self) -> dict[str, ReviewSourceEntry]:
        return {entry.source_id: entry for entry in self.entries}

    def resolve(self, source_ids: Iterable[str]) -> tuple[SourceEvidence, ...]:
        ids = tuple(source_ids)
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("Evidence IDs must be nonempty and unique within an item")
        sources = self.by_id
        if any(source_id not in sources for source_id in ids):
            raise ValueError("Evidence source ID does not belong to the analyzed snapshots")
        return tuple(sources[source_id].to_evidence() for source_id in ids)

    def render_annotated_sources(self) -> str:
        """Render each source line once; preserve blank lines and unclassified text."""
        return "\n\n".join(
            label
            + "\n"
            + "\n".join(
                f"[{entry.source_id}] {entry.text}"
                for entry in self.entries
                if entry.source_type is source_type
            )
            for label, source_type in (
                ("SOLUTION INTENT", EvidenceSource.SOLUTION_INTENT),
                ("REVIEW TRANSCRIPT", EvidenceSource.MEETING_TRANSCRIPT),
            )
        )


def _normalized_with_original_positions(value: str) -> tuple[str, list[int]]:
    characters: list[str] = []
    positions: list[int] = []
    offset = 0
    while offset < len(value):
        character = value[offset]
        characters.append("\n" if character == "\r" else character)
        positions.append(offset)
        offset += 2 if value[offset : offset + 2] == "\r\n" else 1
    normalized = "".join(characters)
    left = len(normalized) - len(normalized.lstrip())
    right = len(normalized.rstrip())
    return normalized[left:right], positions[left:right]


def _index_source(value: str, source_type: EvidenceSource) -> tuple[ReviewSourceEntry, ...]:
    normalized, positions = _normalized_with_original_positions(value)
    if not normalized:
        raise ValueError("Review sources must contain nonblank text")
    prefix = "si" if source_type is EvidenceSource.SOLUTION_INTENT else "transcript"
    digest = review_source_fingerprint(value)[:12]
    section = speaker = timestamp = None
    offset = 0
    entries = []
    for line_number, line in enumerate(normalized.split("\n"), 1):
        if source_type is EvidenceSource.SOLUTION_INTENT:
            heading = _HEADING.match(line)
            if heading:
                section = heading.group("title").strip()
        else:
            utterance = _UTTERANCE.match(line)
            if utterance:
                speaker = utterance.group("speaker").strip()
                timestamp = utterance.group("timestamp").strip()
        start = positions[offset] if offset < len(positions) else len(value)
        end = positions[offset + len(line) - 1] + 1 if line else start
        entries.append(
            ReviewSourceEntry(
                source_id=f"{prefix}-{digest}-{line_number:03d}",
                source_type=source_type,
                text=line,
                line_number=line_number,
                original_start=start,
                original_end=end,
                original_text=value[start:end],
                section=section,
                speaker=speaker,
                timestamp=timestamp,
            )
        )
        offset += len(line) + 1
    return tuple(entries)


def build_review_source_index(solution_intent: str, review_transcript: str) -> ReviewSourceIndex:
    return ReviewSourceIndex(
        solution_intent=solution_intent,
        review_transcript=review_transcript,
        entries=(
            *_index_source(solution_intent, EvidenceSource.SOLUTION_INTENT),
            *_index_source(review_transcript, EvidenceSource.MEETING_TRANSCRIPT),
        ),
        si_content_fingerprint=review_source_fingerprint(solution_intent),
        transcript_content_fingerprint=review_source_fingerprint(review_transcript),
    )
