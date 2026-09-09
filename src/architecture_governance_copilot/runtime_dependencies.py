"""Narrow runtime dependency wiring for offline and configured fake review modes."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from architecture_governance_copilot.extractors import (
    DeterministicDemoExtractor,
    GovernanceExtractor,
)
from architecture_governance_copilot.integrations.aif import (
    AifGovernanceExtractor,
    FakeAifTransport,
)
from architecture_governance_copilot.integrations.azure_devops import (
    AdoFieldMapping,
    AdoTargetConfiguration,
)
from architecture_governance_copilot.integrations.confluence import (
    ConfluenceApiResponse,
    ConfluenceContentApiReader,
    ConfluenceReader,
    FakeConfluenceContentTransport,
)
from architecture_governance_copilot.models import SolutionIntentReviewContext

INTERNAL_FAKE_ENABLED_ENV = "AGC_INTERNAL_FAKE_ENABLED"
INTERNAL_FAKE_PROVIDER_ID_ENV = "AGC_INTERNAL_FAKE_PROVIDER_ID"
OFFLINE_PROVIDER_CONFIGURATION_ID = "offline-deterministic-v1"
DEFAULT_INTERNAL_FAKE_PROVIDER_ID = "internal-fake-aif-v1"
INTERNAL_FAKE_PAGE_ID = "synthetic-page-204"


class ReviewMode(StrEnum):
    """Configured source/provider mode for governance review analysis."""

    OFFLINE = "offline"
    INTERNAL_FAKE = "internal_fake"


@dataclass(frozen=True, slots=True)
class ReviewModeDescriptor:
    """Safe UI metadata for one available review mode."""

    mode: ReviewMode
    label: str
    provider_configuration_identity: str


@dataclass(frozen=True, slots=True)
class ReviewRuntime:
    """Dependencies required by explicit load and analysis actions."""

    descriptor: ReviewModeDescriptor
    extractor: GovernanceExtractor
    confluence_reader: ConfluenceReader | None = None
    confluence_page_id: str | None = None
    review_transcript: str | None = None
    review_context: SolutionIntentReviewContext | None = None
    ado_target: AdoTargetConfiguration | None = None


def available_review_modes(
    environ: Mapping[str, str] | None = None,
) -> tuple[ReviewModeDescriptor, ...]:
    """Expose internal fake mode only when explicitly enabled."""
    environment = os.environ if environ is None else environ
    descriptors = [
        ReviewModeDescriptor(
            mode=ReviewMode.OFFLINE,
            label="Offline demo",
            provider_configuration_identity=OFFLINE_PROVIDER_CONFIGURATION_ID,
        )
    ]
    if _is_enabled(environment.get(INTERNAL_FAKE_ENABLED_ENV)):
        configured_identity = environment.get(
            INTERNAL_FAKE_PROVIDER_ID_ENV,
            DEFAULT_INTERNAL_FAKE_PROVIDER_ID,
        ).strip()
        if not configured_identity:
            configured_identity = DEFAULT_INTERNAL_FAKE_PROVIDER_ID
        descriptors.append(
            ReviewModeDescriptor(
                mode=ReviewMode.INTERNAL_FAKE,
                label="Internal fake · no network",
                provider_configuration_identity=configured_identity,
            )
        )
    return tuple(descriptors)


def review_mode_descriptor(
    mode: ReviewMode,
    environ: Mapping[str, str] | None = None,
) -> ReviewModeDescriptor:
    """Return one available descriptor or reject unavailable internal mode."""
    descriptor = next(
        (item for item in available_review_modes(environ) if item.mode is mode),
        None,
    )
    if descriptor is None:
        raise ValueError("The requested review mode is not configured.")
    return descriptor


def build_review_runtime(
    mode: ReviewMode,
    environ: Mapping[str, str] | None = None,
) -> ReviewRuntime:
    """Construct mode-specific dependencies lazily for an explicit user action."""
    descriptor = review_mode_descriptor(mode, environ)
    if mode is ReviewMode.OFFLINE:
        return ReviewRuntime(
            descriptor=descriptor,
            extractor=DeterministicDemoExtractor(),
        )

    samples_dir = Path(__file__).resolve().parents[2] / "samples"
    transcript = (samples_dir / "internal_fake_review_transcript.txt").read_text(encoding="utf-8")
    context = SolutionIntentReviewContext.model_validate_json(
        (samples_dir / "internal_fake_review_metadata.json").read_text(encoding="utf-8")
    )
    response = (samples_dir / "internal_fake_aif_result.json").read_text(encoding="utf-8")
    confluence_response = (samples_dir / "internal_fake_confluence_page.json").read_text(
        encoding="utf-8"
    )
    confluence_transport = FakeConfluenceContentTransport(
        {
            INTERNAL_FAKE_PAGE_ID: ConfluenceApiResponse(
                status_code=200,
                content_type="application/json; charset=utf-8",
                body=confluence_response,
            )
        }
    )
    reader = ConfluenceContentApiReader(confluence_transport)
    transport = FakeAifTransport([response])
    extractor = AifGovernanceExtractor(
        transport,
        provider_configuration_identity=descriptor.provider_configuration_identity,
    )
    return ReviewRuntime(
        descriptor=descriptor,
        extractor=extractor,
        confluence_reader=reader,
        confluence_page_id=INTERNAL_FAKE_PAGE_ID,
        review_transcript=transcript,
        review_context=context,
        ado_target=internal_fake_ado_target(),
    )


def internal_fake_ado_target() -> AdoTargetConfiguration:
    """Return the explicit non-network target used by the internal fake workflow."""
    return AdoTargetConfiguration(
        organization_url="https://example.invalid/ado/synthetic-org",
        project="Synthetic Governance",
        work_item_type="Governance Action",
        fields=AdoFieldMapping(
            title="System.Title",
            description="System.Description",
            assigned_to="System.AssignedTo",
            due_date="Microsoft.VSTS.Scheduling.DueDate",
            priority="Microsoft.VSTS.Common.Priority",
            tags="System.Tags",
            correlation="Custom.GovernanceCorrelation",
            classification_values={
                "Custom.GovernanceClassification": "Architecture",
            },
        ),
        owner_identities={
            "Casey Wong": "casey.wong.synthetic@example.invalid",
        },
        parent_work_item_ids={"SYN-204": 204},
        priority_values={"high": 1, "medium": 2, "low": 3},
    )


def _is_enabled(value: str | None) -> bool:
    return value is not None and value.strip().lower() in {"1", "true", "yes", "on"}
