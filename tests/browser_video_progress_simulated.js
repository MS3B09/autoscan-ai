// Simulated browser workflow: no video bytes, codec work, or hosted inference.
async (page) => {
  const origin = new URL(page.url()).origin;
  const workspace = await page.context().newPage();
  await workspace.addInitScript(() => {
    const requests = [];
    window.uploadStubs = requests;
    window.XMLHttpRequest = class {
      upload = {};
      open(method, url) { this.url = new URL(url); this.method = method; }
      getResponseHeader() { return this.response.type; }
      send(file) {
        requests.push(this);
        this.upload.onprogress({ lengthComputable: true, loaded: file.size / 2, total: file.size });
      }
      abort() { this.onabort(); this.onloadend(); }
      respond(status, data, type = 'application/json') {
        this.status = status;
        this.response = new Blob([data], { type });
        this.onload();
        this.onloadend();
      }
    };
    document.addEventListener('error', event => {
      if (event.target instanceof HTMLVideoElement) event.stopPropagation();
    }, true);
  });
  let state = 'queued';
  let frames = 0;
  await workspace.route('**/api/**', route => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    if (request.method() === 'POST') throw Error('Simulated uploads must not hit the network');
    if (path.endsWith('/video')) return route.fulfill({ contentType: 'video/mp4', body: 'test stub' });
    return route.fulfill({ json: { media_type: 'video', state, frame_count: 463, processed_frames: frames,
      queue_position: 2, expires_at: Date.now() / 1000 + 60, width: 64, height: 48,
      settings: { types: ['vehicle', 'logo', 'plate'], confidence: 40 }, detections: [] } });
  });
  const bar = name => workspace.getByRole('progressbar', { name, exact: typeof name === 'string' });
  const uploaded = index => workspace.evaluate(index => window.uploadStubs[index].upload.onload(), index);
  const respond = (index, status, data, type) => workspace.evaluate(
    ([index, status, data, type]) => window.uploadStubs[index].respond(status, data, type), [index, status, data, type]);
  try {
    await workspace.goto(origin + '/detect#video');
    await workspace.getByLabel('Source video', { exact: true }).setInputFiles({ name: 'stub.mp4', mimeType: 'text/plain', buffer: Buffer.from('not a video') });
    await bar('Video upload').waitFor();
    if (await bar('Video upload').getAttribute('value') !== '50') throw Error('Expected measured upload progress');
    await uploaded(0);
    await bar('Checking video…').waitFor();
    for (const width of [320, 1440]) {
      await workspace.setViewportSize({ width, height: 850 });
      if (await workspace.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw Error('Progress overflows at ' + width);
    }
    await workspace.emulateMedia({ reducedMotion: 'reduce' });
    if (await bar('Checking video…').evaluate(el => getComputedStyle(el, '::before').animationName) !== 'none') throw Error('Reduced motion ignored');
    await respond(0, 408, JSON.stringify({ detail: 'Mock upload timeout' }));
    await workspace.getByRole('alert').filter({ hasText: 'Mock upload timeout' }).waitFor();
    await bar('Checking video…').waitFor({ state: 'hidden' });
    await workspace.getByRole('button', { name: 'Retry video validation' }).click();
    await bar('Video upload').waitFor();
    await uploaded(1);
    await respond(1, 200, 'preview stub', 'video/mp4');
    await workspace.getByRole('button', { name: 'Detect video', exact: true }).click();
    await bar('Video upload').waitFor();
    await uploaded(2);
    await bar('Checking video…').waitFor();
    await respond(2, 202, JSON.stringify({ id: 'browser-regression', token: 'test-only-key' }));
    await bar(/Queued.*Position 2/).waitFor();
    state = 'processing';
    await bar(/Waiting for the free GPU/).waitFor();
    frames = 120;
    await bar('Frames processed').waitFor();
    if (await bar('Frames processed').getAttribute('aria-valuetext') !== '120 of 463 frames processed') throw Error('Incorrect detection frame progress');
    frames = 463;
    await bar(/Finalizing video/).waitFor();
    state = 'empty';
    await workspace.getByRole('button', { name: 'Download JSON', exact: true }).waitFor();
    if (await workspace.getByRole('progressbar').count()) throw Error('Completed jobs must not show loading');
    return 'Measured progress, retry, checking, queue, frame counting, finalizing and completion passed without video bytes';
  } finally { await workspace.close(); }
}
