# Image downloads — issue #4

Completed `success` and `empty` jobs expose three downloads:

| Request | Content |
| --- | --- |
| `GET /api/jobs/{id}/download/image` | Annotated PNG, byte-identical to `/image` |
| `GET /api/jobs/{id}/download/json` | UTF-8 JSON, job data without per-detection class IDs |
| `GET /api/jobs/{id}/download/csv` | UTF-8 CSV with BOM and CRLF record separators |

Every request requires `Authorization: Bearer <job token>`, just like status and
preview retrieval. Tokens never enter URLs or exports. Responses use
`Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, and attachment names
`autoscan-{id}.{png|json|csv}`; visitor filenames never become paths or headers.
Unknown formats and missing/wrong/deleted/expired capabilities return 404.
Unfinished, failed, and cancelled jobs return 409. Storage/serialization failures
return sanitized 503 errors, without attachments or partial result bodies.

Exports are assembled completely in memory while holding the existing job lock.
There is no second storage/inference path or extra export cache. Delete now and
the existing 1,800-second post-completion expiry protect all three downloads and
remove the job's source/result artifacts. An already received or saved client
copy cannot be remotely erased. The browser aborts pending downloads and revokes
its object URLs when it forgets a job.

## JSON export schema 1.1

The 2026-11-17 simplification removes `class_id` from downloaded JSON detections
and CSV columns for both images and videos. Status/internal model identities
remain unchanged (status schema 1.0); exports do not mutate the retained result.
Consumers of old exports must use class names rather than the removed column.

The top-level object contains:

| Field | Meaning |
| --- | --- |
| `schema_version` | String `"1.1"`; version of this export contract |
| `id` | Random job identifier, not its access token |
| `state` | `success` or `empty` for a downloadable result |
| `filename` | Original source filename, unchanged metadata |
| `settings` | `types`: requested object types in execution order; `confidence`: integer minimum percent, 25–100 |
| `width`, `height` | Normalized input dimensions in pixels |
| `coordinate_system` | Description of the oriented/composited input coordinate space |
| `detections` | Array described below; empty array when no objects match |
| `models` | Trusted model metadata keyed by `vehicle`, `logo`, `plate`: SHA-256 checkpoint digest and raw class-ID/name map (JSON keys are strings) |
| `runtime` | Actual Python version and installed package versions, including Torch, Torchvision, Ultralytics, NumPy, Pillow, Gradio, Spaces, FastAPI, Starlette |
| `expires_at` | Unix timestamp in seconds, thirty minutes after completion |
| `error` | `null` for completed downloadable jobs |

Each detection contains `source_filename` (unchanged), `object_type` (`vehicle`,
`logo`, `plate`), raw `class_name`, readable `label`, numeric
`confidence` in **0–1**, floating-point `bbox: [x1,y1,x2,y2]`, and pixel `width`
and `height`. Numeric values are not rounded for export. Detection order and
values are the same as the job's displayed result; UI percentages/coordinates
are rounded only for readability. There is no additional filtering at download.

Boxes use pixels from the **top-left of the EXIF-oriented, white-composited RGB
input**, not CSS/display dimensions. The PNG is not resized, reoriented, or
re-encoded for download. `x1 < x2`, `y1 < y2`; coordinates stay inside the input.
Vehicles retain COCO identities 2=car, 5=bus, 7=truck. Logo spellings are preserved.
Plate raw class name `"0"` has `label: "Plate"`; it is
**not plate transcription or OCR text**.

## CSV columns

Stable column order:

```text
source_filename,object_type,class_name,label,confidence,x1,y1,x2,y2,width,height
```

One row per selected detection, with the same numeric units/values as JSON. An
empty result is a valid header-only CSV; its PNG is still readable without boxes.
The standard CSV writer escapes commas, quotes, and record separators. A UTF-8
BOM helps spreadsheet applications preserve non-ASCII filenames.

CSV **text cells** whose first non-whitespace character is `=`, `+`, `-`, or `@`
(including full-width variants) receive a leading apostrophe to prevent formula
evaluation. Numeric cells remain numbers. JSON always retains the exact original
text, and should be used when lossless filename/class metadata is required.

This schema is image-only. Detection rows are independent observations reusable
by the later video workflow; no tracking, OCR, history, or database is introduced.

## Verification

Run the local HTTP contract suite and frontend checks as documented in
[`image-workspace.md`](image-workspace.md). `tests/test_hosted_image_api.py` now
checks downloads against real hosted job results, special-character/formula-like
filenames, selected-only and empty exports, readable PNG bytes, and protected
retrieval/deletion/expiry. Opt-in hosted tests still need a deployed current
service and available GPU quota; skipped tests are not passes. Developer-only
authenticated submission is documented in [authenticated-image-tests.md](authenticated-image-tests.md);
the default remains anonymous.

Actual browser downloads and remaining verification gates are recorded in
[`evidence/issue-4-verification.md`](evidence/issue-4-verification.md).
