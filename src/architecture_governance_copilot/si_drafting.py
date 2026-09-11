"""Solution Intent drafting provider boundary and deterministic demo implementation."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Protocol, runtime_checkable

from architecture_governance_copilot.models import (
    DraftInputType,
    SolutionIntentDraft,
    SolutionIntentDraftRequest,
)

_TEMPLATE_FILENAME = "si_template.md"
_SOURCE_CONTEXT_FILENAME = "source_context.txt"
_SUPPORTING_CONTEXT_FILENAME = "supporting_context.md"
_DRAFT_FILENAME = "solution_intent.md"
_REQUIRED_FILENAMES = (
    _TEMPLATE_FILENAME,
    _SOURCE_CONTEXT_FILENAME,
    _SUPPORTING_CONTEXT_FILENAME,
    _DRAFT_FILENAME,
)
DETERMINISTIC_DRAFTING_PROVIDER_CONFIGURATION_ID = "deterministic-demo-drafter-v1"


@runtime_checkable
class SolutionIntentDrafter(Protocol):
    """Generate a proposed Solution Intent from supplied project context."""

    def draft(self, request: SolutionIntentDraftRequest) -> SolutionIntentDraft:
        """Return a validated draft for human review."""
        ...


class DeterministicDraftingFixtureError(ValueError):
    """Indicate that a bundled deterministic drafting fixture is invalid."""


class DeterministicDemoDrafter:
    """Draft locally from the synthetic workspace and supplied evidence."""

    provider_name = "Deterministic demo drafter"
    provider_configuration_id = DETERMINISTIC_DRAFTING_PROVIDER_CONFIGURATION_ID

    def __init__(self, samples_dir: Path | None = None) -> None:
        self._samples_dir = (
            samples_dir
            if samples_dir is not None
            else Path(__file__).resolve().parents[2] / "samples"
        )
        paths = {name: self._samples_dir / name for name in _REQUIRED_FILENAMES}
        for name, path in paths.items():
            if not path.is_file():
                raise DeterministicDraftingFixtureError(
                    f"Deterministic drafting sample file is missing: {name}"
                )

        self._template = _read_text(paths[_TEMPLATE_FILENAME], _TEMPLATE_FILENAME)
        self._source_context = _read_text(
            paths[_SOURCE_CONTEXT_FILENAME],
            _SOURCE_CONTEXT_FILENAME,
        )
        self._supporting_context = _read_text(
            paths[_SUPPORTING_CONTEXT_FILENAME],
            _SUPPORTING_CONTEXT_FILENAME,
        )
        self._draft = _read_text(paths[_DRAFT_FILENAME], _DRAFT_FILENAME)

        for label, value in (
            ("template", self._template),
            ("source-code context", self._source_context),
            ("supporting-document context", self._supporting_context),
            ("generated draft", self._draft),
        ):
            if not value.strip():
                raise DeterministicDraftingFixtureError(f"Deterministic {label} fixture is empty.")

    def validate_request(self, request: SolutionIntentDraftRequest) -> None:
        """Validate deterministic compatibility without producing a draft."""
        if request.project_name != "Digital Payment Notification Service":
            raise ValueError("Project name does not match the deterministic drafting fixture.")
        if _normalize_document(request.template) != _normalize_document(self._template):
            raise ValueError("SI template does not match the deterministic drafting fixture.")
        if _normalize_document(request.source_code_context) != _normalize_document(
            self._source_context
        ):
            raise ValueError(
                "Source-code context does not match the deterministic drafting fixture."
            )
        if not _normalize_document(request.supporting_documents or ""):
            raise ValueError("Supporting evidence must not be empty.")

    def draft(self, request: SolutionIntentDraftRequest) -> SolutionIntentDraft:
        """Preserve the canonical sample; otherwise assemble an evidence-aware demo draft."""
        self.validate_request(request)
        return SolutionIntentDraft(
            project_name=request.project_name,
            content=(
                self._draft
                if _normalize_document(request.supporting_documents or "")
                == _normalize_document(self._supporting_context)
                else _draft_from_evidence(request)
            ),
            provider_name=self.provider_name,
            input_types=[
                DraftInputType.TEMPLATE,
                DraftInputType.SOURCE_CODE,
                DraftInputType.SUPPORTING_DOCUMENTS,
            ],
            assumptions=[
                "All supplied context is synthetic and represents selected project excerpts.",
                "The draft must be reviewed by the project team before governance review.",
                "Missing or uncertain design details remain explicit in the generated draft.",
            ],
        )


class SolutionIntentDraftingService:
    """Coordinate SI drafting without coupling callers to a provider implementation."""

    def __init__(self, drafter: SolutionIntentDrafter) -> None:
        self._drafter = drafter

    def generate_draft(
        self,
        request: SolutionIntentDraftRequest,
    ) -> SolutionIntentDraft:
        """Delegate SI drafting to the configured provider."""
        return self._drafter.draft(request)


def _read_text(path: Path, filename: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise DeterministicDraftingFixtureError(
            f"Deterministic drafting sample file is unreadable: {filename}"
        ) from exc


def _normalize_document(document: str) -> str:
    return document.replace("\r\n", "\n").replace("\r", "\n").strip()


# Lexical grouping offers a reproducible demo, never a claim of semantic interpretation.
_SECTION_TERMS = {
    3: ("scope", "channel", "customer", "payment"),
    4: ("architecture", "component", "broker", "event"),
    5: ("interface", "api", "retry", "idempot"),
    6: ("data", "retention", "postgres", "storage"),
    7: ("rto", "rpo", "recover", "availability", "resilien"),
    8: ("security", "encrypt", "secret", "token", "auth"),
    9: ("log", "metric", "monitor", "alert", "observab"),
    10: ("deploy", "release", "kubernetes", "replica"),
    11: ("support", "owner", "runbook", "escalat"),
}


def _quoted_text(text: str) -> str:
    """Indent source text so Markdown/HTML cannot become generated instructions or headings."""
    return "\n".join("    " + line for line in text.splitlines())


def _draft_from_evidence(request: SolutionIntentDraftRequest) -> str:
    evidence = _normalize_document(request.supporting_documents or "")
    lines = [(index, line) for index, line in enumerate(evidence.splitlines(), 1) if line.strip()]
    digest = hashlib.sha256(evidence.encode()).hexdigest()
    parts = [
        f"# Solution Intent - {request.project_name}",
        "> Offline demo draft assembled from the confirmed inputs. Human review required. "
        "No model or external service was called.",
    ]
    for heading in re.findall(r"^## \d+\. .+$", request.template, re.MULTILINE):
        number = int(heading.split()[1].rstrip("."))
        parts.append(heading)
        if number == 1:
            parts.append(
                "Status: Draft — awaiting human review. No architecture approval recorded."
            )
        elif number == 2:
            parts.append(
                f"This draft records the supplied evidence for {request.project_name}. "
                "Topic excerpts below are grouped by keywords and remain unverified source claims. "
                "Complete evidence and selected repository context appear in the appendix."
            )
        elif number == 12:
            parts.append(
                "- Confirm the relevance and consistency of every source claim.\n"
                "- Resolve contradictory or missing information before approval.\n"
                "- Complete the sections marked To be confirmed; no design decisions are inferred."
            )
        else:
            matches = [
                (index, line)
                for index, line in lines
                if any(term in line.lower() for term in _SECTION_TERMS.get(number, ()))
            ]
            if matches:
                parts.append("Proposed inputs for this section — confirm applicability:")
                for index, line in matches:
                    parts.extend([f"Evidence L{index}:", _quoted_text(line)])
                parts.append(
                    "To be confirmed: validate these inputs and complete the design narrative."
                )
            else:
                parts.append(
                    "To be confirmed: supply and review the design details for this section."
                )
    parts.extend(
        [
            "## Appendix — Confirmed source context",
            "### Supporting evidence",
            f"SHA-256: `{digest}`. Line references use this normalized evidence text. "
            "Document identities and hashes remain in the source-package manifest.",
            _quoted_text(evidence),
            "### Selected repository context",
            "Source excerpt only; not proof of deployment or operational readiness.",
            _quoted_text(request.source_code_context),
        ]
    )
    return "\n\n".join(parts)
