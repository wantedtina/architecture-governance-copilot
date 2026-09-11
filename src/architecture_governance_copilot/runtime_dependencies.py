"""Narrow runtime dependency wiring for offline and configured fake review modes."""

from __future__ import annotations

import hashlib
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
from architecture_governance_copilot.models import (
    GovernanceResult,
    ReviewInputManifest,
    SolutionIntentReviewContext,
)
from architecture_governance_copilot.publication import AdoDeliveryCapability
from architecture_governance_copilot.synthetic_aif import SyntheticReviewResponder
from architecture_governance_copilot.synthetic_delivery import resolve_synthetic_target

INTERNAL_FAKE_ENABLED_ENV = "AGC_INTERNAL_FAKE_ENABLED"
INTERNAL_FAKE_PROVIDER_ID_ENV = "AGC_INTERNAL_FAKE_PROVIDER_ID"
OFFLINE_PROVIDER_CONFIGURATION_ID = "offline-deterministic-v3"
DEFAULT_INTERNAL_FAKE_PROVIDER_ID = "internal-fake-aif-v3"
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


DEPLOYMENT_PROFILE_ENV = "AGC_DEPLOYMENT_PROFILE"


class DeploymentProfile(StrEnum):
    DEMO = "demo"
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class DeploymentConfigurationError(ValueError):
    """Invalid explicit deployment configuration; never a fallback trigger."""


@dataclass(frozen=True, slots=True)
class DeploymentPolicy:
    profile: DeploymentProfile
    review_modes: tuple[ReviewModeDescriptor, ...]

    @property
    def reviewer_outcome_allowed(self) -> bool:
        """Current human outcome policy is approved only for non-production acceptance."""
        return self.profile in {
            DeploymentProfile.DEMO,
            DeploymentProfile.DEVELOPMENT,
            DeploymentProfile.TEST,
        }

    @property
    def drafting_allowed(self) -> bool:
        return self.profile is not DeploymentProfile.PRODUCTION

    @property
    def identity(self) -> str:
        facts = (
            self.profile.value,
            tuple(
                (item.mode.value, item.provider_configuration_identity)
                for item in self.review_modes
            ),
        )
        return hashlib.sha256(repr(facts).encode()).hexdigest()


def resolve_deployment_policy(environ: Mapping[str, str] | None = None) -> DeploymentPolicy:
    """Resolve only explicit operator settings; never inspect or contact a live provider."""
    environment = os.environ if environ is None else environ
    raw_flag = environment.get(INTERNAL_FAKE_ENABLED_ENV)
    enabled = False
    if raw_flag is not None:
        normalized = raw_flag.strip().lower()
        if normalized not in {"1", "true", "yes", "on", "0", "false", "no", "off"}:
            raise DeploymentConfigurationError("AGC_INTERNAL_FAKE_ENABLED must be a valid boolean.")
        enabled = normalized in {"1", "true", "yes", "on"}
    raw_profile = environment.get(DEPLOYMENT_PROFILE_ENV)
    try:
        profile = (
            DeploymentProfile(raw_profile.strip().lower())
            if raw_profile is not None
            else (DeploymentProfile.DEVELOPMENT if enabled else DeploymentProfile.DEMO)
        )
    except ValueError as exc:
        raise DeploymentConfigurationError(
            "AGC_DEPLOYMENT_PROFILE must be demo, development, test, or production."
        ) from exc
    if enabled and profile in {DeploymentProfile.DEMO, DeploymentProfile.PRODUCTION}:
        raise DeploymentConfigurationError(
            "Internal fake requires the development or test deployment profile."
        )
    descriptors = []
    if profile is not DeploymentProfile.PRODUCTION:
        descriptors.append(
            ReviewModeDescriptor(
                ReviewMode.OFFLINE, "Offline demo", OFFLINE_PROVIDER_CONFIGURATION_ID
            )
        )
    if enabled:
        identity = environment.get(
            INTERNAL_FAKE_PROVIDER_ID_ENV, DEFAULT_INTERNAL_FAKE_PROVIDER_ID
        ).strip()
        if not identity:
            raise DeploymentConfigurationError(
                "AGC_INTERNAL_FAKE_PROVIDER_ID must not be blank when Internal fake is enabled."
            )
        descriptors.append(
            ReviewModeDescriptor(ReviewMode.INTERNAL_FAKE, "Internal fake · no network", identity)
        )
    return DeploymentPolicy(profile, tuple(descriptors))


def available_review_modes(
    environ: Mapping[str, str] | None = None,
) -> tuple[ReviewModeDescriptor, ...]:
    """Return only capabilities allowed by the validated deployment policy."""
    return resolve_deployment_policy(environ).review_modes


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
    transport = FakeAifTransport(
        [response],
        response_factory=SyntheticReviewResponder(
            (samples_dir / "internal_fake_solution_intent.md").read_text(encoding="utf-8"),
            transcript,
            response,
        ),
    )
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
            "Avery Patel": "avery.patel.synthetic@example.invalid",
            "Riley Chen": "riley.chen.synthetic@example.invalid",
        },
        parent_work_item_ids={"SYN-204": 204},
        priority_values={"high": 1, "medium": 2, "low": 3},
    )


def configured_delivery_capability(
    environ: Mapping[str, str] | None = None,
    *,
    confirmed_manifest: ReviewInputManifest | None = None,
    review_result: GovernanceResult | None = None,
) -> AdoDeliveryCapability | None:
    """Resolve the explicitly enabled fake capability independently of the UI mode label."""
    environment = os.environ if environ is None else environ
    if not any(
        item.mode is ReviewMode.INTERNAL_FAKE
        for item in resolve_deployment_policy(environment).review_modes
    ):
        return None
    runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE, environment)
    snapshot = runtime.confluence_reader.get_page(runtime.confluence_page_id)

    capability = AdoDeliveryCapability(
        provider_identity="in-memory-fake-ado-v1",
        source_page_id=snapshot.page_id,
        source_space=snapshot.space,
        source_url=snapshot.url,
        source_version=snapshot.version,
        source_canonicalizer_version=snapshot.canonicalizer_version,
        source_content_fingerprint=snapshot.content_fingerprint,
        analysis_provider_identity=runtime.descriptor.provider_configuration_identity,
        transcript_fingerprint=hashlib.sha256(
            runtime.review_transcript.strip().encode()
        ).hexdigest(),
        metadata_fingerprint=hashlib.sha256(
            runtime.review_context.model_dump_json().encode()
        ).hexdigest(),
        target=runtime.ado_target,
    )

    if confirmed_manifest is not None:
        source_fields = (
            "source_page_id",
            "source_space",
            "source_url",
            "source_version",
            "source_canonicalizer_version",
            "source_content_fingerprint",
        )
        if (
            confirmed_manifest.review_mode != ReviewMode.INTERNAL_FAKE.value
            or confirmed_manifest.provider_configuration_identity
            != capability.analysis_provider_identity
            or any(
                getattr(confirmed_manifest, field) != getattr(capability, field)
                for field in source_fields
            )
        ):
            return None
        capability = capability.model_copy(
            update={
                "transcript_fingerprint": confirmed_manifest.transcript_fingerprint,
                "metadata_fingerprint": confirmed_manifest.metadata_fingerprint,
            }
        )
    if review_result is not None:
        if (
            confirmed_manifest is None
            or hashlib.sha256(review_result.context.model_dump_json().encode()).hexdigest()
            != confirmed_manifest.metadata_fingerprint
        ):
            return None
        capability = capability.model_copy(
            update={"target": resolve_synthetic_target(capability.target, review_result)}
        )
    return capability
