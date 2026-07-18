"""Governance extraction provider interfaces and implementations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol, runtime_checkable

from pydantic import ValidationError

from architecture_governance_copilot.models import (
    GovernanceResult,
    SolutionIntentReviewContext,
)

_SOLUTION_INTENT_FILENAME = "solution_intent.md"
_TRANSCRIPT_FILENAME = "review_transcript.txt"
_METADATA_FILENAME = "review_metadata.json"
_EXPECTED_RESULT_FILENAME = "expected_result.json"
_REQUIRED_FILENAMES = (
    _SOLUTION_INTENT_FILENAME,
    _TRANSCRIPT_FILENAME,
    _METADATA_FILENAME,
    _EXPECTED_RESULT_FILENAME,
)


@runtime_checkable
class GovernanceExtractor(Protocol):
    """Extract a structured governance result from one Solution Intent review."""

    def extract(
        self,
        solution_intent: str,
        review_transcript: str,
        context: SolutionIntentReviewContext,
    ) -> GovernanceResult:
        """Return a validated governance result for the supplied review inputs."""
        ...


class DeterministicFixtureError(ValueError):
    """Indicate that the bundled deterministic demo fixture is invalid."""


class DeterministicDemoExtractor:
    """Return the frozen result only for the matching bundled synthetic review."""

    def __init__(self, samples_dir: Path | None = None) -> None:
        self._samples_dir = (
            samples_dir
            if samples_dir is not None
            else Path(__file__).resolve().parents[2] / "samples"
        )
        paths = {name: self._samples_dir / name for name in _REQUIRED_FILENAMES}

        for name, path in paths.items():
            if not path.is_file():
                raise DeterministicFixtureError(f"Deterministic sample file is missing: {name}")

        self._solution_intent = _read_text(
            paths[_SOLUTION_INTENT_FILENAME], _SOLUTION_INTENT_FILENAME
        )
        self._review_transcript = _read_text(paths[_TRANSCRIPT_FILENAME], _TRANSCRIPT_FILENAME)
        metadata_text = _read_text(paths[_METADATA_FILENAME], _METADATA_FILENAME)
        expected_result_text = _read_text(
            paths[_EXPECTED_RESULT_FILENAME], _EXPECTED_RESULT_FILENAME
        )

        if not self._solution_intent.strip():
            raise DeterministicFixtureError("Deterministic Solution Intent fixture is empty.")
        if not self._review_transcript.strip():
            raise DeterministicFixtureError("Deterministic review transcript fixture is empty.")

        self._context = _validate_metadata(metadata_text)
        self._expected_result = _validate_expected_result(expected_result_text)
        if self._expected_result.context != self._context:
            raise DeterministicFixtureError(
                "Deterministic expected-result context does not match review metadata."
            )

    def extract(
        self,
        solution_intent: str,
        review_transcript: str,
        context: SolutionIntentReviewContext,
    ) -> GovernanceResult:
        """Return an independent result when all inputs match the demo fixture."""
        if not solution_intent.strip():
            raise ValueError("Solution Intent input must not be blank.")
        if not review_transcript.strip():
            raise ValueError("Review transcript input must not be blank.")
        if _normalize_document(solution_intent) != _normalize_document(self._solution_intent):
            raise ValueError("Solution Intent does not match the deterministic demo fixture.")
        if _normalize_document(review_transcript) != _normalize_document(self._review_transcript):
            raise ValueError("Review transcript does not match the deterministic demo fixture.")
        if context != self._context:
            raise ValueError("Review context does not match the deterministic demo fixture.")

        return self._expected_result.model_copy(deep=True)


def _read_text(path: Path, filename: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise DeterministicFixtureError(
            f"Deterministic sample file is unreadable: {filename}"
        ) from exc


def _validate_metadata(raw_json: str) -> SolutionIntentReviewContext:
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise DeterministicFixtureError("Deterministic review metadata is not valid JSON.") from exc

    try:
        return SolutionIntentReviewContext.model_validate(payload)
    except ValidationError as exc:
        raise DeterministicFixtureError("Deterministic review metadata is invalid.") from exc


def _validate_expected_result(raw_json: str) -> GovernanceResult:
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise DeterministicFixtureError("Deterministic expected result is not valid JSON.") from exc

    try:
        return GovernanceResult.model_validate(payload)
    except ValidationError as exc:
        raise DeterministicFixtureError("Deterministic expected result is invalid.") from exc


def _normalize_document(document: str) -> str:
    return document.replace("\r\n", "\n").replace("\r", "\n").strip()
