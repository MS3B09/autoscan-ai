# Release checklist — issues #5, #6, and #7

Updated 2026-11-17. The owner now requests the final **free production release** at
**https://autoscan-ai.netlify.app/** and ticket closeout, subject to unresolved
required checks. Production is **not published**. This checklist separates
implementation, prior evidence, the owner's checks, and remaining release gates.

**Latest work and blocker:** [final-release evidence](evidence/issue-7-final-release.md).
Saved owner exports validate 1080p/runtime/hashes and matching CSV; hostname is
assigned, exact origins configured. Explicit permission to lift the prior
inference/hosted-video hold is needed to complete the remaining hosted checks;
neither that permission nor a waiver is inferred from the general release request.

## Current owner instructions

- **No model inference or hosted/browser/diagnostic video tests** until the owner
  explicitly lifts that prior hold for the remaining hosted acceptance checks.
  The reserved owner clip check has passed. For the requested
  **1080p update**, the owner explicitly approved **local CPU-only codec/API video
  tests** and updating the backend/draft. This narrowly lifts the earlier local
  video-test hold, not the inference/hosted-video/production restrictions. Keep
  unfiltered discovery and opt-in hosted/model/diagnostic suites excluded.
- The 1080p change and local-only evidence are tracked in
  [issue-5-1080p.md](evidence/issue-5-1080p.md); earlier 720p hosted runs are not
  upgraded to 1080p capacity evidence.
- **Owner final video check passed (reported 2026-11-16).** The owner reports
  successful video testing after the 1080p draft handoff. This is user-reported
  workflow evidence, not independent resource/lifecycle measurements or approval
  for agent reruns, production promotion or automatic ticket closure.
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
| Short-video implementation | 1080p implemented; owner's final video check reported PASS after the current draft handoff. No agent rerun. Earlier hosted capacity evidence remains 720p-only; maximum 1080p resource behavior, hosted active cancellation and video-specific thirty-minute retention remain unverified. | #5 / #7 |
| Compare showcase | Implementation complete; owner now requests formal closeout with the existing licensing exception/unverified. Eight technical criteria evidenced; rights criterion is not independently passed. | #6 |
| Quota reset messages and developer adapter | Existing quota-message API preserved in backend `d160158`; health/still-image preview passed without inference. Live quota reset response unexercised. No automatic fallback to cached WRITE credentials. | #6 follow-up / #7 |
| Public Netlify release | Owner requests final free release. Existing site renamed `autoscan-ai`, production origin wired, same candidate hashes verified; still unpublished while required hosted-check permission/evidence is unresolved. | #7 |
| Local release preparation | Runbook/Node pin, latest approved 39-test local suite (12 policy-deferred), typechecks/build and scoped artifact/history secret checks recorded; fixed-baseline reviews completed. No fresh suite rerun for reconciliation. | #7 |
| Approved source push / Netlify draft | 1080p source `e719d8a` pushed; Free-plan draft `6afb4f606cabececacad1489` ready, no published deploy, Git unlinked. Scoped agent checks passed; owner additionally reports video success. No complete release acceptance. | #5 / #7 |
| Final gate reconciliation | Current matrix records criterion 9 covered, approved subset/reviews for criterion 10, and remaining workflow/lifecycle/resource/runtime evidence plus production/hostname decisions. | #7 |

Acceptance/checklist reconciliation is complete as of 2026-11-16: #5 has six
evidenced and three partial/deferred criteria; #6 has eight evidenced and one
owner exception/unverified criterion. Both remain open; #7 is not release-accepted.
See [the criterion-by-criterion reconciliation](evidence/acceptance-reconciliation.md).

**Current post-owner-pass matrix and next decisions:**
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
[current 1080p handoff](evidence/issue-5-1080p.md). Use that immutable
draft, not the unpromoted production hostname. Git integration remains unlinked
to avoid automatic publication.

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

## Release sequence and next decisions

The preparation/owner-check sequence below is historical. Current action is the
explicit hosted-check authorization described in the latest evidence, followed by
the already-requested production promotion if those checks pass. The hostname
decision and runtime-export request are no longer outstanding.

1. **Local release candidate preparation — #7, completed at approved scope.** Instructions, permitted checks
   and local artifact inspection are recorded in the runbook/evidence above.
   The fixed-baseline Standards/Spec review is recorded, including the corrected
   status-wording finding. Fresh deployed source/model/runtime inventory and final
   uploaded-artifact checks still belong to the approved deployment, not the local
   preparation pass.
2. **Approved preview — #7, completed at permitted scope.** Free-plan draft ready;
   exact origin added, HTTPS/refresh/headers/keyboard/desktop/mobile and native
   still-preview/preflight checks passed without inference. This was a local-build
   file-digest deployment, not a Netlify Git build, full inference workflow or
   production promotion. Remaining job/lifecycle/runtime/resource evidence stays
   explicit in the linked handoff.
3. **Owner's final video test — #5 / #7, reported PASS.** Recorded the owner's
   successful video-check report following the 1080p candidate handoff; no agent
   rerun or independently inspected artifacts. Reconcile remaining acceptance
   evidence without treating this happy-path report as cancellation/retention/
   load-test proof. Additional quota-consuming checks still need approval.
4. **Final evidence reconciliation — #7, report complete; decisions open.** Use
   the current matrix to resolve/disposition partial required subchecks. Existing
   downloaded JSON may supply runtime/model hashes without new inference; request
   only those nonsecret fields if available. No blanket waiver, new testing or
   renewed licensing research is authorized by this task.
5. **Production promotion and closeout — #7.** Once remaining technical checks
   are satisfied, obtain approval and promote the same candidate. Retain the
   owner's licensing decision and unverified compliance in the closeout; do not
   turn it into a legal-clearance claim. Verify deployed
   routing/UI/headers without new inference. Record actual URLs, passed/skipped/
   deferred checks, isolation/lifecycle/resource evidence, and any remaining
   limitations. A pre-release local or preview run is not automatically proof of
   all production-origin safeguards; unresolved required criteria keep #7 open.

## Safe checks during the video hold

For the 1080p change, the owner additionally approved the local
`test_video_api.py` codec/API suite with substituted external compute. All other
checks stay explicitly selected after inspecting scope; do not run unfiltered
discovery or opt-in hosted/model/diagnostic suites. Existing
image-API and developer-adapter contract tests use fake external compute/HTTP,
not hosted inference. Type checks, frontend build, static inspection, and document
checks do not themselves require a video job. Historical test totals must remain
dated; a narrower new check is not a fresh full-suite pass.
