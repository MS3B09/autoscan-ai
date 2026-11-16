# Ultralytics: public portfolio demo with private training materials

Research/access date: **2026-11-16**. First-party evidence, not legal advice.
Scope: Ultralytics' own published position and grants; separate AGPL/architecture review remains necessary.

## Short answer

**No published Ultralytics exception was found permitting this exact arrangement merely because it is a free, personal, noncommercial demo.**
Ultralytics offers personal projects a free **AGPL-3.0 compliance route**, not a disclosure waiver.
Its current licensing FAQ and version-pinned guidance expressly include training scripts and configurations in the source-publication scope [1–3].
Consequently, public frontend/backend code plus the two fine-tuned `.pt` files alone does **not establish compliance with the vendor's stated requirements** while training materials remain private.
**Recommendation: do not clear the public-demo licensing gate on a personal/noncommercial exception; keep it blocked under the owner's unchanged publication boundary.**
This is not a finding that every historical notebook is legally mandatory, or that an Enterprise purchase is the only legally possible outcome.

## Confirmed setup and applicability

- AutoScan is a free public portfolio application; application code and two trained weights may be public.
- MS3B09 confirms training both custom models on the repository-linked Roboflow datasets, starting from `yolov8n.pt`; notebooks/configuration will not be shared.
- Inference is pinned to `ultralytics==8.4.189`; that does not establish the historical trainer version.
- These owner-confirmed facts are recorded in [release-licensing.md](release-licensing.md#owner-clarification--2026-11-16); no further provenance questionnaire is needed for this vendor-policy answer.
- The custom models are fine-tuned from Ultralytics weights, so the vendor's express trained/fine-tuned-model statements address this setup directly [1].
- Roboflow dataset permissions are separate: neither public dataset links nor trainer ownership supplies an exception to Ultralytics' licensing position [1,4 §11.6].

## Exact official statements

### Personal projects: conditional free route, not an exception [1]

Section **Choosing your license → Free / AGPL-3.0** says:
> This license is the right one for you if you are comfortable open-sourcing your entire project under AGPL-3.0.

The included use cases name:
> Personal projects, learning, and experimentation

Section **Paid / Ultralytics Enterprise License** also names:
> Customer-facing solutions where you do not want to publish code, configs, training scripts, and related components

Read together, these do not authorize withholding training source just because visitors pay nothing.

### Licensing FAQ: models and complete corresponding source [1]

Under **What license do I need to use Ultralytics YOLO?**:
> If you use Ultralytics YOLO code, models, architectures, training pipelines, or trained/fine-tuned models, you must either:
> - Open-source your entire project under AGPL-3.0, or
> - Obtain an Ultralytics Enterprise License.

The same answer says compliance includes:
> the larger application, modifications, scripts, configuration files, and, where applicable, model weights.

Under **Are Ultralytics YOLO trained models licensed under the AGPL-3.0 license?**:
> Yes. All Ultralytics YOLO trained models fall under the AGPL-3.0 License by default. The AGPL-3.0 License covers the training code and the models produced by that training code.

These are the vendor's assertions; this note does not independently decide the copyright status of every training output.

### Version-pinned guidance: publication includes training and configuration [2,3]

At **v8.4.189**, `docs/en/help/contributing.md`, **How to Comply with AGPL-3.0 → Publish Your Source Code**, lists:
> Scripts for training, validation, and inference.
> Model weights if modified or fine-tuned.
> Configuration files, environment setups (`requirements.txt`, `Dockerfiles`).

It also lists backend/frontend web-application code and training data **“if required to run/retrain and redistributable.”**
The tagged root `CONTRIBUTING.md` gives the same substantive publication scope (its training bullet omits “and”); the current rendered guide repeats it [2,3].
Context7 resolved Ultralytics and queried `/ultralytics/ultralytics/v8.4.189`; both tagged files were also fetched directly, rather than relying on current `main` alone.

## Policy is not an extra contractual exception

The tagged `LICENSE` is the GNU AGPLv3 text; no added personal-demo/training-secrecy exception appears there [5].
Ultralytics' current **Terms of Service §5.3** says:
> In the event of any conflict between these Terms and the applicable Ultralytics YOLO Model license, the license terms shall prevail in respect of your use of the models.

Section **5.5** adds:
> Nothing in these Terms is intended to restrict any rights granted under applicable open-source licenses, including the AGPL-3.0.

Accordingly, broad website claims are evidence of the vendor's position, not a substitute for applying the actual license to the covered work.
The examined sources do not say that every original exploratory notebook, unrelated experiment, secret, or credential must be published; nor do they approve substituting only inference code for required training source.
No general public personal/noncommercial waiver or project-specific grant was evidenced. A searched student-license URL currently returns the legal index, not usable exception terms [6].
The official R&D alternative is also **not a free public-demo exception**: its grant is **“Subject to payment of the applicable Fee”**, and §4 prohibits **“Provide services to third parties using the Software”** [7].

## Practical routes and the remaining decisive issue

- **Free open route:** comply with the applicable AGPL scope and publish the required corresponding source, licensing/notices, fine-tuned weights and setup material; Ultralytics' guidance includes training scripts/configs. This conflicts with the stated boundary if those materials are required. Do not publish private files or silently relicense contributors' work.
- **Paid proprietary alternative:** Enterprise is the vendor-advertised way to avoid the open-source requirements [1]. Its actual agreement §5 requires an **Annual Fee**; scope and coverage for already-trained models must be established by an actual agreement, not assumed from a quote [8]. No purchase/contact is authorized or performed.
- **Unchanged boundary:** hold public release. An explicit applicable grant could change the result, but none is evidenced and a free exception is not promised.
- **Remaining decisive issue:** whether the covered work's legally required corresponding source can be complete without the withheld training materials, or an actual applicable alternative grant covers that withholding. The vendor pages do not resolve that narrower legal/source-form question. This is not missing trainer identity, dataset provenance, or owner permission to publish app/weight files.

## Primary sources (all accessed 2026-11-16)

1. https://www.ultralytics.com/license — Choosing your license; licensing FAQs quoted above.
2. https://raw.githubusercontent.com/ultralytics/ultralytics/v8.4.189/docs/en/help/contributing.md — Open-Sourcing Your YOLO Project / How to Comply; current rendered counterpart: https://docs.ultralytics.com/help/contributing/ .
3. https://raw.githubusercontent.com/ultralytics/ultralytics/v8.4.189/CONTRIBUTING.md — Open-Sourcing Your YOLO Project; final licensing FAQ.
4. https://www.ultralytics.com/legal/terms-of-service — page dated 2026-10-02; §§5.3, 5.5, 11.6.
5. https://raw.githubusercontent.com/ultralytics/ultralytics/v8.4.189/LICENSE — GNU AGPLv3; vendor-hosted counterpart: https://www.ultralytics.com/legal/agpl-3-0-software-license .
6. https://www.ultralytics.com/legal/ultralytics-student-software-license-terms — retrieved legal index; general docs FAQ also checked: https://docs.ultralytics.com/help/FAQ/ .
7. https://www.ultralytics.com/legal/ultralytics-rd-license-terms-multi-project — page dated 2026-03-03; §§2–4.
8. https://www.ultralytics.com/legal/enterprise-software-license — introduction; §§1, 2, 5, 18.

Not checked: enforceability, private agreements, private training files, credentials, or weight contents; no tests/builds/inference/GPU/video activity, vendor contact, purchases, commits or GitHub comments.
