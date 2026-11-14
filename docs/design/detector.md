# Detector surface

Mode: Operate. Audience: a portfolio visitor trying one image, without an account.
The visual authority is approved Option A (see `mockup-round.md`), not a new theme.
The showcase and export controls belong to later tickets.

## Direction contract

**Thesis:** select, inspect, then explicitly detect. The comparison is the main
working object; no demonstration boxes or invented counts fill its empty state.

**Own-world:** warm manila, near-black ink, orange primary action, grotesk text,
fine rules, shallow corners. Tokens live in `web/src/tokens.css`; the detector
inherits the approved system without changing its reference image.

**Story:** choose a supported image, see its validated/oriented source, choose
objects and confidence, start inference, inspect real labels/boxes, delete the job.
Failure and successful empty results must read differently.

**First viewport:** plain top navigation, compact task heading, labelled upload
and native settings, explicit action, stable live feedback, then equal original
and annotated image areas. At phone width these stack without horizontal scroll.

**Form:** paired-image workbench, pinned by the parent spec and approved Option A;
seed: none (no new direction draw). No marketing hero or generated imagery.

**Finish:** unreviewed and undocumented is unfinished; this build ends with the
finish review, the verdict, DESIGN.md, and every shipping raster carrying its
provenance. This is an extension of the existing approved visual world, so it
preserves that world rather than introducing a replacement DESIGN.md. No rasters
ship in the frontend: source and result images arrive only at runtime.

## Verification

Desktop and mobile renders and the real-HTTP local workflow were checked in
Edge. The local empty-result compute substitute is not hosted inference evidence.
See `../evidence/issue-3-verification.md` for the review outcome and remaining gates.
