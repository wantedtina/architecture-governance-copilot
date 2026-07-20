"""Solution Intent drafting provider boundary and deterministic demo implementation."""

from __future__ import annotations

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


@runtime_checkable
class SolutionIntentDrafter(Protocol):
    """Generate a proposed Solution Intent from supplied project context."""

    def draft(self, request: SolutionIntentDraftRequest) -> SolutionIntentDraft:
        """Return a validated draft for human review."""
        ...


class DeterministicDraftingFixtureError(ValueError):
    """Indicate that a bundled deterministic drafting fixture is invalid."""


class DeterministicDemoDrafter:
    """Return the frozen synthetic SI draft for the matching drafting context."""

    provider_name = "Deterministic demo drafter"

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

    def draft(self, request: SolutionIntentDraftRequest) -> SolutionIntentDraft:
        """Return an independent known draft when all demo inputs match."""
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
        if _normalize_document(request.supporting_documents or "") != _normalize_document(
            self._supporting_context
        ):
            raise ValueError(
                "Supporting-document context does not match the deterministic drafting fixture."
            )

        return SolutionIntentDraft(
            project_name=request.project_name,
            content=self._draft,
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
