# Release runbook — #7

This is preparation, **not deployment approval**. Follow the owner's current
[release checklist](release-checklist.md): no agent-run inference or video tests,
no push, Space update, Netlify upload/promotion, or paid resources without approval.
The final candidate video check belongs to the owner. Licensing remains an
[owner-directed exception / unverified](evidence/release-licensing.md#owner-directed-workflow-decision--2026-11-16).
Preserve the original Streamlit app, checkpoint bytes, credits and notices.

## Runtime and dependencies

| Component | Reproducible input |
| --- | --- |
| Frontend | Node **24.13.0** (`netlify.toml`), npm **11.6.2**, `web/package-lock.json`; use `npm ci`, not a dependency update |
| Inference Space | Python **3.10.13**, Gradio **6.32.0** in `image_service/space-README.md`; install `image_service/requirements.txt` as the Space root `requirements.txt` |
| System libraries | `validation_space/packages.txt` as Space root `packages.txt`: `libgl1`, `libglib2.0-0`; PyAV provides the media codec interface |
| Lightweight local checks | Python **3.13.12** and the explicitly listed test packages below; this is **not** the hosted inference runtime |

The backend pins Torch 2.8.0, Torchvision 0.23.0, Ultralytics 8.4.189,
NumPy 1.26.4, OpenCV 4.11.0.86, Pillow 11.3.0, dill 0.4.1, psutil 7.2.2,
Gradio 6.32.0, spaces 0.51.3, FastAPI 0.162.5, Starlette 1.7.0,
Uvicorn 0.54.0, AnyIO 4.15.1 and PyAV 17.1.0. The requirements file is
authoritative. Transitive Python packages/platform images are not fully locked:
record actual installed versions from the approved build and revalidate any drift.
Do not install the legacy root Streamlit requirements into this environment.

For an eligible GPU/ZeroGPU environment, provision Python 3.10.13 in a separate
environment, install `python -m pip install -r image_service/requirements.txt`,
and use `python -m image_service.app` from the repository root. **Do not run this
entrypoint during preparation:** import/startup provisions and loads models onto
CUDA. It is not a supported CPU/local-contract-test server. Local full-model
installation was previously blocked by disk space; it has not been revalidated.

## Local frontend (no inference needed)

From the repository root, using the Node/npm versions above:

```powershell
cd web
npm ci
$env:VITE_AUTOSCAN_API = 'https://ms3b09-autoscan-ai-images.hf.space'
npm run typecheck
npm run build
npm run preview -- --port 4173 --strictPort
```

Open `http://127.0.0.1:4173/` and `/detect`. This serves the production assets;
it does not emulate Netlify routing/headers. Merely opening the page does not run
inference. An image selection calls validation/preview; **Detect** submits a job
and consumes quota, so do not press it during preparation. Do not select videos.
For hot reload use `npm run dev -- --port 5173 --strictPort` instead of preview.

## Configuration and credentials

| Setting | Placement / value |
| --- | --- |
| `VITE_AUTOSCAN_API` | Public **build-time** frontend variable: `https://ms3b09-autoscan-ai-images.hf.space`, no trailing path, token, query or credentials. Set in the terminal for local builds or Netlify's build environment for approved hosted builds. Changing it requires a rebuild. |
| `AUTOSCAN_ORIGINS` | Space **variable**, comma-separated exact frontend origins (scheme + host + optional port), no paths/trailing slash/whitespace/wildcard. Include the actual candidate URL and eventual production origin. For local preview add `http://127.0.0.1:4173`; default development origins are only port 5173. |
| HF deployment credential | Local interactive `hf auth login` / protected tooling only. Never a frontend variable or a Space runtime secret for this public model source. Keep the existing WRITE credential separate from optional developer READ access. |
| Netlify credential | Interactive CLI login or protected local tooling only; never `VITE_*`, command arguments containing token values, source, or published assets. |

No HF owner token is required by the public backend at runtime. All `VITE_*`
values are public; do not put secrets in any of them or any `.env` file intended
for publication. Never deploy `scripts/dev_api.py`, use its loopback URL in a
public build, or silently borrow cached WRITE credentials for inference.
Optional local developer access is described in
[authenticated-image-tests.md](authenticated-image-tests.md), not required for release.

CORS is not authentication. Status, downloads, cancel and delete use the separate
in-memory job capability in `Authorization`, never a URL or owner token. Do not
save browser storage, HARs, logs or screenshots containing capabilities/media as
public evidence. Sanitize retained evidence and disable application access logs.

## Pinned checkpoints (download/hash only, no deserialization)

The existing `models/logo.pt` and `models/plate.pt` must remain unchanged. For a
fresh checkout hydrate their Git LFS files, then verify the hashes below; LFS
pointer text is not a model. Do not retrain, convert or substitute checkpoints.
To obtain the **generic vehicle** detector without starting inference:

```powershell
python -m pip install huggingface-hub==1.16.1
@'
from pathlib import Path
from shutil import copyfile
from huggingface_hub import hf_hub_download
from scripts.validate_inference import CHECKPOINT_SHA256, checkpoint_hash
source = hf_hub_download(
    "Ultralytics/YOLOv8", "yolov8n.pt",
    revision="27f858f2dc238503a66ce10248cf7ec71a3ded5d", token=False)
assert checkpoint_hash(Path(source)) == CHECKPOINT_SHA256["vehicle"]
target = Path("models/yolov8n.pt")
if target.exists():
    assert checkpoint_hash(target) == CHECKPOINT_SHA256["vehicle"]
else:
    copyfile(source, target)
for kind, filename in [("logo", "logo.pt"), ("plate", "plate.pt"), ("vehicle", "yolov8n.pt")]:
    assert checkpoint_hash(Path("models") / filename) == CHECKPOINT_SHA256[kind], kind
print("All three trusted digests match; no model was loaded.")
'@ | python -
```

Run from the root in a tooling environment, not the frontend. The service's
fallback source is the public T1 Space at immutable revision
`da8e0cdd5a03d0d3c60fab3f942910ef6472310b`, `models/{logo,plate,yolov8n}.pt`.
Both paths require the same hashes; startup fails rather than substituting weights.

| File | SHA-256 |
| --- | --- |
| `logo.pt` | `52e8aceec272ba35decc6b85f61cb21af06a4c14f9f245cfedb22caf465cf356` |
| `plate.pt` | `aa9742bb9fe5728cbe74027a9c4f8842d6c11f1423903b8ec8fc97e05e6293bb` |
| `yolov8n.pt` | `31e20dde3def09e2cf938c7be6fe23d9150bbbe503982af13345706515f2ef95` |

## Permitted local checks during the hold

Create/activate a disposable Python 3.13.12 environment outside the checkout.
These direct test dependencies reproduce the current local contract environment,
not Torch or hosted model compatibility:

```powershell
python -m pip install fastapi==0.136.1 starlette==1.0.0 httpx==0.28.1 pillow==12.1.1 av==17.1.0 anyio==4.12.1 mypy==1.19.0
python -m unittest discover -s tests -p test_image_api.py -v
python -m unittest discover -s tests -p test_dev_api.py -v
python -m unittest discover -s tests -p test_hosted_image_client.py -v
python -m unittest discover -s tests -p test_validate_inference.py -k test_help_does_not_require_inference_dependencies -v
python -m unittest discover -s tests -p test_validate_inference.py -k test_missing_vehicle_weights_fail_before_creating_outputs -v
python -m unittest discover -s tests -p test_validate_inference.py -k test_untrusted_checkpoint_is_rejected_before_loading_inference_libraries -v
python -m unittest discover -s tests -p test_validate_inference.py -k test_existing_output_directory_is_not_overwritten -v
python -m mypy image_service scripts/dev_api.py --ignore-missing-imports --follow-imports skip --check-untyped-defs
```

Together these select **29 tests**: fake external compute/HTTP and four CLI safety
checks. Despite its filename, `test_hosted_image_client.py` uses only intercepted
HTTP/fake credentials. No model inference, video fixtures, decoding or hosting
claim. Do **not** run unfiltered discovery, the whole diagnostic test file,
`/validate`, hosted image/video suites or `browser_video_workflow.js` during the hold.
Retain separate totals for passed, failed, runner-skipped and policy-deferred tests;
29 local passes do not replace the deferred full suite. Frontend typecheck/build
commands are above; artifact checks and the fixed review baseline are in
[preparation evidence](evidence/issue-7-preparation.md).

## Backend update — only after explicit approval

1. Record the approved source SHA, current Space SHA, variables, hardware and
   model digests **before** changing anything. Inspect the remote file inventory;
   stop if unfamiliar files or a concurrent update need reconciliation. Confirm
   the existing `MS3B09/autoscan-ai-images` Space still uses free `zero-a10g`, one
   process/replica and no paid storage, auto-upgrade or paid fallback. If it cannot
   remain free, stop and return the evidence to the owner; do not switch hardware.
2. Use only the [explicit packaging mapping](image-workspace.md#space-packaging).
   Include all five implementation modules, root entrypoint, Space README,
   self-contained requirements, system packages and `scripts/validate_inference.py`.
   Do not upload the root working tree, test fixtures, developer adapter, `.env`,
   `.git`, training materials, logs or visitor media. Preserve existing licenses
   and notices. Optional bundled weights must match the digests above.
3. Upload that mapping as **one commit**, not file-by-file live updates. With the
   locally authenticated `huggingface_hub.HfApi`, use `CommitOperationAdd` for each
   mapped destination and `create_commit(repo_id="MS3B09/autoscan-ai-images",
   repo_type="space", revision="main", parent_commit=RECORDED_SPACE_SHA,
   operations=EXPLICIT_OPERATIONS, commit_message=REVIEWED_MESSAGE)`.
   `parent_commit` must be the recorded revision, not a newly fetched value that
   bypasses concurrent-change protection. This is an API recipe, not a command to
   execute now. Never use broad folder uploads or delete unrelated remote files.
4. Set `AUTOSCAN_ORIGINS` to the exact approved origins. Variables trigger a
   restart: jobs/capabilities are ephemeral and can be lost. Record the new Space
   commit, effective runtime/build logs (sanitized) and installed versions. Check
   `GET /api/health` and image preview without inference only with approval;
   health is not a promise of available GPU quota. Do not call generic Gradio
   queues/uploads/files or diagnostic inference to test readiness.

## Netlify candidate — only after explicit approval

Use an existing owner-approved **free** site/account; check its actual free quota
and disable paid additions/automatic recharge. Do not link/push a production
branch that can auto-publish unreviewed work. Lock automatic publishing on an
existing Git-connected site before release changes. Record its previous production
deploy ID and URL for rollback. No Netlify site or preview URL has been verified
by this preparation task.

Build from the approved source with `npm ci` and the public backend URL above;
inspect `web/dist` for secrets and record hashes before uploading. From the root,
using an installed Netlify CLI (record `netlify --version`), authenticate via
`netlify login`, select the approved existing site with `netlify link`, then:

```powershell
netlify deploy --no-build --context deploy-preview --message "AutoScan reviewed candidate"
```

This uploads the already-inspected assets as a **draft**, not production; never
add `--prod` or `--prod-if-unlocked`. Run from the root so `netlify.toml` supplies
`web/dist`, `/detect` and `/detect/` rewrites, and security headers. Do not drag/drop
`dist` alone: that omits this repository's routing/header configuration. A CLI
upload/Netlify credential is still a deployment and requires approval.

Record the immutable draft URL/deploy ID; add that exact origin to the backend's
allowlist with separate backend-change approval. Without inference, inspect HTTPS,
root and both detector refresh routes, desktop/mobile/keyboard navigation, focus,
statuses/errors and image validation/preview. Verify `nosniff`, `no-referrer` and
camera/microphone/geolocation denial on actual responses. Local Vite checks do
not establish these Netlify headers. Keep API browser requests anonymous, with
no owner credential, and don't confuse an Origin-header HTTP probe with a native
browser preflight/result/download/cancel/delete verification.

Only the owner runs the agreed representative final video workflow on this exact
candidate; record playback, MP4/JSON/CSV and Delete now outcome. Do not expand that
run into cancellation/expiry/load tests. Independently disposition remaining #7
requirements (including image/empty results, isolation, cleanup, expiry, bounds
and failure states); leave safely unexercised ones unverified, not passed.

## Promotion, rollback and closeout — separate approvals

- **Promote:** after the gates and owner approval, use Netlify's deploy details
  **Publish Deploy** for the recorded draft ID, preserving the tested bytes rather
  than rebuilding with different environment/dependencies. Confirm production
  origin in `AUTOSCAN_ORIGINS` and record the live deploy ID/HTTPS URL, actual
  source/Space revisions, runtime versions and model digests. Recheck routes,
  headers/UI without inference. Any unverified required gate keeps #7 open.
- **Frontend rollback:** with approval, publish the recorded previous successful
  deploy from Netlify's UI; do not rebuild old source or reset local Git. Keep
  automatic publishing locked so the next Git build cannot overwrite the rollback.
  Recheck routes/headers and backend compatibility. If there was no previous deploy,
  stop public traffic via owner-approved site controls instead of inventing one.
- **Backend rollback:** with approval, restore the exact mapped file bytes from
  the recorded last-good Space revision in a new atomic commit, using the current
  recorded Space SHA as `parent_commit`. Restore its nonsecret variables separately;
  do not reset/delete unrelated remote work, expose credentials or change models.
  A rollback/restart loses live jobs; it cannot recover deleted or expired results.
  Validate health/routing without inference; a necessary GPU recheck needs approval.
- **Closeout:** record passed/failed/skipped/deferred checks and the rights exception
  in #7 evidence. No production URL, deployed-origin pass, full-suite rerun or legal
  clearance may be inferred from local preparation. The full review/test and
  lifecycle/resource gaps remain explicit until properly resolved.

## Free-tier and lifecycle limits

One global inference invocation, two pending slots (preview also takes a slot),
eight retained jobs, six job-upload and twelve preview attempts per rolling ten
minutes, all shared server-side. Do not add workers/replicas: coordination is
in memory. Images: 10 MB/12 MP. Videos: 20 MB/10 s/720p/600 decoded frames;
no truncation or subsampling. Results expire 1,800 s after success; failures and
cancellations clean artifacts. Delete revokes access immediately, active work
stops at a safe boundary. Refresh/restart can lose jobs; no history/recovery.
See [API/privacy details](image-workspace.md) and [video limits](video-workspace.md).

Platform quota, cold starts and availability can fail before these limits.
No automatic retry, credential rotation, paid compute or SLA. A reset timestamp
is supplied only when the platform provides a valid wait; it is not a reservation.
Representative historical timings are not accuracy/throughput guarantees.

Documentation checked against official references on 2026-11-16:
[Vite environment/security](https://vite.dev/guide/env-and-mode),
[Netlify Node setup](https://docs.netlify.com/build/configure-builds/manage-dependencies/),
[CLI draft deploy](https://cli.netlify.com/commands/deploy/),
[atomic rollback](https://docs.netlify.com/deploy/manage-deploys/manage-deploys-overview/),
[Space configuration](https://huggingface.co/docs/hub/spaces-config-reference),
[pinned downloads](https://huggingface.co/docs/huggingface_hub/guides/download),
[explicit Hub commits](https://huggingface.co/docs/huggingface_hub/guides/upload).
