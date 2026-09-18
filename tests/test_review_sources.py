"""Physical-line index behavior against original source locations."""

import pytest

from architecture_governance_copilot.models import EvidenceSource
from architecture_governance_copilot.review_sources import (
    SOURCE_INDEX_VERSION,
    build_review_source_index,
)


def test_line_index_preserves_original_spans_and_normalizes_newlines() -> None:
    si = "\r\n  # Overview\r\nRepeated text\r\n\r\n## 2. Recovery\r\nRepeated text  \r\n"
    transcript = "\r\nPreamble\r\n[09:00] Lee: Follow up\r\n  on the proposed date.\r\n"
    index = build_review_source_index(si, transcript)
    normalized = build_review_source_index(
        si.replace("\r\n", "\n").strip(), transcript.replace("\r\n", "\n").strip()
    )
    assert index.version == SOURCE_INDEX_VERSION
    assert [item.source_id for item in index.entries] == [
        item.source_id for item in normalized.entries
    ]
    for item in index.entries:
        original = si if item.source_type is EvidenceSource.SOLUTION_INTENT else transcript
        assert original[item.original_start : item.original_end] == item.original_text
    repeated = [item for item in index.entries if item.text.strip() == "Repeated text"]
    assert repeated[0].source_id != repeated[1].source_id
    assert [item.section for item in repeated] == ["Overview", "Recovery"]
    preamble = next(item for item in index.entries if item.text == "Preamble")
    assert preamble.speaker is None and preamble.timestamp is None
    continuation = next(item for item in index.entries if "proposed date" in item.text)
    assert continuation.speaker == "Lee" and continuation.timestamp == "09:00"
    assert continuation.to_evidence().quote == "on the proposed date."


def test_repeated_headings_and_plain_transcript_remain_distinct() -> None:
    index = build_review_source_index(
        "## Scope\nSame\n## Scope\nSame", "Plain action\nPlain action"
    )
    assert len(index.by_id) == 6
    assert len({item.source_id for item in index.entries}) == 6
    assert all(item.speaker is None for item in index.entries)
    assert index.render_annotated_sources().count("Plain action") == 2
    ids = [item.source_id for item in index.entries if item.text == "Same"]
    assert len(index.resolve(ids)) == 2
    assert index.resolve(ids)[0].reference != index.resolve(ids)[1].reference


def test_changed_source_cannot_reuse_previous_ids() -> None:
    old = build_review_source_index("SI", "Action")
    changed = build_review_source_index("SI", "Changed action")
    with pytest.raises(ValueError, match="snapshots"):
        changed.resolve([old.entries[-1].source_id])


def test_unknown_duplicate_and_blank_line_evidence_are_rejected() -> None:
    index = build_review_source_index("SI\n\nMore", "Transcript")
    for ids in ([], ["unknown"], [index.entries[0].source_id] * 2):
        with pytest.raises(ValueError):
            index.resolve(ids)
    with pytest.raises(ValueError, match="Blank source"):
        index.resolve([index.entries[1].source_id])
    with pytest.raises(ValueError, match="nonblank"):
        build_review_source_index(" ", "Transcript")
