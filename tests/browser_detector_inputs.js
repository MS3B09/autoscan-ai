// Browser-only regression: fake preview response, no hosted validation or inference.
async (page) => {
  await page.bringToFront();
  const origin = new URL(page.url()).origin;
  const source = await (await page.request.get(origin + '/examples/lexus-lx570.jpg')).body();
  let previews = 0;
  const handler = async route => {
    if (!route.request().url().includes('/api/preview?')) throw new Error('Unexpected inference request');
    previews++;
    await route.fulfill({ status: 200, contentType: 'image/jpeg', body: source });
  };
  await page.route('**/api/**', handler);
  try {
    for (const type of ['image', 'video']) {
      await page.goto(origin + '/detect#' + type);
      await page.getByRole('radio', { name: type === 'image' ? 'Image' : 'Video', exact: true }).waitFor();
      if (!await page.getByRole('radio', { name: type === 'image' ? 'Image' : 'Video', exact: true }).isChecked()) throw new Error('Wrong hash default: ' + type);
      const input = page.getByLabel('Source ' + type, { exact: true });
      const accept = await input.getAttribute('accept');
      if (accept.includes('.jpg') !== (type === 'image') || accept.includes('.mp4') !== (type === 'video')) throw new Error('Upload filter does not match selection');
      if (await page.title() !== 'AutoScan AI | Image & Video Detector') throw new Error('Wrong page title');
    }
    await page.goto(origin + '/detect');
    await page.getByRole('radio', { name: 'Image', exact: true }).waitFor();
    if (!await page.getByRole('radio', { name: 'Image', exact: true }).isChecked()) throw new Error('Default is not image');
    await page.getByLabel('Source image', { exact: true }).setInputFiles({ name: 'wrong.mp4', mimeType: 'video/mp4', buffer: source });
    await page.getByRole('alert').filter({ hasText: 'supported image' }).waitFor();
    if (previews) throw new Error('Wrong input type was uploaded');
    await page.getByLabel('Source image', { exact: true }).setInputFiles({ name: 'photo.jpg', mimeType: 'image/jpeg', buffer: source });
    await page.waitForFunction(() => !document.querySelector('button.primary').disabled);
    await page.getByRole('radio', { name: 'Video', exact: true }).check();
    await page.getByLabel('Source video', { exact: true }).waitFor();
    if (await page.getByLabel('Source video', { exact: true }).inputValue()) throw new Error('Mode switch kept incompatible source');
    if (!await page.getByRole('button', { name: 'Detect video', exact: true }).isDisabled()) throw new Error('Mode switch left stale preview ready');
    if (await page.locator('.comparison img').count()) throw new Error('Mode switch kept stale preview');
    await page.goBack();
    await page.getByLabel('Source image', { exact: true }).waitFor();
    await page.goForward();
    await page.getByLabel('Source video', { exact: true }).waitFor();
    await page.getByRole('radio', { name: 'Video', exact: true }).focus();
    await page.keyboard.press('ArrowLeft');
    await page.getByLabel('Source image', { exact: true }).waitFor();
    if (await page.getByRole('heading', { name: 'Temporary by design.' }).count()) throw new Error('Removed privacy section remains');
    for (const width of [320, 390, 640, 768, 1000, 1440, 1920]) {
      await page.setViewportSize({ width, height: 1000 });
      if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw new Error('Overflow at ' + width);
    }
    for (const [width, type] of [[1440, 'image'], [390, 'video']]) {
      await page.goto(origin + '/detect#' + type);
      await page.setViewportSize({ width, height: 1000 });
      await page.evaluate(() => { window.scrollTo(0, 0); document.activeElement?.blur(); });
      await page.screenshot({ path: `C:/Users/User/AppData/Local/Temp/opencode/autoscan-detector-${width}.png`, fullPage: true });
    }
    return { checks: ['hash defaults', 'file filters', 'wrong-type rejection', 'source reset', 'history navigation', 'radio keyboard', 'responsive layouts', 'page title'], previews, inference: 0 };
  } finally { await page.unroute('**/api/**', handler); }
}
