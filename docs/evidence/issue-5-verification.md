# Issue #5 verification

Date: 2026-11-14 (local session). Scope: short-video implementation, not public
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

Six video API test methods pass using real codecs, HTTP routes, threads, and
temporary files, with only external model compute substituted. Coverage includes:

- All six containers; content/filename mismatch; actual decoding and silent H.264.
- Exactly 20 MB/chunked overflow, exactly ten seconds/over-duration, exactly
  600 frames/601-frame rejection, landscape and portrait 720p/oversized rejection.
- VFR source timestamps `[0, .1, .4, .9]`, every-frame observations, complete output
  frame counts/timing, matching JSON/CSV, and readable empty/header-only exports.
- Tampered zero-duration MP4 sample timing, corrupt payloads/truncation.
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

## Remaining verification limits

- The opt-in hosted unittest is provided but was not separately rerun after the
  successful native browser invocation; it would spend another GPU allocation.
- Fresh hosted worst-case 600-frame/all-model inference, active video cancellation,
  and a new thirty-minute video retention wait are not established by that run.
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
