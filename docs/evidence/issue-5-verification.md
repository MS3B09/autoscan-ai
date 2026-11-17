# Issue #5 verification

**2026-11-17 closeout:** #5 is closed under the owner's final release request and
explicit no-more-tests decision. Retained technical evidence and owner 1080p PASS
remain scoped; hosted active cancellation/video-expiry/resource gaps are accepted
unverified exceptions, not new passes. See [publication evidence](issue-7-final-release.md).
The pending owner-check/closeout statements below are historical.

Current acceptance status (2026-11-16): implementation is complete; six criteria
are evidenced and three retain deferred verification. No new video checks may be
run by the agent; the owner reserves the final candidate test. See
[acceptance-reconciliation.md](acceptance-reconciliation.md) and
[the release checklist](../release-checklist.md). Results below are historical.

Date: 2026-11-14–15 (local session). Scope: short-video implementation, not public
release approval. Review baseline: user-confirmed `07ca289a70a9af246f7cbd40652d1c36ad791925`.

## Implemented

The protected image-job workflow now processes short videos frame by frame and
offers silent H.264 MP4, frame-level JSON, and CSV. See
[the contract and limits](../video-workspace.md). No checkpoint, legacy Streamlit
change, paid hardware, account requirement, audio preservation, OCR, or tracking.

## Local tests

Red/green at the already-approved HTTP-job seam:

1. A real video preview initially failed with 415 at the image-only format gate.
2. A frame-level video job initially failed because the worker still selected
   `source.png`; it passed after extending the shared worker and export routes.

Nine video API test methods pass using real codecs, HTTP routes, threads, and
temporary files, with only external model compute substituted. Coverage includes:

- All six containers; content/filename mismatch; actual decoding and silent H.264.
- Exactly 20 MB/chunked overflow, exactly ten seconds/over-duration, exactly
  600 frames/601-frame rejection, landscape and portrait 720p/oversized rejection.
- VFR source timestamps `[0, .1, .4, .9]`, every-frame observations, complete output
  frame counts/timing, matching JSON/CSV, and readable empty/header-only exports.
- Tampered zero-duration MP4 sample timing, corrupt payloads/truncation.
- AVI truncation at a complete frame boundary, including a rewritten outer RIFF
  length; nested LIST/chunk lengths must still fit the actual body.
- Native-codec timeout and temporary directory/write failures return actionable,
  sanitized errors, leave no uploaded files, and do not block health requests.
- Real observed first-frame progress, bounded queue, queued/active cancellation,
  source/partial-file cleanup, failure sanitization, capability protection,
  deletion, and accelerated server expiry with physical cleanup.

The unchanged image API file separately passed all eleven methods. TypeScript,
service mypy (with documented third-party import flags), and production build
passed during implementation. Final suite/review results are appended below.

## Real hosted anonymous browser run

Space revision:
[`0fb4c6fabc3fbaea368f492ee3056ff13b99d7a7`](https://huggingface.co/spaces/MS3B09/autoscan-ai-images/commit/0fb4c6fabc3fbaea368f492ee3056ff13b99d7a7).
Only the explicit service-source/requirements/README mapping was uploaded; no
visitor media, credentials, or checkpoints. Management API observed free
`zero-a10g` hardware. No paid resources were requested.

The existing dev server at `http://127.0.0.1:5173/detect` was already configured for
the hosted API. Although a separate local-compute adapter was prepared for browser
contract checks, **this run used the real hosted backend**, not that substitute.
The public client used `credentials: 'omit'`, no HF token or login. Source preview
completed without a job submission; only Detect video submitted inference.

The fixture is the changing-traffic clip from #2, SHA-256
`b1485225e56b5117d31990163238468766175c5188c1169d828905a834c92015`:
5,447,771 bytes, 1280×720, ten seconds, 300 source frames. Attribution and its
remaining release-rights caveat stay in the #2 evidence/validation Space README.
It is compatibility/capacity footage, not an accuracy benchmark.

Observed result and independently checked saved browser downloads:

| Check | Observation |
| --- | --- |
| Processed / encoded / decoded output | 300 / 300 / 300 frames |
| Output | H.264, silent MP4, 1280×720, ten seconds, 6,488,612 bytes |
| Output timing | Every output timestamp matches source index/30 within one microsecond |
| Detections / CSV rows | 2,375 / 2,375, with identical frame indices/timestamps |
| Trusted models | All three SHA-256 identities match the pinned diagnostic constants |
| Encoder runtime | PyAV 17.1.0 recorded in JSON |
| Actual browser playback | Source and annotated video advance; annotated playback reaches `ended` after seeking near the end; no media error |
| Downloads | Native browser MP4/JSON/CSV download events, activated by keyboard, safe generated names |
| Visitor isolation | Independent browser context denied status/video/all exports with missing and wrong capabilities |
| Delete now | Old routes revoked; video removed from UI and upload focus restored |
| Layout | 1440px desktop and 390px mobile fit without horizontal overflow |

The initial browser script timed out while waiting for the long preview/MP4
transfer. The completed job was resumed for playback/download/isolation/deletion
checks **without another GPU submission**. Hosted media transfer times observed
were roughly 38 seconds for preview and 45 seconds for the result; these are
single-run network observations, not processing latency/FPS promises. Request
budgets remain finite; network failures offer retry instead of false success.

Artifacts remain outside shipping files under
`C:\Users\User\AppData\Local\Temp\opencode\issue5-*`; tool-managed copies also
exist in the pre-existing untracked `.playwright-mcp/` directory. No source media,
raw detection payload, or job capability is included in this evidence document.

## Final hosted 600-frame gate

The revised isolated-codec service was deployed at
[`facae23f4684cda04e9f92e02d54073f67a2a44b`](https://huggingface.co/spaces/MS3B09/autoscan-ai-images/commit/facae23f4684cda04e9f92e02d54073f67a2a44b).
Management API observed **RUNNING**, current/requested free **zero-a10g**.
One anonymous invocation of `test_hosted_video_api.py` passed in **218.033 seconds**
(including uploads, status polling, repeated downloads, isolation probes, and
deletion; not an inference latency measurement). No implicit deployment token,
quota retry, alternate identity, or paid fallback was used.

The capacity fixture duplicates each changing-traffic source frame once during
test-fixture preparation, producing a ten-second, 60-fps, 1280×720, **600-frame**
input. This is not application sampling/interpolation or an accuracy benchmark.
Fixture size: **5,503,461 bytes**; SHA-256
`53c5a4bc5b3721792f8083a0d1cda7f3f15628d24b2df6047d4a9ff9a6ec8e10`.

- **600 decoded source / 600 processed / 600 decoded output frames**.
- **4,719 observations / CSV rows**, with matching source frame indices/timestamps,
  selected types/confidences, all three original model digests, and JSON/status.
- Silent H.264 MP4, ten seconds, 1280×720, **7,128,980 bytes**.
- Preview/download bytes agree; missing/wrong capabilities deny every protected
  result operation; Delete now revokes every old result/download route.
- The actual saved final-hosted MP4 was also played in **Chromium 157.0.8103.52**:
  it advanced, sought near its ten-second end, reached `ended`, and had no media
  error. This last playback used local-file response replay, not a new hosted job.

Final 25-row pagination and 390/1440px layouts were checked by replaying the saved
real 300-frame result through test-only browser routes (with an explicitly
simulated fresh expiry, not a retention test). Pagination advanced, both layouts
fit without horizontal overflow, and rendered captures were inspected. The
earlier native hosted browser run remains the end-to-end upload/download evidence.

## Independent review

### Standards

One documented-standard finding: temporary-directory creation/input writing sat
outside the storage-error boundary and could return a generic 500. Moved both
inside the boundary; the HTTP regression covers both failures, sanitization, and
physical cleanup. Reviewer confirmed resolved; no remaining standards findings.

### Spec

One implementation finding: AVI header frame counts can represent empty time slots,
so bypassing a simple count comparison also admitted physically truncated AVI.
Added RIFF bounds validation. Follow-up review caught a rewritten outer length
that still concealed a truncated nested `movi` LIST; validation now walks nested
RIFF/LIST chunk boundaries too. Both reproductions have red/green HTTP regressions.
No unrelated feature or detector change was added.

Review totals: **Standards 1 fixed; Spec 1 fixed (including nested-length variant)**.
The spec reviewer independently repeated valid AVI / original truncation /
rewritten outer-length truncation: **200 / 422 / 422**, with no temporary files
left by any case. No implementation findings remain from that focused follow-up.

## Final post-review checks

- `python -m unittest discover -s tests -v`: **40 tests, 30 passed, ten explicitly
  skipped**, 55.315 seconds, exit zero. Hosted opt-ins and local PyTorch integration
  skips are not counted as passes; the real hosted 600-frame test is reported
  separately above. A prior full run preceded the nested-AVI follow-up; this final
  rerun includes that fix and both malformed-AVI variants.
- Service/new-test mypy: **eight files passed**, using `--ignore-missing-imports
  --follow-imports skip --check-untyped-defs`; not strict third-party checking.
- Final TypeScript and production build passed (Vite: 11.51 seconds).
- `node --check tests/browser_video_workflow.js` and Git whitespace checks passed.
- Final service revision:
  [`dbafd5210c59c719fdce59556d400be4f870859d`](https://huggingface.co/spaces/MS3B09/autoscan-ai-images/commit/dbafd5210c59c719fdce59556d400be4f870859d).
  The sole service change after the 600-frame pass is nested AVI validation; the
  MP4 inference/encoding path is unchanged. Actual hosted GPU-free AVI preview
  checks on this revision observed **200 / 422 / 422** for valid / truncated /
  rewritten-outer-length-truncated containers. Hardware remained free ZeroGPU.

## Remaining verification limits

- Fresh hosted active video cancellation and a new thirty-minute video retention
  wait are not established by these runs.
  The shared lifecycle has prior real image retention evidence and new deterministic
  video contract checks; these do not become fresh hosted video passes.
- Desktop Chromium at mobile viewport size is not a physical iOS/Safari/Android
  codec matrix. No new screen-reader, accuracy, adversarial fuzzing, or public-load
  benchmark. Public Netlify-origin/release checks remain #7.
- Impeccable mechanical detector returned `[]`. Hallmark static sweep returned
  zero FAIL, two video-poster REFLEX findings (waived in CSS: native private-blob
  media, no public/invented poster), and two inherited selector WARNs. Its automatic
  render tier could not find Chrome; actual Playwright renders/playback were
  inspected separately. No design-system replacement or unrelated cleanup.
- A local Windows run of representative media hit native resource/stall failures;
  this is not reported as passing. It motivated subprocess timeout isolation and
  bounded codec threads. The final real hosted Linux 600-frame run above passed;
  local GPU inference remains unavailable without PyTorch/CUDA.
