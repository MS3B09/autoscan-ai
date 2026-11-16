# Issue #6 — Option A showcase

Current workflow update (2026-11-16): the owner removed the internal licensing
hold; compliance is unverified, not a legal pass. Earlier gate findings below are
historical. See [the owner decision](release-licensing.md#owner-directed-workflow-decision--2026-11-16)
and [the current checklist](../release-checklist.md). Public deployment still
requires separate approval and technical release checks.

Date: 2026-11-15. **Showcase implemented; public release is not approved.**
Review baseline confirmed by the user:
`a3be322662d258d08ee9e891977e1e94ae9c9e0c`.

## Scope

- `/` renders the semantic Compare showcase; `/detect` and `/detect/` retain the
  existing image/video workspace. Netlify no longer redirects the root; both
  detector paths have explicit 200 rewrites for direct navigation and refresh.
- Shared navigation, wordmark, tokens, focus treatment, and orange actions join
  the two surfaces. Image/video API clients and processing logic are unchanged.
- Image/video entry links lead to the existing native file picker. They do not
  pretend to transfer an already-selected file across navigation.
- Paired photographs, actual detection legend, keyboard-scrollable JSON/CSV
  previews, native sample downloads, all 24 checkpoint logo classes, the five
  original contributors, datasets, and source links are present.
- No new dependency, backend feature, model/checkpoint change, retraining, OCR,
  tracking, account, history, paid resource, or deployment was introduced.

## Real sample and rights

The existing PlatesMania photograph was not shipped or stripped of its watermark.
The user chose a licensed replacement, accepted its source/result assets in the
visual plan review, and explicitly approved **“Yes, bypass photo matching”** only
for photography and example detection data. The approved Option A composition,
typography character, spacing, palette, and hierarchy remain authoritative.
The immutable reference is attached to [issue #6](https://github.com/MS3B09/autoscan-ai/issues/6).

**Lexus LX 570**, by **M 93**, is self-photographed and explicitly permits
redistribution and derivatives for any purpose with attribution. The checked
[Commons revision](https://commons.wikimedia.org/w/index.php?title=File:Lexus_LX_570_20090620_rear.JPG&oldid=1254744190)
and author/permission links are preserved in the page and
`web/public/examples/attribution.txt`. Wikimedia's 1280px thumbnail preserves the
whole photograph; no source watermark was removed.

One anonymous call to the existing production job API returned **success**, with
all three selected types at **40%**, **1280 × 915** pixels, and four detections:

| Raw identity | Confidence |
| --- | --- |
| vehicle / truck (7) | 0.8277940154075623 |
| vehicle / car (2) | 0.6059869527816772 |
| logo / lexus (10) | 0.9543265700340271 |
| plate / 0 (0), readable label Plate | 0.7541951537132263 |

PNG/JSON/CSV were downloaded from that same job, copied byte-for-byte to the
deliberately public sample directory, and the job was deleted. No capability or
credential is shipped. JSON contains the actual original model digests, runtime,
settings, historical job ID and expiry; it is an archived sample, not a live job.
The source SHA-256 is
`094eaadda95cb65a3303caf3e35039be61af977e23ad89cf840c527a15b50243`;
the annotated PNG is
`b3a0f2c40e14cb82a006e913ab1f02c8d1bea88b07eef90d853786bd76aca04d`.

The SUV being labeled **truck**, and a side step being falsely labeled **Plate**,
are preserved and explained. This German photograph has no Moroccan plate.
Neither generated comp scores nor corrected/invented predictions are used.
This run establishes example provenance, not accuracy, throughput, or availability.

### Unresolved rights gate

Photograph permission does **not** clear the detectors or their training data.
The repository has Apache-2.0 text; pinned Ultralytics `8.4.189` documents AGPL-3.0
or enterprise terms for code/models and corresponding-source requirements for a
hosted application. Its primary documentation was checked through Context7.
Both original Roboflow dataset URLs returned **403**, so their licenses and the
custom checkpoints' training-data/redistribution provenance were not confirmed.
No enterprise license is claimed, purchased, or inferred. No project license
was changed and no unpublished source was pushed.

**Owner/upstream confirmation and a compliant source/license arrangement remain
required before public release.** The UI states that model/dataset licensing is
uncleared. Keep #6's rights criterion open; #7 is not release-approved by this work.

## Browser boundary and checks

The user approved a new browser-test boundary. It observes the public UI rather
than React internals, and does not replace the existing diagnostic/API boundaries.
Tests follow the repository's existing Playwright function-file convention:

- Start the configured Vite development server or `npm run preview -- --port 5174`
  after a production build. Navigate Playwright to that origin.
- Run `tests/browser_showcase.js` with `browser_run_code_unsafe(filename)`:
  native JSON/CSV download events; actual sample-preview/export consistency;
  stable CSV columns and all four rows/coordinates/confidences; contributor and
  24-brand preservation; image/video entries; direct refresh and trailing slash;
  keyboard skip/focus/disclosure/downloads; no clipped controls/overflow at
  **320, 390, 640, 641, 700, 768, 800, 1280, 1440, 1536, and 1920px**.
- Run `tests/browser_detector_states.js` at the same origin: explicit submission,
  unchanged defaults, job capability headers, locked controls, queued/processing/
  success/empty/error/cancelled/expired/unavailable UI, download failure/retry,
  keyboard download, deletion/focus restoration, responsive results and the
  full-width mobile coordinate caption. **Passed with test-only HTTP responses**;
  fresh timestamps and three-second expiry are simulated, not retention evidence.
  Native confirmation is accepted by a test-only `window.confirm` substitute.
- Real published source/result bytes back the simulated-state run. The empty
  fixture was corrected after visual review to return the unannotated source;
  a guard now rejects reusing the annotated success image for empty-state captures.

Red/green: root navigation initially failed on the missing showcase heading and
then passed; sample download initially failed on the missing action and then
passed after the data section was added. Later expanded checks passed.

## Visual verification

The reference and actual **1536 × 1024** first viewport were compared side by side;
desktop/mobile full pages, 1280 × 800 and 1920 × 1080 folds, and detector success,
empty, error and expired states were opened and inspected. Captures remain in the
local, pre-existing untracked `.impeccable/review/` tooling directory, not shipping
web assets. Native browser viewport checks are not a physical-device matrix.

- Initial Hallmark hero review requested a visible mobile pair and more usable
  annotation inspection. Both images now remain paired on mobile; exact readable
  legend values, stronger swatches, and full-size image links preserve the output.
- Fresh finish review requested stronger actions/navigation, corrected empty-state
  evidence, and truthful tooling-state reconciliation. The same reviewer scored
  **all four fixes resolved**, disposition **ship for those fixes only**. This is
  not a new whole-surface or machine-gate approval.
- Measured normal-text contrast: ink/paper **14.45:1**, muted/paper **5.90:1**,
  muted/sheet **6.91:1**, dark ink/orange **5.58:1**, hover **4.67:1**,
  error/paper **6.58:1**. White-on-orange comp lettering was not copied.
- Impeccable mechanical detector returned `[]` over the changed UI sources.
- Hallmark static sweep has zero FAIL. Its rendered sweep reports text-under/
  crowded-edge findings for full text-range rectangles inside deliberately clipped,
  scrollable code panes. The fresh reviewer confirmed **no actual painted overlap**.
  Two inherited selector WARNs concern button recipes/table tabular figures; native
  private-blob video posters retain their explicit waiver.
- Automated Impeccable plate matching rejects the JPEG as non-PNG and the new
  photograph as different from the old comp, even after the authorized bypass.
  This machine gate is **not passed**. Local state preserves that failure, corrects
  the artifact path, and separately records manual evidence; later native phases
  are not falsely certified. Final comp-diff reports **73% overall drift** and
  **91% band agreement**, including the deliberately changed photo/data/copy.
  It is a diagnostic, not a fabricated pixel-match pass.
- `DESIGN.md` and `.impeccable/design.json` record the implemented tokens and
  shared system following the review, without overwriting an incumbent design.

## Local validation and review

- Targeted image API suite: **11 passed**. Targeted video API suite: **9 passed**.
- TypeScript passed repeatedly; configured production build passed. One earlier
  build command timed out; its later configured rerun passed, not a hidden pass.
- Netlify TOML assertion confirms no root redirect and both explicit detector
  rewrites. Actual deployed-Netlify routing/CORS remains #7.
- Final suite, production-preview browser reruns, and two-axis code review are
  recorded in the completion addendum after the fixed-point review.

Not checked here: physical iOS/Safari/Android codecs, screen-reader session,
accuracy benchmark, public load, a new hosted expiry wait or active video
cancellation, fresh full hosted integration suite, or production deployment.

## Completion addendum

- Configured production build and TypeScript passed after the review fix.
- Final `python -m unittest discover -s tests -v`: **40 tests, 30 passed,
  10 explicitly skipped**, 33.091 seconds, exit zero. Hosted/model opt-ins are
  not reported as fresh passes; the one real sample job is separate evidence.
- Both browser function files passed against the configured production preview
  at `http://127.0.0.1:5174`, not only Vite's development server.
- JSON/CSV/JPEG/PNG samples were verified **byte-identical in Git's index**.
  `.gitattributes` preserves their original bytes across platforms and recognizes
  the service's intentional CSV CRLF endings; Git whitespace checks passed.
- Required two-axis review ran in fresh parallel contexts against the confirmed
  starting commit. **Standards: 0 documented violations, 0 actionable smells.**
  **Spec: 1 responsive defect and 1 unresolved rights criterion.**
- The spec reviewer reproduced clipped navigation at **641px**, just above the
  compact-header breakpoint. A new browser regression first failed with
  `Clipped controls at 641: GitHub`. A single shared `flex-wrap: wrap` fixes both
  routes without inventing a menu or moving the mobile breakpoint. Expanded
  root checks cover eleven widths; detector navigation is also checked at
  640/641/700/768/800px. The configured production-preview rerun passed.

The responsive defect is fixed; the rights criterion remains open as documented
above. This completion does not authorize deployment, licensing changes, or
closing the issue as fully accepted.

### Independent follow-up

Source commits: `fe87aea` (showcase) and `8bac723` (navigation regression fix),
both local and not pushed. The standards reviewer rechecked the follow-up diff:
**0 documented violations, 0 actionable smells**. The spec reviewer independently
checked both routes on the production preview at **640, 641, 650, 660, 680, 700,
768, and 800px** and confirmed no clipped or overlapping navigation. No remaining
implementation defect or scope creep was identified in that focused follow-up.

Review totals remain separated: **Standards 0 findings; Spec 2 initial findings,
1 fixed, 1 open (model/dataset rights).** The narrowly scoped visual-fix ship
verdict and the independent responsive check do not certify the blocked native
Impeccable pipeline. Its `finish --disposition ship` refused while the authorized
photography exception leaves `plates` open; no automated completion is claimed.
Design tokens and the exception are documented; no original reference was altered.

## Licensing follow-up — 2026-11-16

The previous Roboflow 403 observation is historical. A new public-source audit
found the original logo dataset declares **CC BY 4.0**, and the plate dataset
declares **Public Domain / CC0 1.0**. Dataset declarations/license links are now
recorded in the sample attribution notice. Commons photo permission was
reconfirmed. See [release-licensing.md](release-licensing.md) for primary sources.

**The rights gate remains open:** public dataset declarations do not establish
the exact custom checkpoints' creators, training chain, redistribution grants,
or an approved AGPL/source arrangement for this release. No project license,
checkpoint or dependency was changed, and no release is authorized by the audit.
The owner's new testing hold is in [../release-checklist.md](../release-checklist.md):
no agent-run video tests/inference; the owner reserves the final video check.
