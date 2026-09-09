"""Tests for the bounded fake Confluence read contract."""

from __future__ import annotations

import copy
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from architecture_governance_copilot.integrations.confluence import (
    CANONICALIZER_VERSION,
    CONTENT_API_EXPANSION,
    STORAGE_CANONICALIZER_VERSION,
    ConfluenceApiResponse,
    ConfluenceBodyFormat,
    ConfluenceContentApiReader,
    ConfluenceContentTransport,
    ConfluencePagePayload,
    ConfluenceReadError,
    FakeConfluenceContentTransport,
    FakeConfluenceReader,
    build_confluence_snapshot,
    canonicalize_confluence_body,
)

SAMPLES = Path(__file__).resolve().parents[1] / "samples"


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
        ({"body_format": "editor"}, "format"),
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


def _api_body() -> dict[str, Any]:
    return json.loads((SAMPLES / "internal_fake_confluence_page.json").read_text(encoding="utf-8"))


def _api_reader(
    body: str | dict[str, Any],
    *,
    status_code: int = 200,
    content_type: str = "application/json; charset=utf-8",
) -> tuple[ConfluenceContentApiReader, FakeConfluenceContentTransport]:
    transport = FakeConfluenceContentTransport(
        {
            "synthetic-page-204": ConfluenceApiResponse(
                status_code=status_code,
                content_type=content_type,
                body=body,
            )
        }
    )
    reader = ConfluenceContentApiReader(
        transport,
        clock=lambda: datetime(2026, 9, 9, 10, 30, tzinfo=UTC),
    )
    return reader, transport


@pytest.mark.parametrize("serialize", [False, True])
def test_content_api_reader_maps_one_expanded_response_explicitly(
    serialize: bool,
) -> None:
    body = _api_body()
    supplied_body: str | dict[str, Any] = json.dumps(body) if serialize else body
    reader, transport = _api_reader(supplied_body)

    assert isinstance(transport, ConfluenceContentTransport)
    assert transport.calls == []
    snapshot = reader.get_page(" synthetic-page-204 ")

    assert transport.calls == [("synthetic-page-204", CONTENT_API_EXPANSION)]
    assert snapshot.page_id == "synthetic-page-204"
    assert snapshot.title == "Solution Intent - Synthetic Order Routing Service"
    assert snapshot.space == "SYNTHETIC"
    assert snapshot.version == 7
    assert snapshot.url == (
        "https://example.invalid/wiki/spaces/SYNTHETIC/pages/synthetic-page-204"
    )
    assert snapshot.raw_body == body["body"]["storage"]["value"]
    assert snapshot.body_format is ConfluenceBodyFormat.STORAGE
    assert snapshot.canonicalizer_version == STORAGE_CANONICALIZER_VERSION
    assert (
        snapshot.canonical_text
        == (SAMPLES / "internal_fake_solution_intent.md").read_text(encoding="utf-8").strip()
    )
    assert snapshot.retrieved_at == datetime(2026, 9, 9, 10, 30, tzinfo=UTC)
    assert "history" not in type(snapshot).model_fields
    assert "upstreamExtension" not in type(snapshot).model_fields


def test_same_version_with_changed_storage_body_changes_content_identity() -> None:
    original_body = _api_body()
    changed_body = copy.deepcopy(original_body)
    changed_body["body"]["storage"]["value"] = changed_body["body"]["storage"]["value"].replace(
        "The service currently runs in a single availability zone.",
        "The synthetic service now has a documented recovery option.",
    )

    original = _api_reader(original_body)[0].get_page("synthetic-page-204")
    changed = _api_reader(changed_body)[0].get_page("synthetic-page-204")

    assert original.version == changed.version == 7
    assert original.raw_body != changed.raw_body
    assert original.content_fingerprint != changed.content_fingerprint


@pytest.mark.parametrize(
    ("body", "status_code", "content_type", "message"),
    [
        (
            {"results": [], "start": 0, "limit": 25, "size": 0},
            200,
            "application/json",
            "collection",
        ),
        (_api_body(), 401, "application/json", "successful"),
        ("<html>synthetic login</html>", 200, "text/html", "JSON content"),
        ("not-json", 200, "application/json", "valid JSON"),
    ],
)
def test_content_api_reader_rejects_collection_http_and_login_responses(
    body: str | dict[str, Any],
    status_code: int,
    content_type: str,
    message: str,
) -> None:
    reader, _ = _api_reader(
        body,
        status_code=status_code,
        content_type=content_type,
    )

    with pytest.raises(ConfluenceReadError, match=message) as captured:
        reader.get_page("synthetic-page-204")

    assert "synthetic login" not in str(captured.value)


def _without_version(body: dict[str, Any]) -> None:
    del body["version"]


def _without_body(body: dict[str, Any]) -> None:
    del body["body"]


def _without_storage_value(body: dict[str, Any]) -> None:
    del body["body"]["storage"]["value"]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda body: body.update({"id": "different-page"}), "requested page"),
        (lambda body: body.update({"type": "blogpost"}), "not a page"),
        (lambda body: body.update({"status": "trashed"}), "current state"),
        (_without_version, "version"),
        (lambda body: body["version"].update({"number": 0}), "version"),
        (lambda body: body["version"].update({"number": True}), "version"),
        (_without_body, "body"),
        (_without_storage_value, "storage body is missing"),
        (
            lambda body: body["body"]["storage"].update({"value": "  "}),
            "explicitly empty",
        ),
        (
            lambda body: body["body"]["storage"].update({"representation": "view"}),
            "representation",
        ),
        (
            lambda body: body["_links"].update({"base": "https://user@example.invalid/wiki"}),
            "approved web URL",
        ),
        (
            lambda body: body["_links"].update({"webui": "https://different.example.invalid/page"}),
            "approved web URL",
        ),
    ],
)
def test_content_api_reader_rejects_incomplete_or_mismatched_page_objects(
    change: object,
    message: str,
) -> None:
    body = copy.deepcopy(_api_body())
    change(body)  # type: ignore[operator]
    reader, _ = _api_reader(body)

    with pytest.raises(ConfluenceReadError, match=message):
        reader.get_page("synthetic-page-204")


def test_storage_converter_preserves_headings_paragraphs_lists_tables_and_text() -> None:
    storage = (
        "<h2>Review &amp; Controls</h2>"
        "<p>A <strong>synthetic</strong> paragraph.<br>Second line.</p>"
        "<ol><li>First item</li><li>Second item</li></ol>"
        "<table><tr><th>Control</th><th>State</th></tr>"
        "<tr><td>Publish</td><td>Disabled</td></tr></table>"
    )

    assert canonicalize_confluence_body(storage, ConfluenceBodyFormat.STORAGE) == (
        "## Review & Controls\n"
        "A synthetic paragraph. Second line.\n"
        "1. First item\n"
        "2. Second item\n"
        "| Control | State |\n"
        "| --- | --- |\n"
        "| Publish | Disabled |"
    )


@pytest.mark.parametrize(
    "storage",
    [
        "<ac:structured-macro ac:name='toc'></ac:structured-macro>",
        "<ac:image><ri:attachment ri:filename='synthetic.png'/></ac:image>",
        "<iframe src='https://example.invalid'></iframe>",
        "<p>Supported</p><custom-widget>Hidden text</custom-widget>",
        "<p>Incomplete",
    ],
)
def test_storage_converter_blocks_unsupported_or_incomplete_content(storage: str) -> None:
    with pytest.raises(ConfluenceReadError):
        canonicalize_confluence_body(storage, ConfluenceBodyFormat.STORAGE)


def test_content_api_transport_failure_is_wrapped_without_leaking_details() -> None:
    transport = FakeConfluenceContentTransport(
        {"synthetic-page-204": RuntimeError("synthetic secret response body")}
    )
    reader = ConfluenceContentApiReader(transport)

    with pytest.raises(ConfluenceReadError) as captured:
        reader.get_page("synthetic-page-204")

    assert str(captured.value) == "The configured page could not be retrieved."
