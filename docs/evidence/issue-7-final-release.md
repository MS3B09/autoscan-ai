# Final release work — #5 / #6 / #7

Updated **2026-11-17**. The owner requested completing the remaining work, closing
the tickets and making the final app available at **https://autoscan-ai.netlify.app/**,
and supplied locally saved video JSON/CSV. This authorizes the requested free
production release once required gates are resolved; it does not provide observed
passes or explicitly lift the prior inference/hosted-video testing restriction.

**Current status: hostname/configuration prepared; production not published.**
Do not describe this as a completed public release. The remaining blocker is an
explicit decision on the previously prohibited hosted acceptance checks, not a
new request for production approval or another runtime report.

## Owner-supplied exports: locally verified, not newly inferred

The supplied files were read locally; neither the full files nor their paths,
source filename, detections, job identifier or capabilities are published here.
No associated live job was accessed or reconstructed.

Assert-based validation passed:

- Successful **1920×1080** video with matching source/output dimensions,
  **87 declared / 87 processed frames**, **2.8862195528862196 seconds**.
- **662 JSON detections / 662 CSV rows**, with matching types/classes/labels,
  confidence, bounding coordinates, dimensions, frame indices/timestamps and source
  identity. Indices/times fall inside the declared clip. Values remain private.
- All three exported model SHA-256 values match the trusted repository constants:
  vehicle `31e20dde3def09e2cf938c7be6fe23d9150bbbe503982af13345706515f2ef95`,
  logo `52e8aceec272ba35decc6b85f61cb21af06a4c14f9f245cfedb22caf465cf356`,
  plate `aa9742bb9fe5728cbe74027a9c4f8842d6c11f1423903b8ec8fc97e05e6293bb`.

Exported runtime inventory:

| Runtime/package | Reported version |
| --- | --- |
| Python | 3.10.13 |
| torch / torchvision | 2.8.0 / 0.23.0 |
| ultralytics / numpy | 8.4.189 / 1.26.4 |
| pillow / av | 11.3.0 / 17.1.0 |
| gradio / spaces | 6.32.0 / 0.51.3 |
| fastapi / starlette | 0.162.5 / 1.7.0 |

These match the declared corresponding pins. This is inventory from the owner's
completed-run export, not independent current-process introspection or a timestamped
frontend/backend revision attestation. No MP4 was supplied/independently replayed;
the owner's earlier video-workflow PASS retains its general user-reported scope.
The files substantiate short-clip 1080p success and export consistency, **not**
maximum-workload resources, cancellation or an actual video-expiry wait.

## Requested hostname and backend wiring

- Existing Netlify site **`1661ca1f-7c9b-4f69-b8ee-635ac7a49eee`** was renamed from
  `autoscan-ai-ms3b09` to **`autoscan-ai`**, by a name-only update. Readback confirms
  **https://autoscan-ai.netlify.app**, same site ID, **published_deploy null**,
  Git unlinked. Team remains `mosab04-ns`, **Free**; no new site/plan/billing change.
- Same immutable deploy **`6afb4f606cabececacad1489`**, source **`e719d8a`**, now at
  **https://6afb4f606cabececacad1489--autoscan-ai.netlify.app/detect**.
  All **16 public artifacts** still match the retained manifest hashes. `/`,
  `/detect`, `/detect/` returned **200**, exact recorded HTML and security headers.
  Historical URLs in prior evidence retain the former site name.
- Appended only the exact renamed-draft and requested-production origins to
  `AUTOSCAN_ORIGINS`, preserving all four existing origins. This configuration
  change caused a normal build/restart transition; subsequent management readback
  returned **RUNNING / zero-a10g / one current/requested replica** and health
  **200 / ready / 1800-second retention / 1 active / 2 pending**. No deliberate
  restart/loss test or inference ran. Live ephemeral jobs can be lost on restart.
- Backend source remains **`d160158db56c1cdf6113a575b8b01bb763f81b73`**.
  No code, checkpoint, dependency, replica, storage or paid-resource change.
- Production root still returned **404** because promotion has not occurred.
  The requested name is configured, not a promise that the app is already live.

## Fresh permitted checks

- Explicitly selected local suite: **39 passed / 0 failed or errors /
  0 runner-skipped**, **59.500 seconds**, exit 0. **12 policy-deferred** of 51;
  no unfiltered discovery or opt-in inference/hosted/diagnostic suite ran.
- Python typecheck: **success, seven files**. TypeScript and Vite **7.3.8** build:
  **passed**. Build output was not uploaded; production will preserve the already
  reviewed immutable candidate bytes, not silently replace them with this rebuild.
- Fresh anonymous Chromium context: all three candidate routes at eight widths
  **320–1920 px**, no horizontal overflow, one H1, no missing image alt, zero page
  runtime errors. Inspected desktop/mobile showcase and mobile still-preview
  captures locally; public sample only, no private owner media.
- Keyboard skip link had a visible solid outline; confidence changed **40 → 41**
  via ArrowRight. Native still-image preview returned **200**, exact renamed-origin
  CORS and `no-store`, **no Authorization or Cookie**; no Detect submission occurred.
- Native requests for seven unknown-job status/media/export/cancel/delete operations
  with a deliberately invalid bearer returned readable **404**, exact-origin CORS
  and `no-store`. This is current-origin denial coverage, **not live-job isolation,
  successful protected downloads, active cancellation or expiry evidence**.
- First browser harness checked readiness before React had consumed the successful
  preview response. Inspection showed enabled Detect/no alert; rerun waited for
  actual enabled state and passed. No product defect or source edit was needed.
- Impeccable mechanical check of the existing UI sources returned **`[]`**.
  These scoped checks are not a full WCAG, physical-device or live-result audit.

## Closeout and remaining blocker

- **#6** can close as implementation complete with the already-directed licensing
  exception/unverified disposition. Eight technical criteria retain evidence; the
  mixed rights criterion is **not an independent legal pass**. The owner now
  explicitly requested ticket closeout. Preserve notices/private-training boundary.
- **#5 / #7:** saved exports resolve the requested runtime/hash evidence and add
  real owner-export 1080p/CSV consistency. Historical 720p capacity, image retention,
  shared lifecycle and prior isolation evidence remain valid at their own scope.
- To satisfy the remaining deployed requirements rather than waive them, obtain
  explicit permission lifting the prior no-inference/hosted-video hold for a
  **bounded final acceptance run**: current-origin image/valid-empty workflows,
  representative 1080p video, protected operations/isolation, active cancellation
  and an actual thirty-minute video-retention wait. Use only free anonymous quota,
  no owner-token fallback, paid resources, submission retries or quota-exhaustion
  testing. Stop and report if free capacity is unavailable.
- No permission to waive these required checks is inferred from a general final
  release request. No new video/source upload is requested from the owner here;
  existing/publicly licensed fixtures can be used after authorization. Quota/busy/
  cold-start states that cannot be safely exercised remain explicitly unverified,
  as the original issue allows. No extra accuracy/SLA or device-matrix gate.
- Once that blocker is resolved and checks pass, promote the **same deploy ID**,
  verify actual production routes/headers/native origin/UI, then close #5/#7 and
  parent #1 with distinct passes/limitations. Do not seek production approval again
  unless the scope, cost or candidate changes.
