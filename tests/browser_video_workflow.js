// Run with browser_run_code_unsafe(filename) on the workspace backed by a real HTTP API.
// Fixture/downloads stay outside the repository. A local compute substitute is NOT hosted evidence.
async (page) => {
  const directory = 'C:/Users/User/AppData/Local/Temp/opencode';
  const submissions = [];
  let resultRequest;
  page.on('request', request => {
    if (request.method() === 'POST' && request.url().includes('/api/jobs?')) submissions.push(request.url());
    if (request.url().includes('/download/json')) resultRequest = request;
  });
  if (!await page.getByLabel('Annotated silent video', { exact: true }).count()) {
   await page.getByRole('radio', { name: 'Video', exact: true }).check();
   await page.getByLabel('Source video', { exact: true }).setInputFiles(directory + '/issue5-traffic.mp4');
  const detect = page.getByRole('button', { name: 'Detect video', exact: true });
  await detect.waitFor({ state: 'visible' });
  await page.waitForFunction(() => ![...document.querySelectorAll('button')].find(b => b.textContent === 'Detect video').disabled,
    undefined, { timeout: 65_000 });
  if (submissions.length) throw new Error('Upload started inference without explicit submission');
  const source = page.getByLabel('Source video preview', { exact: true });
  await source.evaluate(async video => { video.muted = true; await video.play(); });
  await page.waitForFunction(() => document.querySelector('video').currentTime > .1);
  await source.evaluate(video => video.pause());
  await detect.click();
  await page.getByRole('button', { name: 'Download annotated video (MP4)', exact: true }).waitFor({ timeout: 180_000 });
  }
  const annotated = page.getByLabel('Annotated silent video', { exact: true });
  await annotated.waitFor({ timeout: 65_000 });
  await annotated.evaluate(async video => { video.muted = true; await video.play(); });
  await page.waitForFunction(() => document.querySelectorAll('video')[1].currentTime > .1);
  const playback = await annotated.evaluate(video => {
    const result = { duration: video.duration, width: video.videoWidth, height: video.videoHeight, currentTime: video.currentTime, error: video.error };
    video.pause();
    video.currentTime = video.duration - .2;
    return result;
  });
  await annotated.evaluate(video => video.play());
  await page.waitForFunction(() => document.querySelectorAll('video')[1].ended);
  const downloads = [];
  const sourceStem = (await page.locator('.file-copy strong').textContent()).replace(/\.[^.]+$/, '');
  for (const [label, extension] of [['Download annotated video (MP4)', 'mp4'], ['Download JSON', 'json'], ['Download CSV', 'csv']]) {
    const event = page.waitForEvent('download');
    await page.getByRole('button', { name: label, exact: true }).focus();
    await page.keyboard.press('Enter');
    const download = await event;
    const filename = download.suggestedFilename();
     const valid = extension === 'mp4' ? /^autoscan-[a-f0-9]{32}\.mp4$/.test(filename) : filename === `${sourceStem}_detections.${extension}`;
     if (!valid) throw new Error('Wrong download filename');
    await download.saveAs(`${directory}/issue5-browser.${extension}`);
    downloads.push({ filename, extension });
  }
  for (const width of [1440, 390]) {
    await page.setViewportSize({ width, height: 1000 });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    if (overflow) throw new Error(`Horizontal overflow at ${width}px`);
    const bounds = await annotated.boundingBox();
    if (bounds.width > width || bounds.width <= 0) throw new Error('Video does not fit viewport');
    await page.screenshot({ path: `${directory}/issue5-video-${width}.png`, fullPage: true });
  }
  const endpoint = resultRequest.url().replace('/download/json', '');
  const authorization = (await resultRequest.allHeaders()).authorization;
  const isolated = await page.context().browser().newContext();
  const visitor = await isolated.newPage();
  await visitor.goto(page.url());
  const isolation = await visitor.evaluate(async endpoint => {
    const codes = [];
    for (const suffix of ['', '/video', '/download/video', '/download/json', '/download/csv']) {
      for (const headers of [{}, { Authorization: 'Bearer another-visitor' }]) {
        codes.push((await fetch(endpoint + suffix, { headers, credentials: 'omit' })).status);
      }
    }
    return codes;
  }, endpoint);
  await isolated.close();
  if (isolation.some(code => code !== 404)) throw new Error('Cross-visitor isolation failed');
  await page.evaluate(summary => { window.__autoscanVideoCheck = summary; },
    { submissions: submissions.length, reusedCompletedJob: !submissions.length, playback, downloads, isolation });
  await page.getByRole('button', { name: 'Delete now', exact: true }).click();
  await page.getByRole('dialog', { name: 'Delete this job?' }).getByRole('button', { name: 'Delete job' }).click();
   await page.waitForFunction(() => document.querySelector('button.primary')?.disabled);
  if (await annotated.count()) throw new Error('Deleted video remains visible');
  const revoked = await page.evaluate(async ({ endpoint, authorization }) => {
    const codes = [];
    for (const suffix of ['', '/video', '/download/video', '/download/json', '/download/csv']) {
      codes.push((await fetch(endpoint + suffix, { headers: { Authorization: authorization }, credentials: 'omit' })).status);
    }
    return codes;
  }, { endpoint, authorization });
  if (revoked.some(code => code !== 404)) throw new Error('Deleted video access was not revoked');
  await page.evaluate(revoked => { window.__autoscanVideoCheck.revoked = revoked; }, revoked);
  return { submissions: submissions.length, reusedCompletedJob: !submissions.length, playback, downloads, isolation, revoked };
}
