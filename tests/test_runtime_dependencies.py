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

    snapshot = runtime.confluence_reader.get_page(runtime.confluence_page_id)
    result = runtime.extractor.extract(
        snapshot.canonical_text,
        runtime.review_transcript,
        runtime.review_context,
    )

    assert snapshot.body_format.value == "storage"
    assert snapshot.version == 7
    assert "| Control | State |" in snapshot.canonical_text
    assert result.context == runtime.review_context
    assert len(result.findings) == 1
    assert len(result.action_items) == 1
