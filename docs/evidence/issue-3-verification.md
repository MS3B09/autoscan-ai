# Issue #3 verification

Date: 2026-11-14. **Implemented; closeout verification advanced below.** Real
authenticated image/empty inference, queue/cancellation, and hosted-backed browser
flows now pass. Actual thirty-minute retention is running; native anonymous
inference still hits platform quota. Do not read the historical failed attempts
below as a description of the later authenticated results. Netlify deployment and
deployed-origin verification belong to release issue #7.

## Hosted service

- Space: <https://huggingface.co/spaces/MS3B09/autoscan-ai-images>.
- Initial service revision:
  [`3740200c4fa2902e9dc4ed2dc695f5c246320d34`](https://huggingface.co/spaces/MS3B09/autoscan-ai-images/commit/3740200c4fa2902e9dc4ed2dc695f5c246320d34).
- Final corrected service revision:
  [`97b94dc12cb7a0a55cde962db1a078a459c03707`](https://huggingface.co/spaces/MS3B09/autoscan-ai-images/commit/97b94dc12cb7a0a55cde962db1a078a459c03707),
  also observed `RUNNING` on free `zero-a10g`.
- Management API observed `RUNNING`, current/requested hardware `zero-a10g`.
  No paid resources, billing, hardware upgrade, or alternate account was used.
- Anonymous `GET /api/health`: 200; retention 1,800 seconds, one active, two pending.
- A real anonymous all-model image job was submitted. The first hosted test
  failed honestly with **“Free GPU quota is exhausted. Try again after the
  platform resets its quota.”** The fail-fast run stopped after **1 failed test**
  (2.459 seconds). No further GPU requests were made in that initial run. No
  successful detections from this new service are claimed.
- A separate GPU-free hosted validation run observed successful PNG, JPG, JPEG,
  BMP, and WebP previews, corrupt-content rejection, checkpoint rejection, and
  misleading-extension rejection. Its oversized-upload assertion failed because
  the slow upload hit the 30-second streaming timeout (408), not the expected
  byte-limit rejection (413). **The run failed**, rather than being counted as a
  passing test. An early Content-Length ceiling was added afterward.
- Repeating that Python-client run against the correction encountered a Windows
  connection abort while synchronously sending the oversized body. That run also
  **failed**, not passed. A header-only Python probe timed out at the intermediary;
  it did not establish rejection. The hosted test now uses the existing system
  curl client with `Expect: 100-continue`, which can receive early rejection while
  sending. An actual anonymous curl probe completed with **exit 0 / HTTP 413** on
  the corrected deployment. Four separate hosted invalid-settings requests each
  returned **422**. At that point the entire GPU-free test method had not been
  rerun after the client correction; the subsequent full-method pass is recorded
  separately below, not retroactively applied to those failed attempts.

### Recheck — 2026-11-14, approximately 11:38 UTC

- Anonymous health check: **200**, still reporting 1,800-second retention, one
  active inference job, and two pending slots.
- The complete GPU-free hosted validation method
  `test_b_supported_previews_and_invalid_content_and_settings`: **1 test passed**,
  exit 0, **9.030 seconds**. This closes the earlier client/oversized-upload
  verification gap: supported formats, corrupt/misleading/checkpoint uploads,
  oversize rejection, invalid settings, and reported retention passed together.
- One anonymous real-inference compatibility test was attempted: **1 test
  failed**, exit 1, **2.756 seconds**, with “Free GPU quota is exhausted. Try again
  after the platform resets its quota.” Its job was deleted by the test's cleanup.
  No further GPU jobs were submitted after that response; no owner credentials,
  alternate identity, or paid resources were used to bypass the quota.
- Real inference, selected-only predictions, real empty inference, GPU-backed
  lifecycle checks, and the actual 30-minute expiry test remain unverified.

### Storage recovery — 2026-11-14, from 12:22 UTC

- C: had approximately 2.5 GiB free after the user's cleanup. The workspace was
  already serving at `http://127.0.0.1:5173/detect` (HTTP 200); the attempted
  duplicate launch stopped on the occupied port rather than replacing it.
- A single anonymous real-inference recheck at **12:23 UTC** still failed on the
  platform quota: **1 failed test**, **3.020 seconds**. Its job was cleaned up, and
  no additional GPU jobs were submitted after that response. Storage recovery did
  not reset or bypass anonymous GPU quota.
- The actual Edge browser successfully validated the public compatibility fixture
  through the hosted preview API at **12:31 UTC**: **HTTP 200**, correct development
  CORS origin, **40%** default confidence, and **zero inference submissions** on
  upload. This remains a preview check, not real inference or Netlify evidence.
- The previously timed-out Hallmark rendered sweep now completed with **exit 0,
  0 FAIL, 2 WARN**, producing five inspected desktop/mobile captures (1280, 1440,
  1920, and 375-pixel widths). The warnings are heuristic secondary-button and
  table-number-style findings; the actual UI has one orange primary action and
  tabular numerals on result cells. No design changes were needed.
- The production build, with the public backend URL explicitly configured, and
  TypeScript checks passed (**7.41 seconds**). All **8 local API tests passed**
  using the normal C: temporary directory (**2.619 seconds**). Mypy again passed
  for all five service files. The full default suite passed with **14 passed,
  9 explicitly not run**, **23 total**, **8.405 seconds**.
- Local CPU compatibility was attempted in the existing isolated Python 3.10.13
  environment, using the official CPU index and pinned Torch/Torchvision versions.
  The **590.7 MiB** Torch CPU wheel still exceeded available temporary space while
  extracting. Installation stopped; the temporary extraction directory was
  automatically removed. Torch and Torchvision remain absent in that environment,
  and C: returned to approximately 2.5 GiB free. No local CPU inference pass is
  claimed, and no further installation attempts were made.
- The original application, model checkpoints, requirements, hosted service, and
  production inference device were not changed. CPU setup was a diagnostic
  attempt, not a replacement backend or a quota workaround. Hosted inference and
  actual 30-minute hosted expiry remain open gates.

The initial large-checkpoint upload attempts failed locally (full C: drive/Xet
I/O problems and a timed-out upload). No checkpoints were replaced. The service
instead provisions the same artifacts from the exact public T1 revision and
checks all trusted digests before deserialization. Only the explicit source-file
mapping was uploaded. The diagnostic Space and Streamlit app remain unchanged.

## Browser

Actual Edge captures at 1440×1000 and 390×844 were opened and inspected. Checks
covered default selections and 40% confidence, keyboard entry, absence of mobile
horizontal overflow, and normalized preview before explicit inference.

A **real browser** on `http://127.0.0.1:5173` successfully POSTed the existing
public compatibility fixture to the hosted preview API, using `credentials:
'omit'`, without an HF token. Response: **200**, with
`Access-Control-Allow-Origin: http://127.0.0.1:5173`. Inference submissions on
selection: **zero**. This is a development-origin CORS pass, **not** a Netlify
deployment or a successful inference pass.

The complete local browser flow used real HTTP against the production job API
with a controlled external-compute substitute: choose/validate, explicit start,
empty result and protected annotated-image retrieval, clear results while keeping
the source, change confidence by keyboard, rerun, Delete now, and focus restored
to the enabled upload input. No substitute is available in the production
entrypoint. These checks establish UI/API behavior, not model or hosting capacity.

The source fixture is `imgs/image.JPG`, an existing **already-annotated composite**.
Neither it nor the substitute's identical output is evidence of new detections,
clean empty-model output, accuracy, or annotation quality. Visitor images and
browser captures were not placed in shipping static assets or the public Space.

## Local checks and review

- New API contract file: **8 tests passed** (10.901 seconds on the recorded run).
  Decoding, invalid settings/content, formats, empty state, selection/settings
  metadata, access isolation, resource bounds, active/queued cancellation and
  deletion, error redaction, storage capacity, shortened expiry, and shared rate
  limiting are exercised at the approved HTTP-job seam.
- Python: mypy passed for the five new service files, with
  `--ignore-missing-imports --follow-imports skip --check-untyped-defs`. This checks
  the service bodies, not third-party libraries or fully annotated interfaces.
- Frontend TypeScript checking and production build passed.
- Impeccable detector: `[]` (no findings). Hallmark static: no FAIL/REFLEX; minor
  heuristic warnings remain about secondary button fills/table typography.
  Hallmark's initial automated render sweep timed out; that attempt is **not** a
  render-tool pass. The later storage-recovery sweep above completed successfully.
  The separate actual-browser captures/workflow above also passed.
- The independent UI finish review requested terminal recovery, image-fetch-
  independent expiry, and post-unlock focus restoration. All three were fixed;
  final reviewer scoring is recorded below.

## Final checks

- Full default suite, latest storage-recovery run: **23 tests, 14 passed,
  9 not run**, exit 0, 8.405 seconds.
  Opt-in hosted tests and local Torch inference were explicitly skipped; they are
  not included in the passing count. The separate real hosted GPU failure above
  remains a failure and is not erased by the default suite.
- The latest production frontend build and TypeScript check passed (7.41 seconds);
  mypy passed for all five new service files. Whitespace checking passed.
- API tests were rerun on NTFS after intermittent permission errors in removable-
  drive temporary-directory cleanup. All eight then passed (2.500 seconds). Those
  filesystem errors were not hidden with ignore-cleanup flags; no production
  Windows workaround or weakened cleanup was added.
  This Windows run used `TEMP`/`TMP=D:\autoscan-image-tests-tmp`; npm's cache was
  redirected to `web/.cache/npm` because C: was full. Use a writable NTFS temporary
  directory and cache for reproducing checks in this disk-constrained environment.
- The independent UI reviewer scored all three original findings **resolved**:
  terminal recovery, image-fetch-independent expiry, post-unlock keyboard focus.
  This is a ship verdict for those fixes, **not a production-release approval**.

## Standards review

No hard documented-standard violation was established. One low-priority judgment
call identified the repeated active-state list; it now has one module-local
constant. **1 finding, resolved.**

## Spec review

One test-order bug was found: inference checks could spend the six-attempt budget
before the queue check expected 503. The queue check now runs first; production
limits are unchanged. The reviewer verified the correction. One further finding
covers acknowledged release-verification gaps below. **2 findings: test bug
resolved, verification gate open.** No scope creep was identified.

## Original open gates (see later closeout results below)

- New-service real inference success, selected-only predictions and real empty
  inference, annotation inspection, or GPU-backed concurrency/cancellation under
  live quota. T1 remains compatibility evidence, not a substitute for these checks.
- Actual 30-minute hosted expiry (opt-in test not run); the short local HTTP test
  and reported production configuration are not claimed as an elapsed-time pass.
- Public load/peak memory, arbitrary adversarial codecs, an availability SLA, or
  detection accuracy. Admission budgets are conservative policy, not benchmarks.
- A deployed Netlify origin or its CORS/browser workflow. No Netlify credentials
  or site were configured, and no public frontend URL is claimed.
- Screen-reader testing or the legacy Streamlit app running interactively in this
  disk-constrained environment. Its source/requirements/checkpoints are preserved.

## Closeout checks — 2026-11-14

Scope: finish earlier #2/#3 work before returning to #4. #2 was reconciled and
closed as a feasibility pass; this is not public-release approval. No new video,
showcase, Netlify deployment, or paid resource was introduced.

### Hosted API

Verified through the Hub identity API, without GPU use: account `MS3B09`, token
name `autoscan-inference`, role `read`, `isPro: false`. The dedicated token was
supplied via a Windows DPAPI-encrypted temporary handoff, never a repository file
or frontend variable. The saved WRITE deployment login was not replaced.

| Check | Result | Evidence |
| --- | --- | --- |
| Bounded admission and cancellation | 1 passed, 8.207 s | `issue-3-hosted-admission.log` |
| Plate-only selection at 40%, and successful empty result at 100%, including exports | 1 passed, 12.811 s (two image jobs) | `issue-3-hosted-selection-empty.log` |
| Supported previews, corrupt/misleading/checkpoint/oversized inputs, invalid settings | 1 passed, 18.498 s | `issue-3-hosted-validation-closeout.log` |
| Actual thirty-minute hosted retention | Running, not yet a pass | Await terminal test output |

The tests retain their protected image/result/download checks. Local API contract
file independently passed **11 tests in 6.200 seconds**. Full default suite:
**30 tests, 21 passed, 9 explicitly skipped**, 10.395 seconds. Mypy passed seven
service/test files; TypeScript and production build passed (Vite: 5.07 seconds).
The design detector returned `[]`. No failed/skipped check is counted as a pass.

### Actual browser with real hosted inference

The real workspace ran at `http://127.0.0.1:5173/detect`, configured to the public
image Space. A temporary, one-use localhost adapter added HF authentication only
to submission server-side. The browser's original submission had no HF token;
native preview/status/image/export/delete requests went directly to the hosted
API with the ordinary job capability. **Submission was instrumented developer
verification, not a successful native anonymous submission or deployed-origin
CORS proof.** No production code or service configuration gained a relay or key.

- Existing public composite fixture: **seven real detections** across vehicles,
  logos, and plates; displayed count matches hosted status. Saved actual browser
  PNG/JSON/CSV downloads were independently decoded/compared: every selected
  detection, raw identity, dimension, coordinate, and confidence agrees. The
  792,328-byte PNG exactly equals the annotated preview. This already-annotated
  compatibility fixture does not establish accuracy or new example photography.
- Clean white 48×32 fixture, plate-only at 100%: keyboard submission and all three
  browser downloads passed; `state: empty`, zero detections, valid header-only
  CSV, no error, and image bytes identical to the normalized no-box source.
- An independent browser context could not retrieve status/images/any download,
  cancel, or delete the successful job. UI Delete now succeeded, cleared the
  result, restored upload focus, and left all old protected URLs returning 404.
  The empty and quota-failed verification jobs were also deleted.
- Hosted preview before explicit Detect image made **zero inference submissions**.
  Default selections/40%, empty-selection rejection, keyboard 25–100% bounds,
  desktop/mobile wrapping, and no horizontal overflow were verified.
- A native anonymous browser submission first received the actual shared upload
  limit (429), with a useful error and enabled retry rather than false success.
  After that window cleared, one native anonymous submission was admitted (202)
  but ended in explicit **ZeroGPU quota exhaustion**, not empty success; no
  downloads were offered. No further anonymous GPU submissions were made.
- Desktop/mobile captures were opened and inspected. They remain in the approved
  temporary directory as `issue-3-*`, not shipping assets. Full-page capture made
  the fixed skip link appear visible; live focus/scroll assertions showed it was
  actually hidden correctly, so no skip-link styling was changed.
- Initial browser verification code hit a large-buffer spread stack error and a
  thirty-second download-event timeout. Chunk iteration and a ninety-second test
  event budget fixed the harness; saved outputs were then rechecked. Production
  request timeouts were unchanged, and recovering download checks did not submit
  additional inference jobs.

### Minimal UI correction

Mobile CSS changed the table to block layout but left its coordinate caption as
`table-caption`, shrinking it to about 73 px in a 343 px table. A one-property
probe confirmed the cause. The mobile block rule now includes `caption`, which
fills the table width; desktop table semantics/styling remain unchanged.

`tests/browser_image_layout.js` reproduces the width failure on a completed job,
passes after the fix, and checks skip-link focus/visibility at 390 and 1440 px.
Run it using `browser_run_code_unsafe` with that filename after completing an
image job. It is an explicit browser check, not part of Python test discovery.

The temporary auth adapter was stopped and the encrypted handoff file removed.
The retention test had already loaded its credential before that cleanup. No
owner token entered frontend code, URLs, captured output, or shipping assets.

### Still open at this point

- The real thirty-minute hosted retention test must reach its terminal result.
- A native anonymous successful image/browser flow remains unverified while the
  platform denies GPU quota. The authenticated relay flow is not a substitute for
  public-visitor acceptance; carry this explicitly into the release gate.
- Deployed Netlify-origin CORS/full workflow, independent release-level load and
  licensing review, and video/browser playback belong to later tickets. No
  screen-reader session or interactive legacy Streamlit run was attempted here.
