"""Offline candidate contract, source binding, and deterministic fixture safeguards."""

import inspect
import json
import shutil
from pathlib import Path
from typing import get_type_hints

import pytest
from pydantic import ValidationError

from architecture_governance_copilot.extractors import (
    DeterministicDemoExtractor,
    DeterministicFixtureError,
    GovernanceExtractor,
)
from architecture_governance_copilot.models import SolutionIntentReviewContext
from architecture_governance_copilot.review_candidates import (
    ReviewCandidateAnalysis,
    parse_candidate_payload,
    validate_candidate_analysis_binding,
)

SAMPLES = Path(__file__).resolve().parents[1] / "samples"


@pytest.fixture
def sample_inputs():
    return (
        (SAMPLES / "solution_intent.md").read_text(),
        (SAMPLES / "review_transcript.txt").read_text(),
        SolutionIntentReviewContext.model_validate_json(
            (SAMPLES / "review_metadata.json").read_text()
        ),
    )


@pytest.fixture
def copied_samples(tmp_path):
    shutil.copytree(SAMPLES, tmp_path / "samples")
    return tmp_path / "samples"


def test_synchronous_candidate_protocol_and_canonical_payload(sample_inputs):
    extractor = DeterministicDemoExtractor()
    assert isinstance(extractor, GovernanceExtractor)
    assert get_type_hints(extractor.extract)["return"] is ReviewCandidateAnalysis
    assert not inspect.iscoroutinefunction(extractor.extract)
    result = extractor.extract(*sample_inputs)
    expected = parse_candidate_payload((SAMPLES / "expected_candidates.json").read_text())
    assert [(i.kind, i.text, list(i.evidence_source_ids)) for i in result.items] == [
        (i.kind, i.text, i.evidence_source_ids) for i in expected.items
    ]
    assert [i.kind for i in result.items] == ["finding"] * 3 + ["action"] * 2
    assert result.context.model_dump() == sample_inputs[2].model_dump()
    assert not hasattr(result, "review_outcome")
    validate_candidate_analysis_binding(result, *sample_inputs)


def test_default_directory_is_independent_of_cwd(sample_inputs, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert len(DeterministicDemoExtractor().extract(*sample_inputs).items) == 5


@pytest.mark.parametrize("ending", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("surround", [False, True])
def test_normalized_sources_preserve_ids_and_original_snapshots(sample_inputs, ending, surround):
    si, transcript, context = sample_inputs
    original = DeterministicDemoExtractor().extract(*sample_inputs)
    si, transcript = si.replace("\n", ending), transcript.replace("\n", ending)
    if surround:
        si, transcript = f"\n{si}\n", f"\n{transcript}\n"
    result = DeterministicDemoExtractor().extract(si, transcript, context)
    assert [i.evidence_source_ids for i in result.items] == [
        i.evidence_source_ids for i in original.items
    ]
    assert result.solution_intent == si
    assert result.review_transcript == transcript


def test_edited_transcript_keeps_unmatched_source_without_new_categories(sample_inputs):
    si, _, context = sample_inputs
    transcript = (
        "Finding: recovery is not defined.\nAction: test recovery.\n"
        "Risk: capacity.\nUnclassified note."
    )
    result = DeterministicDemoExtractor().extract(si, transcript, context)
    assert [i.kind for i in result.items] == ["finding", "action"]
    assert result.review_transcript == transcript
    assert all(i.evidence[0].quote in transcript for i in result.items)
    assert result == DeterministicDemoExtractor().extract(si, transcript, context)
    assert not hasattr(result, "missing_evidence")


def test_edited_metadata_is_copied_but_si_identity_is_fixed(sample_inputs):
    si, tr, context = sample_inputs
    changed = context.model_copy(update={"review_round": 3, "domain_architect": "Demo Reviewer"})
    result = DeterministicDemoExtractor().extract(si, tr, changed)
    assert result.context.model_dump() == changed.model_dump()
    assert result.context is not changed
    with pytest.raises(ValueError, match="Review context"):
        DeterministicDemoExtractor().extract(
            si, tr, context.model_copy(update={"si_version": "99"})
        )
    with pytest.raises(ValueError, match="Solution Intent.*does not match"):
        DeterministicDemoExtractor().extract(si + "Changed SI", tr, context)


@pytest.mark.parametrize("blank", ["", " ", "\n\t"])
@pytest.mark.parametrize("position", [0, 1])
def test_blank_input_preflight_rejects(sample_inputs, blank, position):
    inputs = list(sample_inputs)
    inputs[position] = blank
    with pytest.raises(ValueError, match="must not be blank"):
        DeterministicDemoExtractor().extract(*inputs)


def test_analysis_and_nested_evidence_are_immutable_and_independent(sample_inputs):
    first = DeterministicDemoExtractor().extract(*sample_inputs)
    second = DeterministicDemoExtractor().extract(*sample_inputs)
    assert first == second and first is not second
    with pytest.raises(ValidationError):
        first.items[0].text = "changed"
    with pytest.raises(ValidationError):
        first.items[0].evidence[0].quote = "changed"
    with pytest.raises(ValidationError):
        first.context.project_name = "changed"


@pytest.mark.parametrize(
    "name",
    [
        "solution_intent.md",
        "review_transcript.txt",
        "review_metadata.json",
        "expected_candidates.json",
    ],
)
@pytest.mark.parametrize("failure", ["missing", "unreadable"])
def test_missing_and_unreadable_fixtures_reject(copied_samples, name, failure):
    if failure == "missing":
        (copied_samples / name).unlink()
    else:
        (copied_samples / name).write_bytes(b"\xff")
    with pytest.raises(DeterministicFixtureError, match=f"file is {failure}"):
        DeterministicDemoExtractor(copied_samples)


@pytest.mark.parametrize("name", ["review_metadata.json", "expected_candidates.json"])
def test_invalid_fixture_json_rejects(copied_samples, name):
    (copied_samples / name).write_text("{")
    with pytest.raises(DeterministicFixtureError, match="not valid JSON"):
        DeterministicDemoExtractor(copied_samples)


@pytest.mark.parametrize("mutation", ["shape", "old_domain", "bad_id", "bad_metadata"])
def test_invalid_fixture_contract_or_binding_rejects(copied_samples, mutation):
    target = copied_samples / "expected_candidates.json"
    payload = json.loads(target.read_text())
    if mutation == "shape":
        payload["items"][0]["kind"] = "risk"
    elif mutation == "old_domain":
        payload = json.loads((copied_samples / "expected_result.json").read_text())
    elif mutation == "bad_id":
        payload["items"][0]["evidence_source_ids"] = ["stale-id"]
    else:
        target = copied_samples / "review_metadata.json"
        payload = json.loads(target.read_text())
        payload["review_round"] = 0
    target.write_text(json.dumps(payload))
    with pytest.raises(DeterministicFixtureError, match="invalid"):
        DeterministicDemoExtractor(copied_samples)


@pytest.mark.parametrize("name", ["solution_intent.md", "review_transcript.txt"])
def test_empty_fixture_rejects(copied_samples, name):
    (copied_samples / name).write_text(" \n\t")
    with pytest.raises(DeterministicFixtureError, match="empty"):
        DeterministicDemoExtractor(copied_samples)
