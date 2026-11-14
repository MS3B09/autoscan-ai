// Run with browser_run_code_unsafe(filename) on /detect after a completed image job.
async (page) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const caption = await page.locator('caption').boundingBox();
  const table = await page.locator('table').boundingBox();
  if (!caption || !table || caption.width < table.width * 0.9) {
    throw new Error(`Mobile coordinate caption is too narrow: ${caption?.width} / ${table?.width}`);
  }
  for (const width of [390, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.getByRole('button', { name: 'Download JSON', exact: true }).focus();
    const skip = page.getByRole('link', { name: 'Skip to detector', exact: true });
    const hidden = await skip.boundingBox();
    if (hidden.y + hidden.height > 0) {
      throw new Error(`Unfocused skip link remains visible at ${width}px: y=${hidden.y}`);
    }
    await skip.focus();
    const visible = await skip.boundingBox();
    if (visible.y < 0 || visible.y > 8) {
      throw new Error(`Focused skip link is not at the viewport top: y=${visible.y}`);
    }
  }
  return { captionWidth: caption.width, tableWidth: table.width };
}
