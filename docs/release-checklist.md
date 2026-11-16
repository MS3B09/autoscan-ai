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
- MS3B09 confirms training both custom models. **Training notebooks/configuration
  will not be shared:** do not request or publish them, assume a new checkpoint
  license, or treat trainer identity as clearing upstream rights. Assess a
  compatible source/licensing arrangement before clearing the release gate.
- Pushing source, updating the existing Space, and publishing/promoting Netlify
  deployments still require approval. Never enable paid resources or expose HF
  tokens in frontend variables, bundles, URLs, logs, or repositories.

## Current status

| Item | Evidence / status | Ticket |
| --- | --- | --- |
| Images and exports | Previously implemented/verified; owner reports the new local developer image workflow works. This is user-reported, not a fresh agent-run test or independent quota-accounting measurement. | #3 / #4 (closed), #7 integration |
| Short-video implementation | Implemented; prior hosted 300/600-frame evidence exists. Fresh hosted active cancellation and video-specific thirty-minute retention remain unverified. Final new video check is owner-only and deferred. | #5 |
| Compare showcase | Implemented and reviewed; existing photo permission/attribution is documented. Model/dataset rights remain a release gate. | #6 |
| Quota reset messages and developer adapter | Committed as `839f4b8`; local HTTP/browser checks passed. Public reset messages need the backend update. No automatic fallback to cached WRITE credentials. | #6 follow-up / #7 |
| Public Netlify release | Not approved or completed. Local/staged evidence is not deployed-origin evidence. | #7 |

Prior evidence: [video](evidence/issue-5-verification.md),
[showcase](evidence/issue-6-verification.md), and
[quota/developer access](evidence/developer-quota-verification.md).

## Remaining work, in order

1. **Licensing/attribution — #6, blocking #7.** Evidence audit complete: original
   dataset declarations are logo CC BY 4.0 and plate CC0/Public Domain; photo
   permission is reconfirmed. MS3B09 confirms training both custom models but will
   not share notebooks/configuration. Resolve the remaining checkpoint/training-
   chain questions and an owner-approved compliant
   source/license arrangement. Do not infer permission from public downloads or
   the repository's Apache-2.0 file. Do not change licenses or buy permission
   without approval. See [the licensing evidence](evidence/release-licensing.md).
2. **Ticket/evidence reconciliation — #5 / #6 / #7, parent #1.** Reconcile
   completed implementation against acceptance criteria and carry forward real
   verification gaps. Record owner-reported image success without claiming an
   independently verified quota debit. Do not close incomplete release gates.
3. **Release candidate preparation — #7.** Finish reproducible runtime,
   dependency, pinned-checkpoint, nonsecret configuration, and deployment/rollback
   instructions. Check frontend artifacts for credentials, keep the explicit
   backend file mapping, and record exact source/model/runtime revisions. Run only
   permitted non-video/non-inference checks and required review after changes.
4. **Approved preview and backend update — #7.** After permission, update the
   free Space's quota-message code and prepare Netlify preview configuration.
   Check HTTPS, root/detector refresh, navigation, desktop/mobile/keyboard UI,
   headers and image preview without inference. These checks alone cannot prove
   authenticated/anonymous GPU execution or the full deployed job lifecycle.
5. **Owner's final video test — #5 / #7.** After preparation, the owner tests a
   representative accepted clip against the release candidate, checking actual
   playback, MP4/JSON/CSV downloads, and deletion. Record outcome and exact build;
   do not silently turn one run into a cancellation/retention/load-test suite.
   Any additional quota-consuming verification needs explicit authorization.
6. **Production promotion and closeout — #7.** Once rights and required checks
   are satisfied, obtain approval and promote the same candidate. Verify deployed
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
