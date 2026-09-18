"""Synthetic protocol replay, not evidence of real endpoint compatibility."""

import copy
import json

import pytest

from architecture_governance_copilot.integrations.aif_candidate_protocol import (
    CANDIDATE_TOOL_NAME,
    CandidateProtocolError,
    build_candidate_request_body,
    decode_candidate_tool_response,
)
from architecture_governance_copilot.models import SolutionIntentReviewContext
from architecture_governance_copilot.review_candidates import candidate_json_schema
from architecture_governance_copilot.review_sources import build_review_source_index


def envelope() -> dict:
    return {
        "choices": [
            {
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "type": "function",
                            "function": {
                                "name": CANDIDATE_TOOL_NAME,
                                "arguments": '{"items": []}',
                            },
                        }
                    ],
                },
            }
        ],
        "usage": {"completion_tokens": 12},
        "custom_outputs": {},
        "metadata": {"synthetic": True},
    }


def test_builder_annotates_complete_sources_once_and_shares_small_schema() -> None:
    si = "# SI\nUnique source wording\n\nUnclassified detail"
    transcript = "[09:00] Lee: Explicit action by 2026-09-21.\nLater classification clarification"
    context = SolutionIntentReviewContext(
        project_name="Synthetic",
        si_title="SI",
        si_version="1",
        current_si_status="draft",
        review_round=1,
    )
    body = build_candidate_request_body(
        model="configured-model", solution_intent=si, review_transcript=transcript, context=context
    )
    assert body["model"] == "configured-model" and body["stream"] is False
    assert "response_format" not in body
    assert body["tools"][0]["function"]["strict"] is True
    assert body["tools"][0]["function"]["parameters"] == candidate_json_schema()
    assert "$ref" not in json.dumps(candidate_json_schema())
    content = body["messages"][1]["content"]
    assert content.count("Unique source wording") == 1
    assert content.count("Later classification clarification") == 1
    for entry in build_review_source_index(si, transcript).entries:
        assert content.count(f"[{entry.source_id}]") == 1
    prompt = body["messages"][0]["content"]
    assert "later explicit reviewer classification" in prompt
    assert "preserve that detail" in prompt


@pytest.mark.parametrize("content", [None, "", "  ", []])
def test_decode_one_tool_call_and_ignore_ordinary_metadata_extensions(content: object) -> None:
    response = envelope()
    response["choices"][0]["message"]["content"] = content
    assert decode_candidate_tool_response(response) == {"items": []}


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update(choices=[]),
        lambda value: value["choices"].append(copy.deepcopy(value["choices"][0])),
        lambda value: value["choices"][0].update(finish_reason="length"),
        lambda value: value["choices"][0]["message"].update(role="user"),
        lambda value: value["choices"][0]["message"].update(content="Conflicting prose"),
        lambda value: value["choices"][0]["message"].update(tool_calls=[]),
        lambda value: value["choices"][0]["message"]["tool_calls"].append({}),
        lambda value: value["choices"][0]["message"]["tool_calls"][0].update(type="custom"),
        lambda value: value["choices"][0]["message"]["tool_calls"][0]["function"].update(
            name="other_tool"
        ),
        lambda value: value["choices"][0]["message"]["tool_calls"][0]["function"].update(
            arguments={"items": []}
        ),
        lambda value: value["choices"][0]["message"]["tool_calls"][0]["function"].update(
            arguments='{"items":"[]"}'
        ),
        lambda value: value["choices"][0]["message"]["tool_calls"][0]["function"].update(
            arguments='"{\\"items\\":[]}"'
        ),
        lambda value: value["choices"][0]["message"]["tool_calls"][0]["function"].update(
            arguments="```json\n{}\n```"
        ),
    ],
)
def test_reject_ambiguous_refused_or_malformed_envelopes(mutation) -> None:
    response = envelope()
    mutation(response)
    with pytest.raises(CandidateProtocolError) as error:
        decode_candidate_tool_response(response)
    assert error.value.category == "invalid_response"


def test_refusal_retains_safe_error_category() -> None:
    response = envelope()
    response["choices"][0]["message"]["refusal"] = "Provider refusal detail"
    with pytest.raises(CandidateProtocolError) as error:
        decode_candidate_tool_response(response)
    assert error.value.category == "refusal"
    assert "Provider refusal detail" not in str(error.value)
