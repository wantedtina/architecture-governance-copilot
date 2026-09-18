# Synthetic sample contract

All fixtures contain synthetic data. Source fixtures are deterministic snapshots, not live exports.

## Active candidate workflow

| Mode | Source package | Active analysis fixture |
| --- | --- | --- |
| Offline | `solution_intent.md`, `review_transcript.txt`, `review_metadata.json` | `expected_candidates.json` |
| Internal fake | `internal_fake_solution_intent.md`, `internal_fake_review_transcript.txt`, `internal_fake_review_metadata.json`, `internal_fake_confluence_page.json` | `internal_fake_review_candidates.json` |

Each active response has only `items` with `kind` (`finding`/`action`), `text`, and
`evidence_source_ids`. The canonical packages have three findings and two actions; this is fixture
content, not a parser cardinality rule. IDs follow `normalized-physical-lines-v1` and are validated
against the corresponding complete source snapshots. Changed source text requires new IDs.

Neither analysis fixture includes outcome, severity, status, priority, owner or due-date fields.
Human Review starts required choices unselected and optional values blank. Explicit human-completion
values used by tests are test inputs, never hidden defaults or provider output. In `tests/fixtures/`,
`offline_human_completion.json` and `internal_fake_human_completion.json` supply explicit human
inputs; the matching `*_reviewed_candidates_result.json` files freeze converter outputs. Regenerate
these outputs through the actual converter when the domain/source contract changes, not by copying
legacy result fixtures. Edited synthetic
transcripts use conservative literal finding/action grouping; all source text remains inspectable.

## Historical complete-result examples

`expected_result.json` and `internal_fake_aif_result.json` are preserved byte-for-byte as historical
full-domain examples. They exercise legacy model/generator compatibility. They are not current
runtime analysis responses, current expected human-confirmed results, or a source of UI business
field defaults. Their six-category contents do not expand the current automated scope.

Current human-confirmed results contain typed `extraction_scope`: only findings/actions were
extracted and the outcome was human-completed. Decisions, risks, open questions and missing evidence
are empty with an explicit not-extracted notice, never a claim that such items do not exist.

The test-only minimal package uses `internal_fake_minimal_review_candidates.json` and
`internal_fake_minimal_human_completion.json` with its matching minimal SI/transcript/metadata.
`internal_fake_minimal_aif_result.json` remains a legacy full-result example.
`synthetic_misclassified_candidates.json` deliberately includes five findings/two actions so tests
can exercise human correction of structurally valid out-of-scope proposals. It is constructed test
data, not raw output transcribed from the live-response photographs.

## Drafting and probe material

`si_template.md`, `source_context.txt` and `supporting_context.md` retain the separate deterministic
SI-drafting contract. A generated local draft does not become an authoritative review input.

The versioned [AIF probe record](../docs/aif-candidate-probe/README.md) preserves the original manual
request artifacts. The generated `implementation-request-v1.json` uses the final builder/index contract;
`sample-request.json` and `postman-request-body.json` remain frozen prototype artifacts.
Constructed test envelopes are synthetic; photographs of a live response are not raw golden bytes.
