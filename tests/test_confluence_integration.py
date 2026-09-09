"""Tests for the bounded fake Confluence read contract."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from architecture_governance_copilot.integrations.confluence import (
    CANONICALIZER_VERSION,
    ConfluenceBodyFormat,
    ConfluencePagePayload,
    ConfluenceReadError,
    FakeConfluenceReader,
    build_confluence_snapshot,
    canonicalize_confluence_body,
)


def _payload(**changes: object) -> ConfluencePagePayload:
    values: dict[str, object] = {
        "page_id": "synthetic-42",
        "title": "Synthetic Solution Intent",
        "space": "SYNTHETIC",
        "version": 3,
        "url": "https://example.invalid/wiki/synthetic-42",
        "raw_body": "# Synthetic SI\r\n\r\nComplete body.  \r\n",
        "body_format": "markdown",
    }
    values.update(changes)
    return ConfluencePagePayload.model_validate(values)


def test_snapshot_retains_complete_source_and_derives_stable_content_identity() -> None:
    first_time = datetime(2026, 9, 9, 9, 0, tzinfo=UTC)
    second_time = first_time + timedelta(minutes=5)

    first = build_confluence_snapshot(_payload(), retrieved_at=first_time)
    second = build_confluence_snapshot(_payload(), retrieved_at=second_time)

    assert first.page_id == "synthetic-42"
    assert first.title == "Synthetic Solution Intent"
    assert first.space == "SYNTHETIC"
    assert first.version == 3
    assert first.url.startswith("https://example.invalid/")
    assert first.raw_body == "# Synthetic SI\r\n\r\nComplete body.  \r\n"
    assert first.body_format is ConfluenceBodyFormat.MARKDOWN
    assert first.canonical_text == "# Synthetic SI\n\nComplete body."
    assert first.canonicalizer_version == CANONICALIZER_VERSION
    assert first.retrieved_at == first_time
    assert second.retrieved_at == second_time
    assert second.content_fingerprint == first.content_fingerprint
    with pytest.raises(ValidationError):
        first.version = 4


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"body_format": "storage"}, "format"),
        ({"truncated": True}, "truncated"),
        ({"fully_processed": False}, "not fully processed"),
    ],
)
def test_snapshot_rejects_unverifiable_page_bodies(
    changes: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ConfluenceReadError, match=message):
        build_confluence_snapshot(
            _payload(**changes),
            retrieved_at=datetime(2026, 9, 9, tzinfo=UTC),
        )


def test_canonicalizer_rejects_an_empty_normalized_body() -> None:
    with pytest.raises(ConfluenceReadError, match="empty"):
        canonicalize_confluence_body("  \r\n ", ConfluenceBodyFormat.PLAIN_TEXT)


def test_fake_reader_is_called_only_explicitly_and_fails_safely() -> None:
    now = datetime(2026, 9, 9, 9, 0, tzinfo=UTC)
    reader = FakeConfluenceReader({"synthetic-42": _payload()}, clock=lambda: now)

    assert reader.calls == []
    snapshot = reader.get_page(" synthetic-42 ")

    assert snapshot.retrieved_at == now
    assert reader.calls == ["synthetic-42"]
    with pytest.raises(ConfluenceReadError, match="not found"):
        reader.get_page("missing")
    assert reader.calls == ["synthetic-42", "missing"]


def test_boundary_models_reject_unknown_fields_and_inconsistent_snapshots() -> None:
    with pytest.raises(ValidationError, match="extra_forbidden"):
        ConfluencePagePayload.model_validate(
            {**_payload().model_dump(), "unexpected": "provider-only"}
        )

    snapshot = build_confluence_snapshot(
        _payload(),
        retrieved_at=datetime(2026, 9, 9, tzinfo=UTC),
    )
    changed = snapshot.model_dump()
    changed["content_fingerprint"] = "untrusted"
    with pytest.raises(ValidationError, match="content_fingerprint"):
        type(snapshot).model_validate(changed)
