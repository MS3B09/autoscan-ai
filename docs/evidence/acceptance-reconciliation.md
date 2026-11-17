# Acceptance reconciliation — #1 / #5 / #6 / #7

> **Historical snapshot with later addenda.** Use
> [final publication](issue-7-final-release.md) for the live URL, closed tickets and
> owner's no-more-tests/accepted-unverified disposition. The earlier
> [release-gate matrix](issue-7-release-gates.md) records the pre-publication
> post-owner-pass decisions. Pending setup/deployment/owner-check wording
> below describes earlier stages, not current blockers. The later local CPU-only
> codec/API exception supersedes the earlier blanket local-video test hold.

Date: **2026-11-16**. Documentation/tracker reconciliation only; no application,
browser, model, image or video tests were run. No inference, push or deployment.
Baseline: local implementation through `73488a5`; earlier evidence retains its
own source/deployed revisions and dates. This is not fresh release verification.

**Later #7 preparation:** [issue-7-preparation.md](issue-7-preparation.md) records
the runbook, Node pin and fresh permitted local checks against `cea69ae`.
Those results supersede the "next preparation task" wording below, not the
historical test accounting or any deployed-origin acceptance gate. No #7
checkbox becomes fully accepted from local preparation alone.

**Later approved deployment step:** [backend-update evidence](issue-7-backend-update.md)
records the quota-message API update and reviewed-source GitHub push. Netlify
dashboard access is blocked; no draft, production URL or deployed-origin pass
exists yet. No #7 checkbox is newly accepted by those partial results.

**Current draft step:** [issue-7-netlify-draft.md](issue-7-netlify-draft.md) supersedes
the earlier no-draft/access-blocker status. A Free-plan immutable preview now has
verified routing/headers/layout/keyboard and native anonymous still-preview CORS.
No live inference, video, production or complete lifecycle criterion is newly
accepted from those scoped checks.

**Latest owner-requested change:** [1080p handoff](issue-5-1080p.md) records the
resolution-only scope override, approved local CPU codec/API tests, new backend
and immutable draft. Earlier hosted 720p evidence is not a 1080p capacity pass;
the final hosted clip check remains owner-only and production remains unapproved.

**Owner report after the 1080p handoff:** the owner now reports the final video
check **passed**. See [the recorded report](issue-5-1080p.md#owners-final-video-report--2026-11-16).
This supersedes the owner-check-pending status, not separate lifecycle/resource/
isolation gaps, deferred tests or production approval. No new agent checks ran.

## How to read the tracker

- **Evidenced:** implemented and supported by the cited retained checks; may be
  checked on the implementation ticket. This does not imply a new hosted pass.
- **Partial / deferred:** implemented, but the combined criterion has an explicit
  remaining verification gap; leave its checkbox unchecked.
- **Owner exception / unverified:** the owner removed the licensing workflow hold.
  This is neither a legal pass nor a request for more private training files.
- **Pending release:** needs #7 preparation/deployment-origin evidence; not passed
  merely because a local workflow or the separate hosted API worked.

**No video testing or inference.** The owner reserves the final video test after
preparation. Do not run unfiltered discovery, diagnostic `/validate`, or even
local video tests to fill the gaps below. The hold also forbids disguising new
quota-consuming checks as checklist reconciliation. Do not invent results or
expand the owner's final run into more jobs without approval.

## Parent #1: correct the implementation status

| Slice | Current disposition |
| --- | --- |
| #2 backend feasibility | Closed previously; retain existing scope/limitations. |
| #3 image workspace / #4 exports | Closed previously. Owner additionally reports the new developer image workflow works; no independent quota-debit measurement is claimed. |
| #5 short videos | Implemented, with prior real 300/600-frame evidence. Acceptance remains open for deferred owner/lifecycle checks below; not "still to implement." |
| #6 Compare showcase | Implemented/reviewed. Eight criteria evidenced; the mixed rights criterion remains an owner exception/unverified, not a workflow blocker. Formal closeout remains open; no further feature coding identified by this reconciliation. |
| #7 public release | Open. No Netlify production/deployed-origin release approval; backend quota-message update remains undeployed. |

Parent #1 remains open. Its older November 14 progress entries are history,
superseded by the current status, not rewritten as if new checks happened then.

## #5: short-video acceptance (original criterion order)

Primary evidence: [issue-5-verification.md](issue-5-verification.md), particularly
Local tests, Real hosted anonymous browser run, Final hosted 600-frame gate,
Independent review, and Remaining verification limits.

| # | Agreed criterion, abbreviated | Disposition / evidence |
| --- | --- | --- |
| 1 | Six containers; actual decoded 20 MB / 10 s / 720p / 600-frame ceilings | **Evidenced.** Prior nine local HTTP/real-codec methods cover containers, boundaries/mismatch and truncation. Hosted 600-frame/720p output passed; this does not claim every container was freshly hosted. |
| 2 | Explicit submission, selected types, trusted checkpoints, confidence 25–100/default 40 | **Evidenced.** Existing contract checks and native hosted browser preview-without-submit; trusted identities/settings retained in results. |
| 3 | Every accepted frame, no truncation/subsampling/stretching/partial success | **Evidenced.** Prior 300/300 and 600/600 processing/output checks, source timing, and AVI nested-length regressions. The 600-frame fixture duplicated source frames during preparation; the application did not sample. |
| 4 | Real progress and meaningful timing/codec/inference/quota/busy failures | **Evidenced at implementation/contract scope.** Real frame progress and sanitized failure/timeout checks are recorded; all production-origin failure states are not claimed exercised. |
| 5 | Cancellation stops work safely and cleans partial artifacts | **Partial.** Prior local HTTP/thread/file evidence covers queued/active cancellation; fresh hosted active-video cancellation remains unverified. No new run scheduled. |
| 6 | Silent coherent MP4 actually plays in browser | **Evidenced.** Native hosted 300-frame browser playback/downloads; actual 600-frame hosted MP4 also reached playback end via local-file replay. Replay is not a second hosted browser upload. |
| 7 | Complete frame-level JSON/CSV with indices/timestamps, not unique tracks | **Evidenced.** Prior 2,375/4,719 observation/CSV-row matches, source timing and VFR/local empty-export coverage. |
| 8 | Private operations, cleanup, 30-minute expiry, Delete now, bounded work | **Partial.** Hosted isolation/deletion and local cleanup/accelerated expiry/bounds exist. Actual 30-minute image evidence is shared-lifecycle evidence, not a fresh 30-minute video wait. |
| 9 | Representative real clips, boundaries, failures/cancellation, browser/mobile exports | **Partial.** Substantial real hosted/local/browser evidence exists; the lifecycle gaps above and owner's final candidate video check remain deferred. No physical-device/browser matrix is claimed. |

Tracker: **6/9 evidenced; 3/9 partial/deferred**. Keep #5 open. The final owner
run checks the agreed candidate workflow; it does not automatically establish
active cancellation, a 30-minute wait, or every #7 release criterion. Any gap
not safely exercised needs an explicit evidence disposition, not silent passing.

## #6: showcase acceptance (original criterion order)

Primary evidence: [issue-6-verification.md](issue-6-verification.md), including
Real sample and rights, Browser boundary and checks, Visual verification,
Completion addendum, and Independent follow-up. Later user-requested quota/access
work is separately recorded in [developer-quota-verification.md](developer-quota-verification.md).

| # | Agreed criterion, abbreviated | Disposition / evidence |
| --- | --- | --- |
| 1 | Root showcase, working detector navigation, direct-route refresh setup | **Evidenced locally/configured.** `/`, `/detect`, `/detect/` and preview refresh checks; Netlify rewrites configured. Actual deployed Netlify routing remains #7. |
| 2 | Approved Compare hierarchy/palette/type, Hallmark/Impeccable rendered checks | **Evidenced with documented photo exception.** Render/manual review and mechanical/static checks recorded. Automatic Impeccable photo matching stayed blocked under the authorized replacement; it is not called a machine pass. |
| 3 | Actual validated before/after outputs and real exports, not comp values | **Evidenced.** Four detections and PNG/JSON/CSV from one anonymous real job, preserved byte-for-byte with false positives explained. |
| 4 | Image/video entry actions reach the implemented workflow | **Evidenced.** Prior browser navigation/native-picker entry checks; no fictitious file transfer or new inference implied. |
| 5 | Honest detection scope, no deferred OCR/webcam/tracking or invented metrics | **Evidenced.** Recorded scope/copy review and real-example caveats. |
| 6 | Credits/datasets/24 brands plus photo/model rights | **Owner exception / unverified for model licensing.** Credits, dataset notices, photo permission and unchanged watermark handling are evidenced. Owner removed the licensing hold; do not check the combined criterion as independently passed. |
| 7 | Semantic interactive components and consistent detector system | **Evidenced.** Shared system, keyboard controls/downloads and retained workflow checks; not a flattened mockup. |
| 8 | Desktop/mobile reference comparison, focus/contrast/labels/status/states | **Evidenced locally.** Eleven showcase widths, boundary-width navigation fix, measured contrast and simulated detector states. Physical devices/screen-reader sessions and deployed origin remain unverified. |
| 9 | Preserve image/exports and video slice without unasked signup/decorative work | **Evidenced.** Prior full suites/reviews and scoped UI changes; quota/access addition was separately user-requested. No new video check is authorized by that history. |

Tracker: **8/9 evidenced; 1 owner exception/unverified**. Keep #6 open for formal
closeout rather than implicitly closing it from a workflow override. The owner
decision is [recorded here](release-licensing.md#owner-directed-workflow-decision--2026-11-16);
do not reopen licensing as an internal preparation blocker.

## #7: release evidence handoff (original criterion order)

No #7 checkbox is fully accepted by this reconciliation. Existing evidence is
useful input to release verification, not proof of a deployed Netlify product.

| # | Release criterion | Remaining disposition |
| --- | --- | --- |
| 1 | HTTPS Netlify showcase/detector, refresh, free backend, preserve legacy app | **Pending.** Configuration/legacy preservation exist; approved Netlify deployment, actual URLs and origin wiring remain. |
| 2 | Deployed image/video workflow, selections, exports, empty result, MP4 playback | **Pending.** Prior hosted/local evidence plus user-reported image success; final candidate video check is owner-only after preparation. |
| 3 | Native anonymous cross-origin preflight and protected operations | **Pending deployed origin.** Prior local-origin native hosted browser success exists; it is not Netlify-origin proof. |
| 4 | Cross-visitor isolation, framework-route denial, cleanup/deletion/expiry | **Partial historical evidence.** Prior image retention, video isolation/deletion and contract checks; deployed configuration and unexercised video lifecycle cases need explicit disposition. |
| 5 | Limits, globally bounded work, rate controls, representative resource behavior | **Partial historical evidence.** Local boundary/admission tests and real 300/600-frame workloads exist. Final deployment/resource configuration and any unmeasured behavior must be distinguished; no new load/video job authorized. |
| 6 | Useful busy/quota/cold-start/decoding/restart errors without fake success | **Partial.** Contract/UI regressions and historical failures exist; quota-reset change needs backend deployment. Record safely unexercised live states as unverified. |
| 7 | Deployed visual/mobile/keyboard/accessibility workflow | **Pending deployed origin.** Existing local/preview visual evidence is retained, not a fresh deployed pass. |
| 8 | Original digests/runtime, notices, no exposed tokens, no paid resources | **Partial.** Existing pins/notices/auth safeguards; owner licensing exception recorded. Final revision/model/runtime inventory, artifact secret checks and free deployment configuration remain. |
| 9 | Reproducible runtime/setup/pinned model/configuration/deployment instructions | **Partial; next preparation task.** Existing slice docs are inputs; consolidate supported setup, secret placement, free-tier limits and deployment/rollback instructions. |
| 10 | Applicable tests/review, exact URLs, passed/failed/skipped and honest gates | **Partial.** Most recent retained suite: 50 total, 40 passed/10 skipped; build/mypy and fixed-baseline reviews passed before the hold. No fresh full-suite pass or release review claimed here. Run only permitted checks for the final candidate; deferred checks remain explicit. |

## Source and test accounting

- Video implementation/fixes: `24aa19a`, `a3be322`; latest recorded hosted service
  revision: `dbafd5210c59c719fdce59556d400be4f870859d`. Not freshly queried here.
- Showcase/navigation/evidence: `fe87aea`, `8bac723`, `1429017`.
- Quota reset/local developer adapter: `839f4b8`; new public backend error-message
  deployment remains pending. Owner-reported image success is separate evidence.
- Licensing/owner-policy documentation through `73488a5` changes workflow status,
  not historical test outcomes. Training materials remain private.
- Current validation: static document/link/checklist checks only. No browser,
  runtime/media tests or inference. Existing unrelated untracked tooling is untouched.

Next: #7 release-candidate instructions and permitted non-inference checks, then
approved backend/Netlify preview work, the owner's final video check (#5/#7), and
approved production promotion/closeout. See [the checklist](../release-checklist.md).

Tracker bodies updated and read back: [parent #1](https://github.com/MS3B09/autoscan-ai/issues/1),
[video #5](https://github.com/MS3B09/autoscan-ai/issues/5),
[showcase #6](https://github.com/MS3B09/autoscan-ai/issues/6), and
[release #7](https://github.com/MS3B09/autoscan-ai/issues/7). Original acceptance
wording was preserved; only supported checkboxes and current-status notes changed.
