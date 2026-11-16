# Release checklist — issues #5, #6, and #7

Updated 2026-11-16. Public release is **not approved**. This checklist separates
implementation, prior evidence, the owner's checks, and remaining release gates.

## Current owner instructions

- **Do not run video tests or video inference.** The owner reserves the final
  video test until the remaining preparation is finished, to conserve HF quota.
  This includes hosted/browser/diagnostic video checks and, conservatively, local
  video tests. Do not run unfiltered test discovery that includes them. Earlier
  test commands/evidence are historical, not authorization to rerun them.
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
- Pushing source, updating the existing Space, and publishing/promoting Netlify
  deployments still require approval. Never enable paid resources or expose HF
  tokens in frontend variables, bundles, URLs, logs, or repositories.

## Current status

| Item | Evidence / status | Ticket |
| --- | --- | --- |
| Images and exports | Previously implemented/verified; owner reports the new local developer image workflow works. This is user-reported, not a fresh agent-run test or independent quota-accounting measurement. | #3 / #4 (closed), #7 integration |
| Short-video implementation | Implemented; prior hosted 300/600-frame evidence exists. Fresh hosted active cancellation and video-specific thirty-minute retention remain unverified. Final new video check is owner-only and deferred. | #5 |
| Compare showcase | Implemented/reviewed; photo permission/attribution documented. Owner removed the licensing workflow hold; compliance remains unverified, not a passed check. | #6 |
| Quota reset messages and developer adapter | Committed as `839f4b8`; local HTTP/browser checks passed. Public reset messages need the backend update. No automatic fallback to cached WRITE credentials. | #6 follow-up / #7 |
| Public Netlify release | Not approved or completed. Local/staged evidence is not deployed-origin evidence. | #7 |

Acceptance/checklist reconciliation is complete as of 2026-11-16: #5 has six
evidenced and three partial/deferred criteria; #6 has eight evidenced and one
owner exception/unverified criterion. Both remain open; #7 is not release-accepted.
See [the criterion-by-criterion reconciliation](evidence/acceptance-reconciliation.md).

Prior evidence: [video](evidence/issue-5-verification.md),
[showcase](evidence/issue-6-verification.md), and
[quota/developer access](evidence/developer-quota-verification.md).

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

## Remaining work, in order

1. **Release candidate preparation — #7.** Finish reproducible runtime,
   dependency, pinned-checkpoint, nonsecret configuration, and deployment/rollback
   instructions. Check frontend artifacts for credentials, keep the explicit
   backend file mapping, and record exact source/model/runtime revisions. Run only
   permitted non-video/non-inference checks and required review after changes.
2. **Approved preview and backend update — #7.** After permission, update the
   free Space's quota-message code and prepare Netlify preview configuration.
   Check HTTPS, root/detector refresh, navigation, desktop/mobile/keyboard UI,
   headers and image preview without inference. These checks alone cannot prove
   authenticated/anonymous GPU execution or the full deployed job lifecycle.
3. **Owner's final video test — #5 / #7.** After preparation, the owner tests a
   representative accepted clip against the release candidate, checking actual
   playback, MP4/JSON/CSV downloads, and deletion. Record outcome and exact build;
   do not silently turn one run into a cancellation/retention/load-test suite.
   Any additional quota-consuming verification needs explicit authorization.
4. **Production promotion and closeout — #7.** Once remaining technical checks
   are satisfied, obtain approval and promote the same candidate. Retain the
   owner's licensing decision and unverified compliance in the closeout; do not
   turn it into a legal-clearance claim. Verify deployed
   routing/UI/headers without new inference. Record actual URLs, passed/skipped/
   deferred checks, isolation/lifecycle/resource evidence, and any remaining
   limitations. A pre-release local or preview run is not automatically proof of
   all production-origin safeguards; unresolved required criteria keep #7 open.

## Safe checks during the video hold

For code changes, select individual non-video tests after inspecting their scope;
do not run the complete suite or any opt-in hosted/model/diagnostic suite. Existing
image-API and developer-adapter contract tests use fake external compute/HTTP,
not hosted inference. Type checks, frontend build, static inspection, and document
checks do not themselves require a video job. Historical test totals must remain
dated; a narrower new check is not a fresh full-suite pass.
