import { defineConfig, devices } from '@playwright/test';
import { envConfig } from './src/config/env';

export default defineConfig({
  testDir: './tests-ts',
  timeout: 90_000,
  expect: { timeout: envConfig.defaultTimeoutMs },
  fullyParallel: true,
  retries: process.env.CI ? 2 : 1,
  workers: process.env.CI ? 4 : undefined,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'reports/playwright-html', open: 'never' }],
    ['json', { outputFile: 'reports/playwright-results.json' }]
  ],
  use: {
    baseURL: envConfig.baseUrl,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: envConfig.defaultTimeoutMs,
    navigationTimeout: envConfig.defaultTimeoutMs
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], headless: envConfig.headless }
    }
  ]
});
