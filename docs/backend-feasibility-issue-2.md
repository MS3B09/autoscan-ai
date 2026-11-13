# Issue #2: free-backend feasibility

Date: 2026-11-13. Scope: [#2](https://github.com/MS3B09/autoscan-ai/issues/2),
under [the parent specification](https://github.com/MS3B09/autoscan-ai/issues/1).

## Decision

**PASS for T1 feasibility, not for production release.** Model compatibility,
anonymous browser completion, measured ten-second-video capacity, and the bounded
temporary-result isolation/deletion/expiry mechanism pass. This is a feasibility
experiment, not the production backend or a release/accuracy/availability pass.
No downstream implementation was started.

**Final rerun is not green:** the anonymous inference test hit the platform's
daily runs limit after earlier successful real calls. Latest result: **8 passed,
1 quota-blocked failure, 1 not run**. GPU requests stopped; no credentials, paid
compute, or alternate identity was used to evade this limit. The earlier browser
and final-revision HTTP success reports remain the feasibility evidence.

## Hosted evidence

Space: <https://huggingface.co/spaces/MS3B09/autoscan-ai-validation>.

- The authenticated management API identified the existing account as `MS3B09`,
  with `isPro: false`. No subscription, hardware change, or billing action was made.
- The runtime API confirmed `RUNNING`, current and requested hardware `zero-a10g`.
  The observed GPU was **NVIDIA RTX PRO 6000 Blackwell Server Edition MIG 2g.48gb**;
  `zero-a10g` is the platform's hardware identifier, not a claim about that GPU model.
  [Recorded runtime/account evidence](evidence/issue-2-runtime.json) and
  [final build log](evidence/issue-2-build.log) are retained.
- [Browser evidence](evidence/issue-2-browser-inference.json) records a successful
  cross-origin POST and completed event stream from **https://example.com**, with
  `credentials: 'omit'`, no HF token, and no account login. Both responses were 200.
- That inference ran at Space revision
  [`05f3d74ee0ba877fbaa1d341fc4a4cbea591e915`](https://huggingface.co/spaces/MS3B09/autoscan-ai-validation/commit/05f3d74ee0ba877fbaa1d341fc4a4cbea591e915).
- This is a real browser CORS check, but **not** a test from a deployed Netlify
  frontend, which does not exist yet.
- The final diagnostic revision is
  [`da8e0cdd5a03d0d3c60fab3f942910ef6472310b`](https://huggingface.co/spaces/MS3B09/autoscan-ai-validation/commit/da8e0cdd5a03d0d3c60fab3f942910ef6472310b).
  Its [independent anonymous HTTP inference report](evidence/issue-2-hosted-final-report.json)
  also passed all model, image, and 300-frame assertions after the launch changes.

### Preservation and compatibility

Before deserialization, all three SHA-256 digests must match the trusted identities
in `scripts/validate_inference.py`. The diagnostic hashes them again after image
and video inference and fails if any changed.

The two custom identities were independently rechecked against the original Git
LFS pointers at Git commit `b2d35e76f8d220677a54ee5437635748427a7f1a`:

```text
git show b2d35e76f8d220677a54ee5437635748427a7f1a:models/logo.pt
git show b2d35e76f8d220677a54ee5437635748427a7f1a:models/plate.pt
```

| Checkpoint | Trusted SHA-256 |
| --- | --- |
| Logo | `52e8aceec272ba35decc6b85f61cb21af06a4c14f9f245cfedb22caf465cf356` |
| Plate | `aa9742bb9fe5728cbe74027a9c4f8842d6c11f1423903b8ec8fc97e05e6293bb` |
| YOLOv8n vehicle | `31e20dde3def09e2cf938c7be6fe23d9150bbbe503982af13345706515f2ef95` |

Vehicle provenance: `Ultralytics/YOLOv8`, file `yolov8n.pt`, pinned revision
`27f858f2dc238503a66ce10248cf7ec71a3ded5d`. Its Hub LFS SHA-256 was independently
confirmed against the local provisioned artifact. No checkpoint was rewritten,
converted, retrained, or replaced. The Streamlit application is unchanged.

All 24 logo classes, plate `{0: "0"}`, and COCO IDs **2=car, 5=bus, 7=truck**
survived loading. **Specification discrepancy:** the parent mentions `peuugeot`,
but the trusted checkpoint's raw class 16 is `peugeot`. Safe inspection of its
pickle opcodes and actual hosted loading agree. The diagnostic now checks the
real checkpoint identity; it does not rename any model class.

The existing composite image produced **7 detections** (logo 1, plate 3, vehicle 3).
Every image/frame prediction was checked for finite confidence/coordinates,
confidence in the requested range, original dimensions, and positive in-bounds
boxes. Counts and visual examples are **compatibility evidence, not accuracy**.

### Representative video and resources

The accepted fixture contains actual changing traffic, not a looped still image.
Source and CC BY-SA 4.0 attribution are in `validation_space/README.md`.

| Observation | Measured result |
| --- | --- |
| File | `fixtures/traffic-10s.mp4` |
| SHA-256 | `b1485225e56b5117d31990163238468766175c5188c1169d828905a834c92015` |
| Input bytes | 5,447,771 (below 20,000,000) |
| Dimensions | 1280 × 720 |
| Duration/rate | 10 seconds, 30 fps |
| Independently decoded source frames | 300 |
| Frames processed by all three detectors and written | 300 |
| Annotated frames decoded | 300 |
| Image inference, including first prediction | 4.890 seconds |
| Video inference and encoding | 8.665 seconds |
| Entire diagnostic | 14.343 seconds |
| Browser submission through completion | 17.245 seconds |
| Process RSS at completion | 2,045,157,376 bytes |

These are **one-run observations**, not latency/FPS promises, peak-memory
measurements, worst-case capacity, or evidence for every allowed input format.
Inputs over 20 MB, ten seconds, 1280×720, or 600 decoded frames are rejected;
accepted frames are never silently truncated or sampled. The hosted fixture is
constant-frame-rate; arbitrary variable-frame-rate timestamp handling is not
established. The diagnostic output is `mp4v`, decodable with OpenCV, **not verified
browser-playable**. Production silent H.264 output/playback remains a separate gate.

### Queue, quota, startup, and failures

Observed, not simulated:

1. Original build failed resolving `/tmp/scripts/requirements-validation.txt`.
   Requirements are now self-contained. `spaces==0.51.3` matches the platform's
   injected package, and `dill==0.4.1` avoids its preinstalled multiprocess conflict.
2. The first repaired build loaded models but stopped on the incorrect logo-name
   assertion. The next ran inference but Gradio's JSON serializer rejected integer
   map keys. Both diagnostic bugs were fixed without changing checkpoint bytes.
3. During the startup failure, a credential-free browser fetch received **503**,
   `Your space is in error, check its status on hf.co`, after 53.356 seconds. This
   is an unavailable observation, not a measured healthy cold start.
4. An anonymous API request returned an SSE error:
   `You have exceeded your ZeroGPU quota (180s requested vs. 174s left). Try again in 23:57:07.`
   It suggested authentication, but **no credentials were supplied and accounts
   were not made a requirement**. Lowering the declared GPU duration allowed the
   later anonymous run. The observed reservation exceeded the decorator duration;
   do not assume declared GPU seconds equal the required remaining quota.
5. The successful browser stream emitted a heartbeat then `complete`. It did not
   expose a separate queue-wait duration. The diagnostic allows one active job and
   two pending jobs; queue saturation, concurrent load, and healthy sleep/wake
   latency were **not tested**. Final declared GPU duration is 60 seconds, with no
   availability guarantee and no paid fallback.
6. The first mounted FastAPI attempt conflicted with Gradio's default Space SSR
   listener on port 7860. Disabling SSR removed the port conflict, but a plain
   ASGI mount still failed the platform's GPU-function startup check: the pinned
   `spaces==0.51.3` initializes ZeroGPU through Gradio's launch hook. The diagnostic
   now uses ordinary `demo.launch()`, then attaches the small FastAPI router to
   the returned app. It does not patch the platform or any checkpoint. SSR is off.
7. After the successful final-revision HTTP integration run, a clean full-suite
   rerun returned `You have exceeded your ZeroGPU runs limit. Authenticate with a
   Hugging Face token for more quota`. This is distinct from the duration/quota
   reservation error. The per-day run threshold and reset time were not provided
   by this response and are not claimed here. No further GPU requests were made.

### Isolated temporary results

The diagnostic implements only a bounded fixed-JSON feasibility probe, not T2's
production image-job lifecycle. It uses a private temporary directory, a fresh
256-bit per-result capability, protected GET/DELETE routes, `no-store` responses,
and server-side deletion timers. Knowing the filesystem path must not permit
retrieval through Gradio's generic file routes. No visitor media is accepted.

[Cross-origin browser isolation evidence](evidence/issue-2-browser-isolation.json)
on the final revision observed:

| Request | HTTP status |
| --- | --- |
| Own capability, read | 200 |
| Missing capability, read | 404 |
| Another probe's capability, read/delete | 404 / 404 |
| Known private path through `/gradio_api/file=` | 403 |
| Known private path through legacy `/file=` | 404 |
| Own capability, delete | 204 |
| Own capability, read after delete | 404 |

Real hosted integration checks also observed successful retrieval followed by
404 after waiting 31 seconds **without any deletion request**. This tests the
server-side accelerated expiry mechanism, not a mock clock or browser unload hook.

The accelerated expiry is **30 seconds**, deliberately not the production
30-minute retention requirement. Production upload/result/cancellation/expiry
behavior and failure/restart cleanup still need their own integration tests.

## Reproduction

Use cached local HF authentication **only for management/uploads**, never in the
browser probe. Upload the explicit mapping in `backend-validation.md`, not the
working tree. No paid resources are needed.

Prepare the capacity fixture with FFmpeg (no model dependencies required):

```text
curl -A "AutoScanAI-validation/1.0 (https://github.com/MS3B09/autoscan-ai)" -L https://upload.wikimedia.org/wikipedia/commons/c/c6/Traffic_flow_in_front_of_UI_.webm -o traffic-original.webm
ffmpeg -n -i traffic-original.webm -t 10 -vf scale=1280:720,fps=30 -an -c:v libx264 -crf 23 -pix_fmt yuv420p -movflags +faststart traffic-10s.mp4
```

Original SHA-256:
`6701610f38f129bcb1aec5e5fd08740f1acaa6479aa60b5248fad9b30f0d60d3`.
The observed derived hash used FFmpeg from the `imageio-ffmpeg==0.6.0` Windows
wheel (Lavf61.7.100/Lavc61.19.100); different encoder builds can produce different
bytes. The exact accepted fixture is retained in the pinned Space revision.
Commons flags the source for license review; resolve this before portfolio release.

Python is 3.10.13. The successful report records **every installed distribution
and version**, including platform-supplied packages. Direct model pins are in
`scripts/requirements-validation.txt`; hosted SDK pins are in the self-contained
`validation_space/requirements.txt`. To extract the recorded environment:

```text
python -c "import json; p=json.load(open('docs/evidence/issue-2-browser-inference.json')); print('\n'.join(k+'=='+v for k,v in sorted(p['report']['installed_distributions'].items())))"
```

That records the observed set; it is not a promise that future platform base
images never change. Revalidate digests, classes, outputs, and versions after any
dependency or hosting change.

```powershell
python -m py_compile scripts/validate_inference.py validation_space/app.py tests/test_validate_inference.py tests/test_hosted_validation.py
$env:AUTOSCAN_VALIDATION_URL='https://ms3b09-autoscan-ai-validation.hf.space'
$env:AUTOSCAN_VALIDATION_REPORT='hosted-report.json'
python -m unittest discover -s tests -v
```

For local real inference, install the diagnostic dependencies in an isolated
environment, provision the pinned vehicle checkpoint, and run:

```text
python scripts/validate_inference.py --vehicle-weights PATH_TO_TRUSTED_YOLOV8N --output-dir NEW_DIRECTORY --video traffic-10s.mp4
```

Without `--video`, the CLI retains its three-frame compatibility smoke check.
Without PyTorch and `AUTOSCAN_VEHICLE_WEIGHTS`, local inference tests are explicitly
**not run**, even when real hosted tests succeed. No project static typechecker
is configured/installed; `py_compile` is a syntax check, not typechecking.

An initial full-suite invocation ran **10 tests: 9 passed, 1 explicitly not run**
(local PyTorch integration), including all three real hosted checks. Its PowerShell
stderr pipeline formatted unittest's successful stderr output as a
`NativeCommandError` even though unittest reported `OK (skipped=1)`. A subsequent
clean subprocess capture produced the [retained final test output](evidence/issue-2-tests.log):
**8 passed, 1 failed due to the real anonymous runs limit, 1 not run**. This later
failure is not described as passing or skipped. The successful earlier inference
report was retained; the failed rerun did not replace it.

## Not established by this ticket

- Detection accuracy, a service SLA, throughput under load, peak resources, or all
  image/video codecs and adversarial media.
- A deployed Netlify frontend, browser-playable annotated video, production media
  access control, uploads, exports, cancellation, or actual 30-minute retention.
- Dataset/model usage-rights approval for release; preserve the original credits
  and dataset references. The fixture's open-license attribution is recorded but
  its Commons review flag is not treated as legal clearance.
