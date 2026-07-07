import { test as base, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { NetworkMonitor } from '../utils/networkMonitor';
import { envConfig } from '../config/env';

type Fixtures = {
  networkMonitor: NetworkMonitor;
  authenticatedPage: import('@playwright/test').Page;
};

export const test = base.extend<Fixtures>({
  networkMonitor: async ({ page }, use, testInfo) => {
    const monitor = new NetworkMonitor();
    monitor.attach(page);
    await use(monitor);
    await testInfo.attach('api-events', {
      body: JSON.stringify(monitor.apiEvents, null, 2),
      contentType: 'application/json'
    });
    await testInfo.attach('console-events', {
      body: JSON.stringify(monitor.consoleEvents, null, 2),
      contentType: 'application/json'
    });
  },

  authenticatedPage: async ({ page }, use) => {
    await new LoginPage(page).login();
    await use(page);
  }
});

export { expect, envConfig };
