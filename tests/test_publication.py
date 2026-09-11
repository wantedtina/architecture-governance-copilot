"""Tests for exact-preview, confirmed, duplicate-aware ADO publication."""

from __future__ import annotations

import copy
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from architecture_governance_copilot.integrations.azure_devops import (
    AdoApiResponse,
    AdoFieldMapping,
    AdoGatewayError,
    AdoGatewayErrorCategory,
    AdoTargetConfiguration,
    FakeAdoGateway,
    InMemoryFakeAdoGateway,
)
from architecture_governance_copilot.integrations.confluence import (
    ConfluencePageSnapshot,
)
from architecture_governance_copilot.models import GovernanceResult
from architecture_governance_copilot.publication import (
    AdoPublicationCoordinator,
    AdoPublicationOperation,
    PublicationStatus,
    PublicationValidationError,
    build_ado_publication_preview,
    confirm_ado_publication_preview,
)
from architecture_governance_copilot.runtime_dependencies import ReviewMode, build_review_runtime


def _target(**updates: object) -> AdoTargetConfiguration:
    values: dict[str, object] = {
        "organization_url": "https://example.invalid/ado/synthetic-org",
        "project": "Synthetic Governance",
        "work_item_type": "Governance Action",
        "api_version": "7.1",
        "fields": AdoFieldMapping(
            title="System.Title",
            description="System.Description",
            assigned_to="System.AssignedTo",
            due_date="Microsoft.VSTS.Scheduling.DueDate",
            priority="Microsoft.VSTS.Common.Priority",
            tags="System.Tags",
            correlation="Custom.GovernanceCorrelation",
            classification_values={"Custom.GovernanceClassification": "Architecture"},
        ),
        "owner_identities": {
            "Avery Patel": "avery.patel.synthetic@example.invalid",
            "Riley Chen": "riley.chen.synthetic@example.invalid",
        },
        "parent_work_item_ids": {"SYN-204": 204},
        "priority_values": {"high": 1, "medium": 2, "low": 3},
    }
    values.update(updates)
    return AdoTargetConfiguration.model_validate(values)


def _preview_inputs() -> tuple[
    GovernanceResult,
    ConfluencePageSnapshot,
    AdoTargetConfiguration,
]:
    runtime = build_review_runtime(
        ReviewMode.INTERNAL_FAKE,
        {"AGC_INTERNAL_FAKE_ENABLED": "1"},
    )
    assert runtime.confluence_reader is not None
    assert runtime.confluence_page_id is not None
    assert runtime.review_transcript is not None
    assert runtime.review_context is not None
    snapshot = runtime.confluence_reader.get_page(runtime.confluence_page_id)
    result = runtime.extractor.extract(
        snapshot.canonical_text,
        runtime.review_transcript,
        runtime.review_context,
    )
    return result, snapshot, _target()


def test_preview_is_exact_encoded_and_contains_no_mock_disclaimer() -> None:
    result, snapshot, target = _preview_inputs()

    preview = build_ado_publication_preview(result, snapshot, 0, target)

    assert preview.request.url == (
        "https://example.invalid/ado/synthetic-org/Synthetic%20Governance/"
        "_apis/wit/workitems/$Governance%20Action?api-version=7.1"
    )
    assert preview.request.content_type == "application/json-patch+json"
    assert all(operation.op == "add" for operation in preview.request.operations)
    fields = {
        operation.path.removeprefix("/fields/"): operation.value
        for operation in preview.request.operations
        if operation.path.startswith("/fields/")
    }
    assert fields["System.Title"] == "Document retry and backoff controls"
    assert fields["System.AssignedTo"] == "riley.chen.synthetic@example.invalid"
    assert fields["Microsoft.VSTS.Common.Priority"] == 1
    assert fields["Custom.GovernanceClassification"] == "Architecture"
    assert fields["Custom.GovernanceCorrelation"] == preview.request.correlation_id
    assert "Supporting Evidence:" in fields["System.Description"]
    assert result.action_items[0].evidence[0].reference in fields["System.Description"]
    assert "provider-reference" not in fields["System.Description"]
    assert "No real Azure DevOps work item has been created" not in fields["System.Description"]
    parent = next(
        operation for operation in preview.request.operations if operation.path == "/relations/-"
    )
    assert parent.value["url"].endswith("/_apis/wit/workItems/204")


def test_preview_and_confirmation_fingerprints_cover_all_mutable_bindings() -> None:
    result, snapshot, target = _preview_inputs()
    original = build_ado_publication_preview(result, snapshot, 0, target)
    changed_result = result.model_copy(deep=True)
    changed_result.missing_evidence = []
    changed_mapping = target.model_copy(
        update={
            "fields": target.fields.model_copy(
                update={"classification_values": {"Custom.GovernanceClassification": "Risk"}}
            )
        }
    )
    changed_snapshot = snapshot.model_copy(
        update={"version": snapshot.version + 1},
    )

    result_preview = build_ado_publication_preview(changed_result, snapshot, 0, target)
    mapping_preview = build_ado_publication_preview(result, snapshot, 0, changed_mapping)
    source_preview = build_ado_publication_preview(result, changed_snapshot, 0, target)

    assert result_preview.preview_fingerprint != original.preview_fingerprint
    assert mapping_preview.preview_fingerprint != original.preview_fingerprint
    assert source_preview.preview_fingerprint != original.preview_fingerprint
    assert result_preview.request.correlation_id == original.request.correlation_id
    assert mapping_preview.request.correlation_id == original.request.correlation_id
    confirmation = confirm_ado_publication_preview(
        original,
        confirmed_at=datetime(2026, 9, 9, 11, 0, tzinfo=UTC),
    )
    assert confirmation.preview_fingerprint == original.preview_fingerprint


@pytest.mark.parametrize(
    ("result_change", "target", "message"),
    [
        (
            lambda result: setattr(result.action_items[0], "owner", "Unmapped Owner"),
            _target(),
            "owner",
        ),
        (lambda result: setattr(result.action_items[0], "due_date", None), _target(), "due date"),
        (
            lambda result: setattr(result.context, "ado_ticket_id", "SYN-NOT-MAPPED"),
            _target(),
            "parent",
        ),
    ],
)
def test_unmapped_or_missing_required_values_block_preview(
    result_change: object,
    target: AdoTargetConfiguration,
    message: str,
) -> None:
    result, snapshot, _ = _preview_inputs()
    result_change(result)  # type: ignore[operator]

    with pytest.raises(PublicationValidationError, match=message):
        build_ado_publication_preview(result, snapshot, 0, target)


def test_required_classification_mapping_cannot_be_empty() -> None:
    with pytest.raises(ValidationError):
        AdoFieldMapping(
            title="System.Title",
            description="System.Description",
            assigned_to="System.AssignedTo",
            due_date="Microsoft.VSTS.Scheduling.DueDate",
            priority="Microsoft.VSTS.Common.Priority",
            tags="System.Tags",
            correlation="Custom.GovernanceCorrelation",
            classification_values={},
        )


def test_successful_publication_transitions_create_once_and_verify_read_back() -> None:
    result, snapshot, target = _preview_inputs()
    preview = build_ado_publication_preview(result, snapshot, 0, target)
    confirmation = confirm_ado_publication_preview(preview)
    transitions: list[AdoPublicationOperation] = []
    gateway = InMemoryFakeAdoGateway()
    coordinator = AdoPublicationCoordinator(gateway, transition=transitions.append)

    operation = coordinator.publish(
        preview=preview,
        confirmation=confirmation,
        reviewed_result=result,
        source_snapshot=snapshot,
        target=target,
    )

    assert [item.status for item in transitions] == [
        PublicationStatus.SUBMITTING,
        PublicationStatus.SUCCEEDED,
    ]
    assert operation.status is PublicationStatus.SUCCEEDED
    assert operation.receipt is not None and operation.receipt.verified
    assert operation.receipt.work_item_id == 7001
    assert len(gateway.create_calls) == 1
    assert gateway.read_calls == [7001]

    with pytest.raises(PublicationValidationError, match="protected"):
        coordinator.publish(
            preview=preview,
            confirmation=confirmation,
            reviewed_result=result,
            source_snapshot=snapshot,
            target=target,
            prior_operations={operation.correlation_id: operation},
        )
    assert len(gateway.create_calls) == 1


def test_correlation_reconciliation_finds_existing_item_without_second_create() -> None:
    result, snapshot, target = _preview_inputs()
    preview = build_ado_publication_preview(result, snapshot, 0, target)
    confirmation = confirm_ado_publication_preview(preview)
    gateway = InMemoryFakeAdoGateway()
    first = AdoPublicationCoordinator(gateway).publish(
        preview=preview,
        confirmation=confirmation,
        reviewed_result=result,
        source_snapshot=snapshot,
        target=target,
    )

    reconciled = AdoPublicationCoordinator(gateway).publish(
        preview=preview,
        confirmation=confirmation,
        reviewed_result=result,
        source_snapshot=snapshot,
        target=target,
    )

    assert first.status is reconciled.status is PublicationStatus.SUCCEEDED
    assert len(gateway.create_calls) == 1
    assert reconciled.message.startswith("Existing correlated")


def test_stale_or_unconfirmed_preview_never_calls_gateway() -> None:
    result, snapshot, target = _preview_inputs()
    preview = build_ado_publication_preview(result, snapshot, 0, target)
    stale_result = result.model_copy(deep=True)
    stale_result.missing_evidence = []
    gateway = InMemoryFakeAdoGateway()

    with pytest.raises(PublicationValidationError, match="previewed and confirmed again"):
        AdoPublicationCoordinator(gateway).publish(
            preview=preview,
            confirmation=confirm_ado_publication_preview(preview),
            reviewed_result=stale_result,
            source_snapshot=snapshot,
            target=target,
        )

    assert gateway.lookup_calls == []
    assert gateway.create_calls == []


def _create_body(preview: object, *, title: str) -> dict[str, object]:
    return {
        "id": 7100,
        "rev": 1,
        "url": "https://example.invalid/ado/project/_apis/wit/workItems/7100",
        "fields": {"System.Title": title},
        "_links": {"html": {"href": "https://example.invalid/ado/project/_workitems/edit/7100"}},
    }


def test_known_created_id_is_retained_when_read_back_fields_mismatch() -> None:
    result, snapshot, target = _preview_inputs()
    preview = build_ado_publication_preview(result, snapshot, 0, target)
    create_body = _create_body(preview, title=preview.action_title)
    read_body = copy.deepcopy(create_body)
    read_body["fields"] = {"System.Title": "Mismatched title"}
    gateway = FakeAdoGateway(
        create_results=[
            AdoApiResponse(status_code=201, content_type="application/json", body=create_body)
        ],
        read_results={
            7100: AdoApiResponse(
                status_code=200,
                content_type="application/json",
                body=read_body,
            )
        },
    )

    operation = AdoPublicationCoordinator(gateway).publish(
        preview=preview,
        confirmation=confirm_ado_publication_preview(preview),
        reviewed_result=result,
        source_snapshot=snapshot,
        target=target,
    )

    assert operation.status is PublicationStatus.UNKNOWN_RESULT
    assert operation.receipt is not None
    assert operation.receipt.work_item_id == 7100
    assert not operation.receipt.verified
    assert len(gateway.create_calls) == 1


@pytest.mark.parametrize(
    ("create_result", "expected_status"),
    [
        (
            AdoGatewayError(AdoGatewayErrorCategory.DEFINITE_FAILURE),
            PublicationStatus.DEFINITELY_FAILED,
        ),
        (
            AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT),
            PublicationStatus.UNKNOWN_RESULT,
        ),
        (TimeoutError("synthetic timeout details"), PublicationStatus.UNKNOWN_RESULT),
    ],
)
def test_create_failures_have_explicit_safe_terminal_states(
    create_result: Exception,
    expected_status: PublicationStatus,
) -> None:
    result, snapshot, target = _preview_inputs()
    preview = build_ado_publication_preview(result, snapshot, 0, target)
    gateway = FakeAdoGateway(create_results=[create_result])

    operation = AdoPublicationCoordinator(gateway).publish(
        preview=preview,
        confirmation=confirm_ado_publication_preview(preview),
        reviewed_result=result,
        source_snapshot=snapshot,
        target=target,
    )

    assert operation.status is expected_status
    assert "synthetic timeout" not in operation.message


@pytest.mark.parametrize(
    "lookup_result",
    [
        AdoGatewayError(AdoGatewayErrorCategory.UNKNOWN_RESULT),
        TimeoutError("synthetic lookup details"),
    ],
)
def test_lookup_failure_is_definite_no_create_and_can_be_reconfirmed(
    lookup_result: Exception,
) -> None:
    result, snapshot, target = _preview_inputs()
    preview = build_ado_publication_preview(result, snapshot, 0, target)
    gateway = FakeAdoGateway(correlation_results={preview.request.correlation_id: lookup_result})

    operation = AdoPublicationCoordinator(gateway).publish(
        preview=preview,
        confirmation=confirm_ado_publication_preview(preview),
        reviewed_result=result,
        source_snapshot=snapshot,
        target=target,
    )

    assert operation.status is PublicationStatus.DEFINITELY_FAILED
    assert gateway.create_calls == []
    assert "synthetic lookup" not in operation.message


def test_malformed_success_retains_known_id_and_blocks_as_unknown() -> None:
    result, snapshot, target = _preview_inputs()
    preview = build_ado_publication_preview(result, snapshot, 0, target)
    gateway = FakeAdoGateway(
        create_results=[
            AdoApiResponse(
                status_code=201,
                content_type="application/json",
                body={"id": 7200, "rev": 1},
            )
        ]
    )

    operation = AdoPublicationCoordinator(gateway).publish(
        preview=preview,
        confirmation=confirm_ado_publication_preview(preview),
        reviewed_result=result,
        source_snapshot=snapshot,
        target=target,
    )

    assert operation.status is PublicationStatus.UNKNOWN_RESULT
    assert operation.receipt is not None
    assert operation.receipt.work_item_id == 7200


@pytest.mark.parametrize("status", [PublicationStatus.SUCCEEDED, PublicationStatus.UNKNOWN_RESULT])
def test_original_action_identity_survives_exclusion_and_protects_history(status) -> None:
    result, snapshot, target = _preview_inputs()
    original = build_ado_publication_preview(result, snapshot, 1, target)
    reviewed = result.model_copy(deep=True)
    reviewed.action_items = [reviewed.action_items[1]]
    reviewed.action_items[0].title = "Human edited surviving action"
    current = build_ado_publication_preview(reviewed, snapshot, 0, target, original_action_index=1)
    assert current.request.correlation_id == original.request.correlation_id
    assert current.preview_fingerprint != original.preview_fingerprint
    prior = AdoPublicationOperation(
        status=status,
        correlation_id=original.request.correlation_id,
        request_binding_fingerprint=original.request.binding_fingerprint,
        message="Retained.",
    )
    gateway = InMemoryFakeAdoGateway()
    with pytest.raises(PublicationValidationError, match="protected"):
        AdoPublicationCoordinator(gateway).publish(
            preview=current,
            confirmation=confirm_ado_publication_preview(current),
            reviewed_result=reviewed,
            source_snapshot=snapshot,
            target=target,
            original_action_index=1,
            prior_operations={prior.correlation_id: prior},
        )
    assert gateway.create_calls == []
    with pytest.raises(PublicationValidationError, match="changed"):
        AdoPublicationCoordinator(gateway).publish(
            preview=current,
            confirmation=confirm_ado_publication_preview(current),
            reviewed_result=reviewed,
            source_snapshot=snapshot,
            target=target,
        )


@pytest.mark.parametrize("status", [PublicationStatus.SUCCEEDED, PublicationStatus.UNKNOWN_RESULT])
def test_legacy_compacted_correlation_is_retained_after_restoration(status) -> None:
    result, snapshot, target = _preview_inputs()
    compact = result.model_copy(deep=True)
    compact.action_items = [compact.action_items[1]]
    legacy = build_ado_publication_preview(compact, snapshot, 0, target)
    restored = build_ado_publication_preview(result, snapshot, 1, target)
    prior = AdoPublicationOperation(
        status=status,
        correlation_id=legacy.request.correlation_id,
        request_binding_fingerprint=legacy.request.binding_fingerprint,
        message="Legacy result.",
    )
    gateway = InMemoryFakeAdoGateway()
    with pytest.raises(PublicationValidationError, match="protected"):
        AdoPublicationCoordinator(gateway).publish(
            preview=restored,
            confirmation=confirm_ado_publication_preview(restored),
            reviewed_result=result,
            source_snapshot=snapshot,
            target=target,
            prior_operations={prior.correlation_id: prior},
        )
    assert gateway.create_calls == []


def test_legacy_gateway_match_prevents_create_without_local_history() -> None:
    result, snapshot, target = _preview_inputs()
    compact = result.model_copy(deep=True)
    compact.action_items = [compact.action_items[1]]
    legacy = build_ado_publication_preview(compact, snapshot, 0, target)
    current = build_ado_publication_preview(result, snapshot, 1, target)
    gateway = FakeAdoGateway(correlation_results={legacy.request.correlation_id: (7001,)})
    outcome = AdoPublicationCoordinator(gateway).publish(
        preview=current,
        confirmation=confirm_ado_publication_preview(current),
        reviewed_result=result,
        source_snapshot=snapshot,
        target=target,
    )
    assert outcome.status is PublicationStatus.UNKNOWN_RESULT
    assert outcome.receipt.work_item_id == 7001
    assert legacy.request.correlation_id in outcome.message
    assert gateway.create_calls == []


def _readiness_inputs():
    from architecture_governance_copilot.runtime_dependencies import configured_delivery_capability
    from architecture_governance_copilot.ui_support import (
        confirm_review_input_manifest,
        initialize_session_state,
        load_internal_review_into_state,
    )

    result, snapshot, _ = _preview_inputs()
    runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE, {"AGC_INTERNAL_FAKE_ENABLED": "1"})
    state = {}
    initialize_session_state(state)
    state["agc_review_mode"] = "internal_fake"
    load_internal_review_into_state(
        state,
        snapshot=snapshot,
        transcript=runtime.review_transcript,
        context=result.context,
        provider_configuration_identity=runtime.descriptor.provider_configuration_identity,
    )
    manifest = confirm_review_input_manifest(state)
    capability = configured_delivery_capability({"AGC_INTERNAL_FAKE_ENABLED": "1"})
    return result, snapshot, manifest, capability


def test_readiness_is_ordered_explicit_and_does_not_depend_on_mode_label() -> None:
    from architecture_governance_copilot.publication import (
        DeliveryStatus,
        assess_delivery_readiness,
    )

    result, snapshot, manifest, capability = _readiness_inputs()
    before = result.model_dump_json()
    readiness = assess_delivery_readiness(result, snapshot, manifest, capability)
    assert readiness.status is DeliveryStatus.READY
    assert [a.action_index for a in readiness.actions] == [0, 1]
    assert all(a.ready for a in readiness.actions)
    assert readiness.actions[0].resolved_assignee == "riley.chen.synthetic@example.invalid"
    assert readiness.actions[1].mapped_parent == 204
    assert readiness.actions[0].mapped_priority == 1
    assert (
        assess_delivery_readiness(
            result, snapshot, manifest.model_copy(update={"review_mode": "other"}), capability
        )
        == readiness
    )
    assert result.model_dump_json() == before


@pytest.mark.parametrize(
    "field,value,blocker",
    [
        ("owner", "Unmapped Owner", "Unmapped Owner"),
        ("owner", None, "owner is required"),
        ("due_date", None, "due date is required"),
    ],
)
def test_preflight_names_each_blocked_action_and_preserves_other_ready_action(
    field, value, blocker
) -> None:
    from architecture_governance_copilot.publication import assess_delivery_readiness

    result, snapshot, manifest, capability = _readiness_inputs()
    setattr(result.action_items[0], field, value)
    readiness = assess_delivery_readiness(result, snapshot, manifest, capability)
    assert not readiness.actions[0].ready
    assert blocker in " ".join(readiness.actions[0].blockers)
    assert result.action_items[0].title in readiness.actions[0].blockers[0]
    assert readiness.actions[1].ready


@pytest.mark.parametrize(
    "field",
    [
        "source_page_id",
        "source_space",
        "source_url",
        "source_content_fingerprint",
        "transcript_fingerprint",
        "metadata_fingerprint",
        "provider_configuration_identity",
    ],
)
def test_mismatched_package_is_unavailable(field) -> None:
    from architecture_governance_copilot.publication import (
        DeliveryStatus,
        assess_delivery_readiness,
    )

    result, snapshot, manifest, capability = _readiness_inputs()
    changed = manifest.model_copy(update={field: "mismatch"})
    readiness = assess_delivery_readiness(result, snapshot, changed, capability)
    assert readiness.status is DeliveryStatus.UNAVAILABLE
    assert all(not a.ready for a in readiness.actions)


def test_preflight_parent_priority_optional_fields_and_no_provider() -> None:
    from architecture_governance_copilot.publication import (
        DeliveryStatus,
        assess_delivery_readiness,
    )

    result, snapshot, manifest, capability = _readiness_inputs()
    unavailable = assess_delivery_readiness(result, snapshot, manifest, None)
    assert unavailable.status is DeliveryStatus.UNAVAILABLE
    target = capability.target.model_copy(
        update={"parent_work_item_ids": {"OTHER": 1}, "priority_values": {"low": 3}}
    )
    readiness = assess_delivery_readiness(
        result, snapshot, manifest, capability.model_copy(update={"target": target})
    )
    assert "parent" in " ".join(readiness.actions[0].blockers)
    assert "priority" in " ".join(readiness.actions[0].blockers)
    result.action_items = []
    assert (
        assess_delivery_readiness(result, None, None, None).status is DeliveryStatus.NOT_APPLICABLE
    )


def test_capability_rejects_unknown_fields_and_blank_identity() -> None:
    _, _, _, capability = _readiness_inputs()
    from architecture_governance_copilot.publication import AdoDeliveryCapability

    for update in ({"provider_identity": " "}, {"unexpected": True}):
        with pytest.raises(ValidationError):
            AdoDeliveryCapability.model_validate(capability.model_dump() | update)


def test_readable_summary_contains_every_exact_request_field_and_binding() -> None:
    from architecture_governance_copilot.publication import publication_request_summary

    result, snapshot, target = _preview_inputs()
    preview = build_ado_publication_preview(result, snapshot, 1, target)
    summary = publication_request_summary(preview, target)
    for operation in preview.request.operations:
        assert operation.value in summary.values()
    assert summary["Reviewed owner"] == result.action_items[1].owner
    assert summary["Resolved assignee"] == target.owner_identities[result.action_items[1].owner]
    assert summary["Reviewed priority"] == result.action_items[1].priority.value
    assert summary["Correlation"] == preview.request.correlation_id
