"""Bounded Confluence read contract with deterministic offline fakes."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
RawBody = Annotated[str, StringConstraints(min_length=1)]

CANONICALIZER_VERSION = "plain-text-v1"


class ConfluenceBodyFormat(StrEnum):
    """Body formats supported by the external fake boundary."""

    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"


class _BoundaryModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ConfluencePagePayload(_BoundaryModel):
    """Minimal upstream page fields accepted by the fake read adapter."""

    page_id: NonEmptyString
    title: NonEmptyString
    space: NonEmptyString
    version: int = Field(ge=1)
    url: NonEmptyString
    raw_body: RawBody
    body_format: str
    truncated: bool = False
    fully_processed: bool = True


class ConfluencePageSnapshot(_BoundaryModel):
    """Immutable-in-practice source snapshot used throughout one review session."""

    page_id: NonEmptyString
    title: NonEmptyString
    space: NonEmptyString
    version: int = Field(ge=1)
    url: NonEmptyString
    retrieved_at: datetime
    raw_body: RawBody
    body_format: ConfluenceBodyFormat
    canonical_text: NonEmptyString
    canonicalizer_version: NonEmptyString
    content_fingerprint: NonEmptyString

    @model_validator(mode="after")
    def validate_snapshot(self) -> ConfluencePageSnapshot:
        """Reject snapshots whose derived fields do not match their retained body."""
        expected_text = canonicalize_confluence_body(self.raw_body, self.body_format)
        if self.canonical_text != expected_text:
            raise ValueError("canonical_text does not match the retained raw body")
        expected_fingerprint = confluence_content_fingerprint(expected_text)
        if self.content_fingerprint != expected_fingerprint:
            raise ValueError("content_fingerprint does not match canonical_text")
        if self.retrieved_at.tzinfo is None:
            raise ValueError("retrieved_at must include timezone information")
        return self


class ConfluenceReadError(RuntimeError):
    """Report a safe, recoverable fake Confluence read failure."""


@runtime_checkable
class ConfluenceReader(Protocol):
    """Read one configured Confluence page snapshot by explicit page ID."""

    def get_page(self, page_id: str) -> ConfluencePageSnapshot:
        """Return a complete canonical source snapshot."""
        ...


def canonicalize_confluence_body(
    raw_body: str,
    body_format: ConfluenceBodyFormat | str,
) -> str:
    """Canonicalize only externally verifiable plain-text-like formats."""
    try:
        supported_format = ConfluenceBodyFormat(body_format)
    except ValueError as exc:
        raise ConfluenceReadError("The page body format is not supported by this adapter.") from exc
    if supported_format not in {
        ConfluenceBodyFormat.MARKDOWN,
        ConfluenceBodyFormat.PLAIN_TEXT,
    }:
        raise ConfluenceReadError("The page body format is not supported by this adapter.")
    canonical_text = raw_body.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not canonical_text:
        raise ConfluenceReadError("The page body is empty after canonicalization.")
    return canonical_text


def confluence_content_fingerprint(canonical_text: str) -> str:
    """Hash canonical page content without retrieval-time metadata."""
    return hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()


def build_confluence_snapshot(
    payload: ConfluencePagePayload,
    *,
    retrieved_at: datetime,
) -> ConfluencePageSnapshot:
    """Validate a complete payload and derive its canonical source fields."""
    if payload.truncated:
        raise ConfluenceReadError("The page body is truncated and cannot be analyzed.")
    if not payload.fully_processed:
        raise ConfluenceReadError("The page body was not fully processed.")
    canonical_text = canonicalize_confluence_body(payload.raw_body, payload.body_format)
    return ConfluencePageSnapshot(
        page_id=payload.page_id,
        title=payload.title,
        space=payload.space,
        version=payload.version,
        url=payload.url,
        retrieved_at=retrieved_at,
        raw_body=payload.raw_body,
        body_format=ConfluenceBodyFormat(payload.body_format),
        canonical_text=canonical_text,
        canonicalizer_version=CANONICALIZER_VERSION,
        content_fingerprint=confluence_content_fingerprint(canonical_text),
    )


class FakeConfluenceReader:
    """Return configured synthetic pages without network access."""

    def __init__(
        self,
        pages: Mapping[str, ConfluencePagePayload | Exception],
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._pages = dict(pages)
        self._clock = clock or (lambda: datetime.now(UTC))
        self.calls: list[str] = []

    def get_page(self, page_id: str) -> ConfluencePageSnapshot:
        """Read exactly one configured page and record the explicit invocation."""
        normalized_page_id = page_id.strip()
        if not normalized_page_id:
            raise ConfluenceReadError("A configured page ID is required.")
        self.calls.append(normalized_page_id)
        configured = self._pages.get(normalized_page_id)
        if configured is None:
            raise ConfluenceReadError("The configured page was not found.")
        if isinstance(configured, Exception):
            raise configured
        return build_confluence_snapshot(configured, retrieved_at=self._clock())
