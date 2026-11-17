# Owner-requested 1080p support — #5 / #7

> **Published 2026-11-17:** https://autoscan-ai.netlify.app/detect. Same reviewed
> deploy `6afb4f606cabececacad1489`; site renamed before promotion. #5/#7 are closed
> under the owner's explicit no-more-tests decision, with unverified exceptions
> retained. See [final publication](issue-7-final-release.md). Preparation URLs and
> pending-check statements below retain their historical scope.

Date: 2026-11-16. The owner requested accepting a clip whose screenshot reports
**1920×1080**, about **two seconds**, **30.14 fps**, then explicitly approved
**local CPU-only codec/API video tests and a backend/draft update**. This does not
authorize model inference, hosted/browser video checks, production promotion or
paid resources. The screenshot is metadata, not the actual file or proof of its
container, decodability, precise duration or upload size.

## Change and preserved boundaries

- Production video validation now accepts up to **1920×1080**, or portrait
  equivalent, in both the stream-header and decoded-frame checks.
- The native decoder still has a bounded pixel-allocation guard, increased to
  **2,097,152** pixels to allow codec alignment padding around a 1080p frame.
- Preview and job processing preserve source dimensions; no silent scaling,
  cropping, truncation or frame sampling was added. The UI advertises **1080p**.
- **20 MB, ten seconds, 600 decoded frames**, timeouts, encoding/output bounds,
  selected models/confidence, capability isolation, one active inference slot,
  bounded admission/rate limits, cleanup and retention remain unchanged.
- No checkpoint bytes, model/runtime dependency pins, GPU reservation or legacy
  Streamlit code changed. The separate historical diagnostic retains its original
  720p compatibility fixture/ceiling; it is not the public media-job API.

## Local evidence — no model execution or hosted video

The existing public HTTP job-API seam was used with real local codecs/files and
substituted external compute; no new seam or inference dependency was added.

1. New landscape/portrait 1080p preview/job regression was **red first**: both
   sizes returned the former **413 / 720p** rejection.
2. After the shared validation change, the same test passed. It verifies complete
   three-frame silent H.264 previews and job downloads at **1920×1080** and
   **1080×1920**, with matching job/output dimensions and capability-based cleanup.
3. Updated boundary cases retain 720p compatibility, accept former just-over-720p
   sizes and reject **1922×1080 / 1920×1082**. Existing duration/frame/byte,
   format, timing, cancellation, expiry, corrupt-media, timeout and storage checks
   stay in the local codec/API suite. **10/10 passed**, native exit **0**.
4. Final explicitly selected applicable suite: **39 passed, 0 failed,
   0 runner-skipped**, **50.210 s**, native exit **0**. This includes the ten local
   video API methods plus the previous 29 safe image/adapter/client/CLI methods.
   **12 methods policy-deferred/not run** (51 methods now exist); no unfiltered
   discovery, hosted/model suite or diagnostic video invocation ran.
5. Python typecheck: **passed, seven files**. Frontend typecheck/build: **passed**,
   Vite **7.3.8**. Mechanical check of the changed UI source returned **`[]`**.

These short fixtures are compatibility/regression checks, not a 1080p workload
benchmark. A 1080p frame has **2.25×** the pixels of 720p. Existing real hosted
300/600-frame evidence remains **720p-only**; full-resolution inference latency,
peak resources and maximum-workload feasibility are **unverified**. No owner
quota was spent by the local tests. The owner's final hosted clip check and all
other unresolved #5/#7 release gates remain separate.

## Deployment and review handoff

### Standards

Independent read-only review of source **`e719d8a`** against the existing
owner-approved fixed baseline **`cea69ae7f60c84ad8532eca803510283473fc6d2`** found
**0 findings and 0 actionable smells**. Both validation boundaries and the bounded
decoder guard are preserved. No tests, inference or hosted probes ran in review.

### Spec

The separate read-only review found **0 actionable defects or unrequested scope**.
The owner's instruction supersedes the old 720p ceiling only for resolution.
Actual-file compatibility and 1080p free-hosted inference/resource capacity remain
unverified; no such pass is inferred from local tests. Review totals: **Standards
0, Spec 0 actionable findings; no worst finding on either axis**.

### Refreshed backend and draft

- Reviewed/pushed source: **`e719d8a97e7d97961b528efd5e6ea5ef19ee8d5e`**.
- Backend: **`d160158db56c1cdf6113a575b8b01bb763f81b73`**, parent
  `b6c91e23f1b0fcb8bfb3ab65d906d53fbcc2e9b5`. Backed up the pinned prior Space
  revision, compared all explicit mapped files, and atomically updated **only
  `image_service/video.py`**, guarded by the prior SHA. The published file bytes
  match local SHA-256 `fe4ba01e1799e1c3d23391ff1d1c18868b14c6cec807f19f8625bc68d36806d5`.
  Existing custom checkpoint hashes were rechecked before upload.
- Final backend metadata: **RUNNING / free zero-a10g / one current/requested
  replica**. Anonymous health: **200 / ready / 1800 s retention / 1 active /
  2 pending / no-store**. No new full installed-package inventory is claimed.
- Existing Netlify site: `1661ca1f-7c9b-4f69-b8ee-635ac7a49eee`, project
  `autoscan-ai-ms3b09`, team `mosab04-ns`, **Free**. Created one new file-digest
  deploy with explicit **`draft:true`**; all 18 uploads returned 200. Final
  metadata: **ready / deploy-preview / published_at null / no published deploy /
  Git unlinked**. No production, plan, billing or hardware change.
- New deploy ID: **`6afb4f606cabececacad1489`**.
- **Owner's current test URL:**
  <https://6afb4f606cabececacad1489--autoscan-ai-ms3b09.netlify.app/detect>.
- [Retained artifact hashes](issue-5-1080p-artifacts.json): 18 files including the
  literal TOML-equivalent rule files. All **16 public files** fetched anonymously
  matched SHA-256 and passed scoped credential/capability pattern checks. All
  three HTTPS routes returned the exact new HTML and expected security headers.
  No Netlify Git build ran, and no provider build-image reproducibility is claimed.
- Appended only the new exact HTTPS draft origin to `AUTOSCAN_ORIGINS`; retained
  both existing local origins and the earlier approved draft origin. No wildcard,
  production origin, token, secret, paid resource or replica was added.
- Isolated browser check: visible **1080p / 20 MB / 10 s / 600 frames**, direct
  refresh and eleven widths **320–1920 px** passed with zero page runtime errors.
  Inspected local desktop/mobile captures under
  `.playwright-mcp/issue5-1080p-6afb4f60-{desktop,mobile}.png`; no design change.
- A separate allowed **still JPEG** preview verified actual browser preflight
  **204**, preview **200**, exact new-origin CORS and `no-store`, without owner
  Authorization/Cookie/Referer or any job attempt. This was **not a video check**.
  Temporary request guards/capture were removed, leaving a clean detector page.

No hosted/browser video preview, video processing or model inference ran. The
prior `6afb394cb63bcc5d8c896112` draft is historical; use the **new URL** above.
Do not reuse its acceptance evidence as a fresh 1080p runtime pass. The owner can
now perform the reserved final clip check; remaining #5/#7 safeguards and separate
production approval still apply.

### Deployment-record follow-up review

Read-only review of documentation candidate `024bf9f` found **one Standards P3**:
the reusable API recipe could be read as creating a new site for every refresh.
**Resolved:** it now explicitly reuses the recorded site ID and limits site
creation to initial provisioning. No duplicate site was created by this task.
The separate Spec follow-up found **0 actionable findings**. Final follow-up
totals: **Standards 1 wording finding, resolved; Spec 0**. No remaining review
defect or new inference/deployment claim results from that documentation fix.

Licensing remains the existing owner-directed exception/unverified disposition;
all notices and private-training boundaries are preserved. #5/#6/#7 stay open.

## Owner's final video report — 2026-11-16

The owner reported after the refreshed 1080p handoff:

> I ran it on video now and all is good. Video check successfully passed.

**Disposition: owner-reported PASS of the reserved final video check.** The
candidate under handoff is deploy `6afb4f606cabececacad1489` (source `e719d8a`,
backend `d160158`). The message does not include an independently captured build
URL, job report, timing, resource measurement or downloaded artifacts. Record the
reported workflow success without inventing per-action measurements or claiming
independent agent verification. Earlier "owner check pending" statements above
describe the preparation phase and are superseded by this report.

No agent test, inference, video preview, media inspection or deployment ran for
this update. No quota attribution or maximum 1080p workload claim is added. The
report does not separately verify active cancellation, a thirty-minute expiry,
cross-visitor isolation, resource/failure cases or deferred tests. These still
need honest evidence reconciliation/disposition; do not require or run more
quota-consuming checks without approval. Production promotion and ticket closure
are not authorized by reporting a successful video test.

Current cross-ticket release gates and remaining evidence/production decisions:
[issue-7-release-gates.md](issue-7-release-gates.md).
