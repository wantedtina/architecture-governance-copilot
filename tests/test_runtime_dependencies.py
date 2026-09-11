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
