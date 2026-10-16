import { test, expect } from '@playwright/test';
import { readFile } from 'node:fs/promises';
import AxeBuilder from '@axe-core/playwright';

test.beforeEach(async ({page}) => {
  page.on('pageerror', error => { throw error; });
});

test('run, inspect boundaries, branch, compare and export through the real kernel', async ({page}, testInfo) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await expect(page.getByRole('heading', {level: 1})).toHaveText('What holds under pressure?');
  await expect(page.locator('#scenario')).toHaveValue('s2');
  await page.screenshot({path: testInfo.outputPath('workbench-desktop.png'), fullPage: true});
  await page.locator('#horizon').fill('12');
  await page.getByRole('button', {name: 'Run scenario', exact: true}).click();
  await expect(page.locator('#status')).toContainText('Run completed');
  await expect(page.locator('#view')).toHaveValue('public');
  await expect(page.getByLabel('Permit inspection')).toBeChecked();
  await expect(page.locator('#outcomes')).toContainText('Overturned appeals / resolved appeals');
  await expect(page.locator('#outcomes')).toContainText('Resolved appeals / filed appeals');
  await expect(page.locator('#assumptions')).not.toContainText('"hidden_capacity"');
  await page.locator('#timeline').evaluate((element: HTMLInputElement) => { element.value = element.max; element.dispatchEvent(new Event('input', {bubbles: true})); });
  await expect(page.locator('#tick-label')).toHaveText('11 / 11');
  await expect(page.locator('#evidence .event-list > li').first()).toBeVisible();

  await page.locator('#view').selectOption('truth');
  await expect(page.locator('#status')).toContainText('post-run ground truth');
  await expect(page.locator('#view')).toBeFocused();
  await expect(page.locator('#assumptions')).toContainText('"hidden_capacity"');
  await page.locator('#view').selectOption('aurora');
  await expect(page.locator('#status')).toContainText('Observation boundary: aurora');
  await expect(page.locator('#view')).toHaveValue('aurora');
  await page.locator('#view').selectOption('public');
  await expect(page.locator('#status')).toContainText('Observation boundary: public');

  await page.locator('#action-train').fill('0.9');
  await page.locator('#branch-run').click();
  await expect(page.getByRole('alert')).toContainText('must sum to 1');
  await page.locator('#action-train').fill('0.2');
  await page.locator('#branch-tick').fill('3');
  await page.locator('#branch-run').click();
  await expect(page.locator('#status')).toContainText('Branch complete');
  await expect(page.locator('#tick-label')).toHaveText('3 / 11');
  await page.locator('#view').selectOption('truth');
  await expect(page.locator('#status')).toContainText('post-run ground truth');
  await expect(page.locator('#assumptions')).toContainText('Branch provenance');
  await page.locator('#view').selectOption('public');
  await expect(page.locator('#status')).toContainText('Observation boundary: public');
  await expect(page.locator('#assumptions')).toContainText('Branch provenance');

  await page.locator('#ensemble-count').fill('2');
  await page.locator('#compare-run').click();
  await expect(page.locator('#status')).toContainText('Compared 4 policies');
  await expect(page.locator('#comparison-results svg')).toBeVisible();
  await expect(page.locator('#comparison-results svg circle')).toHaveCount(4);
  await expect(page.locator('#comparison-results')).toContainText('Service per population');
  await expect(page.locator('#comparison-results')).toContainText('Aurora');
  await page.locator('#compare-mode').selectOption('differences');
  await expect(page.locator('#comparison-results svg circle')).toHaveCount(3);
  await expect(page.locator('#compare-mode')).toBeFocused();

  const downloadPromise = page.waitForEvent('download');
  await page.locator('#export-public').click();
  const download = await downloadPromise;
  const path = await download.path();
  expect(path).not.toBeNull();
  const bundle = JSON.parse(await readFile(path!, 'utf8'));
  expect(bundle).toHaveProperty('artifact_version');
  expect(JSON.stringify(bundle)).toContain('parent_id');
  await expect(page.locator('#status')).toContainText('Nothing was published');
  await page.screenshot({path: testInfo.outputPath('workbench-run.png'), fullPage: true});
  await page.locator('#coverage').fill('0.4');
  await page.locator('#coverage').blur();
  await expect(page.locator('#comparison-results')).toBeEmpty();
  await expect(page.locator('#replay-controls')).toBeEmpty();
  expect(errors).toEqual([]);
});

test('JSON authoring validates server ranges, resolves defaults and treats scenario text as text', async ({page}) => {
  await page.goto('/');
  await page.locator('#advanced > summary').click();
  await expect(page.locator('#scenario-json')).not.toHaveValue('');
  const original = JSON.parse(await page.locator('#scenario-json').inputValue());
  await page.locator('#scenario-json').fill('{ broken');
  await page.locator('#apply-json').click();
  await expect(page.getByRole('alert')).toContainText('Scenario JSON is not valid');
  original.verification.coverage = 2;
  await page.locator('#scenario-json').fill(JSON.stringify(original));
  await page.locator('#apply-json').click();
  await expect(page.getByRole('alert')).toContainText('verification.coverage');
  original.verification = {};
  original.seed = 3_000_000_000;
  original.question = '<img src=x onerror=alert(1)> This is plain text.';
  await page.locator('#scenario-json').fill(JSON.stringify(original));
  await page.locator('#apply-json').click();
  await expect(page.locator('#status')).toContainText('Scenario validated and applied');
  await expect(page.locator('#coverage')).toHaveValue('0.8');
  await expect(page.locator('#seed')).toHaveValue('3000000000');
  await expect(page.locator('#question')).toHaveText(original.question);
  await expect(page.locator('#question img')).toHaveCount(0);
  await page.locator('#run').click();
  await expect(page.locator('#status')).toContainText('Run completed');
});

test('private classification cannot use the public research export', async ({page}) => {
  await page.goto('/');
  await page.locator('#advanced > summary').click();
  await expect(page.locator('#scenario-json')).not.toHaveValue('');
  const scenario = JSON.parse(await page.locator('#scenario-json').inputValue());
  scenario.classification = 'private';
  await page.locator('#scenario-json').fill(JSON.stringify(scenario));
  await page.locator('#apply-json').click();
  await expect(page.locator('#status')).toContainText('Scenario validated and applied');
  await page.locator('#run').click();
  await expect(page.locator('#status')).toContainText('Run completed');
  await page.locator('#export-public').click();
  await expect(page.getByRole('alert')).toContainText(/private/i);
});

test('narrow viewport and keyboard access retain the complete workflow', async ({page}, testInfo) => {
  await page.setViewportSize({width: 390, height: 844});
  await page.emulateMedia({reducedMotion: 'reduce'});
  await page.goto('/');
  await expect(page.locator('#run')).toBeVisible();
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', {name: 'Skip to workbench'})).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#workbench')).toBeFocused();
  await page.locator('#run').click();
  await expect(page.locator('#status')).toContainText('Run completed');
  await expect(page.locator('#view')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  await page.locator('#view').selectOption('truth');
  await expect(page.locator('#status')).toContainText('post-run ground truth');
  await page.screenshot({path: testInfo.outputPath('workbench-mobile.png'), fullPage: true});
  await expect(page.locator('#branch-run')).toBeAttached();
  await expect(page.locator('#compare-run')).toBeAttached();
});

test('startup and request failures recover without losing a replay or draft', async ({page}) => {
  await page.route('**/api/catalog', route => route.abort());
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('not reachable');
  await page.unroute('**/api/catalog');
  await page.getByRole('button', {name: 'Try loading again'}).click();
  await page.locator('#horizon').fill('8');
  await page.locator('#run').click();
  await expect(page.locator('#status')).toContainText('Run completed');
  await page.route('**/api/run', route => route.abort());
  await page.locator('#view').selectOption('truth');
  await expect(page.getByRole('alert')).toContainText('not reachable');
  await expect(page.locator('#view')).toHaveValue('public');
  await expect(page.locator('#horizon')).toHaveValue('8');
  await expect(page.locator('#actors')).toBeVisible();
  await expect(page.locator('#run')).toBeEnabled();
  await page.unroute('**/api/run');
  await page.locator('#view').selectOption('truth');
  await expect(page.locator('#status')).toContainText('post-run ground truth');
  await expect(page.getByRole('alert')).toBeHidden();
});

test('all synthetic presets run with keyboard playback and local-only requests', async ({page}) => {
  const external: string[] = [];
  page.on('request', request => {
    if (new URL(request.url()).origin !== 'http://127.0.0.1:4318') external.push(request.url());
  });
  await page.goto('/');
  for (const preset of ['s1', 's2', 's3', 's4', 's5', 's6']) {
    await page.locator('#scenario').selectOption(preset);
    await page.locator('#run').click();
    await expect(page.locator('#status')).toContainText('Run completed');
    await expect(page.locator('#view')).toHaveValue('public');
    await page.locator('#timeline').focus();
    await page.keyboard.press('End');
    await expect(page.locator('#tick-label')).not.toHaveText(/^0 \/ /);
    await expect(page.locator('#evidence')).toContainText('RECORDS');
  }
  await page.clock.install();
  await page.locator('#timeline').focus();
  await page.keyboard.press('Home');
  await page.locator('#play').click();
  await page.clock.runFor(900);
  await expect(page.locator('#tick-label')).toHaveText(/^1 \/ /);
  await page.locator('#play').click();
  await page.clock.runFor(1800);
  await expect(page.locator('#tick-label')).toHaveText(/^1 \/ /);
  expect(external).toEqual([]);
});

for (const width of [1440, 390]) {
  test(`accessible authoring, replay and comparison at ${width}px`, async ({page}, testInfo) => {
    await page.setViewportSize({width, height: 1000});
    await page.goto('/');
    await expect(page.locator('#run')).toBeVisible();
    const scan = async (state: string) => {
      const result = await new AxeBuilder({page}).analyze();
      await testInfo.attach(`accessibility-${state}.json`, {body: JSON.stringify(result, null, 2), contentType: 'application/json'});
      expect(result.violations).toEqual([]);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
    };
    await scan('initial');
    await page.locator('#run').click();
    await expect(page.locator('#status')).toContainText('Run completed');
    await scan('public');
    await page.locator('#view').selectOption('truth');
    await expect(page.locator('#status')).toContainText('post-run ground truth');
    await page.locator('#ensemble-count').fill('2');
    await page.locator('#compare-run').click();
    await expect(page.locator('#status')).toContainText('Compared 4 policies');
    await scan('truth-comparison');
    await page.locator('#advanced > summary').click();
    await expect(page.locator('#scenario-json')).not.toHaveValue('');
    await scan('authoring');
  });
}
