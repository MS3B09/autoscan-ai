# Quota messages and local developer browser access — 2026-11-15–16

## Scope

User-requested follow-up to #6: show a platform-provided reset timestamp in quota
errors and allow local browser testing with the developer's personal free HF
allowance, while public visitors remain anonymous. No deployment, paid resource,
credential rotation, or public authentication flow is included.

## Implemented

- The pinned `spaces==0.51.3` timed quota error is parsed as a bounded positive
  timedelta (at most 24 hours), rounded up, and exposed as optional `retry_at`
  epoch seconds. Only the timestamp and sanitized category leave the backend.
- The HTTP message includes UTC. The browser's alert uses a visible `<time>`
  with local date/time and timezone for both job failures and submission-time
  quota rejections. Missing/malformed timing has an explicit
  unavailable fallback; it is not inferred from midnight or the error time.
- `python -m scripts.dev_api` prompts for a READ token without echo or cached
  credential fallback. Startup verifies account `MS3B09`, non-Pro status, READ
  role, and free quota. Per-submission preflight checks at least 60 free seconds
  and a remaining run, rejecting unknown quota data or known paid tiers/usage.
- The adapter binds only `127.0.0.1:7862`, enforces the exact API Host/frontend
  Origin and loopback peer, bounds uploads to 20 MB/30 seconds, restricts methods
  and routes, disables environment proxies and redirects, suppresses cookies,
  sanitizes failures, and does not automatically retry submissions.
- Only new-job submissions receive the HF token. Existing-job operations retain
  their per-job capability; preview/health remain anonymous. Browser UI clearly
  identifies local developer mode. Setup/cleanup is documented in
  [authenticated-image-tests.md](../authenticated-image-tests.md).

## Verification

- Full local suite: `python -m unittest discover -s tests -v` — **40 passed,
  10 explicitly skipped** (hosted/model integration prerequisites absent).
- Focused developer HTTP suite: **8 passed**, including credential separation,
  account/tier rejection, Origin/Host/peer enforcement, route allowlist, bounded
  uploads, quota-reset selection/fallback, malformed allowance rejection, and
  sanitized transport/redirect/token-echo failures without submission retry.
- `python -m mypy image_service scripts/dev_api.py --ignore-missing-imports
  --follow-imports skip --check-untyped-defs` — passed.
- `npm run build` in `web/` — TypeScript check and production build passed.
- `tests/browser_detector_states.js` — simulated queued, processing, success,
  empty, quota error (with and without timing), cancelled, expired, and unavailable
  states passed. Includes capability headers, keyboard downloads, deletion focus,
  submission-time quota rejection with/without timing and malformed timestamps,
  and 390/1440px layouts.
- `tests/browser_developer_access.js` — passed against the real local adapter
  with test-only external Hub/Space HTTP replies: preview without inference,
  explicit submission, result, keyboard JSON download, deletion, capability-only
  browser authentication, and 390/1440px layout checks. Screenshot evidence is
  local under `.impeccable/review/`, not a shipping asset.

## Review

Two independent reviews covered changes since `a3be322`, including this staged
follow-up, and connected callers/tests. The first attempt hit the usage limit;
both reviews completed after the user authorized continuation on November 16.

### Standards

No documented-standard breaches or actionable heuristic smells found. The review
checked the API/security contract, domain vocabulary, UI standards, and focused
HTTP tests; it did not establish live hosting behavior.

### Spec

One partial implementation found and fixed: submission-time HTTP 429 responses
discarded `retry_at`, so only job-status failures received browser-local timing.
`APIError` now preserves valid timing, and both alert paths share the same local
date/time presentation. A browser regression failed before the fix and passes
afterward, including absent/malformed timing fallbacks. Live quota attribution
remains an explicit verification blocker, not a passing claim.

Review totals: Standards **0 findings**; Spec **1 finding, fixed**. No outstanding
new implementation findings; the existing rights/release gates remain open.

## Limits / release gates

No real dedicated READ token was supplied, so live browser authentication, quota
attribution, and GPU execution are **not verified** by these checks. The browser
replay uses fake credentials and previously published result bytes, never GPU
inference. The temporary replay and developer frontend are stopped after checking.

The public backend still needs an explicitly authorized deployment for new reset
messages. HF sometimes omits timing; an exact reset cannot then be shown. A quota
preflight is not an atomic reservation and does not guarantee capacity; keep paid
usage disabled. Loopback restrictions do not protect against malicious local
processes or code on the trusted frontend origin. Existing #6 model/dataset rights
and #7 release gates remain unresolved; this change does not clear them.
