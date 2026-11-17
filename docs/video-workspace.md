# Short videos — issue #5

> **Owner instruction, 2026-11-16:** the owner reserves the final hosted video check.
> For the requested 1080p update, local CPU-only codec/API video tests are explicitly
> approved. No model inference, hosted/browser video checks or production promotion
> is authorized. Do not run unfiltered discovery; the diagnostic/model/hosted tests
> remain excluded. See [release-checklist.md](release-checklist.md).

The image-first `/detect` workspace also accepts MP4, MOV, AVI, ASF, M4V, and
MPEG clips. Choosing a file only validates it and builds a silent browser preview.
**Detect video** explicitly submits the chosen types and 25–100% confidence
(40% default). No audio, OCR, tracking, deduplication, frame sampling, or paid
fallback is added. The original Streamlit application/checkpoints are unchanged.

## Validation and processing

- Maximum **20,000,000 upload bytes**, **ten seconds**, **600 decoded frames**,
  and **1920 × 1080** pixels (or portrait equivalent). All limits apply together;
  exceeding one rejects the clip rather than truncating it.
- The owner requested 1080p for a short test clip. Earlier hosted 300/600-frame
  capacity evidence remains **720p evidence**, not proof of 1080p GPU/resource
  behavior. Local codec/API checks do not spend HF quota or establish inference
  performance. The larger frame has 2.25× as many pixels; free-hosted inference at
  the new maximum remains unverified until separately approved evidence exists.
- A decoded-container/extension check and full packet/frame decoding run before
  admission. Checkpoints, playlists, external file/network references, corrupt
  packets/frames, changing geometry, and invalid/non-increasing timestamps are
  rejected. Last-frame duration must be positive and known from frame/stream timing.
- PyAV **17.1.0** binds FFmpeg for timestamp-aware decoding and H.264 encoding.
  It retains Python 3.10 compatibility with the existing Space runtime. Version
  16.1.0 was rejected after a Windows native MPEG-opening crash during testing.
  Existing model/runtime dependencies retain their pins. Native codec diagnostics
  are suppressed so untrusted media metadata cannot become application logs.
- Validation/preview codecs run in a separate process with a **fifty-second wall
  limit**, two encoder threads and one decoder thread. A crash, timeout, or temporary
  disk failure returns an actionable 503, releases admission, and removes files
  instead of hanging the HTTP process. AVI RIFF/LIST chunk bounds are checked
  recursively so truncated containers cannot masquerade as complete shorter clips,
  even when the outer RIFF length has been rewritten.
- Process every decoded frame using every selected trusted detector, preserving
  validation of class identities, coordinates, dimensions, and confidence. Source
  timing is checked again while processing; no assumed FPS drives progress/exports.
- Source presentation timestamps are rebased to zero and encoded on a microsecond
  clock (maximum half-microsecond rounding). Timing too fine to remain strictly
  increasing on that clock is rejected, not silently collapsed. VFR spacing is
  preserved. Rotation is applied to pixels and sample aspect ratio is retained.
- Output is silent **H.264, yuv420p MP4**, with fast-start metadata. Odd source
  dimensions are padded by one black pixel at the right/bottom, never stretched;
  sample aspect ratio compensates to preserve the source display aspect ratio.
  Frame-coordinate dimensions remain the upright source dimensions; JSON reports
  `output_width`/`output_height` separately. Encoded data is capped at 40 MB.
- Every encoded output frame is decoded again and its count/timestamp verified
  before publishing success. That check is **not browser-playback proof**; browser
  verification is separately recorded in [the evidence](evidence/issue-5-verification.md).

## API and schema

Use the existing raw-body `/api/preview` and `/api/jobs` routes. Video preview
returns `video/mp4`, without inference or a job. Submission validates the original
again and stores it under a generated private server filename, never its user name.

Protected routes add:

| Route | Result |
| --- | --- |
| `GET /api/jobs/{id}/video` | Complete silent MP4, otherwise 409 |
| `GET /api/jobs/{id}/download/video` | Same MP4 as a generated-name attachment |
| `GET /api/jobs/{id}/download/json` | Full status/settings/models/runtime/detections |
| `GET /api/jobs/{id}/download/csv` | One row per frame-level detection |

Every existing-job operation requires its independent bearer capability, including
preview, status, exports, cancellation, and deletion. A wrong media endpoint
(`/image` on a video job, for example) returns 404. Pending/failed/cancelled jobs
never offer an apparently complete clip.

Export schema **1.1** retains the [documented detection fields](image-exports.md)
without per-detection class IDs. Video
CSV appends `frame_index,timestamp_seconds` to the eleven image columns; both also
appear on every video JSON detection. `frame_index` is zero-based decode/presentation
order and `timestamp_seconds` is the source timestamp relative to the first frame.
Repeated observations are separate rows, **not unique objects**. Empty JSON has
`detections: []`; empty CSV still contains all thirteen column names. Text-cell
formula protection and UTF-8 BOM encoding are unchanged.

Status adds `media_type`, `queue_position`, and, for video, `frame_count`,
`processed_frames`, `duration_seconds`, `output_width`, and `output_height`.
Pending queue positions come from the actual queue. Frame progress advances only
after detection and encoding of a frame; reaching the last frame displays
finalization/verification, not premature success. Before the first frame, the UI
states that GPU capacity/initial preparation may still be pending. No ETA/FPS claim.
Details are paginated; downloads always include every selected observation.

## Lifecycle and bounds

Video shares the image service's one active job, two pending/admission slots,
six job attempts/twelve previews per rolling ten minutes, and eight retained
results. These are shared bounds, not separate allowances for each media type.
Preview decoding/encoding occupies its admission slot until complete. Upload
streaming remains bounded to thirty seconds, including chunked bodies.

Queued cancellation removes source work immediately. Active cancellation and
Delete now stop at the next detector/frame boundary; encoder/decoder contexts close
before partial files are removed. The GPU slot is not released prematurely.
Source and validation sidecar are deleted after processing; failed/cancelled jobs
retain no media. Successful results expire thirty minutes after completion, checked
on every access and by the independent sweeper. Delete now revokes access at once.
Startup clears the service-owned `job-*` and `preview-*` directories after a crash.
Refresh/restart limitations and blocked generic framework routes remain unchanged.

## Deployment and checks

Add `image_service/video.py` to the explicit Space file mapping in
[image-workspace.md](image-workspace.md), and deploy the updated self-contained
requirements. Keep free `zero-a10g` hardware; no billing change is needed.

```powershell
python -m pip install av==17.1.0
python -m unittest discover -s tests -p test_video_api.py -v
python -m mypy image_service --ignore-missing-imports --follow-imports skip --check-untyped-defs
cd web
npm run build
```

`test_video_api.py` exercises the public HTTP job boundary with real media/codecs
and an external-compute substitute; it does not establish hosted model feasibility.
For a quota-consuming real check, set `AUTOSCAN_IMAGE_URL` and
`AUTOSCAN_VIDEO_SOURCE` to representative footage, then run only
`test_hosted_video_api.py`. It submits once and deletes the job even on failure.
Optional `AUTOSCAN_VIDEO_EVIDENCE` saves downloads outside shipping assets.
Submission defaults to anonymous; explicit developer authentication follows the
same isolated rules as [image tests](authenticated-image-tests.md). Never use the
cached deployment credential implicitly for inference or send it to the frontend.

`tests/browser_video_workflow.js` checks explicit submission, real playback through
the end, keyboard downloads, desktop/mobile fitting, independent-browser-context
isolation, and deletion. It can resume against an already-completed job without
spending another GPU invocation. Inspect its test-only fixture/output paths before
running. Browser/source media must remain outside public Space files and Git.
