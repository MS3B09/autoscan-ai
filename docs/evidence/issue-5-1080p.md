# Owner-requested 1080p support — #5 / #7

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

The implementation source must be reviewed before the approved backend/draft
refresh. Record actual source/backend/deploy IDs, artifact hashes, retained
origins and only permitted non-video hosted checks here after deployment. Do not
reuse the earlier 720p draft's acceptance evidence as a new 1080p runtime pass.

Licensing remains the existing owner-directed exception/unverified disposition;
all notices and private-training boundaries are preserved. #5/#6/#7 stay open.
