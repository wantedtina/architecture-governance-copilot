"""Tests for explicit, zero-network review dependency wiring."""

from __future__ import annotations

from pathlib import Path

import pytest

from architecture_governance_copilot.extractors import DeterministicDemoExtractor
from architecture_governance_copilot.integrations.aif import AifGovernanceExtractor
from architecture_governance_copilot.runtime_dependencies import (
    DEFAULT_INTERNAL_FAKE_PROVIDER_ID,
    INTERNAL_FAKE_ENABLED_ENV,
    INTERNAL_FAKE_PROVIDER_ID_ENV,
    ReviewMode,
    available_review_modes,
    build_review_runtime,
    review_mode_descriptor,
)


def test_offline_mode_is_zero_configuration_and_does_not_read_internal_samples(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject_internal_read(path: Path, *args: object, **kwargs: object) -> str:
        if "internal_fake" in path.name:
            raise AssertionError("offline mode must not read internal fake samples")
        return original_read_text(path, *args, **kwargs)

    original_read_text = Path.read_text
    monkeypatch.setattr(Path, "read_text", reject_internal_read)

    descriptors = available_review_modes({})
    runtime = build_review_runtime(ReviewMode.OFFLINE, {})

    assert [descriptor.mode for descriptor in descriptors] == [ReviewMode.OFFLINE]
    assert isinstance(runtime.extractor, DeterministicDemoExtractor)
    assert runtime.confluence_reader is None
    assert runtime.review_transcript is None


def test_internal_fake_requires_explicit_configuration() -> None:
    with pytest.raises(ValueError, match="not configured"):
        review_mode_descriptor(ReviewMode.INTERNAL_FAKE, {})

    descriptor = review_mode_descriptor(
        ReviewMode.INTERNAL_FAKE,
        {INTERNAL_FAKE_ENABLED_ENV: "true"},
    )

    assert descriptor.provider_configuration_identity == DEFAULT_INTERNAL_FAKE_PROVIDER_ID


def test_internal_fake_runtime_uses_separate_synthetic_sources_and_explicit_calls() -> None:
    environment = {
        INTERNAL_FAKE_ENABLED_ENV: "1",
        INTERNAL_FAKE_PROVIDER_ID_ENV: "configured-fake-aif-v2",
    }

    runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE, environment)

    assert isinstance(runtime.extractor, AifGovernanceExtractor)
    assert runtime.descriptor.provider_configuration_identity == "configured-fake-aif-v2"
    assert runtime.review_context is not None
    assert runtime.review_context.project_name == "Synthetic Order Routing Service"
    assert runtime.review_transcript is not None
    assert "Priya Shah" not in runtime.review_transcript
    assert runtime.confluence_reader is not None
    assert runtime.confluence_page_id is not None
    assert runtime.ado_target is not None
    assert runtime.ado_target.project == "Synthetic Governance"
    assert runtime.ado_target.work_item_type == "Governance Action"
    assert runtime.ado_target.fields.classification_values == {
        "Custom.GovernanceClassification": "Architecture"
    }
    assert runtime.ado_target.owner_identities == {
        "Avery Patel": "avery.patel.synthetic@example.invalid",
        "Riley Chen": "riley.chen.synthetic@example.invalid",
    }

    snapshot = runtime.confluence_reader.get_page(runtime.confluence_page_id)
    result = runtime.extractor.extract(
        snapshot.canonical_text,
        runtime.review_transcript,
        runtime.review_context,
    )

    assert snapshot.body_format.value == "storage"
    assert snapshot.version == 8
    assert "## 10. Decisions, Assumptions, and Gaps" in snapshot.canonical_text
    assert result.context == runtime.review_context
    assert len(result.findings) == 3
    assert len(result.decisions) == 1
    assert len(result.risks) == 1
    assert len(result.action_items) == 2
    assert len(result.open_questions) == 1
    assert len(result.missing_evidence) == 2


def test_delivery_configuration_is_explicit_and_bound_to_fake_package() -> None:
    from architecture_governance_copilot.runtime_dependencies import configured_delivery_capability

    assert configured_delivery_capability({}) is None
    capability = configured_delivery_capability({INTERNAL_FAKE_ENABLED_ENV: "1"})
    assert capability.source_page_id == "synthetic-page-204"
    assert capability.source_version == 8
    assert capability.provider_identity == "in-memory-fake-ado-v1"
    assert capability.target.organization_url.startswith("https://example.invalid/")


@pytest.mark.parametrize("profile", ["demo", "development", "test", "production"])
@pytest.mark.parametrize("flag", [None, "true", "false"])
def test_deployment_matrix(profile: str, flag: str | None) -> None:
    from architecture_governance_copilot.runtime_dependencies import (
        DeploymentConfigurationError,
        configured_delivery_capability,
        resolve_deployment_policy,
    )

    environment = {"AGC_DEPLOYMENT_PROFILE": profile}
    if flag is not None:
        environment[INTERNAL_FAKE_ENABLED_ENV] = flag
    if flag == "true" and profile in {"demo", "production"}:
        with pytest.raises(DeploymentConfigurationError):
            resolve_deployment_policy(environment)
        return
    policy = resolve_deployment_policy(environment)
    assert policy.drafting_allowed is (profile != "production")
    assert len(policy.review_modes) == (
        0 if profile == "production" else 2 if flag == "true" else 1
    )
    assert (configured_delivery_capability(environment) is not None) is (flag == "true")


@pytest.mark.parametrize(
    "key,value",
    [
        ("AGC_DEPLOYMENT_PROFILE", ""),
        ("AGC_DEPLOYMENT_PROFILE", "live-secret-value"),
        (INTERNAL_FAKE_ENABLED_ENV, ""),
        (INTERNAL_FAKE_ENABLED_ENV, "typo-secret-value"),
        (INTERNAL_FAKE_PROVIDER_ID_ENV, ""),
    ],
)
def test_invalid_policy_fails_without_echoing_values(key: str, value: str) -> None:
    from architecture_governance_copilot.runtime_dependencies import (
        DeploymentConfigurationError,
        resolve_deployment_policy,
    )

    with pytest.raises(DeploymentConfigurationError) as exc:
        resolve_deployment_policy({INTERNAL_FAKE_ENABLED_ENV: "true", key: value})
    if "secret" in value:
        assert value not in str(exc.value)


@pytest.mark.parametrize("flag", ["1", " TRUE ", "yes", "on", "0", "false", "no", "off"])
def test_legacy_policy_and_boolean_spellings(flag: str) -> None:
    from architecture_governance_copilot.runtime_dependencies import resolve_deployment_policy

    policy = resolve_deployment_policy({INTERNAL_FAKE_ENABLED_ENV: flag})
    enabled = flag.strip().lower() in {"1", "true", "yes", "on"}
    assert policy.profile.value == ("development" if enabled else "demo")
    assert (
        policy.identity
        == resolve_deployment_policy(
            {
                INTERNAL_FAKE_ENABLED_ENV: flag,
                "UNRELATED": "ignored",
            }
        ).identity
    )


@pytest.mark.parametrize("mode", list(ReviewMode))
def test_production_never_constructs_a_provider(mode: ReviewMode, monkeypatch) -> None:
    def forbidden(*args, **kwargs):
        raise AssertionError("Provider construction is forbidden")

    monkeypatch.setattr(
        "architecture_governance_copilot.runtime_dependencies.DeterministicDemoExtractor", forbidden
    )
    monkeypatch.setattr(
        "architecture_governance_copilot.runtime_dependencies.FakeAifTransport", forbidden
    )
    with pytest.raises(ValueError, match="not configured"):
        build_review_runtime(mode, {"AGC_DEPLOYMENT_PROFILE": "production"})


def test_internal_fake_response_uses_current_metadata_and_transcript():
    from architecture_governance_copilot.models import ReviewOutcome

    runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE, {INTERNAL_FAKE_ENABLED_ENV: "1"})
    si = runtime.confluence_reader.get_page(runtime.confluence_page_id).canonical_text
    context = runtime.review_context.model_copy(
        update={"domain_architect": "Demo Reviewer", "review_round": 2}
    )
    metadata_only = runtime.extractor.extract(si, runtime.review_transcript, context)
    assert metadata_only.context == context
    assert len(metadata_only.findings) == 3
    transcript = "Action: test synthetic failover.\nUnclassified synthetic text."
    edited = runtime.extractor.extract(si, transcript, context)
    assert edited.review_outcome is ReviewOutcome.NOT_STATED
    assert edited.action_items[0].title == "Action: test synthetic failover."
    assert edited.action_items[0].evidence[0].quote in transcript
    assert not edited.findings
    assert edited.context == context


def test_dynamic_fake_capability_remains_bound_to_synthetic_source_and_mode():
    from architecture_governance_copilot.models import ReviewInputManifest, ReviewInputProvenance
    from architecture_governance_copilot.runtime_dependencies import configured_delivery_capability

    environment = {INTERNAL_FAKE_ENABLED_ENV: "1"}
    runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE, environment)
    snapshot = runtime.confluence_reader.get_page(runtime.confluence_page_id)
    canonical = configured_delivery_capability(environment)
    fields = {
        key: getattr(canonical, key)
        for key in ReviewInputManifest.model_fields
        if hasattr(canonical, key)
    }
    manifest = ReviewInputManifest(
        **{
            **fields,
            "source_retrieved_at": snapshot.retrieved_at,
            "transcript_fingerprint": "edited-transcript",
            "metadata_fingerprint": "edited-metadata",
            "transcript_provenance": ReviewInputProvenance.USER_ENTERED,
            "metadata_provenance": ReviewInputProvenance.USER_ENTERED,
            "transcript_edited": True,
            "metadata_edited": True,
            "review_mode": "internal_fake",
            "provider_configuration_identity": runtime.descriptor.provider_configuration_identity,
        }
    )
    bound = configured_delivery_capability(environment, confirmed_manifest=manifest)
    assert bound.transcript_fingerprint == "edited-transcript"
    assert bound.target == canonical.target
    from architecture_governance_copilot.models import GovernanceResult

    result = GovernanceResult(context=runtime.review_context, review_outcome="not_stated")
    assert (
        configured_delivery_capability(
            environment, confirmed_manifest=manifest, review_result=result
        )
        is None
    )
    for changes in (
        {"source_version": 99},
        {"review_mode": "offline"},
        {"provider_configuration_identity": "other"},
    ):
        assert (
            configured_delivery_capability(
                environment, confirmed_manifest=manifest.model_copy(update=changes)
            )
            is None
        )
    assert (
        configured_delivery_capability(
            {"AGC_DEPLOYMENT_PROFILE": "production"}, confirmed_manifest=manifest
        )
        is None
    )


def test_edited_sample_preserves_explicit_action_details_and_acknowledgements():
    runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE, {INTERNAL_FAKE_ENABLED_ENV: "1"})
    transcript = runtime.review_transcript + "\nAdditional context."
    result = runtime.extractor.extract(
        runtime.confluence_reader.get_page(runtime.confluence_page_id).canonical_text,
        transcript,
        runtime.review_context,
    )
    assert len(result.action_items) == 2
    assert [(a.owner, a.due_date.isoformat()) for a in result.action_items] == [
        ("Riley Chen", "2026-09-18"),
        ("Avery Patel", "2026-09-21"),
    ]
    for action in result.action_items:
        assert len(action.evidence) == 2
        assert all(e.quote in transcript for e in action.evidence)


@pytest.mark.parametrize(
    "line",
    [
        "I will test recovery by 2026-09-20.",
        "[09:00] Avery Patel: Action: test recovery by 2026-09-20.",
    ],
)
def test_synthetic_rules_do_not_invent_commitment_owner(line):
    from architecture_governance_copilot.demo_review import group_transcript_candidates

    runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE, {INTERNAL_FAKE_ENABLED_ENV: "1"})
    result = group_transcript_candidates(line, runtime.review_context)
    assert result.action_items[0].owner is None


def test_synthetic_rules_retain_ambiguous_acknowledgement_and_dates():
    from architecture_governance_copilot.demo_review import group_transcript_candidates

    runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE, {INTERNAL_FAKE_ENABLED_ENV: "1"})
    transcript = (
        "[09:00] Avery Patel: I will test recovery by 2026-09-20 or 2026-09-21.\n"
        "[09:01] Avery Patel: I accept ownership of the recovery action "
        "and its 2026-09-20 due date."
    )
    result = group_transcript_candidates(transcript, runtime.review_context)
    assert result.action_items[0].due_date is None
    assert len(result.missing_evidence) == 1


def test_historical_date_is_not_a_due_date():
    from architecture_governance_copilot.demo_review import group_transcript_candidates

    runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE, {INTERNAL_FAKE_ENABLED_ENV: "1"})
    result = group_transcript_candidates(
        "[09:00] Avery Patel: I will review the report from 2026-09-20.", runtime.review_context
    )
    assert result.action_items[0].due_date is None


def test_dynamic_alias_capability_requires_confirmed_matching_metadata():
    from architecture_governance_copilot.models import GovernanceResult
    from architecture_governance_copilot.runtime_dependencies import configured_delivery_capability

    environment = {INTERNAL_FAKE_ENABLED_ENV: "1"}
    runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE, environment)
    result = GovernanceResult(context=runtime.review_context, review_outcome="not_stated")
    assert configured_delivery_capability(environment, review_result=result) is None
