"""Synthetic aliases are explicit, stable and independent of enterprise connectors."""

from datetime import date

from architecture_governance_copilot.models import (
    ActionItem,
    ActionPriority,
    EvidenceSource,
    GovernanceResult,
    ReviewOutcome,
    SourceEvidence,
)
from architecture_governance_copilot.runtime_dependencies import (
    ReviewMode,
    build_review_runtime,
    internal_fake_ado_target,
)
from architecture_governance_copilot.synthetic_delivery import (
    resolve_synthetic_target,
    synthetic_owner_identity,
    synthetic_parent_id,
)


def test_aliases_preserve_canonical_and_support_free_form_values():
    target = internal_fake_ado_target()
    assert synthetic_owner_identity("Riley Chen", target) == target.owner_identities["Riley Chen"]
    assert synthetic_parent_id("SYN-204", target) == 204
    for value in ("SYN-205", "Custom ticket / second review", "Reviewer & Team", "123"):
        assert synthetic_owner_identity(value, target).endswith("@example.invalid")
        assert synthetic_owner_identity(value, target) == synthetic_owner_identity(value, target)
        assert 0 < synthetic_parent_id(value, target) < 2**53
        assert synthetic_parent_id(value, target) == synthetic_parent_id(value, target)
    assert synthetic_parent_id("SYN-205", target) != synthetic_parent_id("SYN-206", target)
    assert synthetic_owner_identity("Taylor", target) != synthetic_owner_identity("Taylor2", target)
    assert synthetic_parent_id("  ", target) is None
    assert synthetic_owner_identity("  ", target) is None


def test_target_extension_does_not_change_reviewed_values_or_base_target():
    runtime = build_review_runtime(ReviewMode.INTERNAL_FAKE, {"AGC_INTERNAL_FAKE_ENABLED": "1"})
    result = GovernanceResult(
        review_outcome=ReviewOutcome.NOT_STATED,
        context=runtime.review_context.model_copy(update={"ado_ticket_id": "Free-form ticket"}),
        action_items=[
            ActionItem(
                title="Reviewed action",
                owner="Custom Owner",
                due_date=date(2026, 9, 20),
                priority=ActionPriority.MEDIUM,
                evidence=[
                    SourceEvidence(
                        source_type=EvidenceSource.MEETING_TRANSCRIPT, quote="Synthetic action"
                    )
                ],
            )
        ],
    )
    before = result.model_dump_json()
    target = resolve_synthetic_target(runtime.ado_target, result)
    assert result.model_dump_json() == before
    assert "Custom Owner" not in runtime.ado_target.owner_identities
    assert "Free-form ticket" not in runtime.ado_target.parent_work_item_ids
    assert target.owner_identities["Custom Owner"].endswith("@example.invalid")
    assert target.parent_work_item_ids["Free-form ticket"] > 0
