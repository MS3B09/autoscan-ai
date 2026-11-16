# #7 Netlify draft handoff — 2026-11-16

**Draft only; production release is not approved or complete.** The earlier
Netlify connection blocker is resolved. No inference, video test, production
publication, paid resource or billing upgrade occurred. #5/#6/#7 remain open.

**Superseded candidate:** the owner's later approved 1080p change has a new
backend/draft and a narrow local-video-test exception. Use
[the current 1080p handoff](issue-5-1080p.md), not this earlier draft URL. Results
below remain historical; they are not fresh 1080p inference/capacity evidence.

## Exact candidate

- Showcase: <https://6afb394cb63bcc5d8c896112--autoscan-ai-ms3b09.netlify.app/>.
- Detector: <https://6afb394cb63bcc5d8c896112--autoscan-ai-ms3b09.netlify.app/detect>.
- Project: **`autoscan-ai-ms3b09`**, team **`mosab04-ns`**.
- Site ID: `1661ca1f-7c9b-4f69-b8ee-635ac7a49eee`.
- Deploy ID: **`6afb394cb63bcc5d8c896112`**, state **ready**, context
  **deploy-preview**, `published_at: null`, site `published_deploy: null`.
- Frontend source: **`7fb3fc1189dc245d7f5cf65b530ce254aa02ccd5`**, already pushed.
  Later evidence-only commits do not rebuild/change this immutable candidate.
- Backend: <https://ms3b09-autoscan-ai-images.hf.space>, source
  **`b6c91e23f1b0fcb8bfb3ab65d906d53fbcc2e9b5`**. Final runtime metadata:
  **RUNNING**, current/requested **zero-a10g**, current/requested replicas **1**.

Use the immutable draft URLs above, **not** the unpromoted production hostname.
Git integration is deliberately **unlinked** to avoid automatic publication.
Existing projects were not modified. Do not create a duplicate Git-import project
or click "Deploy project" as if draft approval authorized production.

## Free plan, packaging and credentials

The owner supplied screenshots showing **298.8/300 Free plan credits** before
this draft. Authenticated account reads independently confirmed `type_name: Free`
before creation and after deployment. Current official
[plan documentation](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/)
states Free has a hard credit limit and no auto-recharge option. No plan, credit
purchase, paid add-on or billing setting was changed. This is not a measured
post-deploy credit debit/balance.

Rebuilt locally with locked dependencies and the public HTTPS backend URL;
typecheck/build passed (Vite 7.3.8; unchanged Node/npm/React/TypeScript setup from
the runbook). No Netlify Git build ran: its build-image reproducibility remains
unverified. Staged only `web/dist` plus `_redirects` and `_headers` generated
verbatim from `netlify.toml`; no application/source/model edit.

With the CLI bootstrap still unusable, used the documented file-digest API through
the owner's authenticated Netlify UI session, without extracting, printing or
saving credentials. Created an empty Git-unlinked site, then one deploy with JSON
**`draft: true`** and an 18-file SHA-1 map. Verified server **deploy-preview** context
and no published deploy before uploading. All 18 uploads returned 200. Final
metadata confirmed ready/preview/unpublished/unlinked/Free. No publish/restore call.

An over-strict guard initially halted before upload because the API did not echo
a `draft` boolean. Verified the request flag and returned preview context instead;
uploads resumed on the **same deploy ID**, not a duplicate. A sandbox import
attempt also failed before any deploy request; browser file inputs supplied the
artifact bytes instead. No Netlify authentication was sent to Hugging Face or
included in the published frontend.

[The artifact manifest](issue-7-netlify-artifacts.json) retains all 18 SHA-256 hashes.
Its staging ZIP hash is provenance only: upload used file digests, **not ZIP**.
All **16 public files** were fetched anonymously and matched the exact local bytes.
The two Netlify rule files were verified through actual routing/header effects.
Scoped credential/private-key/credential-URL/job-capability pattern scans found no
matches in staged or fetched artifacts. No `.env`, Python, checkpoint, source map,
developer adapter or visitor media was included. Unknown secrets and all internal
provider logs are not independently certified by that scan.

## Backend origin wiring

Added only the immutable HTTPS draft origin to `AUTOSCAN_ORIGINS`, preserving
both existing development origins:

```text
http://localhost:5173,http://127.0.0.1:5173,https://6afb394cb63bcc5d8c896112--autoscan-ai-ms3b09.netlify.app
```

This public-variable update restarted the Space; source/model/runtime pins,
hardware, replicas and secrets were unchanged. Health returned ready: retention
**1800 s**, max active **1**, max pending **2**. No production origin or wildcard
was added. Promotion needs separate approval and exact production-origin wiring.
Full installed-container versions were not remeasured.

## New permitted checks

| Boundary | Result / limits |
| --- | --- |
| HTTPS `/`, `/detect`, `/detect/` | **200**, exact `index.html`; native navigation and refresh also passed |
| Actual headers | **Passed**: `nosniff`, `no-referrer`, and camera/microphone/geolocation denial |
| Public artifacts | **16/16** SHA-256 matches; no scoped credential-pattern matches |
| Anonymous browser | Isolated Chromium context, job requests guarded; **zero job attempts**, **zero page runtime errors** |
| Native browser CORS | **Three OPTIONS preflights: 204**, exact draft origin allowed; preview POSTs **200 / 422 / 200**, `no-store`, matching allow-origin |
| Still preview | Attributed public Lexus source normalized to **1280×915**; original displayed, annotated panel honestly empty; no inference |
| Credential boundary | Actual preview request: **no Authorization, Cookie or Referer**, correct draft Origin; no owner token/capability |
| Keyboard settings | Three checkboxes toggle; empty selection disables Detect with readable status; confidence Home **25**, End **100**, restored **40**; no submission |
| Corrupt still image | **422** with readable corrupt/unsupported alert, Detect disabled; explicit valid selection restored preview; no automatic retry observed |
| Showcase keyboard/downloads | Skip link, visible focus, 24-brand disclosure and native **static sample** JSON/CSV downloads passed, not new live-job exports |
| Responsive layout | Both routes passed overflow checks at **320, 390, 640, 641, 700, 768, 800, 1280, 1440, 1536, 1920 px**; showcase controls in bounds |
| Visual review | Inspected **1440×1024** desktop and **390×844** mobile against Option A/approved photo exception: warm ground, Red Hat hierarchy, paired showcase and stacked mobile detector preserved |
| Mechanical design detector | Six existing UI/token sources: **`[]`**, no findings; no UI edit or design-system repair |

The 422 produced one expected failed-resource console entry, not a page runtime
error. Browser backend traffic contained only `/api/preview`. No video entry,
fixture, job, `/validate`, fabricated result, quota-error induction or inference
was exercised. No complete WCAG audit, screen-reader session, physical-device/
touch matrix or live-result workflow is claimed.

After recording the checks, removed the temporary browser job-submission guard
and network capture and left a clean detector page with no selected file/job.
The owner's handoff is not affected by test-only request interception.

Local captures (untracked, not deployed assets):
`.playwright-mcp/issue7-6afb394c-{showcase,detector}-{desktop,mobile}.png`.
Source/artifact/route evidence is retained independently of those files.
Impeccable reported the pre-existing stale `.impeccable/design.json` sidecar;
left unchanged. An optional `/impeccable document` refresh is separate work.

## Completion checks

- Final explicitly selected local suite: **29 passed, 0 failed, 0 runner-skipped**
  in **9.696 s** (13 image API, 8 developer adapter, 4 outgoing-credential and
  4 diagnostic CLI safety checks). Fake external compute/HTTP, no hosted jobs.
- **21 methods policy-deferred/not run**, not passes or runner skips. The complete
  50-method suite remains prohibited under the video/inference hold.
- Python typecheck: **passed**, seven files, using the runbook's mypy command.
  Frontend typecheck/build passed before packaging; only evidence/docs changed
  afterward, not the deployed application.
- Retained artifact JSON matched all staged hashes, ZIP and literal TOML rule
  conversions; document links and scoped credential/capability scans passed.
  `git diff --check` passed. No new test files or seams were introduced.
- Independent fixed-baseline Standards/Spec reviews: completed on evidence
  candidate **`9edf5d8`** against the existing owner-approved baseline
  **`cea69ae7f60c84ad8532eca803510283473fc6d2`**. Reports follow; this recording
  update does not change the deployed candidate.

The owner's licensing exception/unverified disposition and all credits/notices
are unchanged. These scoped checks do not establish legal clearance or a complete
public release.

### Standards

**0 findings; 0 actionable smell findings.** The independent read-only review
found no documented-rule violations. Historical evidence is separated from current
draft checks, approvals are bounded, deferred states stay unverified, and repeated
historical facts serve traceability rather than duplicated executable logic.

### Spec

**0 actionable defects; no unrequested scope.** The independent read-only review
confirmed the permitted draft-only work and artifact identifiers match the retained
observations. Live image/video/empty-result workflows, protected operations,
isolation/lifecycle, workload/failures/full installed runtime, the deferred full
suite and production approval remain explicit release gates—not passes from
preview validation. No operational rerun was performed by either reviewer.

Review totals: **Standards 0, Spec 0 actionable findings; no worst finding on
either axis.** This is not complete-release acceptance.

## Owner handoff and remaining tickets

1. **#5 / #7 — owner's final candidate video check:** use the detector URL above
   and one representative accepted short clip. Confirm settings, processing,
   actual MP4 playback, MP4/JSON/CSV downloads and Delete now; report against this
   exact deploy ID. Do not silently add retries, cancellation/expiry or load tests
   to that reserved run. No agent-run inference is approved.
2. **#7 — safeguards:** preview success does not establish live anonymous inference,
   valid empty results, protected result/download/cancel/delete CORS, visitor
   isolation, cleanup/retention, resource behavior or quota/cold-start/restart
   failures. Retain prior evidence and explicit unverified dispositions; additional
   quota-consuming checks need approval. The owner run does not accept every gate.
3. **#5:** hosted active-video cancellation and video-specific real 30-minute expiry
   remain unverified. **#6:** formal closeout retains the owner's licensing
   exception/unverified disposition and all notices; no new licensing hold.
4. **#7 — production:** no promotion or Git linking yet. Obtain separate approval
   after remaining required gates are resolved; promote this same deploy rather
   than rebuilding different bytes. Keep #7 and parent #1 open.
