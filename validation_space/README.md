---
title: AutoScan AI Compatibility Check
sdk: gradio
sdk_version: 6.32.0
python_version: 3.10.13
app_file: app.py
---

# Temporary backend compatibility check

This is a diagnostic Space, not the finished portfolio application. It loads the
unchanged custom logo and plate checkpoints plus the referenced standard YOLOv8n
checkpoint, then runs the existing project composite and all 300 frames of a
ten-second, 1280×720 traffic clip. It accepts no visitor files and returns counts, hashes, runtime versions,
and timings—not downloadable media. Generated diagnostic media is removed after
the call. A successful result is **not** an accuracy benchmark, throughput guarantee, browser
playback check, or proof of future production job isolation, cancellation, or expiry.

## Traffic fixture attribution

`fixtures/traffic-10s.mp4` is an excerpt of **Traffic flow in front of UI .webm**
by **Adefanike**, from Wikimedia Commons:
<https://commons.wikimedia.org/w/index.php?title=File:Traffic_flow_in_front_of_UI_.webm&oldid=948619853>.
Source: <https://upload.wikimedia.org/wikipedia/commons/c/c6/Traffic_flow_in_front_of_UI_.webm>.
Licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
The excerpt and any annotated derivative retain that license. Changes: first ten
seconds, scaled to 1280×720, normalized to 30 fps, silent H.264 MP4. This is one
real traffic scene for capacity observations, not an accuracy evaluation set.
Commons flags the source for license review; this must be reviewed before public
portfolio release.

## Temporary-result feasibility probe

`POST /isolation-probes` creates one small diagnostic JSON file and returns its
identifier and a fresh per-result capability. `GET` and `DELETE` on
`/isolation-probes/{id}` require `Authorization: Bearer <capability>`. Missing,
wrong, or expired capabilities get 404. At most four probes can exist at once.
Files are deleted after **30 seconds** by a server-side timer, or immediately on
authorized DELETE. Private directories are blocked from Gradio's generic file
routes, even when the path is known. Responses are not cacheable and Uvicorn
access logs are disabled. These routes accept no visitor media.

This accelerated fixed-JSON experiment is not the production job lifecycle:
30-minute retention, inference cancellation, uploads, annotated media, exports,
and their cleanup remain work for subsequent tickets. Restart discards probes.

The original project and contributor credits are at
<https://github.com/MS3B09/autoscan-ai>. The source example originates in that
repository; do not treat it as a clean evaluation fixture.
