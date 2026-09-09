"""Bounded Confluence read contract with deterministic offline fakes."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from html.parser import HTMLParser
from typing import Annotated, Protocol, runtime_checkable
from urllib.parse import urljoin, urlparse

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
RawBody = Annotated[str, StringConstraints(min_length=1)]

CANONICALIZER_VERSION = "plain-text-v1"
STORAGE_CANONICALIZER_VERSION = "confluence-storage-v1"
CONTENT_API_EXPANSION = "body.storage,version,space"


class ConfluenceBodyFormat(StrEnum):
    """Body formats supported by the external fake boundary."""

    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"
    STORAGE = "storage"


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


@dataclass(frozen=True, slots=True)
class ConfluenceApiResponse:
    """Minimal HTTP response facts required at the content API boundary."""

    status_code: int
    content_type: str
    body: str | Mapping[str, object]


@runtime_checkable
class ConfluenceContentTransport(Protocol):
    """Fetch one content API object for an explicit page and expansion."""

    def get_content(
        self,
        page_id: str,
        *,
        expand: str,
    ) -> ConfluenceApiResponse:
        """Return response metadata and a JSON-compatible body."""
        ...


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
    if supported_format is ConfluenceBodyFormat.STORAGE:
        canonical_text = _StorageCanonicalizer().convert(raw_body)
    else:
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
        canonicalizer_version=(
            STORAGE_CANONICALIZER_VERSION
            if ConfluenceBodyFormat(payload.body_format) is ConfluenceBodyFormat.STORAGE
            else CANONICALIZER_VERSION
        ),
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


class FakeConfluenceContentTransport:
    """Return synthetic content API responses and record explicit fetches."""

    def __init__(
        self,
        responses: Mapping[str, ConfluenceApiResponse | Exception],
    ) -> None:
        self._responses = dict(responses)
        self.calls: list[tuple[str, str]] = []

    def get_content(
        self,
        page_id: str,
        *,
        expand: str,
    ) -> ConfluenceApiResponse:
        """Return exactly one configured response without making a network call."""
        self.calls.append((page_id, expand))
        configured = self._responses.get(page_id)
        if configured is None:
            raise ConfluenceReadError("The configured page was not found.")
        if isinstance(configured, Exception):
            raise configured
        return configured


class ConfluenceContentApiReader:
    """Validate and map one expanded content API response into a source snapshot."""

    def __init__(
        self,
        transport: ConfluenceContentTransport,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._transport = transport
        self._clock = clock or (lambda: datetime.now(UTC))

    def get_page(self, page_id: str) -> ConfluencePageSnapshot:
        """Fetch one explicit page with body, version, and space in the same response."""
        normalized_page_id = page_id.strip()
        if not normalized_page_id:
            raise ConfluenceReadError("A configured page ID is required.")
        try:
            response = self._transport.get_content(
                normalized_page_id,
                expand=CONTENT_API_EXPANSION,
            )
        except ConfluenceReadError:
            raise
        except Exception as exc:
            raise ConfluenceReadError("The configured page could not be retrieved.") from exc
        payload = _map_content_api_response(normalized_page_id, response)
        return build_confluence_snapshot(payload, retrieved_at=self._clock())


def _map_content_api_response(
    requested_page_id: str,
    response: ConfluenceApiResponse,
) -> ConfluencePagePayload:
    if response.status_code != 200:
        raise ConfluenceReadError("The page request did not return a successful response.")
    media_type = response.content_type.split(";", 1)[0].strip().lower()
    if media_type != "application/json" and not media_type.endswith("+json"):
        raise ConfluenceReadError("The page request did not return JSON content.")
    try:
        body = json.loads(response.body) if isinstance(response.body, str) else response.body
    except json.JSONDecodeError as exc:
        raise ConfluenceReadError("The page response was not valid JSON.") from exc
    if not isinstance(body, Mapping):
        raise ConfluenceReadError("The page response was not a single content object.")
    if "results" in body:
        raise ConfluenceReadError("The page response was a collection, not one content object.")

    page_id = _required_string(body, "id")
    if page_id != requested_page_id:
        raise ConfluenceReadError("The response page did not match the requested page.")
    if _required_string(body, "type") != "page":
        raise ConfluenceReadError("The requested content is not a page.")
    if _required_string(body, "status") != "current":
        raise ConfluenceReadError("The requested page is not in an acceptable current state.")

    version_object = _required_mapping(body, "version")
    version = version_object.get("number")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise ConfluenceReadError("The page response did not include a valid version number.")
    space_object = _required_mapping(body, "space")
    space = _required_string(space_object, "key")
    body_object = _required_mapping(body, "body")
    storage_object = _required_mapping(body_object, "storage")
    if _required_string(storage_object, "representation") != "storage":
        raise ConfluenceReadError("The page response used an unsupported body representation.")
    storage_value = storage_object.get("value")
    if not isinstance(storage_value, str):
        raise ConfluenceReadError("The expanded storage body is missing from the page response.")
    if not storage_value.strip():
        raise ConfluenceReadError("The expanded storage body is explicitly empty.")

    links = _required_mapping(body, "_links")
    url = _approved_web_url(links)
    return ConfluencePagePayload(
        page_id=page_id,
        title=_required_string(body, "title"),
        space=space,
        version=version,
        url=url,
        raw_body=storage_value,
        body_format=ConfluenceBodyFormat.STORAGE,
    )


def _required_mapping(source: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = source.get(key)
    if not isinstance(value, Mapping):
        raise ConfluenceReadError(f"The page response did not include a valid {key} object.")
    return value


def _required_string(source: Mapping[str, object], key: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfluenceReadError(f"The page response did not include a valid {key} value.")
    return value.strip()


def _approved_web_url(links: Mapping[str, object]) -> str:
    web_ui = _required_string(links, "webui")
    base = links.get("base")
    parsed_web_ui = urlparse(web_ui)
    if parsed_web_ui.scheme:
        candidate = web_ui
    elif isinstance(base, str) and base.strip():
        candidate = urljoin(f"{base.rstrip('/')}/", web_ui.lstrip("/"))
    else:
        raise ConfluenceReadError("The page response did not include an approved web URL.")
    parsed = urlparse(candidate)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username
        or parsed.password
    ):
        raise ConfluenceReadError("The page response did not include an approved web URL.")
    if parsed_web_ui.scheme and isinstance(base, str) and base.strip():
        parsed_base = urlparse(base)
        if (parsed.scheme.lower(), parsed.netloc.lower()) != (
            parsed_base.scheme.lower(),
            parsed_base.netloc.lower(),
        ):
            raise ConfluenceReadError("The page response did not include an approved web URL.")
    return candidate


class _StorageCanonicalizer(HTMLParser):
    """Convert a small verified subset of Confluence storage markup to stable text."""

    _INLINE_TAGS = {
        "a",
        "b",
        "code",
        "em",
        "i",
        "s",
        "span",
        "strike",
        "strong",
        "sub",
        "sup",
        "u",
    }
    _REJECTED_TAGS = {
        "ac:image",
        "audio",
        "embed",
        "iframe",
        "img",
        "object",
        "ri:attachment",
        "script",
        "style",
        "video",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._lines: list[str] = []
        self._buffer: list[str] | None = None
        self._block_prefix = ""
        self._list_types: list[str] = []
        self._ordered_counts: list[int] = []
        self._table_rows: list[tuple[list[str], bool]] | None = None
        self._row_cells: list[str] | None = None
        self._row_is_header = False
        self._cell_buffer: list[str] | None = None
        self._open_tags: list[str] = []

    def convert(self, storage_body: str) -> str:
        """Parse all markup and return canonical Markdown-like text."""
        try:
            self.feed(storage_body)
            self.close()
        except ConfluenceReadError:
            raise
        except Exception as exc:
            raise ConfluenceReadError("The storage body could not be converted safely.") from exc
        if (
            self._open_tags
            or self._buffer is not None
            or self._cell_buffer is not None
            or self._table_rows is not None
        ):
            raise ConfluenceReadError("The storage body contains incomplete markup.")
        return "\n".join(self._lines).strip()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        tag = tag.lower()
        self._validate_tag(tag)
        if tag != "br":
            self._open_tags.append(tag)
        if tag in {"ul", "ol"}:
            if self._buffer is not None or self._list_types:
                raise ConfluenceReadError("Nested or embedded lists are not supported.")
            self._list_types.append(tag)
            self._ordered_counts.append(0)
        elif tag == "li":
            if not self._list_types:
                raise ConfluenceReadError("A list item appeared outside a supported list.")
            if self._list_types[-1] == "ol":
                self._ordered_counts[-1] += 1
                prefix = f"{self._ordered_counts[-1]}. "
            else:
                prefix = "- "
            self._begin_block(prefix)
        elif tag in {"p", "div"}:
            if self._cell_buffer is None:
                self._begin_block("")
        elif tag in {f"h{level}" for level in range(1, 7)}:
            self._begin_block(f"{'#' * int(tag[1])} ")
        elif tag == "br":
            self._append_text("\n")
        elif tag == "table":
            if self._table_rows is not None or self._buffer is not None:
                raise ConfluenceReadError("Nested or embedded tables are not supported.")
            self._table_rows = []
        elif tag == "tr":
            if self._table_rows is None or self._row_cells is not None:
                raise ConfluenceReadError("The storage table structure is invalid.")
            self._row_cells = []
            self._row_is_header = False
        elif tag in {"th", "td"}:
            if self._row_cells is None or self._cell_buffer is not None:
                raise ConfluenceReadError("The storage table cell structure is invalid.")
            self._cell_buffer = []
            self._row_is_header = self._row_is_header or tag == "th"

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        self._validate_tag(tag)
        if tag == "br":
            return
        if not self._open_tags or self._open_tags[-1] != tag:
            raise ConfluenceReadError("The storage body contains mismatched markup.")
        self._open_tags.pop()
        if (
            tag in {"li", "p", "div"} | {f"h{level}" for level in range(1, 7)}
            and self._cell_buffer is None
        ):
            self._end_block()
        elif tag in {"th", "td"}:
            if self._cell_buffer is None or self._row_cells is None:
                raise ConfluenceReadError("The storage table cell structure is invalid.")
            cell = _normalize_inline_text("".join(self._cell_buffer)).replace("|", r"\|")
            self._row_cells.append(cell)
            self._cell_buffer = None
        elif tag == "tr":
            if self._row_cells is None or self._table_rows is None:
                raise ConfluenceReadError("The storage table row structure is invalid.")
            if not self._row_cells:
                raise ConfluenceReadError("Empty storage table rows are not supported.")
            self._table_rows.append((self._row_cells, self._row_is_header))
            self._row_cells = None
        elif tag == "table":
            self._end_table()
        elif tag in {"ul", "ol"}:
            if not self._list_types or self._list_types[-1] != tag:
                raise ConfluenceReadError("The storage list structure is invalid.")
            self._list_types.pop()
            self._ordered_counts.pop()

    def handle_data(self, data: str) -> None:
        if data.strip() or self._buffer is not None or self._cell_buffer is not None:
            self._append_text(data)

    def handle_entityref(self, name: str) -> None:
        self._append_text(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self._append_text(f"&#{name};")

    def _validate_tag(self, tag: str) -> None:
        supported = (
            self._INLINE_TAGS
            | self._REJECTED_TAGS
            | {
                "br",
                "div",
                "li",
                "ol",
                "p",
                "table",
                "tbody",
                "td",
                "tfoot",
                "th",
                "thead",
                "tr",
                "ul",
            }
            | {f"h{level}" for level in range(1, 7)}
        )
        if tag.startswith(("ac:", "ri:")) or tag in self._REJECTED_TAGS:
            raise ConfluenceReadError(
                "The storage body contains a macro, image, attachment, or embedded content."
            )
        if tag not in supported:
            raise ConfluenceReadError(f"The storage body contains unsupported markup: {tag}.")

    def _begin_block(self, prefix: str) -> None:
        if self._buffer is not None or self._cell_buffer is not None:
            raise ConfluenceReadError("The storage body contains unsupported nested blocks.")
        self._buffer = []
        self._block_prefix = prefix

    def _append_text(self, value: str) -> None:
        if self._cell_buffer is not None:
            self._cell_buffer.append(value)
        elif self._buffer is not None:
            self._buffer.append(value)
        elif value.strip():
            raise ConfluenceReadError("The storage body contains text outside supported blocks.")

    def _end_block(self) -> None:
        if self._buffer is None:
            raise ConfluenceReadError("The storage body block structure is invalid.")
        value = _normalize_inline_text("".join(self._buffer))
        if value:
            self._append_line(f"{self._block_prefix}{value}")
        self._buffer = None
        self._block_prefix = ""

    def _end_table(self) -> None:
        if self._table_rows is None or self._row_cells is not None:
            raise ConfluenceReadError("The storage table structure is invalid.")
        if not self._table_rows:
            raise ConfluenceReadError("Empty storage tables are not supported.")
        widths = {len(cells) for cells, _ in self._table_rows}
        if len(widths) != 1:
            raise ConfluenceReadError("Storage table rows must have consistent cell counts.")
        for index, (cells, is_header) in enumerate(self._table_rows):
            self._append_line(f"| {' | '.join(cells)} |")
            if index == 0 and is_header:
                self._append_line(f"| {' | '.join('---' for _ in cells)} |")
        self._table_rows = None

    def _append_line(self, value: str) -> None:
        if self._lines and self._lines[-1] == "" and value == "":
            return
        self._lines.append(value)


def _normalize_inline_text(value: str) -> str:
    return " ".join(value.replace("\r\n", "\n").replace("\r", "\n").split())
