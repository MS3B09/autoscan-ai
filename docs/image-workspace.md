# Image workspace — issue #3

The React/TypeScript/Vite workspace lives in `web/`, at `/detect`. Until T5 ships
the showcase, Netlify redirects `/` there. The original Streamlit app, its
requirements, and all checkpoint bytes remain unchanged. Video, downloadable
media, JSON, and CSV controls were not part of issue #3; issue #4 adds them as
documented in [image-exports.md](image-exports.md).

## Run and build

```powershell
cd web
npm ci
$env:VITE_AUTOSCAN_API='https://ms3b09-autoscan-ai-images.hf.space'
npm run dev
npm run build
```

`VITE_AUTOSCAN_API` is a public service URL, **never an HF token**. The service is
a separate free ZeroGPU Space, not the T1 diagnostic. Local API contract tests do
not require Torch or a GPU. Real model compatibility still requires hosted tests.

Netlify reads `netlify.toml`. Set the same public URL in its build environment.
Set the backend Space variable `AUTOSCAN_ORIGINS` to the exact deployed frontend
origin, plus any development origins you need, separated by commas. The default
allows `http://localhost:5173` and `http://127.0.0.1:5173`. CORS is only browser
policy: every private operation also requires the job capability. No browser
credentials, cookies, accounts, localStorage, analytics, or persistent history.

## API contract

All image bodies are raw bytes, not multipart or framework file references.
All responses, including errors and images, are `Cache-Control: no-store`.

| Request | Behavior |
| --- | --- |
| `GET /api/health` | Readiness and fixed retention/concurrency limits; not a GPU-availability promise |
| `POST /api/preview?filename=photo.jpg` | Validate/decode and return a normalized PNG; no job or inference |
| `POST /api/jobs?filename=photo.jpg&types=vehicle,logo,plate&confidence=40` | Validate again, admit an isolated job, return `202 {id, token, state}` |
| `GET /api/jobs/{id}` | Protected status, settings, dimensions, detections, trusted model metadata, expiry |
| `GET /api/jobs/{id}/image` | Protected annotated PNG, only after success/empty; otherwise 409 |
| `GET /api/jobs/{id}/download/{image,json,csv}` | Protected attachments; same job lifecycle, selections, and data as the preview/status |
| `POST /api/jobs/{id}/cancel` | Remove queued work immediately; active work becomes cancelling until a safe detector boundary |
| `DELETE /api/jobs/{id}` | Revoke access immediately, remove queued/completed data, safely stop and clean active work |

Supply `Authorization: Bearer <token>` for every operation on an existing job.
The 256-bit capability is generated separately from its random 128-bit identifier.
Missing/wrong capabilities, deleted jobs, and expired jobs all return 404. Tokens
never appear in URLs. A second visitor's token does not grant access to a job.

States are `queued`, `processing`, `cancelling`, `success`, `empty`, `error`, and
`cancelled`. Zero detections is `empty`, not an inference error. GPU reservation,
startup, and inference share the processing state; no invented progress or ETA.
Busy/storage errors return 503, shared upload limits 429, oversize images 413,
format mismatch/unsupported types 415, corrupt images/invalid settings 422, and
uploads exceeding the streaming-time budget 408.
Quota failures have an explicit job error. Submission is never silently retried.

### Input and coordinates

- PNG, JPG/JPEG, BMP, WebP; actual decoded format must match the extension.
- At most **10,000,000 bytes** and **12,000,000 decoded pixels**. Animated inputs,
  corrupt/truncated media, checkpoints, and other formats are rejected.
- EXIF orientation is applied, alpha is composited over white, and pixels become
  RGB. Metadata and embedded color profiles are not forwarded. The preview endpoint
  and inference use the same normalization, not independently resized inputs.
- The browser displays the normalized PNG before enabling Detect image. Merely
  choosing an image performs validation, never inference. The original file is
  uploaded again only after explicit detection.
- Bounding boxes are floating-point `[x1,y1,x2,y2]` **pixels from the top-left of
  the oriented RGB input**. Width/height describe those pixels; browser scaling
  preserves aspect ratio. Boxes and confidences are checked for finite, positive,
  in-bounds values; they are never invented or silently repaired.
- The requested model selections are independent. Vehicles retain COCO IDs
  2=car, 5=bus, 7=truck. Logo class identities are unchanged, including `peugeot`.
  Plate raw class remains `0`, displayed as “Plate,” never as transcribed text.
- Confidence is an integer percentage, 25–100 inclusive, default 40. The three
  object types start selected. An empty or unknown selection is rejected.

## Resource and abuse controls

This is intentionally a **single process and a single Space replica**. Do not add
ASGI workers/replicas without replacing the in-memory global coordinator. A shared
worker runs one GPU invocation at a time. At most three jobs/uploads are admitted
at once: one active plus two pending. Preview validation also consumes a slot.
Upload streaming is bounded to 10 MB and 30 seconds, including chunked requests.

The service enforces a global rolling ten-minute budget of **six job-upload
attempts** and **twelve preview attempts**, including invalid decoded content.
These are deliberately shared limits, not resettable client IDs or trusted
`X-Forwarded-For` values. Busy rejections don't consume an upload allowance.
There are at most **eight retained job records/results**. Full capacity rejects
new uploads rather than evicting another visitor's unexpired results. Error and
cancelled metadata expire after 60 seconds; queued work expires after five minutes.

T1 observed about 2.05 GB process RSS, an image plus a 300-frame diagnostic in
14.34 seconds, anonymous duration-reservation quota errors, and later a daily
runs limit. A 60-second GPU reservation and small bounded queue reuse that tested
configuration. The admission budgets and eight-result ceiling are conservative
production policy, **not measured throughput/peak-memory guarantees**. They limit
damage without promising to prevent denial of service. Platform anonymous quota
may run out earlier; there is no credential rotation or paid fallback.

The platform-provided `X-IP-Token` is forwarded only into the pinned ZeroGPU
request context for ordinary anonymous quota attribution. It is not application
authorization and does not bypass the shared application budgets.

## Privacy and lifecycle

Each job uses a generated private directory and fixed server-side filenames.
Visitor filenames are only bounded display metadata, never filesystem paths.
Original bytes are discarded after validation; only normalized queued sources are
written. The GPU reads and removes its source before prediction. Cancellation is
checked before each selected detector, and partial output is discarded if a
cancellation arrives during inference. Pending cancellation removes the source
immediately. Failed/cancelled jobs retain no image or detection payload.

Successful results expire **1,800 seconds after completion**, enforced on access
and by an independent server sweeper (within one second), without browser activity.
Delete now immediately invalidates the capability. If compute is currently inside
a detector, deletion finishes at the next safe boundary; the global slot stays
occupied until that compute has really returned. No success is reported for it.

The service owns only the `autoscan-image-jobs/job-*` temporary directories. It
cleans these on startup and all remaining jobs on orderly shutdown. An abrupt
process crash may leave inaccessible files until startup cleanup or host teardown.
Refresh loses the browser's in-memory capability; restart loses the server map.
There is no recovery/history promise. Browser object URLs are revoked when replaced,
deleted, or expired; already received media cannot be remotely erased from a client.

Gradio's ordinary launch hook initializes the pinned ZeroGPU SDK, but **all public
routes are then handled by the restricted API**. Generic framework uploads, files,
queues, and event calls cannot bypass the job contract; a guard also closes these
during launch. Neither source nor result paths are returned. Access logging is
disabled, and exceptions return only sanitized infrastructure categories. No
uploaded image or detection payload is logged, committed, or served as a static
asset. Owner authentication is used only by local deployment tooling.

## Space packaging

Deploy only this explicit mapping; never upload the working tree or visitor media:

| Local | Space |
| --- | --- |
| `image_service/{__init__,api,detector,app}.py` | Same paths |
| `image_service/space-entry.py` | `app.py` |
| `image_service/space-README.md` | `README.md` |
| `image_service/requirements.txt` | `requirements.txt` |
| `validation_space/packages.txt` | `packages.txt` |
| `scripts/validate_inference.py` | Same path |
| Optional pre-bundled `models/logo.pt`, `models/plate.pt` | Same paths |
| Optional pre-bundled, pinned standard YOLOv8n from T1 | `models/yolov8n.pt` |

Missing checkpoints are provisioned server-side from the exact public T1 Space
revision `da8e0cdd5a03d0d3c60fab3f942910ef6472310b`, whose three digests and
original vehicle provenance are recorded in `docs/backend-validation.md`. No
owner token is required. A network/provisioning failure prevents startup, never
substitutes weights. `load_models` verifies all trusted SHA-256 digests
before importing a model deserializer and checks every required class identity.
The model/runtime pins are retained from T1; revalidate after changing them.
Request explicitly free `zero-a10g` hardware. Do not enable billing or paid storage.

## Checks

```powershell
python -m unittest discover -s tests -p test_image_api.py -v
python -m mypy image_service --ignore-missing-imports --follow-imports skip --check-untyped-defs
cd web
npm run typecheck
npm run build
```

The API contract suite uses a controlled external-compute substitute, actual
decoding, threads, files, HTTP routes, and a shortened retention interval. It tests
the approved job-API boundary, not private implementation call counts. It does
**not** establish real model or hosting compatibility.

For actual hosted inference (uses quota; no automatic submission retries):

The commands below default to anonymous requests. For developer-only use of your
free account allowance, follow [authenticated-image-tests.md](authenticated-image-tests.md).

```powershell
$env:AUTOSCAN_IMAGE_URL='https://ms3b09-autoscan-ai-images.hf.space'
python -m unittest discover -s tests -p test_hosted_image_api.py -v
```

The hosted upload-limit check also needs the system `curl` executable. It uses
`Expect: 100-continue` so the server can reject a known-oversized body without
Python's synchronous sender losing the rejection to a Windows connection abort.

That suite includes real selected-model/confidence behavior, raw identities,
format/content/settings validation, empty results, capability isolation,
generic-route denial, concurrent admission, cancellation, and Delete now.
`AUTOSCAN_TEST_30_MINUTE_EXPIRY=1` additionally enables an actual thirty-minute
hosted wait; run that test separately with `-k test_e` rather than exhausting the
shared submission budget with the preceding tests first. Otherwise that test is
**not run**, not passed. Rate/retained-storage
saturation and accelerated expiry are deterministic local HTTP contract checks;
they are not claims about public load capacity. Keep final evidence and deployment
limitations in `docs/evidence/issue-3-verification.md`.
