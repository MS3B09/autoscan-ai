// Run with browser_run_code_unsafe(filename) against the Vite dev/preview server. No inference.
async (page) => {
  await page.bringToFront();
  const origin = new URL(page.url()).origin;
  const errors = [];
  const onError = error => errors.push(error.message);
  page.on('pageerror', onError);
  try {
    await page.goto(origin + '/');
    for (const name of ['See what the models detect.', 'From detections to data', 'Three detectors. Your selection.', 'See it on your own media.']) {
      await page.getByRole('heading', { name, exact: true }).waitFor();
    }
    if (await page.locator('pre, .contributors').count()) throw new Error('Removed landing-page details remain');
    if (await page.locator('.workflow li').count() !== 3) throw new Error('Workflow is incomplete');
    for (const image of await page.locator('.showcase img').all()) {
      if (!await image.evaluate(image => image.complete && image.naturalWidth > 0)) await image.evaluate(image => image.decode());
    }
    for (const name of ['original', 'detections']) {
      const expand = page.getByRole('button', { name: `View ${name} full size`, exact: true });
      await expand.focus();
      await page.keyboard.press('Enter');
      const dialog = page.getByRole('dialog');
      await dialog.waitFor();
      if (new URL(page.url()).pathname !== '/') throw new Error('Full-size image navigated away');
      await page.locator('.wordmark').evaluate(link => link.focus());
      if (!await dialog.evaluate(dialog => dialog.contains(document.activeElement))) throw new Error('Dialog focus escaped');
      await page.keyboard.press('Escape');
      await dialog.waitFor({ state: 'hidden' });
      if (!await expand.evaluate(button => document.activeElement === button)) throw new Error('Dialog did not restore focus');
      await expand.click();
      await page.getByRole('button', { name: 'Close full-size image' }).click();
      await dialog.waitFor({ state: 'hidden' });
    }
    const widths = [320, 390, 640, 641, 768, 1000, 1280, 1440, 1920];
    for (const width of widths) {
      await page.setViewportSize({ width, height: 1000 });
      if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw new Error('Horizontal overflow: ' + width);
      if (width === 1440) {
        const shell = await page.locator('main').boundingBox();
        if (Math.abs(shell.width / width - .8) > .01) throw new Error('Desktop shell is not 80%');
      }
    }
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.screenshot({ path: 'C:/Users/User/AppData/Local/Temp/opencode/autoscan-home-desktop.png', fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: 'C:/Users/User/AppData/Local/Temp/opencode/autoscan-home-mobile.png', fullPage: true });
    await page.reload();
    await page.keyboard.press('Tab');
    if (await page.locator(':focus').textContent() !== 'Skip to project') throw new Error('Skip link is missing');
    await page.keyboard.press('Enter');
    for (const [label, hash] of [['Open image detector', '#image'], ['Try a video', '#video']]) {
      await page.goto(origin + '/');
      await page.getByRole('link', { name: label, exact: true }).click();
      if (new URL(page.url()).hash !== hash) throw new Error('Wrong detector entry: ' + label);
      if (!await page.getByRole('radio', { name: hash === '#video' ? 'Video' : 'Image', exact: true }).isChecked()) throw new Error('Entry did not select input type');
    }
    if (errors.length) throw new Error(errors.join('\n'));
    return { sections: 4, images: 'supplied assets loaded', modal: 'keyboard, close, Escape, focus restoration', responsiveWidths: widths, detectorLinks: ['#image', '#video'] };
  } finally { page.off('pageerror', onError); }
}
