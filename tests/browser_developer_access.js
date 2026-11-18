// Run on the frontend configured with VITE_AUTOSCAN_API=http://127.0.0.1:7862.
// Live execution spends account quota; use the test-only external-HTTP replay for contract checks.
async (page) => {
  const origin = new URL(page.url()).origin;
  await page.goto(origin + '/detect');
  await page.getByText('Local developer mode. Detection uses your personal Hugging Face quota.', { exact: true })
    .waitFor({ timeout: 5000 });
  const requests = [];
  const observe = request => {
    if (request.url().startsWith('http://127.0.0.1:7862/api/')) requests.push(request);
  };
  page.on('request', observe);
  try {
    const source = await (await page.request.get(origin + '/examples/lexus-lx570.jpg')).body();
    await page.getByLabel('Source image', { exact: true })
      .setInputFiles({ name: 'lexus-lx570.jpg', mimeType: 'image/jpeg', buffer: source });
    await page.waitForFunction(() => ![...document.querySelectorAll('button')].find(button => button.textContent === 'Detect image').disabled);
    if (requests.some(request => new URL(request.url()).pathname === '/api/jobs')) throw new Error('Preview submitted inference');
    const response = page.waitForResponse(response => new URL(response.url()).pathname === '/api/jobs' && response.request().method() === 'POST');
    await page.getByRole('button', { name: 'Detect image', exact: true }).click();
    const capability = await (await response).json();
    await page.getByRole('button', { name: 'Download JSON', exact: true }).waitFor({ timeout: 180_000 });
    const download = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Download JSON', exact: true }).focus();
    await page.keyboard.press('Enter');
    if ((await download).suggestedFilename() !== 'lexus-lx570_detections.json') throw new Error('Developer download failed');
    for (const width of [390, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw new Error('Developer UI overflows');
      await page.screenshot({ path: `E:/autoscan-ai/.impeccable/review/developer-${width}.png`, fullPage: true });
    }
    await page.getByRole('button', { name: 'Delete now', exact: true }).click();
    await page.getByRole('dialog', { name: 'Delete this job?' }).getByRole('button', { name: 'Delete job' }).click();
    await page.waitForFunction(() => document.activeElement?.id === 'image');
    for (const request of requests) {
      const authorization = request.headers().authorization;
      if (new URL(request.url()).pathname.startsWith('/api/jobs/')) {
        if (authorization !== 'Bearer ' + capability.token) throw new Error('Private call lost its job capability');
      } else if (authorization) throw new Error('Browser supplied authentication on an upload');
    }
    return { developerMode: 'clearly identified', workflow: 'HTTP preview, explicit submission, result, keyboard download, deletion', browserCredentials: 'job key only' };
  } finally { page.off('request', observe); }
}
