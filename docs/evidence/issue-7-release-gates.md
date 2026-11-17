# #7 release gates after the owner's video pass

> **Later 2026-11-17 work:** [final-release evidence](issue-7-final-release.md)
> records the owner's release/closeout request, verified saved exports, assigned
> `autoscan-ai.netlify.app` hostname, origin wiring and fresh permitted checks.
> The production/hostname approval and runtime-request statements below describe
> the earlier handoff; remaining hosted-test authorization is now the blocker.

Date: **2026-11-16**. Implementation source **`e719d8a`**, backend
**`d160158db56c1cdf6113a575b8b01bb763f81b73`**. The final video check is
**PASS, owner-reported**, recorded in `872a854`; not an independent agent trace.

**Evidence reconciliation complete; release acceptance and production approval
remain open.** This task used retained evidence, read-only management/build
metadata and checkpoint hashing. No application/media tests, inference, lifecycle
mutations, restart, deployment or paid change ran.

## Candidate and fresh read-only observations

- Detector: <https://6afb4f606cabececacad1489--autoscan-ai-ms3b09.netlify.app/detect>.
  Showcase: the same immutable origin at `/`.
- Netlify site `1661ca1f-7c9b-4f69-b8ee-635ac7a49eee`, project
  **`autoscan-ai-ms3b09`**, team `mosab04-ns`: **Free**, candidate **ready /
  deploy-preview / published_at null**, site **published_deploy null**, Git
  repository **unlinked**. The configured default hostname is
  `https://autoscan-ai-ms3b09.netlify.app`, not an already-promoted release.
  `https://autoscan-ai.netlify.app` is not configured for this site; availability
  and any rename remain separate decisions.
- Backend <https://ms3b09-autoscan-ai-images.hf.space>: expected source above,
  **RUNNING / zero-a10g**, **one current/requested replica**. The two local and
  two immutable-draft origins remain configured; no production origin was added.
- Both local custom checkpoint hashes freshly matched
  `scripts/validate_inference.py`. No model was deserialized. This is not a fresh
  readback of running model bytes.
- Current backend build logs returned **31 chunks**, with no recognized credential
  patterns and **no usable installed-package version records**. Raw logs were not
  saved/echoed; run/job/media logs were not accessed. Declared pins are not observed
  runtime versions, and pattern scans are not a blanket credential guarantee.

## Evidence used, with its original boundaries

- [1080p handoff](issue-5-1080p.md) and [artifact manifest](issue-5-1080p-artifacts.json):
  exact current draft, 16 public-file hashes, routes/headers/layout/keyboard checks
  and native anonymous **still-image preview** preflight/response. No agent-hosted
  video or inference pass is implied.
- [Owner video report](issue-5-1080p.md#owners-final-video-report--2026-11-16):
  successful final workflow reported after this handoff; no independently captured
  per-action, runtime, memory, latency or maximum-workload evidence supplied.
- [Image evidence](issue-3-verification.md) and [exports](issue-4-verification.md):
  retained real selected/empty workflows, isolation/deletion and actual 1,810-second
  image retention, with their recorded origins/authentication/revisions.
- [Video evidence](issue-5-verification.md): real anonymous 300/600-frame **720p**
  processing, playback, exports, isolation/deletion, plus local codec/lifecycle
  checks. It is not a fresh 1080p capacity or thirty-minute video-expiry pass.
- [Showcase evidence](issue-6-verification.md), [quota/adapter checks](developer-quota-verification.md)
  and [runbook](../release-runbook.md) retain their own dates and scopes.
  Authorization/lifecycle code was retained through the narrow quota/1080p updates;
  that supports reuse of implementation evidence, not invented fresh observations.

## #7 acceptance criteria, original order

Each row covers the combined original criterion. Partial means leave its checkbox
open; covered preparation does not authorize promotion or waive another gate.

| # | Criterion | Current evidence and remaining disposition |
| --- | --- | --- |
| 1 | HTTPS routes, free backend, preserve Streamlit | **Draft verified; production pending.** Current routes/refresh/headers and backend wiring recorded; legacy app preserved. Separate production/hostname approval and same-candidate production checks remain. |
| 2 | Complete deployed image/video settings, processing, exports, empty results/playback | **Partial.** Owner final video PASS plus retained real image/empty/video evidence. Current-candidate image/valid-empty and granular combined workflow coverage still need evidence/disposition; the general report does not independently attest every action. |
| 3 | Native anonymous preflight and protected result/cancel/delete/download | **Partial.** Current-origin native still-preview CORS passed; prior native protected operations exist on earlier origins. Current-candidate protected-operation coverage remains unresolved, not implied by preview or an Origin-header probe. |
| 4 | Visitor isolation, file-route denial, deletion/cleanup/expiry | **Partial.** Retained real isolation/deletion/image retention and local video cleanup/cancellation/accelerated expiry. Hosted active-video cancellation and video-specific thirty-minute expiry remain unverified; disposition current deployed coverage against the retained shared-code evidence. |
| 5 | Limits, global concurrency, queue/rate controls, representative resources | **Partial.** Local 1080p boundary checks, unchanged other ceilings, one replica and historical 300/600-frame 720p workloads. 1080p resource/maximum-workload behavior is unmeasured; a short successful clip is not that benchmark. |
| 6 | Useful capacity/quota/cold-start/decoding/restart behavior | **Partial; unexercised states declared.** Contract/UI evidence, historical failures, deployed reset-message code and current corrupt-image handling exist. Current live reset/quota/busy/cold-start/restart cases were not all exercised; the issue permits explicitly recording safely unexercised states, not claiming passes. |
| 7 | Deployed desktop/mobile/keyboard/accessibility workflow | **Partial.** Current empty/preview layouts/focus/settings/static downloads plus prior complete result/state keyboard evidence. Current complete live-result/keyboard coverage needs reconciliation; no owner keyboard test is invented. |
| 8 | Unchanged digests, deployed models/runtime, rights, credential safety, free resources | **Partial + existing owner rights exception.** Pins/hash enforcement, fresh local hashes, scoped source/artifact/log checks, preserved notices and Free/ZeroGPU metadata. Fresh installed-runtime/running-model inventory is incomplete; licensing remains owner exception/unverified, not legal clearance or a renewed hold. |
| 9 | Reproducible runtime/setup/pinned model/configuration/deployment instructions | **Covered.** Runbook records supported runtimes/dependencies, pinned detector and hashes, public configuration/secret placement, free limits, agreed checks and deployment/rollback. Supported manual deployment does not require a Netlify Git build. |
| 10 | Applicable suite/review, distinct outcomes, URLs and honest blockers | **Approved subset/reviews recorded; overall partial.** Source `e719d8a`: **39 passed / 0 failed / 0 runner-skipped**, **12 policy-deferred** of 51; build/typechecks and fixed-baseline Standards/Spec reviews recorded. Not a fresh or full 51-method pass; deferred checks and required gates remain explicit. |

## Remaining decisions, without new quota use

1. **#7 runtime/model inventory:** if the owner already downloaded the successful
   run's JSON, request only **`runtime` and `models.*.sha256`**. Do not request the
   full report, detections, filename, job ID/key, media or training materials.
   Relate it to the candidate/backend if known, and label it owner-supplied rather
   than independent runtime introspection. If unavailable, retain the gap; no new
   inference job is implicitly authorized.
2. **#5 / #7 technical evidence:** resolve the partial subchecks using existing
   evidence where valid. Any remaining required check needs explicitly scoped
   authorization or an explicit owner revision/exception, labelled as such rather
   than a test pass. No new inference, hosted video/lifecycle test, restart or
   safeguard waiver is authorized by reconciliation. Default: keep open.
3. **#7 production:** only after required gates are resolved or explicitly
   dispositioned, obtain separate production/hostname approval. Promote the same
   immutable bytes, add the exact approved production origin and perform agreed
   non-inference production checks. No promotion or rename occurred here.

No new feature/code defect is asserted. Do not add Git-build, accuracy/FPS/SLA,
exhaustive physical-device/screen-reader or private-training-disclosure gates that
were not agreed. The owner-directed licensing continuation remains in force;
preserve attribution and record compliance as unverified.

## Ticket status

- **#5:** owner final video PASS recorded; criteria 5/8 and combined verification
  criterion 9 remain partial. No automatic closure or repeat GPU request.
- **#6:** eight criteria evidenced; mixed rights criterion remains owner
  exception/unverified. Formal closeout remains open, not renewed licensing work.
- **#7:** criterion 9 covered; other combined criteria remain partial or await
  production. Approved tests/reviews are recorded, not erased or overstated.
- **#1:** parent stays open pending child closeout.

## Reconciliation checks and review

- Four changed documents passed local file-link and scoped credential-pattern
  checks; all ten criterion rows and distinct test accounting were checked.
  `git diff --check` passed. Application, tests, models and deploy config unchanged.
- Independent read-only review of candidate **`aedc0a6`**, full three-dot diff from
  owner-approved baseline **`cea69ae7f60c84ad8532eca803510283473fc6d2`**:
  **Standards 0 actionable findings; Spec 0 actionable findings**, no worst finding
  on either axis. Both preserved the original #7 criteria and evidence boundaries.
- No suite rerun, inference, live application check or deployment ran for these
  documentation checks/reviews. Their scope does not establish release acceptance.
