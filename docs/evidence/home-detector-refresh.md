# Home and Detector refinement — 2026-11-17

The owner requested the supplied Home images, a shorter landing page, 80%-width
desktop content, in-page image expansion, explicit image/video input selection,
settings navigation, removal of class IDs from the UI/downloads, and new browser
identity. The same request explicitly authorized committing, pushing, and updating
the existing live app after each change. No paid resources or hosted inference
tests were requested or used.

## Published changes

| GitHub commit | Change | Netlify production deploy |
| --- | --- | --- |
| `97e44f0` | Home content, supplied assets, native image dialogs, shared shell | `6afca5367bc56f98fe600544` |
| `5abaec4` | Detector selection/URL state, settings shortcut, readable classes, car favicon/title | `6afca729eb01b307086a66dc` |
| `5b44c5e` | JSON/CSV export simplification and matching download help | `6afca810778de6140d28b370` |

All three commits were pushed to `origin/main`. Production remains
<https://autoscan-ai.netlify.app>, on the same **Free**, Git-unlinked Netlify site
`1661ca1f-7c9b-4f69-b8ee-635ac7a49eee`. No site duplication, billing change, or
automatic publishing was enabled. Previous production before this task was
`6afb4f606cabececacad1489`; each row above also supplies an incremental rollback
point. Redirects/security headers were retained through deploy-file equivalents
of `netlify.toml`.

The backend's single changed file, `image_service/api.py`, was atomically deployed
to the existing `MS3B09/autoscan-ai-images` Space:

- Previous revision: `d160158db56c1cdf6113a575b8b01bb763f81b73`.
- New revision: `4a05b37b23c3a91e305505a2598cf43dc67bf500`.
- Deployed file SHA-256: `6c73a7526c419974cb80459c9cf4b4c1051e23867da7c0ef987fed76c04d83e3`;
  downloaded revision bytes match the local file.
- All ten mapped baseline files matched the previous GitHub source before update;
  the commit used the recorded parent revision to reject concurrent changes.
- Hardware/requested hardware remains `zero-a10g`, one current/requested replica,
  no persistent storage. Checkpoints, model names, dependencies, and origins are
  unchanged. A deployment restart can lose existing temporary jobs.
- Health returned **200**, `ready`, retention **1800 seconds**, one active and two
  pending slots. Final management readback reports **RUNNING** on the new revision;
  health is not a GPU/quota-availability or inference claim.

JSON download schema is now **1.1**, omitting per-detection `class_id`; CSV omits
that column for images/videos. Names, labels, confidence, boxes, dimensions and
video frame/timestamp fields are retained. Status/internal model identities and
model-provenance class maps remain unchanged. Historical public example exports
are retained as regression fixtures, not advertised on Home.

## Checks

- TypeScript/Vite production build: passed.
- Home browser regression: passed locally and on production; supplied images,
  four-section hierarchy, dialog close/Escape/focus restoration, image/video entry
  selection, and no horizontal overflow at nine widths from **320–1920px**.
- Detector-input browser regression: passed locally and on production; hash/default
  selection, filtered uploads, rejection of the wrong type, clearing incompatible
  sources, Back/Forward, radio keyboard behavior, title, and seven responsive widths.
  Preview HTTP is intercepted; no live validation/inference is exercised.
- Simulated detector-state browser regression: passed locally; settings scrolling,
  focus/unlock with retained local source, hidden class IDs, download retry,
  quota/error/empty/cancelled/expiry/unavailable UI, responsive results. These are
  intercepted responses, not real hosted jobs or lifecycle measurements.
- Three focused local backend tests: **3 passed**, no skips/failures. Image
  detections and empty exports, spreadsheet safety, video observations/timestamps,
  omission of class IDs, and unchanged retained status data. Video uses a local
  CPU codec and fake external compute, not a detector.
- Impeccable mechanical detector over changed UI: **`[]`**. Desktop/mobile
  rendered Home/Detector captures were visually inspected.
- Final production artifact check: **19 files byte-identical** to local build;
  HTML matches after removing only Netlify's injected hosting comment.
- `/`, `/detect`, `/detect/`: **200** with `nosniff`, `no-referrer`, and
  camera/microphone/geolocation denial. Car SVG favicon is present.

No full suite, new hosted GPU inference, real image/video result download,
thirty-minute wait, load test, or independent asset/model licensing verification
was run. Existing rights notices and README contributor/dataset credits remain.
The new annotated sample was supplied by the owner and is labeled an example;
it is not newly measured model output or an accuracy benchmark.
