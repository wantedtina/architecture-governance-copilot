# Internal Integration Handoff

## Purpose and status

This handoff defines the bounded company-specific work needed to connect the already-tested
Confluence, AIF, and Azure DevOps boundaries. It contains no company endpoint, tenant, project,
field, identity, token, cookie, or confidential content.

The external repository currently passes the fake-integration preparation gate. It does **not**
pass the internal live gate. The deterministic offline path remains the submission baseline and
must continue to work with all internal connections disabled.

## Non-negotiable controls

- Use only a designated synthetic Confluence page, synthetic transcript, and synthetic ADO target.
- Keep provider output as a proposal. Human Review and a separate exact-publication confirmation
  remain mandatory.
- Do not send a Create request until target, mapping, source freshness, preview identity, and
  correlation reconciliation all pass.
- Never retry a Create automatically. A timeout or ambiguous response remains `unknown_result`
  until reconciled.
- Retain a known work-item ID even when GET verification fails. Do not infer that reset, restart,
  or missing local state means no remote record exists.
- Store runtime configuration and credentials only in the approved internal secret/configuration
  mechanism. Do not add them to this repository, fixtures, screenshots, logs, or exceptions.
- Do not treat Confluence and ADO as an atomic transaction.

## Adapter map

| Marker | Existing boundary | Internal input required | Existing fake evidence | Required live acceptance |
| --- | --- | --- | --- | --- |
| `TODO(INTERNAL-CONFLUENCE)` | `ConfluenceContentTransport.get_content()` in `integrations/confluence.py` | Approved base URL, page ID, authentication scheme, TLS/proxy requirements, timeout, deployed Confluence version | Content API response parsing; storage-body canonicalization; heading, paragraph, list, and table coverage; version/body drift and malformed-response tests | Read the designated synthetic page by explicit ID; verify HTTP status, JSON Content-Type, returned ID/title/space, `version.number`, `body.storage.representation`, complete nonempty body, canonical text, and stable content fingerprint |
| `TODO(INTERNAL-AIF)` | `AifTransport.analyze()` in `integrations/aif.py` | Approved endpoint/deployment, authentication scheme, API version, timeout, request envelope, structured-response envelope, provider configuration identity | Request/schema contract; context match; refusal/timeout/malformed response; source quote/context validation; local trusted reference assignment | Analyze a previously unbundled synthetic page and transcript; verify returned context exactly; reject one deliberately invalid quote; ensure only validated locally assigned references enter Human Review |
| `TODO(INTERNAL-ADO)` | `AdoGateway` in `integrations/azure_devops.py` | Approved organization/project/type, field references, classification values, owner identities, parent ID, authentication scheme, API version, timeout | Encoded `$` work-item type; exact JSON Patch; correlation lookup; one Create; receipt mapping; GET field/relation verification; duplicate, stale, definite-failure, and unknown-result paths | Read the existing synthetic item first; confirm target/type/required fields/allowed classification/identity/parent mappings; then separately preview and confirm one designated Create; verify returned ID/revision/API URL/browser URL and every expected field/relation by GET |

## Required implementation sequence

1. **Confirm configuration outside Git.** Record the approved synthetic targets, minimum
   authentication method, deployed API versions, timeout policy, and operator authorization in the
   internal work item. Do not copy secret values into acceptance notes.
2. **Implement Confluence read only.** Adapt the company response into `ConfluenceApiResponse` and
   reuse `ConfluenceContentApiReader`. Reject login HTML, collection-shaped responses, wrong IDs,
   missing versions, non-storage bodies, truncation, unsupported macros, and body/version drift.
3. **Implement AIF transport only.** Adapt `AifGovernanceRequest` to the approved provider envelope
   and return only its structured JSON result. Keep context and evidence validation in
   `AifGovernanceExtractor`; do not trust provider-supplied evidence references.
4. **Run new-input analysis acceptance.** Use a synthetic page that is not one of the bundled
   fixtures. It must reach the shared Human Review. Repeat with one invalid quote and confirm the
   response is rejected before Human Review.
5. **Confirm ADO mappings read-only.** GET the already-created designated synthetic item without a
   cookie jar. Verify the approved authentication scheme independently; do not infer that Bearer and
   PAT Basic authentication are interchangeable.
6. **Implement correlation lookup and GET.** Map only the minimal response contract. Zero matches
   permits the later Create, one match proceeds to GET reconciliation without Create, and multiple
   matches block for manual reconciliation.
7. **Run one controlled Create.** Re-read the Confluence source, prepare the exact JSON Patch from
   the human-confirmed record, validate it, obtain a separate publication confirmation, recheck
   eligibility, and submit exactly once. GET the returned ID and compare target, type, expected
   fields, and parent relation.
8. **Exercise safety branches.** Verify stale-source rejection, duplicate correlation handling,
   double-click/rerun protection, definite pre-Create failure, timeout/unknown result, known ID with
   failed GET, and preservation of local reviewed outputs and remote reconciliation facts.
9. **Disable internal connections and rerun offline acceptance.** No internal import, configuration,
   or network dependency may be required by the deterministic flow.

## Protocol details to preserve

### Confluence

The current refined contract expects an explicit content-object GET with expansion
`body.storage,version,space`. The transport returns only status, Content-Type, and a JSON-compatible
body. The reader owns response validation and storage canonicalization. Fetching a page for
publication freshness must return one body and its matching version from the same response.

If the deployed version or approved API route differs, adapt only the internal transport. Do not
weaken the snapshot model or accept partial/truncated content. Unsupported storage macros must fail
closed until a deterministic conversion rule and tests are approved.

### AIF

The request includes the exact SI text, transcript, review context, JSON schema constraints,
provider configuration identity, and source fingerprints. The internal transport may translate the
wire envelope but must not omit or replace those facts. Provider errors must map to the existing safe
categories without exposing response bodies or internal diagnostics to the UI.

### Azure DevOps

The Create contract uses:

```text
POST {organization}/{encoded-project}/_apis/wit/workitems/${encoded-type}?api-version=7.1
Content-Type: application/json-patch+json
```

The request body is the exact displayed array of JSON Patch `add` operations. Do not copy
server-generated state, identity, board, or process-default fields. Required process-specific
classification values must come from approved configuration. The response mapper retains only
integer `id`, positive `rev`, `fields`, API `url`, `_links.html.href`, and relations needed for
verification; extra upstream fields are ignored.

Correlation lookup must be scoped to the approved project and type. Escape the correlation value
using the approved query mechanism and test injection-like values. The internal gateway must not
log authorization headers, cookies, request bodies containing confidential content, or raw error
responses.

## Live acceptance record

Complete this record in the approved internal system, not in this public repository.

| Check | Current repository status | Internal evidence to record |
| --- | --- | --- |
| Previously unbundled synthetic Confluence page read and canonicalized | Not run | Page/version identity and redacted request/response structure |
| New synthetic input reaches shared Human Review | Not run | Provider configuration identity and acceptance timestamp |
| Invalid provider quote is rejected before Human Review | Passed with fake; live not run | Safe error category and test case identifier |
| Existing synthetic ADO item read without cookies | Not run | Approved auth scheme, status, ID/revision, verified field names |
| One separately confirmed Create and GET read-back | Passed with in-memory fake; live not run | Correlation, ID/revision, redacted field comparison, operator |
| Stale, duplicate, and unknown-result branches | Passed with fakes; live not run | Test identifiers and reconciliation outcome |
| Offline flow with internal connections disabled | Passed | Frozen implementation commit `ce5fd3f2a760504da40440558180c5245ed291e9`; see `SUBMISSION_BASELINE.md` for verification results |

Passing fake acceptance is the external-preparation gate only. Mark the internal live gate passed
only after every applicable live check above has direct evidence.

## Conditional secondary writes

ADO Update and Confluence review-page write-back remain deferred. Do not expose controls or start
implementation unless the primary Create path has passed the internal live gate, the user has named
the exact synthetic targets, authorization is confirmed, and sufficient pre-freeze verification
time remains. Never update the source SI page.

If later authorized, ADO Update must GET the current revision, display an exact diff, require a
separate confirmation, include a revision test, and stop on conflict. Confluence write-back may
target only a separately designated synthetic review page and must preview title, space, parent,
body, target, and version before confirmation.
