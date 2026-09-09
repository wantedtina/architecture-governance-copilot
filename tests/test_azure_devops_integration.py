"""Tests for Azure DevOps transport, receipt, and fake gateway contracts."""

from __future__ import annotations

from architecture_governance_copilot.integrations.azure_devops import (
    AdoApiResponse,
    AdoCreateRequest,
    AdoGateway,
    AdoGatewayError,
    AdoGatewayErrorCategory,
    AdoJsonPatchOperation,
    FakeAdoGateway,
    parse_work_item_response,
)


def test_work_item_response_maps_receipt_fields_and_ignores_extensions() -> None:
    response = AdoApiResponse(
        status_code=200,
        content_type="application/json; charset=utf-8",
        body={
            "id": 7001,
            "rev": 3,
            "url": "https://example.invalid/ado/project/_apis/wit/workItems/7001",
            "fields": {"System.Title": "Synthetic action"},
            "relations": [{"rel": "Synthetic", "url": "https://example.invalid/parent"}],
            "_links": {
                "html": {"href": "https://example.invalid/ado/project/_workitems/edit/7001"}
            },
            "processGeneratedField": "ignored",
        },
    )

    record = parse_work_item_response(response)

    assert record.work_item_id == 7001
    assert record.revision == 3
    assert record.api_url.endswith("/_apis/wit/workItems/7001")
    assert record.browser_url.endswith("/_workitems/edit/7001")
    assert record.fields == {"System.Title": "Synthetic action"}
    assert "processGeneratedField" not in type(record).model_fields


def test_non_success_is_definite_but_malformed_success_is_unknown() -> None:
    non_success = AdoApiResponse(
        status_code=400,
        content_type="application/json",
        body={"message": "synthetic rejected"},
    )
    malformed_success = AdoApiResponse(
        status_code=201,
        content_type="text/html",
        body="<html>synthetic login</html>",
    )

    for response, category in (
        (non_success, AdoGatewayErrorCategory.DEFINITE_FAILURE),
        (malformed_success, AdoGatewayErrorCategory.UNKNOWN_RESULT),
    ):
        try:
            parse_work_item_response(response)
        except AdoGatewayError as exc:
            assert exc.category is category
            assert "synthetic" not in str(exc)
        else:
            raise AssertionError("Invalid gateway response was accepted.")


def test_fake_gateway_records_explicit_calls_only() -> None:
    gateway = FakeAdoGateway()
    assert isinstance(gateway, AdoGateway)
    assert gateway.lookup_calls == []
    assert gateway.create_calls == []
    assert gateway.read_calls == []


def test_create_request_requires_only_add_operations() -> None:
    request = AdoCreateRequest(
        url="https://example.invalid/ado/project/_apis/wit/workitems/$Task?api-version=7.1",
        operations=(AdoJsonPatchOperation(path="/fields/System.Title", value="Synthetic"),),
        correlation_id="agc-synthetic",
        binding_fingerprint="binding",
    )

    assert request.content_type == "application/json-patch+json"
    assert request.operations[0].op == "add"
