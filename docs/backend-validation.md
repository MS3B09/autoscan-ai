# Backend validation gate

## Status

The build brief and Option A showcase are approved. The user selected hosted-first
validation after the local PyTorch installation failed for lack of disk space.
Real hosted image inference and every-frame processing of a ten-second 720p
traffic clip now pass anonymously from a cross-origin browser. See
[`backend-feasibility-issue-2.md`](backend-feasibility-issue-2.md) for the evidence,
decision, limitations, and outstanding production gates. This is not a release pass.

The local environment has Python 3.13.12 plus Python 3.10.7. An isolated Python
3.10.13 environment was created, but installing PyTorch 2.8.0 CPU wheels failed.
Do not change the original `requirements.txt` or custom checkpoint files to work
around this. Hugging Face CLI authentication was verified as `MS3B09`; the user
authorized hosted validation and the diagnostic Space was created with explicit
`zero-a10g` hardware requested (the API name for free ZeroGPU). Upload/build and
inference were initially pending; creation alone did not pass the gate. This
historical local-install limitation does not describe the later hosted results.

Diagnostic Space: <https://huggingface.co/spaces/MS3B09/autoscan-ai-validation>.

## Human step

For a future session without a login, run `hf auth login` interactively in a terminal and approve the requested access
locally. Do not paste credentials in chat or save them in this repository. The
agent can verify authentication with `hf auth whoami`, then create and populate a
diagnostic Gradio Space using the eligible account's free ZeroGPU allowance. Do
not select paid hardware or a paid plan. Public Space source/committed weights
are downloadable; runtime visitor files are not part of this diagnostic.

## Diagnostic Space contents

Upload this explicit mapping, not the whole working tree or any credentials:

| Local source | Space path |
| --- | --- |
| `validation_space/app.py` | `app.py` |
| `validation_space/README.md` | `README.md` |
| `validation_space/requirements.txt` | `requirements.txt` |
| `validation_space/packages.txt` | `packages.txt` |
| `scripts/validate_inference.py` | `scripts/validate_inference.py` |
| `scripts/requirements-validation.txt` | `scripts/requirements-validation.txt` |
| `models/logo.pt` | `models/logo.pt` |
| `models/plate.pt` | `models/plate.pt` |
| `imgs/image.JPG` | `imgs/image.JPG` |
| Trusted standard `yolov8n.pt` below | `models/yolov8n.pt` |
| Prepared traffic clip (see feasibility report) | `fixtures/traffic-10s.mp4` |

Vehicle checkpoint provenance:
`Ultralytics/YOLOv8`, revision `27f858f2dc238503a66ce10248cf7ec71a3ded5d`,
file `yolov8n.pt`. It was downloaded to
`C:\Users\User\AppData\Local\Temp\opencode\autoscan-reference-weights\yolov8n.pt`.
Re-download that revision if the temporary copy expires; never substitute a newer
YOLO architecture or overwrite the two custom checkpoints.

On the hosted API, call `/validate` with no arguments. Success must preserve the
24-class logo map (including raw class 16, `peugeot`), the plate map
`{0: "0"}`, the COCO car/bus/truck IDs, finite in-bounds boxes, and checkpoint
SHA-256 hashes. All 300 traffic-clip frames must be processed, encoded, and decoded.
The report explicitly lists remaining gates; do not equate this smoke check with
a release pass. The Space accepts no visitor media and returns no public file URLs.

The custom-file digests were independently checked against the committed Git LFS
pointers. All three trusted digests are pinned in `scripts/validate_inference.py`
and checked **before** importing the model loader. A changed or substituted
checkpoint must fail, not be deserialized.

| Checkpoint | SHA-256 |
| --- | --- |
| `models/logo.pt` | `52e8aceec272ba35decc6b85f61cb21af06a4c14f9f245cfedb22caf465cf356` |
| `models/plate.pt` | `aa9742bb9fe5728cbe74027a9c4f8842d6c11f1423903b8ec8fc97e05e6293bb` |
| Standard `yolov8n.pt` | `31e20dde3def09e2cf938c7be6fe23d9150bbbe503982af13345706515f2ef95` |

## Remaining checks before release

- Anonymous browser/API calls from the Netlify frontend, including quota/sleep errors.
- A representative accepted ten-second video with every frame processed, valid
  timestamps, bounded memory/runtime, and browser-playable silent MP4 output.
- Input limits, per-job download access isolation, bounded concurrency/rate limits,
  cancellation cleanup, Delete now, and thirty-minute expiry.
- Real image outputs and structured exports; old screenshot scores are not expected
  values for a new runtime. Detection accuracy requires a separate representative set.

If any requirement cannot be met on free ZeroGPU, revisit hosting with the user;
do not silently drop video, change weights, expose files, or enable paid resources.

## Reproducing locally once space is available

Use an isolated Python 3.10.13 environment with
`scripts/requirements-validation.txt`. For CPU wheels, install the pinned Torch
and Torchvision versions from `https://download.pytorch.org/whl/cpu` first.

```text
python scripts/validate_inference.py --vehicle-weights PATH_TO_TRUSTED_YOLOV8N --output-dir NEW_OUTPUT_DIRECTORY
```

The output directory must not exist. It contains the diagnostic media and report;
it is not a permanent data store. For the integration test, set
`AUTOSCAN_VEHICLE_WEIGHTS` to that trusted checkpoint and run:

```text
python -m unittest discover -s tests -v
```

Without that environment variable and PyTorch, the integration test is explicitly
skipped—not passed. CLI checks still run without inference dependencies.

## Anonymous hosted smoke test

Once the Space is running, set `AUTOSCAN_VALIDATION_URL` to its HTTPS `.hf.space`
app URL and run `python -m unittest discover -s tests -p test_hosted_validation.py -v`.
This submits **one** anonymous GPU job, so it consumes free quota. It checks CORS
preflight with a proposed Netlify origin (not a deployed Netlify site), streams
the result, and independently checks the returned checkpoint digests and frame
counts. `AUTOSCAN_VALIDATION_REPORT` may name a local JSON evidence file. Do not
send the owner's HF token to this API call or embed it in frontend code.

This test file uses HTTP, not a rendered browser. It now also checks the bounded
fixed-JSON isolation probe, deletion, generic file-route denial, and accelerated
30-second expiry. It does not test the future visitor-media upload/download
endpoints, cancellation, or production 30-minute retention. Separate real browser
evidence is linked in the feasibility report.
