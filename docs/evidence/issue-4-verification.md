# Issue #4 verification

Date: 2026-11-14. **Implemented and verified for issue #4's image-export scope.**
All nine acceptance criteria are covered by the reconciliation below, including
authenticated hosted success/selected-only/empty exports, actual hosted-backed
browser downloads, and real thirty-minute expiry. Native anonymous inference
remains quota-blocked; anonymous-public/deployed-origin verification stays an
explicit release gate under #7. This closeout is not production-release approval.

## Scope and contract

The existing private image-job API and `/detect` workspace now expose annotated
PNG, JSON, and CSV downloads. See [the versioned schema](../image-exports.md).
There is no new inference path, persistent export storage, dependency, OCR,
tracking, video feature, checkpoint change, or legacy Streamlit modification.

## Initial local checks

- Red/green at the already-approved HTTP-job boundary: the first export-content
  test failed on the absent download routes, then passed after implementation.
- Focused export checks: **3 passed** (0.987 seconds), including all selected
  object types, original/raw identities, exact floating-point values, selection
  settings, six special-character/formula-like filenames, valid CSV escaping,
  and unchanged oriented RGB image bytes.
- Expanded local API suite covers successful empty exports, unauthenticated and
  wrong/another-job-token retrieval, queued/processing/cancelled/failed states,
  Delete now, accelerated expiry, generic framework-route denial, and sanitized
  storage failures without damaging other jobs. An independent shortened-expiry
  check also observed an empty storage directory after the server sweeper ran.
- Full default suite: **26 tests, 17 passed, 9 explicitly skipped**, exit 0,
  final post-review run: 13.466 seconds. Skips are opt-in hosted/real-inference
  gates, **not passes**.
- Mypy passed all five service files using `--ignore-missing-imports
  --follow-imports skip --check-untyped-defs` (not strict third-party checking).
- TypeScript checks passed repeatedly. Production build passed with the public
  hosted API URL configured (Vite build: 2.95 seconds).
- Whitespace check passed. Impeccable mechanical detector returned `[]`.

## Initial local-backed browser downloads

Edge/Chromium version **157.0.8103.52**, using the actual workspace at
`http://127.0.0.1:5173/detect` and the production API code over real HTTP on port
7861. Only the external-compute adapter was substituted; **this is not model or
hosted-inference evidence**. The substitute exists only in a temporary local
verification script, not the production service or shipping frontend.

- Three-type success: actual browser download events and saved PNG/JSON/CSV files;
  all have generated safe attachment names. JSON contains all three observations
  and readable plate labeling. Saved PNG bytes exactly equal the annotated preview.
- Empty success at 100%: all three downloads work via keyboard activation. Saved
  JSON has `state: "empty"` and `detections: []`; CSV has exactly its twelve-column
  header; PNG pixel data exactly equals the clean red/blue source with no boxes.
  A formula-like Unicode/comma/quote filename is preserved exactly in JSON.
- Simulated CSV 503: useful retry alert, no erroneous downloaded attachment, and a
  subsequent real retry succeeds. This browser error was deliberately injected;
  separate local API fault injection verifies sanitized storage-error responses.
- Server-side deletion followed by a download produces real 404 and clears the
  stale job/download controls. UI Delete now also clears results and restores
  focus to the enabled source input. API tests check revocation for every format.
- Desktop 1440×1000 and mobile 390×844 success/empty captures were opened and
  inspected. Download controls wrap, remain readable, and cause no horizontal
  overflow. Captures and test downloads remain outside shipping assets in
  `C:\Users\User\AppData\Local\Temp\opencode\issue4-*` (tool-managed copies also
  reside in the pre-existing untracked `.playwright-mcp/` directory).

## Initial hosted attempts (historical)

- Updated only `image_service/api.py` in the existing free image Space, using the
  documented explicit-file deployment and a pinned parent revision. Space
  revision: [`61a516f39b4cc3bdc053b97ba30e779d0d88da81`](https://huggingface.co/spaces/MS3B09/autoscan-ai-images/commit/61a516f39b4cc3bdc053b97ba30e779d0d88da81).
- Management API observed **RUNNING** on current/requested **zero-a10g**. No paid
  hardware, billing, quota bypass, alternate account, or checkpoint upload.
- One real anonymous all-model inference/export test was attempted: **1 failed**,
  2.813 seconds, with **“Free GPU quota is exhausted. Try again after the platform
  resets its quota.”** Test cleanup deleted the failed job. No further GPU jobs
  were submitted in that initial attempt. The failure happened before successful
  export assertions; later authenticated checks are recorded below.
- GPU-free hosted preview/input-validation method: **1 passed**, 8.879 seconds.
  This proves preview/validation still works, not that hosted downloads passed.
- Hosted tests now include schema/runtime metadata, JSON/status/CSV consistency,
  readable identical preview/download bytes, selected-only/empty exports,
  special-character/formula-like filenames, capability protection, deletion, and
  expiry. The initial anonymous run did not reach success/export assertions; the
  later user-run and shared #3 results are recorded below. Selected-only/empty and
  actual retention checks had not run at this initial stage; they subsequently
  passed during the shared closeout.

## Remaining release gates and untested extras

- Successful anonymous inference after the platform's quota resets belongs to #7;
  the authenticated developer result does not establish public-visitor availability.
- Deployed Netlify-origin browser/CORS verification belongs to release issue #7.
- No spreadsheet-application interoperability matrix, screen-reader session,
  detection-accuracy benchmark, video check, or public-load test was attempted.

## Independent review (historical finding resolved below)

Reviewed against user-confirmed starting commit
`27da2808a07400c84d4b8e7800b911d8341d6e61`, using separate standards/spec reviewers.

### Standards

**0 documented violations; 1 low-priority judgment call:** local and hosted tests
repeat some CSV-content assertions. Left unchanged: independent explicit test
oracles are small, and a shared helper is optional cleanup, not a blocker.

### Spec

**0 confirmed implementation bugs or scope-creep findings; 1 open acceptance
finding at review time:** successful real hosted exports and actual thirty-minute
expiry were unverified due to quota/the opt-in elapsed-time test. The subsequent
user-run result below advanced only the hosted success/export gate; the shared
#3 closeout subsequently resolved the selected-only/empty/browser/retention gates.
The reviewer also independently ran the local API file:
**11 tests passed**.

These findings do not constitute production-release approval.

## Developer authentication follow-up

Prepared optional `AUTOSCAN_TEST_HF_TOKEN` support for image-job submission only;
the public frontend and backend remain unchanged. The dedicated READ token is
entered locally using the [authenticated test instructions](../authenticated-image-tests.md),
without replacing the saved WRITE deployment credential or storing secrets in
the repository. No real inference token was read or GPU request made by the
agent while preparing this support.

Four GPU-free outgoing-HTTP checks passed: explicit inference authentication,
rejection of unrelated target hosts, independent job-key/private and anonymous
probe behavior, and no fallback to the deployment token. Full default suite:
**30 tests, 21 passed, 9 skipped**, 7.314 seconds. Mypy passed seven service/test
files. These client checks do not establish authenticated hosted inference.

### User-run hosted result

After following the authenticated single-test instructions, the user reported:

```text
Ran 1 test in 23.795s

OK
```

The documented command selects
`test_a_real_selection_confidence_raw_classes_and_private_result`: real hosted
image inference, model identities/confidence, JSON/status/CSV consistency,
formula-like Unicode filename handling, readable preview-identical PNG bytes,
capability isolation, generic-route denial, and deletion/revocation.

This is **user-reported evidence**, not an agent rerun. No identity-check output,
remaining-quota value, or quota-reset timestamp was supplied; exact account quota
attribution is not independently established from this test summary. This result
does not cover selected-only/empty jobs, anonymous inference, actual browser
downloads against the hosted backend, or the thirty-minute expiry test.

## Shared earlier-ticket closeout

The user requested completing #2/#3 before resuming #4. New agent-run evidence is
recorded in [issue-3-verification.md](issue-3-verification.md#closeout-checks--2026-11-14):

- Dedicated READ token identity/role/free account verified without GPU use; the
  encrypted handoff was subsequently removed and the saved WRITE login unchanged.
- Real hosted plate-only/empty export check: **1 passed in 12.811 seconds**, using
  two jobs. Admission/cancellation and preview/input-validation checks also passed.
- Actual browser success with seven real selected detections, and a real 100%
  plate-only empty result: saved PNG/JSON/CSV files decoded and agreed with
  status/preview, including empty/header-only/no-box behavior. A private temporary
  adapter supplied submission authentication server-side only; result access and
  downloads went directly from the browser to the hosted API. The HF token never
  entered the frontend. This is **not** native anonymous submission success.
- Independent browser-context access was denied; Delete now revoked every old
  download, and restored keyboard focus. Shared-limit and native anonymous GPU
  quota errors did not create false success or failed-job downloads.
- Actual thirty-minute hosted expiry passed: **1 test in 1,810.025 seconds**;
  status/preview/all three downloads returned 404 after expiry without browser
  cleanup. The [terminal log](issue-3-hosted-30-minute-expiry.log) is retained.
  This does not establish anonymous-public availability or deployed-origin CORS.

No new #4 feature was added during this earlier-ticket closeout.

## Final acceptance reconciliation

Checked the issue and parent specification against the unchanged export
implementation, its callers, schema documentation, tests, and shared evidence.
No additional product-code change is required.

| #4 criterion | Implementation and verification |
| --- | --- |
| 1. Accessible PNG/JSON/CSV actions and useful unavailable/error states | `web/src/main.tsx` download controls, live status, retry alerts, abort handling, and stale-job clearing; initial browser error/deletion checks plus actual hosted browser downloads. |
| 2. All selected detections and stable documented fields | `docs/image-exports.md` schema 1.0 and twelve CSV columns; `test_downloads_match_all_detections_and_preserve_raw_identities`, real selected-only hosted check, and seven-detection browser result. |
| 3. Job/settings/model/runtime metadata and raw identities, no invented OCR | JSON equals job status; model digests/classes and runtime versions included; raw plate class `0` retains readable label `Plate`. Local contract, user-reported real hosted test, and shared real browser checks cover these fields. |
| 4. CSV rows, escaping, encoding, formula-like text | Standard CSV writer, UTF-8 BOM, text-cell formula protection; six local filename cases and user-reported real hosted Unicode/comma/quote/formula filename test. Numeric values remain numbers. |
| 5. Exact result/image consistency | No extra export filtering or numeric rounding; PNG returns the preview's bytes. Local oriented red/blue check, hosted JSON/status/CSV assertions, and saved 792,328-byte real browser PNG comparison passed. |
| 6. Valid empty exports, not failure | Real hosted plate-only 100% empty job and keyboard browser downloads: empty detection array, header-only CSV, readable unchanged no-box PNG. |
| 7. Capability isolation, deletion, expiry, no file-route bypass | Same authorization and lifecycle as the existing job. Local/hosted denial and deletion checks, independent browser context, generic-route probes, and real 1,810.025-second hosted retention pass. Local shortened-expiry inspection also observed physical storage cleanup. |
| 8. Safe failures without unrelated/partial files or payload logs | Exports assembled in memory before attaching; sanitized errors. Local storage fault injection preserves both jobs and emits no attachment; browser CSV failure/retry passed. Existing production access-log suppression, sanitized inference errors, and disabled prediction verbosity remain unchanged. |
| 9. Hosted API and actual browser verification | User-reported hosted all-model/special-filename pass, agent-run selected-only/empty checks, actual hosted-backed success/empty browser downloads, and elapsed-time retention log. Submission authentication and evidence limits are explicitly recorded above. |

### Final local rerun

- `python -m unittest discover -s tests -v`: **30 tests, 21 passed, 9 explicitly
  skipped**, 18.501 seconds. Hosted/model opt-in skips are not fresh passes.
- Mypy: **7 source files passed**, with the documented third-party import flags.
- `npm run build` with the public image API URL: TypeScript and production build
  passed (Vite: 19.57 seconds).
- `node --check tests/browser_image_layout.js`: passed syntax validation; this
  is not a new rendered browser run.

The earlier independent reviews against
`27da2808a07400c84d4b8e7800b911d8341d6e61` found no implementation bugs or standards
violations. The integrated review through `7f637a0` repeated that conclusion; its
remaining elapsed-time finding is resolved by the retained retention pass. The
optional duplicated CSV test assertions remain unchanged.

**Close #4 for its image-only scope.** This final pass changes evidence only:
no new GPU submission, credential handoff, deployment, dependency, video feature,
or optional refactor. Native anonymous/deployed-origin release checks remain #7;
the authenticated submission adapter is not claimed as either of those passes.
