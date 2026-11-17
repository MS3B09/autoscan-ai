# Release checklist — issues #5, #6, and #7

Updated 2026-11-17. **Live:** https://autoscan-ai.netlify.app/ and
https://autoscan-ai.netlify.app/detect. **#5/#6/#7 and parent #1 are closed.**
Release accepted with explicit owner-directed unverified portions, **not a claim
that every original acceptance checkbox independently passed**.

**Publication and accepted exceptions:** [final-release evidence](evidence/issue-7-final-release.md).
The owner declined further checks: **"I did enough tests myself, no need for more."**
That final decision resolves the earlier release hold without additional agent
tests. Saved exports validate 1080p/runtime/hashes and matching CSV; the same
reviewed deploy is published on Free hosting with the exact production origin.

## Current owner instructions

- **No further tests.** The owner declined the specifically proposed hosted
  acceptance run and directed release/closeout based on their own testing.
  Remaining lifecycle/resource/complete-production-workflow gaps stay explicitly
  **owner-accepted / unverified**; do not convert them into passes or demand reruns.
  The earlier approved local CPU codec/API checks remain retained evidence only.
- The 1080p change and local-only evidence are tracked in
  [issue-5-1080p.md](evidence/issue-5-1080p.md); earlier 720p hosted runs are not
  upgraded to 1080p capacity evidence.
- **Owner final video check passed (reported 2026-11-16).** The owner reports
  successful video testing after the 1080p draft handoff. This is user-reported
  workflow evidence, not independent resource/lifecycle measurements. Separate
  later owner instructions authorize publication/closeout, not agent reruns.
- Do not replace the final owner video check with an agent-run image/video job,
  consume quota just to exercise an error, or retry submissions automatically.
- After each upcoming task, report remaining work in the conversation with its
  ticket number. Keep unverified checks distinct from failures and passes.
- MS3B09 confirms training both custom models on the README-linked datasets,
  starting from `yolov8n.pt`, and permits public app code/model files. **Training
  materials stay private:** do not request or publish notebooks/configuration.
  These factual/publication-scope questions are answered; do not ask repeatedly.
  This is not approval to change licenses or push/deploy immediately.
- **Licensing workflow hold removed by owner (2026-11-16).** After reviewing the
  research and citing the original TeamX repository/Streamlit app, MS3B09
  instructed proceeding without the internal licensing block. Record this as
  **owner-directed continuation, compliance unverified**, not a passed legal check
  or an Ultralytics exception. Preserve notices and research; do not repeatedly
  block preparation on the same already-disclosed issue.
- **Earlier limited deployment approval (2026-11-16):** the owner approved the backend
  quota-message update and Netlify draft, then separately approved pushing the
  reviewed commits to GitHub. Backend update, source push and Netlify draft are
   complete; only permitted non-inference draft checks ran. That earlier approval
   did not include production. The 2026-11-17 request now covers final free
   publication once gates are resolved, not a paid change or an implicit lifting
   of the prior inference/hosted-video hold.
  Never expose HF tokens in frontend variables, bundles, URLs, logs or repositories.

## Current status

| Item | Evidence / status | Ticket |
| --- | --- | --- |
| Images and exports | Previously implemented/verified; owner reports the new local developer image workflow works. This is user-reported, not a fresh agent-run test or independent quota-accounting measurement. | #3 / #4 (closed), #7 integration |
| Short-video implementation | Closed with owner final video PASS, saved 87-frame 1080p export validation and accepted unverified lifecycle/resource portions. No extra inference/testing for publication. | #5 (closed) / #7 |
| Compare showcase | Closed as implementation complete under the owner's closeout request, with existing licensing exception/unverified. Eight technical criteria evidenced; rights criterion remains unchecked/not independently passed. | #6 (closed) |
| Quota reset messages and developer adapter | Existing quota-message API preserved in backend `d160158`; health/still-image preview passed without inference. Live quota reset response unexercised. No automatic fallback to cached WRITE credentials. | #6 follow-up / #7 |
| Public Netlify release | Published `6afb4f606cabececacad1489` at the requested hostname, 2026-11-17T03:01:56.633Z. Free/Git unlinked; production routes 200/exact reviewed HTML/security headers; detector opens. Accepted exceptions remain explicit. | #7 (closed) |
| Local release preparation | Runbook/Node pin, latest approved 39-test local suite (12 policy-deferred), typechecks/build and scoped artifact/history secret checks recorded; fixed-baseline reviews completed. No fresh suite rerun for reconciliation. | #7 |
| Source / deployed bytes | Reviewed source `e719d8a`; same immutable deploy promoted, no rebuild or replacement assets. Later repository commits record documentation/evidence only. | #5 / #7 |
| Final gate reconciliation | Covered evidence, owner-reported results, deferred tests and accepted unverified subchecks remain distinct. No all-checks-passed or legal-clearance claim. Parent and children closed under explicit owner direction. | #1 / #5 / #6 / #7 (closed) |

Final disposition: #5 retains six evidenced criteria and three mixed criteria
with accepted unverified portions; #6 retains eight evidenced and one rights
exception/unverified criterion. #7 is published/closed with its explicit
verification exceptions; #1 is closed. No unchecked criterion is silently relabeled
as an independent pass.
See [the criterion-by-criterion reconciliation](evidence/acceptance-reconciliation.md).

**Historical post-owner-pass matrix:**
[issue-7-release-gates.md](evidence/issue-7-release-gates.md). Earlier snapshots
retain historical results; setup, draft deployment and the owner video check are
no longer pending tasks.

Prior evidence: [video](evidence/issue-5-verification.md),
[showcase](evidence/issue-6-verification.md), and
[quota/developer access](evidence/developer-quota-verification.md).

Current #7 setup/deployment/rollback instructions:
[release-runbook.md](release-runbook.md). Fresh safe-check results, failed install
attempts/recovery, artifact hashes, fixed review baseline and remaining gates:
[issue-7-preparation.md](evidence/issue-7-preparation.md). Historical full-suite
results above are not a new full-suite run.

Later approved deployment/source-push results and the Netlify blocker:
[issue-7-backend-update.md](evidence/issue-7-backend-update.md). Earlier statements
that no deployment/push had occurred are historical, not the current status.

The Netlify connection blocker is now resolved. Exact draft URLs, artifact hashes,
origin wiring, non-inference browser checks and owner handoff:
[1080p handoff](evidence/issue-5-1080p.md). That preparation evidence precedes the
site rename and production promotion; the current user URL is
**https://autoscan-ai.netlify.app/**. Git remains unlinked to avoid automatic
publication of future pushes.

## Licensing disposition — #6 / #7

Research and attribution updates are complete. The original datasets declare
logo CC BY 4.0 and plate CC0/Public Domain; photo permission is documented. The
owner confirms training from the linked datasets and `yolov8n.pt`, permits public
app/model files, and keeps training materials private. The official-source search
found no disclosure exception for a free portfolio demo. The owner nevertheless
instructed removal of the internal licensing hold, citing the prior application.
That decision changes workflow priority, not the license terms or research facts.

Record the rights criterion as **owner-directed exception / unverified**, not
independently passed. Do not change the root license, buy permission, publish
private materials, or claim an older working deployment proves legal clearance.
See [owner decision and sources](evidence/release-licensing.md#owner-directed-workflow-decision--2026-11-16)
and [the official-source findings](evidence/ultralytics-private-training.md).

## Final sequence — completed

1. **#7 preparation/draft:** runbook, selected local checks, source/artifact review,
   Free candidate and exact-origin wiring recorded.
2. **#5 owner video:** reported PASS; saved JSON/CSV supplied and validated locally,
   with runtime inventory and all trusted hashes matching. No private data published.
3. **#5/#7 disposition:** owner explicitly declined the proposed extra tests.
   Remaining independent production workflows/isolation, video cancellation/expiry,
   1080p maximum resources and complete live-result keyboard verification stay
   accepted/unverified. Safely unexercised quota/busy/cold-start states remain so.
4. **#7 publication:** same deploy promoted at the exact requested HTTPS hostname;
   publication metadata/routes/HTML/headers and navigation read back, no uploads,
   previews, inference, suite rerun or additional test jobs.
5. **#5/#6/#7/#1 closeout:** comments explain evidence versus owner exceptions;
   closed states read back. There is no pending task to demand further owner tests,
   source media, runtime exports or private training materials for this release.

## Safe checks during the video hold

For the 1080p change, the owner additionally approved the local
`test_video_api.py` codec/API suite with substituted external compute. All other
checks stay explicitly selected after inspecting scope; do not run unfiltered
discovery or opt-in hosted/model/diagnostic suites. Existing
image-API and developer-adapter contract tests use fake external compute/HTTP,
not hosted inference. Type checks, frontend build, static inspection, and document
checks do not themselves require a video job. Historical test totals must remain
dated; a narrower new check is not a fresh full-suite pass.
