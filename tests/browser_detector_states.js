// Run with browser_run_code_unsafe(filename), starting on the Vite dev/preview server.
// Test-only HTTP responses replay real published detections with simulated states/expiry.
// No hosted inference, isolation, or retention claim is established by this UI regression.
async (page) => {
  const origin = new URL(page.url()).origin;
  const example = await (await page.request.get(origin + '/examples/lexus.json')).json();
  const source = await (await page.request.get(origin + '/examples/lexus-lx570.jpg')).body();
  const annotated = await (await page.request.get(origin + '/examples/lexus-detections.png')).body();
  const csv = await (await page.request.get(origin + '/examples/lexus.csv')).body();
  let state = 'queued';
  let statusFailure = false;
  let downloadFailure = false;
  let expired = false;
  let submissions = 0;
  let expiresAt = Date.now() / 1000 + 1800;
  const handler = async route => {
    const request = route.request();
    const url = new URL(request.url());
    const json = body => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) });
    if (url.pathname === '/api/preview') return route.fulfill({ status: 200, contentType: 'image/jpeg', body: source });
    if (url.pathname === '/api/jobs') {
      submissions++;
      if (url.searchParams.get('confidence') !== '40' || url.searchParams.get('types') !== 'vehicle,logo,plate') throw new Error('Default settings changed');
      return json({ id: 'browser-regression', token: 'test-only-capability' });
    }
    if (request.headers().authorization !== 'Bearer test-only-capability') throw new Error('Workspace dropped job capability');
    if (expired) return route.fulfill({ status: 404, contentType: 'application/json', body: '{"detail":"Job unavailable, deleted, or expired."}' });
    if (request.method() === 'DELETE') return json({ deleted: true });
    if (url.pathname.endsWith('/cancel')) { state = 'cancelled'; return json({ state }); }
    if (url.pathname.includes('/download/')) {
      if (downloadFailure) return route.fulfill({ status: 503, contentType: 'application/json', body: '{"detail":"Temporary download failure."}' });
      if (url.pathname.endsWith('/json')) return json({ ...example, state, detections: state === 'empty' ? [] : example.detections });
      return route.fulfill({ status: 200, contentType: url.pathname.endsWith('/csv') ? 'text/csv' : 'image/png', body: url.pathname.endsWith('/csv') ? csv : annotated });
    }
    if (url.pathname.endsWith('/image')) return route.fulfill({ status: 200,
      contentType: state === 'empty' ? 'image/jpeg' : 'image/png', body: state === 'empty' ? source : annotated });
    if (statusFailure) return route.fulfill({ status: 503, contentType: 'application/json', body: '{"detail":"Backend unavailable. Try again."}' });
    return json({ ...example, state, expires_at: expiresAt, detections: state === 'success' ? example.detections : [],
      error: state === 'error' ? 'Free GPU quota exhausted. Try later.' : null });
  };
  await page.route('**/api/**', handler);
  try {
    const prepare = async () => {
      await page.goto(origin + '/detect');
      const before = submissions;
      await page.getByLabel('Source image or short video', { exact: true }).setInputFiles({ name: 'lexus-lx570.jpg', mimeType: 'image/jpeg', buffer: source });
      await page.waitForFunction(() => ![...document.querySelectorAll('button')].find(button => button.textContent === 'Detect image').disabled);
      if (submissions !== before) throw new Error('Selecting a file started inference');
      await page.getByRole('button', { name: 'Detect image', exact: true }).click();
    };
    await prepare();
    await page.getByRole('status').filter({ hasText: 'Queued.' }).waitFor();
    if (!await page.getByLabel('Source image or short video', { exact: true }).isDisabled()) throw new Error('Queued source is editable');
    state = 'processing';
    await page.getByRole('status').filter({ hasText: 'Processing.' }).waitFor();
    state = 'success';
    await page.getByRole('button', { name: 'Download JSON', exact: true }).waitFor();
    await page.getByRole('img', { name: 'Annotated result with 4 detections', exact: true }).waitFor();
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1000 });
      if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw new Error('Detector overflow: ' + width);
      const table = await page.locator('table').boundingBox();
      const caption = await page.locator('caption').boundingBox();
      if (!caption || !table || caption.width < table.width * .9) throw new Error('Coordinate caption collapsed');
      await page.screenshot({ path: `E:/autoscan-ai/.impeccable/review/detector-success-${width}.png`, fullPage: true });
    }
    downloadFailure = true;
    await page.getByRole('button', { name: 'Download CSV', exact: true }).click();
    await page.getByRole('alert').filter({ hasText: 'CSV download failed' }).waitFor();
    downloadFailure = false;
    const event = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Download CSV', exact: true }).focus();
    await page.keyboard.press('Enter');
    if ((await event).suggestedFilename() !== 'autoscan-browser-regression.csv') throw new Error('Workspace CSV download changed');
    // Accept native confirmation in this simulated-state run; production keeps window.confirm.
    await page.evaluate(() => { window.confirm = () => true; });
    await page.getByRole('button', { name: 'Delete now', exact: true }).click();
    await page.waitForFunction(() => document.activeElement?.id === 'image');
    if (await page.getByRole('button', { name: 'Download JSON', exact: true }).count()) throw new Error('Deleted results remain');
    state = 'empty';
    await prepare();
    await page.getByRole('status').filter({ hasText: 'No objects matched' }).waitFor();
    await page.getByRole('button', { name: 'Download JSON', exact: true }).waitFor();
    if (await page.locator('tbody tr').count()) throw new Error('Empty result shows detections');
    const emptyImage = page.getByRole('img', { name: 'Annotated result with 0 detections', exact: true });
    await emptyImage.waitFor();
    const emptyBytes = await emptyImage.evaluate(async image => {
      await image.decode();
      return (await (await fetch(image.src)).blob()).size;
    });
    if (emptyBytes !== source.length) throw new Error('Empty preview reused the annotated success image');
    await page.screenshot({ path: 'E:/autoscan-ai/.impeccable/review/detector-empty.png', fullPage: true });
    state = 'error';
    await prepare();
    await page.getByText('Free GPU quota exhausted. Try later.', { exact: true }).waitFor();
    if (await page.getByRole('button', { name: 'Download JSON', exact: true }).count()) throw new Error('Failed result offers downloads');
    await page.screenshot({ path: 'E:/autoscan-ai/.impeccable/review/detector-error.png', fullPage: true });
    state = 'queued'; statusFailure = true;
    await prepare();
    await page.getByRole('button', { name: 'Retry job status', exact: true }).waitFor();
    statusFailure = false;
    await page.getByRole('button', { name: 'Retry job status', exact: true }).click();
    await page.getByRole('button', { name: 'Cancel', exact: true }).click();
    await page.getByRole('status').filter({ hasText: 'Cancelled.' }).waitFor();
    state = 'success'; expiresAt = Date.now() / 1000 + 3;
    await prepare();
    await page.getByRole('button', { name: 'Download JSON', exact: true }).waitFor();
    await page.getByRole('status').filter({ hasText: 'Results expired' }).waitFor({ timeout: 8000 });
    if (await page.getByRole('button', { name: 'Download JSON', exact: true }).count()) throw new Error('Expired result offers downloads');
    await page.screenshot({ path: 'E:/autoscan-ai/.impeccable/review/detector-expired.png', fullPage: true });
    expiresAt = Date.now() / 1000 + 1800; expired = true;
    await prepare();
    await page.getByRole('status').filter({ hasText: 'no longer available' }).waitFor();
    return { simulatedStates: ['queued', 'processing', 'success', 'empty', 'error', 'cancelled', 'expired', 'unavailable'], submissions,
      checks: ['explicit submit', 'unchanged defaults', 'capability headers', 'download retry', 'keyboard download', 'deletion focus', 'mobile caption', 'responsive layouts'] };
  } finally { await page.unroute('**/api/**', handler); }
}
