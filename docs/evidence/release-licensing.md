# Release licensing and attribution — #6 / #7

Research/access date: **2026-11-16**. **LICENSING GATE BLOCKED; research complete.**
Evidence/owner follow-up, not legal advice or a legal-clearance opinion.
Implementation unchanged; images work per the user's manual report, not a new test.

## Scope and baseline

Read `AGENTS.md`, `docs/agents/domain.md`, `GLOSSARY.md`, `README.md`, `LICENSE`,
`docs/evidence/issue-6-verification.md`, backend provenance, service pins and `web/public/examples/attribution.txt`; no ADR directory present.
The research pass added this document; related checklist/policy/attribution updates
and issue comments are tracked separately. No tests, builds, inference, GPU use,
deployments, credential access, dependency/model changes or license replacement.
**NO VIDEO TESTING OR VIDEO INFERENCE:** the final video test belongs to the user
after remaining work; historic evidence is not a fresh pass or authorization.

## Focused permission search — 2026-11-16

At the owner's request, checked whether Ultralytics itself permits public app
code/fine-tuned weights with private training notebooks/configuration for a free
personal portfolio demo. **No published personal/noncommercial exception was
found.** Current licensing FAQs and pinned `v8.4.189` guidance explicitly include
training scripts and configuration in the publication scope. Publishing app code
and weights alone does not establish compliance with that stated checklist.

See [ultralytics-private-training.md](ultralytics-private-training.md) for exact
quotations, current/pinned sources, and the distinction between vendor guidance
and applying the GNU license to this specific work. Their terms preserve rights
under the actual open-source license; this is not a legal finding that every
historical notebook must be disclosed. No project-specific permission is evidenced.

With the owner's privacy boundary and no-paid-license constraint unchanged,
**keep #6/#7's public-release gate open**. A suitable explicit permission or qualified
source-scope determination could change the assessment; neither was obtained by
this public-page search. No request was sent and no purchase is authorized.
Other non-inference release preparation can proceed without clearing the gate.

## Known / unknown matrix

| Layer / exact asset | Known evidence | Still unknown / release consequence |
| --- | --- | --- |
| Project software | Root `LICENSE` contains Apache-2.0; README names five contributors and both datasets. | This does not license third-party code, weights or images. Owner must approve an appropriate combined-work/source arrangement. |
| `ultralytics==8.4.189` | `image_service/requirements.txt` pins it; tagged LICENSE is GNU AGPLv3 and package metadata says AGPL-3.0 [U1,U2]. | No approved compliance inventory/source offer tied to the actual release; no alternative grant evidenced. **Blocked.** |
| Vehicle `models/yolov8n.pt` | Backend evidence pins official `Ultralytics/YOLOv8` revision below; that revision's model card says `license: agpl-3.0` [V1]. | Must be included in the source/license/notice arrangement; model permission does not blanket-license COCO images. |
| Custom `models/logo.pt` | MS3B09 confirms training on the README-linked dataset from `yolov8n.pt` and permits public app/model files (2026-11-16); pinned identity below. | Owner-confirmed provenance/publication scope, not an independent audit or replacement for upstream terms. Source/licensing compatibility with private training materials remains **blocked**. |
| Custom `models/plate.pt` | Same owner confirmation: README-linked plate dataset, `yolov8n.pt` starting weights, public app/model files permitted. | Same remaining upstream/source question; no need to establish identity through Roboflow's separately hosted model. **Blocked.** |
| Logo dataset v1 | Public original version page: MS3B, CC BY 4.0, 2,782 images, generated 2024-04-19 [D1,D2]. Owner confirms using the README-linked datasets. | Export/processing history is not independently audited; uploader label is evidence, not a warranty of every image's rights. |
| Plate dataset v1 / public hosted model | Project and version label Public Domain; project license links CC0 1.0. 1,558 images, generated 2022-06-25; hosted model `/1` is Roboflow 2.0 Object Detection (Fast) [D3–D5]. | No separate downloadable-weight grant/identity tying that model to local `plate.pt` established. CC0 affects only rights the affirmer can waive [C2]. |
| Showcase source/annotated photograph | Commons fixed revision confirms M 93, self-photographed Lexus LX 570, 2009-06-20; attribution-only permission expressly allows redistribution, derivatives and commercial use [P1,P2]. | Photo copyright permission evidenced with credit retained; does not clear detectors/data or imply brand endorsement. No new byte/image verification here. |

Recorded SHA-256 identities (read from `scripts/validate_inference.py`, not recomputed):
- Logo: `52e8aceec272ba35decc6b85f61cb21af06a4c14f9f245cfedb22caf465cf356`.
- Plate: `aa9742bb9fe5728cbe74027a9c4f8842d6c11f1423903b8ec8fc97e05e6293bb`.
- Vehicle: `31e20dde3def09e2cf938c7be6fe23d9150bbbe503982af13345706515f2ef95`.
- Vehicle source revision: `27f858f2dc238503a66ce10248cf7ec71a3ded5d` [V1].
Digests establish identity, **not permission**. No checkpoint was downloaded or loaded.

## Software: license text versus vendor guidance

Context7 queried `/ultralytics/ultralytics/v8.4.189`; tagged licensing/contributing primary text was also read [U4].
Ultralytics' published position is AGPL for code/models by default, including custom
training, or an Enterprise agreement; its compliance guide describes the entire
derivative application, frontend/backend, modifications, inference/training scripts,
configuration, fine-tuned weights, and required **redistributable** training data [U3,U4].

The actual GNU AGPL §13 says **if you modify the Program**, the modified version
must prominently offer **all remote interacting users** no-charge network access
to its Corresponding Source [G1]. §1 defines source needed to generate, install,
run and modify the work, including controlling scripts. §§4–6 address notices,
modified works and conveyed object code; §5 distinguishes independent aggregates.
§2 does not automatically place all inference output under AGPL.
These are not a blanket claim that every network/private/commercial use or unrelated frontend requires a new license. Application
boundaries and model/source scope require owner review with upstream or qualified
advice where uncertain; this research does not decide derivative-work law.

Static inspection of this application's integration found `from ultralytics
import YOLO` in `scripts/validate_inference.py:42` and `model.predict(...)` in
`image_service/detector.py:30`, using the pinned installed package, rather than a
vendored Ultralytics source tree. That observation is not a legal finding that
the application is independent or outside AGPL. GNU §2 does not automatically
license all program output under AGPL, while the owner specifically confirms
fine-tuning pretrained `yolov8n.pt`; these facts must not be collapsed into either
"all notebooks are always required" or "unmodified import means no obligations."
No model loading, execution or private-file inspection was used for this check.

An old public GitHub link, Apache text alone, or only selected Space service files
does not demonstrate complete corresponding source for the actual deployed version.
Record exact frontend/backend revisions, covered artifacts, notices/license texts,
setup/build/run scripts, lawful model acquisition and a prominent working source
offer available to remote users without privileged access. Keep credentials and
visitor media out of publication; source disclosure is not a request for either.
Do not erase Apache notices or assume Apache and AGPL components are automatically
incompatible: preserve grants and document the approved scope instead of silently
relicensing everything. No enterprise agreement exists in the reviewed evidence.
Enterprise terms require an actual agreement and annual fee [U5]; a quote, paid
account, private repository or public download is not permission or a free solution.

## Datasets and photograph: narrower conclusions

Earlier #6 evidence recorded Roboflow **403/unavailable**, not “no license.” On
2026-11-16 all cited project/version/model pages returned readable public content.
Logo overview reports **Models: 0**; do not mistake its generic “Free Detection API”
advertisement for a licensed LOGOS TEAMX checkpoint [D2]. Plate overview and model
page show the same Public Domain project label and hosted model details, not a
separate grant for AutoScan's custom weights [D3,D5]. No inference controls used.

CC BY 4.0 permits sharing/adaptation subject to its terms: retain supplied credit,
notices and source link, link the license, indicate modifications, and avoid implied
endorsement [C1]. `web/public/examples/attribution.txt` now records the dataset-page
declarations, named uploaders and license links, without claiming checkpoint
permission. Actual training/preprocessing changes still need confirmation before
release notices can describe them. CC0 waives the
affirmer's rights, not others' rights; neither tool supplies trademark/privacy
clearance or guarantees the uploader owns every constituent image [C1,C2]. Do not
invent dataset-to-weight licensing consequences or publish training data blindly.

Commons revision `1254744190` (2026-07-31) matches the photograph, author, date and attribution-only permission in `attribution.txt` [P1].
That notice identifies the 1280px thumbnail and annotation changes; keep it and the
visible author/source credit with shipped originals/derivatives/downloads. The
Commons site-wide text license is not the photograph's license. This supports the
photo copyright-permission subcheck, **not** an overall #6 or #7 rights pass.

## Owner clarification — 2026-11-16

The owner states: **"It's me who train the two models (MS3B09). No training
notebook/configuration will be shared."** Source: direct project-owner statement
in the implementation conversation. Record trainer identity as confirmed by the
owner, not an independent training-chain audit or a new license grant.

The owner subsequently answers both release-scope questions:
- **"Yes, app code and model files can be public; training materials stay private."**
- **"Yes, those datasets, starting from yolov8n.pt."** This refers to the two
  datasets linked in this repository and both custom checkpoints. It does not
  establish the exact historical base-file revision or training-software version.

The owner's publication permission and training-source summary are now recorded;
do not keep asking for them, a model card, or notebooks/configuration. Publication
scope approval is not an instruction to push/deploy immediately, relicense other
contributors' work, or waive upstream rights. No private training files were read.

**Respect this publication boundary:** do not request or publish training
notebooks/configuration, or assume permission to include them in a source offer.
The statement does not authorize relicensing or clear third-party obligations.
Whether this deployment can comply without those materials remains unresolved;
do not assert either that every training notebook is automatically required by
AGPL or that withholding it is automatically compliant. Determine the applicable
source scope/permission with upstream or qualified advice before release.

## What remains to unblock

1. **Owner questions answered.** Trainer, linked datasets, starting architecture/
   weights name, public app/model publication scope, and private-training boundary
   are confirmed by MS3B09. Retain this as the provenance record; do not present it
   as an independent audit or invent historical revisions/preprocessing details.
2. **Upstream/source compatibility.** Clarify whether the intended public hosted
   application and fine-tuned weights can use the no-fee license path with the
   training materials private. This is an upstream/legal-scope question, not a
   request for more owner provenance documents. If applicable required source
   conflicts with that boundary, hold release unless a suitable grant is established.
3. **Implement only an approved arrangement.** Preserve dataset notices and all
   applicable grants, document the source/weights actually authorized for release,
   and record source access/revisions. Do not replace the root license, buy a
   license, publish training materials, replace/retrain models, push, or deploy
   without the relevant approval. Non-inference release preparation may continue.

### Plain-language clarification request (draft only; not sent)

> I trained two custom models from `yolov8n.pt` using the linked Roboflow datasets
> for a free public portfolio demo using `ultralytics==8.4.189`. The application
> code and trained weights can be public, but training notebooks/configuration
> will remain private. Does your no-fee AGPL licensing route permit this exact
> arrangement, and what corresponding-source materials would be required?

Ask through [Ultralytics' official licensing contact](https://www.ultralytics.com/license)
or obtain qualified advice. This draft is not an answer, exception, paid-license
request or permission to contact anyone on the owner's behalf.

## Free paths and ticket disposition

- **Existing-model AGPL path:** potentially no licensing fee, if the owner can
   satisfy the approved AGPL/source obligations and independently establish custom
   checkpoint/data rights while respecting the no-sharing boundary. Compatibility
   with that boundary is not established; evidence and approval remain required.
- **No-cost explicit permission:** request clarification or an actual written
  exception/grant from the relevant holders; availability is not promised. One
  holder's exception cannot waive another holder's data/photo/software rights.
- **Hold release:** costs nothing and preserves current work while evidence is
  gathered. A different permissively licensed stack/data/models would need a new
  user-approved scope and validation; it is not a fix performed here and conflicts
  with the current checkpoint-preservation requirement unless explicitly changed.
- **#6: BLOCKED on its model-rights acceptance criterion** [I6]. Photo permission
  is evidenced, but research completion/working images do not satisfy that gate.
- **#7: BLOCKED on software/model/data licensing and source arrangement** [I7].
  Other release checks remain separate; the user alone performs the final video
  test after remaining work. Do not mark release cleared or close either rights gate.

## Primary sources (all accessed 2026-11-16)

- [U1] https://raw.githubusercontent.com/ultralytics/ultralytics/v8.4.189/LICENSE
- [U2] https://raw.githubusercontent.com/ultralytics/ultralytics/v8.4.189/pyproject.toml
- [U3] https://www.ultralytics.com/license
- [U4] https://raw.githubusercontent.com/ultralytics/ultralytics/v8.4.189/docs/en/help/contributing.md (also retrieved through Context7 at this version).
- [U5] https://www.ultralytics.com/legal/enterprise-software-license
- [G1] https://www.gnu.org/licenses/agpl-3.0.html#section13 (full text read).
- [V1] https://huggingface.co/Ultralytics/YOLOv8/raw/27f858f2dc238503a66ce10248cf7ec71a3ded5d/README.md
- [D1] https://universe.roboflow.com/ms3b/logos-teamx/dataset/1
- [D2] https://universe.roboflow.com/ms3b/logos-teamx
- [D3] https://universe.roboflow.com/plate-detection/plate_detection-tp5h9
- [D4] https://universe.roboflow.com/plate-detection/plate_detection-tp5h9/dataset/1
- [D5] https://universe.roboflow.com/plate-detection/plate_detection-tp5h9/model/1
- [C1] https://creativecommons.org/licenses/by/4.0/legalcode.en
- [C2] https://creativecommons.org/publicdomain/zero/1.0/legalcode.en
- [P1] https://commons.wikimedia.org/w/index.php?title=File:Lexus_LX_570_20090620_rear.JPG&oldid=1254744190
- [P2] https://commons.wikimedia.org/wiki/Template:Attribution (redirects to attribution-only template).
- [I6] https://api.github.com/repos/MS3B09/autoscan-ai/issues/6
- [I7] https://api.github.com/repos/MS3B09/autoscan-ai/issues/7

Not checked: full transitive-dependency/legacy-asset inventory, legal enforceability, private agreements or per-image ownership audit; none is certified.
