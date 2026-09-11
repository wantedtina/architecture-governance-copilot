"""Deterministic local aliases for free-form demo inputs, never enterprise resolution."""

from __future__ import annotations

import hashlib

from architecture_governance_copilot.integrations.azure_devops import AdoTargetConfiguration
from architecture_governance_copilot.models import GovernanceResult


def synthetic_owner_identity(owner: str, target: AdoTargetConfiguration) -> str | None:
    """Preserve sample mappings; map other nonblank names to reserved fake identities."""
    value = owner.strip()
    if not value:
        return None
    return target.owner_identities.get(value) or (
        "demo-" + hashlib.sha256(value.encode()).hexdigest()[:24] + "@example.invalid"
    )


def synthetic_parent_id(reference: str, target: AdoTargetConfiguration) -> int | None:
    """Return an opaque local ID, not a parsed or verified remote work-item ID."""
    value = reference.strip()
    if not value:
        return None
    return target.parent_work_item_ids.get(value) or (
        1_000_000 + int(hashlib.sha256(value.encode()).hexdigest()[:12], 16)
    )


def resolve_synthetic_target(
    target: AdoTargetConfiguration, result: GovernanceResult
) -> AdoTargetConfiguration:
    """Copy the target with explicit aliases for the current human-review package."""
    owners = dict(target.owner_identities)
    parents = dict(target.parent_work_item_ids)
    for action in result.action_items:
        if action.owner:
            identity = synthetic_owner_identity(action.owner, target)
            if identity is not None:
                owners[action.owner] = identity
    reference = result.context.ado_ticket_id
    if reference:
        identifier = synthetic_parent_id(reference, target)
        if identifier is not None:
            parents[reference] = identifier
    return AdoTargetConfiguration.model_validate(
        {**target.model_dump(), "owner_identities": owners, "parent_work_item_ids": parents}
    )
