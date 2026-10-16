import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1,
  timeout: 60_000,
  forbidOnly: !!process.env.CI,
  reporter: [['list'], ['html', {open: 'never'}]],
  use: {
    baseURL: 'http://127.0.0.1:4318',
    browserName: 'chromium',
    channel: process.env.PLAYWRIGHT_CHANNEL,
    viewport: {width: 1440, height: 1000},
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: 'uv run --project .. isobar serve --port 4318',
    url: 'http://127.0.0.1:4318/api/health',
    reuseExistingServer: false,
  },
});
