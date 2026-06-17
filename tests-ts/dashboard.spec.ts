import { test, expect, envConfig } from '../src/fixtures/baseFixture';
import { DashboardPage } from '../src/pages/DashboardPage';
import { captureUiInventory } from '../src/utils/uiInventory';

test.describe('@dashboard Dashboard validation', () => {
  test('validates widgets, cards, filters, links, tables, and API health', async ({ authenticatedPage, networkMonitor }, testInfo) => {
    const dashboard = new DashboardPage(authenticatedPage);
    await dashboard.open();
    await dashboard.validateWidgets();
    await dashboard.openDateFilter();

    const inventory = await captureUiInventory(authenticatedPage);
    await testInfo.attach('dashboard-inventory', {
      body: JSON.stringify(inventory, null, 2),
      contentType: 'application/json'
    });

    expect(inventory.tables.length).toBeGreaterThanOrEqual(2);
    expect(inventory.links.map(link => link.text)).toEqual(expect.arrayContaining(['All Agents', 'Analytics', 'Billing', 'Support']));

    const failures = envConfig.allowKnownDefects ? networkMonitor.failedApiEvents() : networkMonitor.failedApiEvents({ includeKnown: true });
    expect(failures).toEqual([]);
  });
});
