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
  let quotaTiming = true;
  let submissionQuota = false;
  let submissionRetryAt = 1893456000;
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
      if (submissionQuota) return route.fulfill({ status: 429, contentType: 'application/json', body: JSON.stringify({
        detail: 'Free GPU quota is exhausted. Hugging Face did not provide a reset time. Try again later.',
        ...(quotaTiming ? { retry_at: submissionRetryAt } : {}),
      }) });
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
      ...(state === 'error' && quotaTiming ? { retry_at: 1893456000 } : {}),
      error: state === 'error' ? 'Free GPU quota is exhausted. Hugging Face did not provide a reset time. Try again later.' : null });
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
    const quotaAlert = page.getByRole('alert').filter({ hasText: 'Free GPU quota is exhausted' });
    await quotaAlert.waitFor({ timeout: 5000 });
    const reset = quotaAlert.locator('time');
    if (await reset.getAttribute('datetime') !== '2030-01-01T00:00:00.000Z' || !await reset.isVisible()) {
      throw new Error('Platform reset time is missing from the quota alert');
    }
    if (await page.getByRole('button', { name: 'Download JSON', exact: true }).count()) throw new Error('Failed result offers downloads');
    await page.screenshot({ path: 'E:/autoscan-ai/.impeccable/review/detector-error.png', fullPage: true });
    quotaTiming = false;
    await prepare();
    const fallback = page.getByRole('alert').filter({ hasText: 'Hugging Face did not provide a reset time' });
    await fallback.waitFor();
    if (await fallback.locator('time').count()) throw new Error('Quota fallback invented a reset time');
    submissionQuota = true; quotaTiming = true;
    await prepare();
    const rejected = page.getByRole('alert').filter({ hasText: 'your local time' });
    await rejected.waitFor();
    if (await rejected.locator('time').getAttribute('datetime') !== '2030-01-01T00:00:00.000Z') {
      throw new Error('Submission quota rejection lost its local reset time');
    }
    await page.screenshot({ path: 'E:/autoscan-ai/.impeccable/review/submission-quota.png', fullPage: true });
    quotaTiming = false;
    await prepare();
    await fallback.waitFor();
    if (await fallback.locator('time').count()) throw new Error('Submission quota fallback invented timing');
    quotaTiming = true;
    for (submissionRetryAt of ['2030-01-01', -1, 1e20]) {
      await prepare();
      await fallback.waitFor();
      if (await fallback.locator('time').count()) throw new Error('Malformed submission timing was displayed');
    }
    submissionQuota = false;
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
      checks: ['explicit submit', 'unchanged defaults', 'capability headers', 'download retry', 'keyboard download', 'deletion focus',
        'job and submission quota reset times', 'missing and malformed timing fallback', 'mobile caption', 'responsive layouts'] };
  } finally { await page.unroute('**/api/**', handler); }
}
