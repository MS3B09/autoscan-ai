# Issue #3 verification

Date: 2026-11-14. **Implemented, not a production-release pass.** Real image
inference verification is blocked by anonymous ZeroGPU quota, and Netlify has not
been deployed. Keep issue #3 open until these gates are verified.

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
  (2.459 seconds). No further GPU requests were made. No successful detections
  from this new service are claimed.
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
  returned **422**. The entire GPU-free test method was not rerun after the client
  correction; its individual format/content/size/settings checks were observed as
  described, not retroactively counted as a passing full method.

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
  Hallmark's automated render sweep timed out; it is **not** a render-tool pass.
  The separate actual-browser captures/workflow above did pass.
- The independent UI finish review requested terminal recovery, image-fetch-
  independent expiry, and post-unlock focus restoration. All three were fixed;
  final reviewer scoring is recorded below.

## Final checks

- Full default suite: **23 tests, 14 passed, 9 not run**, exit 0, 6.641 seconds.
  Opt-in hosted tests and local Torch inference were explicitly skipped; they are
  not included in the passing count. The separate real hosted GPU failure above
  remains a failure and is not erased by the default suite.
- The final production frontend build and TypeScript check passed (8.60 seconds);
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

## Still not established

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
