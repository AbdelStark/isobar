// From web/: node scripts/capture-readme.mjs (requires make serve on port 4318).
import {mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {chromium, expect} from '@playwright/test';

const output = new URL('../../docs/assets/', import.meta.url);
await mkdir(output, {recursive: true});
const browser = await chromium.launch();
try {
  const page = await browser.newPage({viewport: {width: 1440, height: 1200}, deviceScaleFactor: 1});
  await page.emulateMedia({reducedMotion: 'reduce'});
  await page.goto('http://127.0.0.1:4318');
  await expect(page.locator('#scenario')).toHaveValue('world');
  await expect(page.locator('#seed')).toHaveValue('42');
  await page.locator('#world-run').click();
  await expect(page.locator('#status')).toContainText('Run completed');
  await page.locator('#nation-fra').click();
  await page.locator('#world-view').selectOption('fra');
  await expect(page.locator('#status')).toContainText('Observation boundary: fra');
  await page.locator('#world-timeline').evaluate(element => {
    element.value = '16';
    element.dispatchEvent(new Event('input', {bubbles: true}));
  });
  await expect(page.locator('#world-tick')).toHaveText('16 / 35');
  const layout = page.locator('.world-layout');
  await layout.evaluate(element => window.scrollTo(0, Math.floor(element.getBoundingClientRect().top + window.scrollY)));
  const box = await layout.boundingBox();
  if (!box || box.y < 0 || box.height < 900) throw new Error('Unexpected world layout dimensions');
  await page.screenshot({path: fileURLToPath(new URL('earth-explorer.png', output)), clip: {...box, height: 900}});
  await page.locator('#inspect-decision').click();
  await expect(page.locator('#decision-analysis')).toContainText('Decision at tick 16');
  await page.locator('#decision-analysis').screenshot({path: fileURLToPath(new URL('decision-inspector.png', output))});
  console.log('Captured the world fixture and actual tick-16 decision; no UI data or styles replaced.');
} finally {
  await browser.close();
}
