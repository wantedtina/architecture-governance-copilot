"""Provider-neutral validation for governance evidence and source locators."""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass

from architecture_governance_copilot.extractors import GovernanceExtractor
from architecture_governance_copilot.models import (
    EvidenceSource,
    GovernanceResult,
    SolutionIntentReviewContext,
    SourceEvidence,
)

_HEADING_PATTERN = re.compile(
    r"^(?P<marks>#{1,6})\s+(?:(?P<number>\d+)\.\s+)?(?P<title>.+?)\s*$",
    re.MULTILINE,
)
_TRANSCRIPT_UTTERANCE_PATTERN = re.compile(
    r"^\[(?P<timestamp>[^\]\r\n]+)\]\s+(?P<speaker>[^:\r\n]+):",
    re.MULTILINE,
)
_TRANSCRIPT_LINE_REFERENCE_PATTERN = re.compile(r"transcript-line-(?P<line>\d+)")
_SI_REFERENCE_PATTERN = re.compile(r"SI-(?P<section>\d+)-[A-Za-z0-9-]+")


class EvidenceValidationError(ValueError):
    """Indicate that provider evidence cannot be resolved to supplied sources."""


@dataclass(frozen=True, slots=True)
class _EvidenceEntry:
    path: str
    evidence: SourceEvidence


@dataclass(frozen=True, slots=True)
class _HeadingSpan:
    level: int
    number: int | None
    title: str
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class _TranscriptUtterance:
    speaker: str
    timestamp: str
    start: int
    end: int


class EvidenceValidatingExtractor:
    """Validate one extractor's result against the exact analyzed source snapshot."""

    def __init__(self, extractor: GovernanceExtractor) -> None:
        self._extractor = extractor

    def extract(
        self,
        solution_intent: str,
        review_transcript: str,
        context: SolutionIntentReviewContext,
    ) -> GovernanceResult:
        """Delegate extraction once, then reject unresolved or conflicting evidence."""
        result = self._extractor.extract(solution_intent, review_transcript, context)
        # Providers cannot claim human provenance to bypass their evidence contract.
        GovernanceResult.model_validate(result.model_dump())
        validate_governance_evidence(result, solution_intent, review_transcript)
        return result


def validate_governance_evidence(
    result: GovernanceResult,
    solution_intent: str,
    review_transcript: str,
) -> None:
    """Validate every result quote, locator, and nonempty reference."""
    normalized_si = _normalize_source(solution_intent)
    normalized_transcript = _normalize_source(review_transcript)
    headings = _heading_spans(normalized_si)
    utterances = _transcript_utterances(normalized_transcript)
    reference_signatures: dict[str, tuple[str, ...]] = {}

    for entry in _iter_evidence(result):
        evidence = entry.evidence
        quote = _normalize_quote(evidence.quote)
        if evidence.source_type is EvidenceSource.SOLUTION_INTENT:
            _validate_solution_intent_evidence(
                entry.path,
                evidence,
                quote,
                normalized_si,
                headings,
            )
        else:
            _validate_transcript_evidence(
                entry.path,
                evidence,
                quote,
                normalized_transcript,
                utterances,
            )
        _record_reference(entry.path, evidence, quote, reference_signatures)


def _iter_evidence(result: GovernanceResult) -> Iterator[_EvidenceEntry]:
    for index, evidence in enumerate(result.outcome_evidence):
        yield _EvidenceEntry(f"outcome_evidence[{index}]", evidence)
    for collection_name in (
        "findings",
        "decisions",
        "risks",
        "action_items",
        "open_questions",
        "missing_evidence",
    ):
        collection = getattr(result, collection_name)
        for item_index, item in enumerate(collection):
            for evidence_index, evidence in enumerate(item.evidence):
                yield _EvidenceEntry(
                    f"{collection_name}[{item_index}].evidence[{evidence_index}]",
                    evidence,
                )


def _validate_solution_intent_evidence(
    path: str,
    evidence: SourceEvidence,
    quote: str,
    source: str,
    headings: tuple[_HeadingSpan, ...],
) -> None:
    quote_spans = _quote_spans(source, quote)
    if not quote_spans:
        _fail(path, "quote was not found in the supplied Solution Intent")
    if evidence.speaker is not None or evidence.timestamp is not None:
        _fail(path, "Solution Intent evidence cannot use speaker or timestamp locators")

    located_quote_spans = quote_spans
    if evidence.section is not None:
        section_title = _normalize_locator(evidence.section)
        matching_sections = [
            heading for heading in headings if _normalize_locator(heading.title) == section_title
        ]
        if not matching_sections:
            _fail(path, f"section locator {evidence.section!r} was not found")
        located_quote_spans = _spans_in_headings(located_quote_spans, matching_sections)
        if not located_quote_spans:
            _fail(path, f"quote does not occur in section {evidence.section!r}")

    if evidence.reference is not None:
        match = _SI_REFERENCE_PATTERN.fullmatch(evidence.reference)
        if match is not None:
            section_number = int(match.group("section"))
            matching_sections = [
                heading
                for heading in headings
                if heading.level == 2 and heading.number == section_number
            ]
            located_quote_spans = _spans_in_headings(
                located_quote_spans,
                matching_sections,
            )
            if not located_quote_spans:
                _fail(
                    path,
                    f"reference {evidence.reference!r} does not resolve to the quote span",
                )


def _validate_transcript_evidence(
    path: str,
    evidence: SourceEvidence,
    quote: str,
    source: str,
    utterances: tuple[_TranscriptUtterance, ...],
) -> None:
    quote_spans = _quote_spans(source, quote)
    if not quote_spans:
        _fail(path, "quote was not found in the supplied review transcript")
    if evidence.section is not None:
        _fail(path, "review transcript evidence cannot use a section locator")

    located_quote_spans = tuple(
        (quote_start, quote_end)
        for quote_start, quote_end in quote_spans
        if any(
            utterance.start <= quote_start
            and quote_end <= utterance.end
            and (evidence.speaker is None or utterance.speaker == evidence.speaker)
            and (evidence.timestamp is None or utterance.timestamp == evidence.timestamp)
            for utterance in utterances
        )
    )
    has_utterance_locator = evidence.speaker is not None or evidence.timestamp is not None
    if has_utterance_locator and not located_quote_spans:
        supplied_locators = " and ".join(
            locator
            for locator in (
                (f"speaker locator {evidence.speaker!r}" if evidence.speaker is not None else ""),
                (
                    f"timestamp locator {evidence.timestamp!r}"
                    if evidence.timestamp is not None
                    else ""
                ),
            )
            if locator
        )
        _fail(path, f"{supplied_locators} do not match the same quote span")

    if evidence.reference is not None:
        match = _TRANSCRIPT_LINE_REFERENCE_PATTERN.fullmatch(evidence.reference)
        if match is not None:
            line_number = int(match.group("line"))
            candidate_spans = located_quote_spans if has_utterance_locator else quote_spans
            if not any(
                _line_number_at(source, quote_start) == line_number
                for quote_start, _ in candidate_spans
            ):
                _fail(
                    path,
                    f"reference {evidence.reference!r} does not resolve to the quote span",
                )


def _record_reference(
    path: str,
    evidence: SourceEvidence,
    quote: str,
    signatures: dict[str, tuple[str, ...]],
) -> None:
    if evidence.reference is None:
        return
    signature = (
        evidence.source_type.value,
        quote,
        evidence.speaker or "",
        evidence.timestamp or "",
        evidence.section or "",
    )
    previous = signatures.setdefault(evidence.reference, signature)
    if previous != signature:
        _fail(path, f"reference {evidence.reference!r} conflicts with earlier evidence")


def _heading_spans(document: str) -> tuple[_HeadingSpan, ...]:
    matches = list(_HEADING_PATTERN.finditer(document))
    headings: list[_HeadingSpan] = []
    for index, match in enumerate(matches):
        level = len(match.group("marks"))
        end = len(document)
        for later in matches[index + 1 :]:
            if len(later.group("marks")) <= level:
                end = later.start()
                break
        raw_number = match.group("number")
        headings.append(
            _HeadingSpan(
                level=level,
                number=int(raw_number) if raw_number is not None else None,
                title=match.group("title").strip(),
                start=match.start(),
                end=end,
            )
        )
    return tuple(headings)


def _transcript_utterances(document: str) -> tuple[_TranscriptUtterance, ...]:
    matches = list(_TRANSCRIPT_UTTERANCE_PATTERN.finditer(document))
    utterances: list[_TranscriptUtterance] = []
    for index, match in enumerate(matches):
        utterances.append(
            _TranscriptUtterance(
                speaker=match.group("speaker").strip(),
                timestamp=match.group("timestamp").strip(),
                start=match.start(),
                end=matches[index + 1].start() if index + 1 < len(matches) else len(document),
            )
        )
    return tuple(utterances)


def _quote_spans(document: str, quote: str) -> tuple[tuple[int, int], ...]:
    spans: list[tuple[int, int]] = []
    start = 0
    while True:
        index = document.find(quote, start)
        if index < 0:
            return tuple(spans)
        spans.append((index, index + len(quote)))
        start = index + 1


def _line_number_at(document: str, offset: int) -> int:
    return document.count("\n", 0, offset) + 1


def _spans_in_headings(
    quote_spans: tuple[tuple[int, int], ...],
    headings: list[_HeadingSpan],
) -> tuple[tuple[int, int], ...]:
    return tuple(
        (quote_start, quote_end)
        for quote_start, quote_end in quote_spans
        if any(heading.start <= quote_start and quote_end <= heading.end for heading in headings)
    )


def _normalize_source(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def _normalize_quote(value: str) -> str:
    return _normalize_source(value)


def _normalize_locator(value: str) -> str:
    return " ".join(value.split())


def _fail(path: str, reason: str) -> None:
    raise EvidenceValidationError(f"Invalid source evidence at {path}: {reason}.")
