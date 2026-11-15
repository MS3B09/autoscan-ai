// Run with browser_run_code_unsafe(filename) against the Vite dev/preview server.
async (page) => {
  const origin = new URL(page.url()).origin;
  const errors = [];
  const onError = error => errors.push(error.message);
  page.on('pageerror', onError);
  const checks = [];
  await page.goto(origin + '/');
  await page.getByRole('heading', { name: 'See what the models detect.', exact: true }).waitFor({ timeout: 5000 });
  await page.getByRole('link', { name: 'Open image detector', exact: true }).click();
  await page.getByLabel('Source image or short video', { exact: true }).waitFor();
  await page.reload();
  await page.getByLabel('Source image or short video', { exact: true }).waitFor();
  await page.getByRole('link', { name: 'Project', exact: true }).click();
  const downloadEvent = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Download sample JSON', exact: true }).click({ timeout: 5000 });
  const download = await downloadEvent;
  if (download.suggestedFilename() !== 'autoscan-example.json') throw new Error('Wrong sample filename');
  const data = await (await page.request.get(origin + '/examples/lexus.json')).json();
  const preview = await page.getByRole('region', { name: 'JSON sample preview', exact: true }).textContent();
  for (const detection of data.detections) {
    if (!preview.includes(String(detection.confidence))) throw new Error('Sample preview differs from export');
  }
  const csvEvent = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Download sample CSV', exact: true }).focus();
  await page.keyboard.press('Enter');
  if ((await csvEvent).suggestedFilename() !== 'autoscan-example.csv') throw new Error('Wrong CSV sample filename');
  const csv = await (await page.request.get(origin + '/examples/lexus.csv')).text();
  const csvPreview = await page.getByRole('region', { name: 'CSV sample preview', exact: true }).textContent();
  if (csvPreview.trim() !== csv.trim()) throw new Error('CSV preview differs from downloaded sample');
  const rows = csv.trim().split(/\r?\n/);
  if (rows.length !== data.detections.length + 1) throw new Error('Sample CSV omits detections');
  if (rows[0].replace(/^\uFEFF/, '') !== 'source_filename,object_type,class_id,class_name,label,confidence,x1,y1,x2,y2,width,height') {
    throw new Error('Sample CSV uses invented columns');
  }
  for (const [index, detection] of data.detections.entries()) {
    const row = rows[index + 1].split(',');
    if (row[0] !== data.filename || row[1] !== detection.object_type || Number(row[5]) !== detection.confidence ||
      row.slice(6, 10).some((value, axis) => Number(value) !== detection.bbox[axis])) throw new Error('CSV and JSON disagree');
  }
  await page.getByText('View all 24 supported logo brands', { exact: true }).focus();
  await page.keyboard.press('Enter');
  const brands = await page.locator('.brand-list li').allTextContents();
  if (brands.length !== 24 || brands.join(',') !== Object.values(data.models.logo.classes).join(',')) throw new Error('Wrong supported brands');
  for (const name of ['El-Ouaragli Zayd', 'El-Abbass Ossama', 'Nassiri Mosab', 'Hassan Fares', 'Aly Guinga']) {
    if (!await page.getByRole('link', { name, exact: true }).isVisible()) throw new Error('Missing contributor: ' + name);
  }
  for (const width of [320, 390, 640, 641, 700, 768, 800, 1280, 1440, 1536, 1920]) {
    await page.setViewportSize({ width, height: width < 640 ? 844 : 1024 });
    if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw new Error('Horizontal overflow: ' + width);
    const clipped = await page.locator('a, summary').evaluateAll(elements => elements.filter(element => {
      const box = element.getBoundingClientRect();
      return !element.classList.contains('skip') && (box.left < 0 || box.right > innerWidth);
    }).map(element => element.textContent));
    if (clipped.length) throw new Error('Clipped controls at ' + width + ': ' + clipped);
    if (width === 390) {
      const images = await page.locator('.showcase-comparison img').all();
      for (const image of images) {
        const box = await image.boundingBox();
        if (!box || box.y + box.height > 844) throw new Error('Comparison is lost below mobile fold');
      }
    }
    checks.push(width);
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload();
  await page.keyboard.press('Tab');
  const focused = await page.locator(':focus').evaluate(element => ({ text: element.textContent, outline: getComputedStyle(element).outlineWidth }));
  // Chromium can round the authored 3px outline to 2.4px at fractional display scaling.
  if (focused.text !== 'Skip to project' || parseFloat(focused.outline) < 2) throw new Error('Keyboard skip link or visible focus missing');
  await page.keyboard.press('Enter');
  if (!page.url().endsWith('#project')) throw new Error('Skip destination is broken');
  await page.getByRole('link', { name: 'Try a video', exact: true }).click();
  const upload = page.getByLabel('Source image or short video', { exact: true });
  if (!(await upload.getAttribute('accept')).includes('.mp4')) throw new Error('Video entry does not accept videos');
  await page.goto(origin + '/detect/');
  await page.reload();
  await upload.waitFor();
  for (const width of [640, 641, 700, 768, 800]) {
    await page.setViewportSize({ width, height: 1000 });
    const clipped = await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('link').evaluateAll(links =>
      links.some(link => link.getBoundingClientRect().right > innerWidth || link.getBoundingClientRect().left < 0));
    if (clipped) throw new Error('Detector navigation clips at ' + width);
  }
  page.off('pageerror', onError);
  if (errors.length) throw new Error(errors.join('\n'));
  return { navigation: 'root, image/video entry, detector refresh and trailing slash', samples: 'native JSON/CSV downloads match real data', brands: 24, responsiveWidths: checks, keyboard: 'skip, focus, details and downloads' };
}
