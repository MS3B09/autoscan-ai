---
name: AutoScan AI
description: Compare — real source and detection output on warm manila.
colors:
  paper: "#fae9c1"
  paper-3: "#f1eadb"
  sheet: "#fffcf5"
  image: "#fefdfb"
  ink: "#191b17"
  muted: "#5c584f"
  rule: "#b9af99"
  accent: "#e96f1b"
  accent-ink: "#191b17"
  accent-hover: "#db5f10"
  focus: "#8c3800"
  error: "#98281d"
  vehicle: "#0059b3"
  logo: "#00696c"
  plate: "#a92316"
typography:
  display:
    fontFamily: "'Red Hat Display', ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(2.5rem, 4.6vw, 4.4rem)"
    fontWeight: 900
    lineHeight: 1
    letterSpacing: "-.03em"
  workspace-headline:
    fontFamily: "'Red Hat Display', ui-sans-serif, system-ui, sans-serif"
    fontSize: "2.5rem"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "-.03em"
  compare-title:
    fontFamily: "'Red Hat Display', ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.875rem"
    fontWeight: 900
    lineHeight: 1
  workspace-title:
    fontFamily: "'Red Hat Display', ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: 1.15
  body:
    fontFamily: "'Red Hat Text', ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "'Red Hat Text', ui-sans-serif, system-ui, sans-serif"
    fontSize: ".9375rem"
    fontWeight: 500
    lineHeight: 1.55
  code:
    fontFamily: "ui-monospace, monospace"
    fontSize: ".8125rem"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  control: "6px"
  panel: "8px"
spacing:
  xs: "4px"
  sm: "8px"
  label: "12px"
  md: "16px"
  lg: "24px"
  columns: "32px"
  xl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.accent-ink}"
    rounded: "{rounded.control}"
    padding: "8px 16px"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
  button-secondary:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "8px 16px"
  button-secondary-hover:
    backgroundColor: "{colors.paper-3}"
  entry:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.accent-ink}"
    rounded: "{rounded.control}"
    padding: "8px 48px"
  input-file:
    textColor: "{colors.ink}"
    width: "100%"
  navigation:
    textColor: "{colors.ink}"
  comparison:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "24px"
  data-preview:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
  legend-label:
    textColor: "{colors.ink}"
---

# Design System: AutoScan AI

## Current refinement — 2026-11-17

The owner's Home-page refinement preserves this visual world but supersedes the
earlier content inventory: a supplied Nissan comparison, short workflow, three
detector descriptions with the supplied brand image, and detector/GitHub actions.
The centered shared shell is now `min(80%, 1440px)`, with 24px gutters at 1000px
and below and 16px gutters at 640px and below. Full-size links are now 44px
in-image SVG buttons opening a native dialog; close and Escape restore focus.
Credits/datasets remain linked in the footer; the licensing notice remains visible.
Historical sample JSON/CSV assets remain available for regression fixtures, not
promoted on the landing page. See `docs/design/showcase.md` for the updated brief.

## Overview

**Creative North Star: "Compare"**

Warm manila ground, dark ink rules, orange actions, heavy grotesk typography, and paired-image hierarchy describe the implemented authority. The showcase lets real source/output images lead; the detector carries the same materials into a quieter, native-control workspace. Comparison, not decoration or performance claims, supplies the emphasis.

This records shipped issue #6, approved Option A; it does not introduce a new world. Ground truth is `web/src/tokens.css`, `style.css`, `showcase.css`, `site.tsx`, `showcase.tsx`, and `main.tsx`. Product constraints live in `PRODUCT.md`; the surface-specific contract remains in `docs/design/showcase.md`.

**Key Characteristics:**
- Warm manila ground and dark ruled structure.
- Orange actions with dark ink text.
- Heavy showcase grotesks; quieter workspace hierarchy.
- Real paired imagery, readable data, and explicit limitations.
- Native controls, visible focus, and distinct responsive layouts.

Evidence: approved `.impeccable/mocks/option-a-compare.png`; actual `.impeccable/review/showcase-1536.png`, `desktop.png`, `mobile.png`, `detector-success-1440.png`, and `detector-success-390.png`. Reviewer handoff disposition is **ship for the four scored fixes**. No machine plate-gate pass is claimed: the user explicitly bypassed photo matching, permitting a licensed replacement photograph with real inference, not fabricated detections. Typography, palette, spacing, layout, and hierarchy retain reference authority.

## Colors

The palette is warm and paper-like, with one action accent and separate functional detection colors. Frontmatter values are normative; names match the CSS token suffixes. No additional tonal scale is established.

### Primary
- **Action orange** (`accent`, `accent-hover`): detector entry, sample downloads, and Detect. **Dark action ink** (`accent-ink`) remains the foreground: contrast is approximately **5.58:1** at rest and **4.67:1** on hover. The approved comp's white action text is not the shipped rule.

### Neutral
- **Warm manila** (`paper`): page ground. **Muted paper** (`paper-3`): empty media stages, context band, and secondary-button hover.
- **Warm sheet** (`sheet`): comparison and data containers, secondary buttons. **Image white** (`image`): contained workspace media background.
- **Dark ink** (`ink`): text and structural rules. **Muted ink** (`muted`): help, captions, credits. **Quiet rule** (`rule`): data and control separators.
- **Focus brown** (`focus`) and **error red** (`error`): interaction outline and error feedback, not decorative accents.
- **Vehicle blue**, **logo teal**, **plate red** (`vehicle`, `logo`, `plate`): legend outlines and result-label underlines. These are semantic categories, not secondary brand palettes; text labels carry meaning alongside color.

**The Dark Action Ink Rule.** Preserve dark ink on orange in both default and hover states; do not copy the comp's white button lettering.

## Typography

Red Hat Display supplies the grotesk headings and wordmark; Red Hat Text supplies prose, controls, and data labels. Locally imported weights are Display (600, 900) and Text (400, 500); system sans-serif entries are fallbacks, not the intended display face. Monospace is code-only.

- **Display:** frontmatter `display`; showcase headline and wordmark use the heavy weight (900). Wordmark size is (2rem), becoming (1.5rem) on mobile.
- **Workspace headline/title:** `workspace-headline` and `workspace-title` use (600); the headline becomes (2rem) on mobile. Do not make the operating workspace as heavy as the showcase.
- **Compare title:** `compare-title`; showcase image captions become (1.25rem) on mobile. Other showcase section headings use their existing fluid sizes, not a new universal scale.
- **Body/label:** regular prose (400), controls and labels (500). Paragraphs normally stop at (72ch); the centered showcase introduction deliberately removes that cap. Help/credits are smaller muted body text, not monospace.
- **Code:** `code` for the JSON/CSV previews only. Confidence, coordinates, and counts use tabular numerals within the body family.

**The Two Weights of Attention Rule.** Keep showcase display at 900 and workspace headings at 600; body text remains 400/500 and monospace remains code-only.

## Layout

The effective shared shell is `min(100% - 64px, 1440px)`, centered; the earlier 1360px declaration is overridden. The ruled header has a (68px) minimum height and wraps naturally whenever the wordmark and navigation no longer fit on one row, including widths just above the mobile breakpoint. Spacing uses the frontmatter steps; (24px) section rhythm, (32px) showcase columns, and (48px) larger separations do different jobs.

- **Wide:** showcase comparison has two equal image columns and a narrower legend (`1fr 1fr minmax(190px, .38fr)`). Images preserve their aspect ratio. Its container uses (16px 24px) padding. Workspace comparison uses two equal columns, (24px) gap/padding, and contained media rather than cropping.
- **At 1000px and below:** showcase legend moves beneath the still-paired images; structured data becomes two columns with introduction/downloads spanning both. Workspace controls become two columns.
- **At 640px and below:** shell becomes `calc(100% - 32px)`; header wraps navigation onto its own row. Showcase images **remain side by side**, with (12px) column gap and legend below; data/context/facts stack. Workspace controls, source/result comparison, and privacy section **stack**; comparison padding becomes (16px). Do not conflate these two mobile layouts.
- **Workspace media/results:** media stages use (4 / 3), minimum heights (260px; mobile 180px), contained images/videos with (520px) maximum media height. Mobile result rows expose field labels via `data-label` while retaining table markup and visually hidden headings. Code panes scroll inside their (128px) height instead of widening the page.

## Elevation & Depth

Flat surfaces; no box-shadow vocabulary is implemented. Warm sheet against manila, muted context paper, and thin rules establish depth. Hover changes fills or underline thickness. Active buttons/entry links move down (1px); reduced-motion preferences remove that movement. No animated transitions are defined.

## Shapes

Controls and action links have restrained rounded corners (`control`); comparison/data containers use `panel`. Dark structural borders are (1px); softer separators use `rule`. Legend swatches are small outlined rectangles (20 × 16px, 3px stroke, 2px corners), not clickable chips. There is no pill or floating-card system.

## Components

- **Buttons and entry links:** substantial, ink-bordered controls. Native buttons/file-selector buttons have at least (44px) height, label weight, and `button-secondary` treatment; Detect uses `button-primary`. Disabled controls use native `disabled`, not-allowed cursor, and (.55) opacity. Entry links navigate rather than upload: centered image entry is (372px) maximum width and (64px) minimum height on desktop, then auto-width/(52px) on mobile. Smaller sample-download links retain the same orange treatment. Focus is a (3px) focus-color outline offset (4px).
- **Inputs:** retain labeled native file, checkbox, and range controls, a fieldset/legend for object types, help associations, and a percentage output. The range is (25–100%, step 1), initially (40%). Uploading/holding a job locks the controls; no inference starts merely by selecting a file. A file-validation failure has an alert and retry action, not a success placeholder.
- **Navigation:** shared car wordmark, Project/Detector/GitHub links, `aria-current`, and decorative inline SVGs. Link targets remain links; preserve skip links and focusable main targets. Mobile uses a full-width navigation row, not an invented menu.
- **Comparison:** labeled Original/Detections figures on warm sheet. Showcase is a published sample with full-size links and a ruled category/confidence legend, explicitly not a live job or accuracy benchmark. Workspace begins with instructional empty wells and uses native video controls when needed; comparison exposes `aria-busy` during active work. Do not populate empty results with example boxes.
- **Feedback and results:** polite live status distinguishes validation, upload, queued, processing, cancelling, success, valid empty result, failure, cancellation, and expiry/unavailability. Errors use `role="alert"`; retries remain explicit. Video frame progress uses native `progress`. Empty success is not an error and can still expose downloads; failed work is not described as empty. Expiry clears unavailable results and invites a new detection; it does not imply persistence or automatic recovery.
- **Data and disclosures:** JSON/CSV previews have body-font headers, code-only contents, keyboard-focusable scroll regions, and an inset focus outline. Downloads preserve native link/button semantics and busy/disabled feedback. Result tables keep captions and readable labels. Native `details`/`summary` discloses logo classes; footer, photo provenance, original contributors, and dataset links stay legible.

The source discloses that model and dataset licensing is not yet cleared for public release. Preserve that disclosure and the replacement photograph's separate provenance; this visual handoff makes no model, license, deployment, or service-availability decision.

## Do's and Don'ts

### Do:
- **Do** preserve dark action ink, visible focus, labeled native controls, and reduced-motion behavior.
- **Do** keep the showcase image pair side by side on mobile while stacking the workspace comparison.
- **Do** show real inference and matching exports, including mistakes, provenance, and temporary-result limitations.
- **Do** retain Display 900/600, Text 400/500, and code-only monospace in their existing roles.

### Don't:
- **Don't** replace semantic links, buttons, inputs, tables, or disclosures with decorative imitations.
- **Don't** invent boxes, benchmark claims, OCR, persistence, automatic retries, or new service features.
- **Don't** add shadows, pills, decorative metadata kickers, or a new visual metaphor to this recorded system.
- **Don't** treat photo-matching bypass or the four-fix ship verdict as a machine plate-gate pass or licensing clearance.

Not canonized or repaired: legacy “Furrow” source-comment naming and the comp's white action text/generated sample detections are not new system rules; current source and the approved photo exception govern. No UI, model, or license files were changed.
