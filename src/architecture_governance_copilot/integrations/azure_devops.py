"""Azure DevOps Create/read-back contracts with deterministic fake gateways."""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Annotated, Protocol, runtime_checkable
from urllib.parse import unquote, urlparse

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

JSON_PATCH_CONTENT_TYPE = "application/json-patch+json"


class _BoundaryModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class AdoFieldMapping(_BoundaryModel):
    """Approved target field references and fixed classification values."""

    title: NonEmptyString
    description: NonEmptyString
    assigned_to: NonEmptyString
    due_date: NonEmptyString
    priority: NonEmptyString
    tags: NonEmptyString
    correlation: NonEmptyString
    classification_values: dict[NonEmptyString, NonEmptyString] = Field(min_length=1)

    @model_validator(mode="after")
    def require_distinct_field_references(self) -> AdoFieldMapping:
        """Prevent one patch operation from silently replacing another."""
        references = [
            self.title,
            self.description,
            self.assigned_to,
            self.due_date,
            self.priority,
            self.tags,
            self.correlation,
            *self.classification_values,
        ]
        if len(references) != len(set(references)):
            raise ValueError("Azure DevOps field references must be distinct.")
        if any(
            not reference.startswith("System.") and "." not in reference for reference in references
        ):
            raise ValueError("Azure DevOps field references must use reference names.")
        return self


class AdoTargetConfiguration(_BoundaryModel):
    """Explicit synthetic target and process mapping used for one publication."""

    organization_url: NonEmptyString
    project: NonEmptyString
    work_item_type: NonEmptyString
    api_version: NonEmptyString = "7.1"
    fields: AdoFieldMapping
    owner_identities: dict[NonEmptyString, NonEmptyString] = Field(min_length=1)
    parent_work_item_ids: dict[NonEmptyString, int] = Field(min_length=1)
    priority_values: dict[NonEmptyString, int] = Field(min_length=1)
    require_owner: bool = True
    require_due_date: bool = True
    require_parent: bool = True

    @model_validator(mode="after")
    def validate_target(self) -> AdoTargetConfiguration:
        """Reject unsafe URLs and invalid configured numeric values."""
        parsed = urlparse(self.organization_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("A valid Azure DevOps organization URL is required.")
        if any(identifier < 1 for identifier in self.parent_work_item_ids.values()):
            raise ValueError("Mapped parent work-item IDs must be positive integers.")
        if any(value < 1 for value in self.priority_values.values()):
            raise ValueError("Mapped priority values must be positive integers.")
        return self


class AdoJsonPatchOperation(_BoundaryModel):
    """One immutable JSON Patch add operation."""

    op: str = "add"
    path: NonEmptyString
    value: object

    @model_validator(mode="after")
    def validate_operation(self) -> AdoJsonPatchOperation:
        if self.op != "add" or not self.path.startswith("/"):
            raise ValueError("Only absolute JSON Patch add operations are supported.")
        return self


class AdoCreateRequest(_BoundaryModel):
    """Exact request represented by a separately confirmable preview."""

    url: NonEmptyString
    content_type: NonEmptyString = JSON_PATCH_CONTENT_TYPE
    operations: tuple[AdoJsonPatchOperation, ...] = Field(min_length=1)
    correlation_id: NonEmptyString
    binding_fingerprint: NonEmptyString


class AdoApiResponse(_BoundaryModel):
    """Minimal HTTP response facts needed for receipt and read-back validation."""

    status_code: int
    content_type: NonEmptyString
    body: str | Mapping[str, object]


class AdoWorkItemRecord(_BoundaryModel):
    """Explicitly mapped work-item fields used for verification."""

    work_item_id: int = Field(ge=1)
    revision: int = Field(ge=1)
    api_url: NonEmptyString
    browser_url: NonEmptyString
    fields: dict[str, object]
    relations: tuple[dict[str, object], ...] = ()


class AdoGatewayErrorCategory(StrEnum):
    """Safe gateway failure categories with clear write uncertainty."""

    DEFINITE_FAILURE = "definite_failure"
    UNKNOWN_RESULT = "unknown_result"


class AdoGatewayError(RuntimeError):
    """Gateway failure that records whether Create may have reached the server."""

    def __init__(self, category: AdoGatewayErrorCategory) -> None:
        self.category = category
        message = (
            "The Azure DevOps request definitely failed before creation."
            if category is AdoGatewayErrorCategory.DEFINITE_FAILURE
            else "The Azure DevOps Create result is unknown and requires reconciliation."
        )
        super().__init__(message)


@runtime_checkable
class AdoGateway(Protocol):
    """Minimal Create, read-back, and correlation-reconciliation boundary."""

    def find_by_correlation(
        self,
        target: AdoTargetConfiguration,
        correlation_id: str,
    ) -> tuple[int, ...]:
        """Return every matching work-item ID without silently choosing one."""
        ...

    def create_work_item(self, request: AdoCreateRequest) -> AdoApiResponse:
        """Submit one already confirmed exact request."""
        ...

    def get_work_item(
        self,
        target: AdoTargetConfiguration,
        work_item_id: int,
    ) -> AdoApiResponse:
        """Read one known work item for field verification."""
        ...


class FakeAdoGateway:
    """Queue synthetic gateway outcomes and record every explicit operation."""

    def __init__(
        self,
        *,
        correlation_results: Mapping[str, Sequence[int] | Exception] | None = None,
        create_results: Sequence[AdoApiResponse | Exception] = (),
        read_results: Mapping[int, AdoApiResponse | Exception] | None = None,
    ) -> None:
        self._correlation_results = dict(correlation_results or {})
        self._create_results = list(create_results)
        self._read_results = dict(read_results or {})
        self.lookup_calls: list[tuple[AdoTargetConfiguration, str]] = []
        self.create_calls: list[AdoCreateRequest] = []
        self.read_calls: list[tuple[AdoTargetConfiguration, int]] = []

    def find_by_correlation(
        self,
        target: AdoTargetConfiguration,
        correlation_id: str,
    ) -> tuple[int, ...]:
        self.lookup_calls.append((target, correlation_id))
        result = self._correlation_results.get(correlation_id, ())
        if isinstance(result, Exception):
            raise result
        return tuple(result)

    def create_work_item(self, request: AdoCreateRequest) -> AdoApiResponse:
        self.create_calls.append(request)
        if not self._create_results:
            raise AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT)
        result = self._create_results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result.model_copy(deep=True)

    def get_work_item(
        self,
        target: AdoTargetConfiguration,
        work_item_id: int,
    ) -> AdoApiResponse:
        self.read_calls.append((target, work_item_id))
        result = self._read_results.get(work_item_id)
        if result is None:
            raise AdoGatewayError(AdoGatewayErrorCategory.DEFINITE_FAILURE)
        if isinstance(result, Exception):
            raise result
        return result.model_copy(deep=True)


class InMemoryFakeAdoGateway:
    """Persist synthetic work items for the configured UI session without network access."""

    def __init__(self, *, next_work_item_id: int = 7001) -> None:
        self._next_work_item_id = next_work_item_id
        self._items: dict[int, dict[str, object]] = {}
        self.lookup_calls: list[str] = []
        self.create_calls: list[AdoCreateRequest] = []
        self.read_calls: list[int] = []

    def find_by_correlation(
        self,
        target: AdoTargetConfiguration,
        correlation_id: str,
    ) -> tuple[int, ...]:
        self.lookup_calls.append(correlation_id)
        correlation_field = target.fields.correlation
        matches: list[int] = []
        for work_item_id, item in self._items.items():
            fields = item.get("fields")
            if isinstance(fields, Mapping) and fields.get(correlation_field) == correlation_id:
                matches.append(work_item_id)
        return tuple(matches)

    def create_work_item(self, request: AdoCreateRequest) -> AdoApiResponse:
        self.create_calls.append(request)
        work_item_id = self._next_work_item_id
        self._next_work_item_id += 1
        fields: dict[str, object] = {}
        relations: list[dict[str, object]] = []
        for operation in request.operations:
            if operation.path.startswith("/fields/"):
                fields[operation.path.removeprefix("/fields/")] = copy.deepcopy(operation.value)
            elif operation.path == "/relations/-" and isinstance(operation.value, Mapping):
                relations.append(dict(operation.value))
        project, work_item_type, organization_url = _request_target_parts(request.url)
        fields["System.TeamProject"] = project
        fields["System.WorkItemType"] = work_item_type
        api_url = f"{organization_url}/{project}/_apis/wit/workItems/{work_item_id}"
        browser_url = f"{organization_url}/{project}/_workitems/edit/{work_item_id}"
        item = {
            "id": work_item_id,
            "rev": 1,
            "url": api_url,
            "fields": fields,
            "relations": relations,
            "_links": {"html": {"href": browser_url}},
        }
        self._items[work_item_id] = item
        return AdoApiResponse(
            status_code=201,
            content_type="application/json",
            body=copy.deepcopy(item),
        )

    def get_work_item(
        self,
        target: AdoTargetConfiguration,
        work_item_id: int,
    ) -> AdoApiResponse:
        del target
        self.read_calls.append(work_item_id)
        item = self._items.get(work_item_id)
        if item is None:
            return AdoApiResponse(
                status_code=404,
                content_type="application/json",
                body={"message": "Synthetic work item was not found."},
            )
        return AdoApiResponse(
            status_code=200,
            content_type="application/json",
            body=copy.deepcopy(item),
        )


def parse_work_item_response(response: AdoApiResponse) -> AdoWorkItemRecord:
    """Map a successful Create or GET response without retaining extra upstream data."""
    if response.status_code not in {200, 201}:
        raise AdoGatewayError(AdoGatewayErrorCategory.DEFINITE_FAILURE)
    media_type = response.content_type.split(";", 1)[0].strip().lower()
    if media_type != "application/json" and not media_type.endswith("+json"):
        raise AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT)
    try:
        body = json.loads(response.body) if isinstance(response.body, str) else response.body
    except json.JSONDecodeError as exc:
        raise AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT) from exc
    if not isinstance(body, Mapping):
        raise AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT)
    work_item_id = body.get("id")
    revision = body.get("rev")
    if (
        isinstance(work_item_id, bool)
        or not isinstance(work_item_id, int)
        or work_item_id < 1
        or isinstance(revision, bool)
        or not isinstance(revision, int)
        or revision < 1
    ):
        raise AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT)
    fields = body.get("fields")
    if not isinstance(fields, Mapping):
        raise AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT)
    api_url = _safe_url(body.get("url"))
    links = body.get("_links")
    if not isinstance(links, Mapping):
        raise AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT)
    html_link = links.get("html")
    if not isinstance(html_link, Mapping):
        raise AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT)
    browser_url = _safe_url(html_link.get("href"))
    relations_value = body.get("relations", ())
    if not isinstance(relations_value, Sequence) or isinstance(relations_value, (str, bytes)):
        raise AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT)
    relations: list[dict[str, object]] = []
    for relation in relations_value:
        if not isinstance(relation, Mapping):
            raise AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT)
        relations.append(dict(relation))
    return AdoWorkItemRecord(
        work_item_id=work_item_id,
        revision=revision,
        api_url=api_url,
        browser_url=browser_url,
        fields=dict(fields),
        relations=tuple(relations),
    )


def _safe_url(value: object) -> str:
    if not isinstance(value, str):
        raise AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT)
    parsed = urlparse(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username
        or parsed.password
    ):
        raise AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT)
    return value


def _request_target_parts(url: str) -> tuple[str, str, str]:
    parsed = urlparse(url)
    segments = [segment for segment in parsed.path.split("/") if segment]
    api_index = segments.index("_apis")
    project = unquote(segments[api_index - 1])
    encoded_type = segments[api_index + 3]
    work_item_type = unquote(encoded_type.removeprefix("$"))
    organization_path = "/".join(segments[: api_index - 1])
    organization_url = f"{parsed.scheme}://{parsed.netloc}"
    if organization_path:
        organization_url = f"{organization_url}/{organization_path}"
    return project, work_item_type, organization_url
