# Reproduce the anonymous browser probes

Open **https://example.com** in a browser, then its developer-tools Console.
Run these snippets there, not on the `.hf.space` origin. They use native browser
`fetch`, no packages, cookies, HF token, owner credentials, or account login.
An exception is a failed probe, not a passing or skipped check. Preserve the
returned result and the Space revision when recording new evidence.

**The inference snippet submits one real GPU job and consumes anonymous quota.**
Do not run it when the platform reports an exhausted duration quota or runs limit;
wait for the platform's reset. The recorded issue #2 successes predate exhaustion.
These are the recorded probes with explicit assertions added for repeatability;
they were not rerun after documentation because the anonymous runs limit had
already been reached.

## Image and every-frame video completion

```javascript
await (async () => {
  if (location.origin !== "https://example.com") throw Error("Use the cross-origin probe page");
  const endpoint = "https://ms3b09-autoscan-ai-validation.hf.space/gradio_api/call/validate";
  const started = performance.now();
  const submission = await fetch(endpoint, {
    method: "POST", credentials: "omit",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data: [] }), signal: AbortSignal.timeout(60000),
  });
  if (!submission.ok) throw Error(`Submission: ${submission.status} ${await submission.text()}`);
  const { event_id } = await submission.json();
  const response = await fetch(`${endpoint}/${event_id}`, {
    credentials: "omit", signal: AbortSignal.timeout(180000),
  });
  if (!response.ok) throw Error(`Completion stream: ${response.status}`);
  const stream = await response.text();
  const complete = stream.split(/\r?\n\r?\n/).find(block => /^event: complete\r?\n/.test(block));
  if (!complete || /event: error/.test(stream)) throw Error(`No successful completion: ${stream}`);
  const data = complete.split(/\r?\n/).find(line => line.startsWith("data: "));
  const report = JSON.parse(data.slice(6))[0];
  const check = (condition, label) => { if (!condition) throw Error(label); };
  check(report.device === "cuda" && Boolean(report.gpu), "Real GPU required");
  const hashes = {
    logo: "52e8aceec272ba35decc6b85f61cb21af06a4c14f9f245cfedb22caf465cf356",
    plate: "aa9742bb9fe5728cbe74027a9c4f8842d6c11f1423903b8ec8fc97e05e6293bb",
    vehicle: "31e20dde3def09e2cf938c7be6fe23d9150bbbe503982af13345706515f2ef95",
  };
  for (const [name, hash] of Object.entries(hashes)) {
    check(report.models[name].sha256 === hash, `Untrusted ${name} checkpoint`);
  }
  check(Object.keys(report.models.logo.classes).length === 24, "24 logo classes required");
  check(report.models.logo.classes[16] === "peugeot", "Raw logo identity changed");
  check(report.models.plate.classes[0] === "0", "Raw plate identity changed");
  check([2, 5, 7].map(id => report.models.vehicle.classes[id]).join() === "car,bus,truck", "COCO identities changed");
  check(report.image.detection_count > 0, "Image compatibility fixture must detect objects");
  const video = report.video;
  check(video.source_frames_decoded === 300 && video.frames_written === 300 && video.frames_decoded === 300,
    "Every accepted source frame must be processed and decoded");
  check(video.width === 1280 && video.height === 720 && video.duration_seconds === 10,
    "Expected representative ten-second 720p clip");
  check(video.source_bytes <= 20000000 && video.source_sha256 ===
    "b1485225e56b5117d31990163238468766175c5188c1169d828905a834c92015", "Unexpected capacity fixture");
  return { origin: location.origin, credentials: "omit", event_id, stream,
    elapsed_seconds: (performance.now() - started) / 1000, report };
})();
```

The server's diagnostic command validates finite, positive, in-bounds boxes and
unchanged checkpoint digests before returning. This probe checks its completed
report, not accuracy or the future production upload/export API.

## Temporary-result isolation and deletion (no GPU)

```javascript
await (async () => {
  if (location.origin !== "https://example.com") throw Error("Use the cross-origin probe page");
  const base = "https://ms3b09-autoscan-ai-validation.hf.space";
  const request = (path, options = {}) => fetch(base + path, {
    credentials: "omit", signal: AbortSignal.timeout(30000), ...options,
  });
  const probes = [];
  const statuses = {};
  try {
    for (let index = 0; index < 2; index++) {
      const response = await request("/isolation-probes", { method: "POST" });
      if (!response.ok) throw Error(`Create probe: ${response.status}`);
      probes.push(await response.json());
    }
    const [first, second] = probes;
    const path = `/isolation-probes/${first.id}`;
    const own = { Authorization: `Bearer ${first.token}` };
    const other = { Authorization: `Bearer ${second.token}` };
    statuses.own_read = (await request(path, { headers: own })).status;
    statuses.no_token_read = (await request(path)).status;
    statuses.other_token_read = (await request(path, { headers: other })).status;
    statuses.other_token_delete = (await request(path, { method: "DELETE", headers: other })).status;
    statuses.gradio_file = (await request(`/gradio_api/file=${first.path}`)).status;
    statuses.legacy_file = (await request(`/file=${first.path}`)).status;
    statuses.own_delete = (await request(path, { method: "DELETE", headers: own })).status;
    statuses.read_after_delete = (await request(path, { headers: own })).status;
    const expected = { own_read: 200, no_token_read: 404, other_token_read: 404,
      other_token_delete: 404, gradio_file: 403, legacy_file: 404,
      own_delete: 204, read_after_delete: 404 };
    for (const [name, status] of Object.entries(expected)) {
      if (statuses[name] !== status) throw Error(`${name}: ${statuses[name]}, expected ${status}`);
    }
    return { origin: location.origin, credentials: "omit", statuses };
  } finally {
    for (const probe of probes) {
      await request(`/isolation-probes/${probe.id}`, {
        method: "DELETE", headers: { Authorization: `Bearer ${probe.token}` },
      });
    }
  }
})();
```

Do not publish the temporary capabilities. Only the status summary needs to be
retained. The separate hosted integration test reproduces server-side expiry by
waiting 31 seconds without deleting or maintaining a browser connection:

```powershell
$env:AUTOSCAN_VALIDATION_URL='https://ms3b09-autoscan-ai-validation.hf.space'
python -m unittest discover -s tests -p test_hosted_validation.py -k temporary_result -v
```

These probes establish the bounded fixed-JSON mechanism only. Production media
isolation, cancellation, browser playback, and 30-minute retention are not tested.
