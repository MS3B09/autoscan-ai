# #7 local release preparation — 2026-11-16

**Local preparation only; not a public release.** No inference, video tests,
browser submissions, source push, Space change or Netlify deployment ran.
The owner-approved fixed review baseline is
`cea69ae7f60c84ad8532eca803510283473fc6d2`. Unrelated untracked tooling is excluded.

**Subsequent approved work:** [backend-update evidence](issue-7-backend-update.md)
records the later Space update and GitHub push. This document's no-push/deployment
statements describe the earlier preparation phase; Netlify draft remains pending.

## Changes and inventory

- [Release runbook](../release-runbook.md): supported runtimes, separate dependency
  setup, pinned vehicle-model acquisition/hash validation, public configuration,
  secret placement, explicit Space mapping/atomic update, draft deployment,
  same-artifact promotion and non-destructive rollback.
- `netlify.toml` now pins Node **24.13.0**, matching local validation. Existing
  `/detect` rewrites and security headers are unchanged. No app/weight changes.
- Root README links the current architecture's setup/status without replacing
  original contributors, datasets, legacy Streamlit code or requirements.
- npm **11.6.2**; lockfile resolutions: React/React DOM **19.3.1**, Vite **7.3.8**,
  TypeScript **5.9.3**, both Red Hat font packages **5.3.0**. Lockfile unchanged.
- Local Python **3.13.12**; contract packages: FastAPI **0.136.1**, Starlette
  **1.0.0**, HTTPX **0.28.1**, Pillow **12.1.1**, PyAV **17.1.0**, AnyIO **4.12.1**,
  mypy **1.19.0**. These are not the hosted inference package versions.
- Hosted configuration remains Python **3.10.13** and the existing direct pins in
  `image_service/requirements.txt`. The retained `web/public/examples/lexus.json`
  reports Python 3.10.13, Torch 2.8.0, Torchvision 0.23.0, Ultralytics 8.4.189,
  NumPy 1.26.4, Pillow 11.3.0, Gradio 6.32.0, spaces 0.51.3, FastAPI 0.162.5,
  Starlette 1.7.0 and PyAV 17.1.0. This is **historical sample metadata**, not a
  fresh deployed inventory or a fully locked transitive environment.
- Fresh SHA-256 checks of `models/logo.pt` and `models/plate.pt` matched
  `52e8aceec272ba35decc6b85f61cb21af06a4c14f9f245cfedb22caf465cf356` and
  `aa9742bb9fe5728cbe74027a9c4f8842d6c11f1423903b8ec8fc97e05e6293bb`.
  Generic vehicle digest/source are retained pins in the runbook; its download
  example was syntax-checked, **not executed**, and no model was deserialized.

## Checks — new results, not the earlier full-suite evidence

| Check | Outcome |
| --- | --- |
| Individual image API contract file | **13 passed**, fake external compute; real image decoding, local HTTP/storage |
| Individual developer adapter contract file | **8 passed**, fake Hub/Space HTTP, no real credential or quota request |
| Final explicitly selected safe suite | **29 passed, 0 failed, 0 runner-skipped** in 5.709 s: 13 image + 8 adapter + 4 outgoing-credential + 4 diagnostic CLI safety methods |
| Excluded tests | **21 not run / policy-deferred**, not runner skips or passes. Static AST count found 50 methods; no unfiltered discovery. Includes local video, diagnostic-video and all opt-in hosted/model checks. |
| Python typecheck | **Passed**, seven files: `python -m mypy image_service scripts/dev_api.py --ignore-missing-imports --follow-imports skip --check-untyped-defs` |
| Frontend typecheck/build | **Passed** in both isolated clean lockfile install and restored checkout, public HTTPS API URL set at build time |
| Configuration/doc static checks | **Passed**: TOML parse, Node pin, unchanged rewrite/header values, mapped module existence, checkpoint example compilation |
| Checkpoint preservation | **Passed** for both existing custom files; generic-model acquisition/loading not rerun |
| Local source/history/artifact credential-pattern scan | **Passed within stated pattern scope**, below; not a certification of unknown credentials or deployed logs |
| Final Standards/Spec review | Completed on candidate `0e28355` against the fixed baseline: Standards found one P3 status-wording inconsistency, resolved by this review-recording update; Spec found zero actionable defects. See separate reports below. |

The exact safe selections and commands are in
[the runbook](../release-runbook.md#permitted-local-checks-during-the-hold).
No new tests/seams were introduced. The applicable subset was run together at the
end; a complete 50-method suite was deliberately **not run**, respecting the hold.
The older 40-passed/10-skipped full-suite result remains historical.

### Failed attempts and recovery

An initial in-place `npm ci` **failed** with Windows `EPERM` unlinking an in-use
Rollup native binary and partially removed ignored dependencies. An attempted
in-place repair timed out; a subsequent typecheck failed because `tsc` was absent.
No existing process was stopped. Offline clean install also **failed** because
the TypeScript tarball was not cached. These attempts are not passed checks.

Copied only tracked frontend inputs to
`C:\Users\User\AppData\Local\Temp\opencode\autoscan-release-7-clean`, then
`npm ci --fetch-retries=0 --fetch-timeout=20000 --no-audit --no-fund` **passed**
(23 packages). Its build/typecheck passed. Restored 199 missing/different ignored
dependency files from that exact install, leaving byte-identical locked binaries
untouched; the checkout build/typecheck then passed too. No source or lockfile
was altered by dependency recovery. Both output trees had identical file sets and
SHA-256 bytes. This workaround does not establish a clean Netlify build.

### Artifact and credential check scope

The scan covered **91 current source files** (90 tracked plus the new runbook at
scan time), **105 locally reachable Git revisions**, and **16 fresh public files**.
It looked for recognizable HF/GitHub/Netlify token prefixes, AWS access-key IDs,
private-key headers and URLs containing basic-auth credentials. No values were
printed; no credentials were read from credential stores. Binary source/model
files were excluded from text checks; all output artifacts were inspected.
The final source scan included **92 files**, covering the new evidence/checklist
text; it found no recognized patterns. Local Markdown-link checks also passed.

The build contained only HTML, JS/CSS, local fonts and the attributed example
image/PNG/JSON/CSV assets. No `.env`, Python, checkpoint or source-map files were
published. Public JSON contained no `token`, `authorization` or `cookie` keys.
The configured public HTTPS backend URL was present. The developer-mode loopback
comparison literal is ordinary bundled code, not the selected public API URL or
a credential. No deployment credential or visitor capability is needed to build.

Key artifact SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `index.html` | `52a83baad4438c38caa2f0018d4e8908217fa4f584cd7791dd13d11f86195cc4` |
| `assets/index-D6a7pq_7.js` | `d20b511be3d46ae7e49fb6c0d5f11991d314af4217c1c07fa278a7dd51dbad48` |
| `assets/index-CJm8rRKw.css` | `2bebba316cddd2c6c4b0e4099ce413b862503cbc3348db29389874dd08837639` |

Aggregate manifest SHA-256:
`d461303a05eaf4928af74e76077a14103fb7bfc8a9501305ea1e5124d8d1e45e`.
Reproduce by sorting the 16 relative POSIX paths lexically, concatenating
`path + "\t" + sha256(file_bytes) + "\n"` as UTF-8, then SHA-256 hashing that text.
Recheck the final approved deploy artifact: byte-identical local builds do not
prove any Netlify candidate, deployed origin, URL or public-log safety.

## Standards

Independent read-only review of `git diff cea69ae7f60c84ad8532eca803510283473fc6d2...HEAD`
at candidate `0e28355` found one **P3** documentation inconsistency: the checklist
said "final review recorded" while this evidence still said "Pending". That
overstated review completion under the owner's requirement to distinguish
unverified checks. **Resolved:** this update records both completed reviews and
removes the pending-review handoff instruction. No baseline smell findings.

## Spec

Independent read-only review of the same candidate against current #7/#1 found
**zero actionable defects or scope creep**; the permitted preparation scope is
satisfied. It confirmed that deployed workflow, origin/isolation/lifecycle,
runtime/resource/accessibility, owner video and full-suite requirements remain
approval-dependent release gates, not passes from this local work. No tests,
inference, credentials or deployment were used by either reviewer.

Review totals: **Standards 1 finding (P3 wording; resolved); Spec 0 actionable
findings.** The review does not authorize or establish a completed release.

## URLs, gates and next action

- Existing service: <https://ms3b09-autoscan-ai-images.hf.space>;
  repository: <https://huggingface.co/spaces/MS3B09/autoscan-ai-images>.
  Last retained service revision:
  `dbafd5210c59c719fdce59556d400be4f870859d`; **not freshly queried or updated**.
- Diagnostic Space: <https://huggingface.co/spaces/MS3B09/autoscan-ai-validation>;
  pinned model-provisioning revision `da8e0cdd5a03d0d3c60fab3f942910ef6472310b`.
  No `/validate` call occurred.
- Netlify candidate/production URL and deploy ID: **not created/verified**.
- **#7:** obtain approval for backend quota-message update and Netlify draft;
  verify native deployed-origin routing/headers/accessibility and permitted image
  preview, then record exact revisions/runtime/free-tier settings. Anonymous
  processing, isolation/lifecycle/retention/resource gates still need their own
  evidence or explicit unverified disposition; no full release acceptance claimed.
- **#5 / #7:** owner-only final representative video check after preparation.
  Hosted active cancellation and video-specific 30-minute expiry remain unverified;
  do not silently add more quota-consuming tests.
- **#6 / #7:** retain the licensing owner exception/unverified disposition and all
  notices. No new licensing hold, legal pass or request for private training data.

Keep #5/#6/#7 open. Promotion, any additional inference and public source push
remain separately approval-gated. No paid plan/hardware/billing change occurred.
