# AIF candidate probe evidence

Document role: manual probe artifacts and observations; not implementation authority.
Recorded: 2026-09-18. Batch 24 local implementation and acceptance are complete; internal live acceptance remains separate.

## Request lineage

| File | Role | Local SHA-256 |
| --- | --- | --- |
| `postman-request-body.json` | Final request body supplied for the user's internal Postman test; probe ID `agc-finding-action-full-input-indexed-v1`. Complete sources are annotated with IDs once. | `f6749ed1ef54d28cfdd5af325ded052be0bd789290808f40f7afcd7d1a753380` |
| `sample-request.json` | Earlier preparation artifact with separate full text and a repeated source index; not the request version associated with the reported result. | `a1d0d78671d27ab6d352c3430381d91413d0fb9fbde4e1b8e10d76f1d7e8f74a` |

Preserve both files unchanged. The final file has a model placeholder; the user supplies the actual
internal model and uses existing endpoint/authentication configuration. These hashes identify our
local artifacts, not independently captured bytes sent over the internal HTTP connection.

The final request contains the complete 1,083-word synthetic SI, 28-line transcript, confirmed
metadata, and 63 unique source IDs. Sources are `samples/internal_fake_solution_intent.md`,
`samples/internal_fake_review_transcript.txt`, and `samples/internal_fake_review_metadata.json`.
All 63 annotated lines and the metadata were checked against those local fixtures.

Probe IDs use the source SHA-256 prefix and original physical line number. The SI digest starts
`f3ea001146e7`; the transcript digest starts `6144121de3cf`. This probe hashes the original source
text, including its terminal newline. Existing application AIF fingerprints normalize newlines and
strip outer whitespace, so they are different. The implemented `normalized-physical-lines-v1` index follows the application normalization.
Its SI/transcript prefixes are `2149aae56b2e` / `3d7d65837021`. The separately generated
`implementation-request-v1.json` uses the same pure request builder as the integration seam and
the stricter prompt. It has not been tested against real AIF and does not inherit live verification.

## User-reported live result

The user reported running the supplied request against the internal AIF endpoint using the
Databricks-hosted Claude Sonnet 5 model and supplied two photographs of the response on 2026-09-18.
No raw response file or exact sent-request capture was supplied. The following observations are
visual/manual evidence, not a machine-parsed live response fixture:

- One visible `emit_review_candidates` function call; `finish_reason` is `tool_calls`.
- `function.arguments` is a serialized JSON string containing `items` with seven candidates:
  five findings and two actions. Visible fields match `kind`, `text`, and `evidence_source_ids`.
- Usage shows 6,266 prompt tokens and 766 completion tokens, totaling 7,032.
- The visible source IDs were manually transcribed for membership checking and all occur in the
  supplied request. This does not establish that every statement or classification is correct.
- The screenshots do not establish HTTP status, elapsed time, exact JSON byte validity, repeated
  reliability, general enforcement of `strict`, or application end-to-end success.

## Semantic assessment

| Observation | Assessment |
| --- | --- |
| Retry-controls, failover-evidence, and retention-approval findings | Supported by the supplied sources and the review's explicit findings summary. |
| Retry-control and failover-exercise actions | Explicit commitments are captured without creating an action for every finding. |
| Alert thresholds/on-call target and support escalation/after-hours findings | Source-backed descriptions, but outside the requested extraction scope: transcript line 17 categorizes them as Missing Evidence, and line 24 names the three findings. |
| Dates described only as `by the proposed date` | Loss of useful specificity: source lines 8/23 and 10/22 state 18 and 21 September 2026. The original prompt allowed dates to remain, so this is not a violation of an explicit date-preservation requirement. |

The expected three findings and two actions are specific to this scenario. Do not implement a
fixed count, topic blacklist, or a rule excluding every mention of missing evidence: failover
evidence is explicitly a finding in this review. Referenced quotes alone omit later category
clarifications; human reviewers need access to complete source context.

## Use in subsequent work

- Keep wire/schema checks, source-resolution checks, semantic assessment, and complete human
  workflow acceptance as distinct results.
- Construct a clearly labeled synthetic adverse-quality regression with the observed pattern;
  do not call it a raw live response or an accepted golden answer. It should pass mechanical
  validation and be corrected by human exclusion before confirmed output.
- If a sanitized raw response is later supplied, preserve its provenance and validate its actual
  envelope and arguments. Do not repair it or infer missing bytes from these photographs.
- The next probe, `implementation-request-v1.json`, is generated by
  `build_candidate_request_body()` and covered by fixture-parity tests. Preserve
  explicit action owners/dates in text and give later explicit review classification precedence.
  Keep business fields human-entered and avoid additional model calls or semantic filtering.
- A targeted repeat on this scenario and a small changed-classification/no-action scenario can
  assess the revised prompt. Record actual results separately; do not make this optional probe
  a blocker to approved local synthetic implementation or confuse it with full internal acceptance.

No endpoint, credentials, message/tool-call IDs, confidential enterprise data, or response images
are copied into these artifacts. Existing historical AIF handoff documents remain unchanged.
