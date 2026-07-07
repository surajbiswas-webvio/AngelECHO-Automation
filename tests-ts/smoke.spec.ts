import { test, expect, envConfig } from '../src/fixtures/baseFixture';
import { DashboardPage } from '../src/pages/DashboardPage';
import { NavigationPage, primaryModules } from '../src/pages/NavigationPage';
import { AgentsPage } from '../src/pages/AgentsPage';
import { agentData } from '../src/data/agentData';

test('@smoke login, dashboard, navigation, agent listing, and settings routes load', async ({ authenticatedPage, networkMonitor }) => {
  const dashboard = new DashboardPage(authenticatedPage);
  await dashboard.expectLoaded();
  await dashboard.validateWidgets();

  const nav = new NavigationPage(authenticatedPage);
  await nav.expectShell();
  await nav.openModule(primaryModules.find(module => module.name === 'All Agents')!);

  const agents = new AgentsPage(authenticatedPage);
  await agents.expectTable();
  await agents.search(agentData.name);

  await nav.openModule(primaryModules.find(module => module.name === 'Members')!);
  await nav.openModule(primaryModules.find(module => module.name === 'Dashboard')!);

  if (!envConfig.allowKnownDefects) {
    expect(networkMonitor.failedApiEvents({ includeKnown: true })).toEqual([]);
    expect(networkMonitor.consoleErrors({ includeKnown: true })).toEqual([]);
  } else {
    expect(networkMonitor.failedApiEvents()).toEqual([]);
    expect(networkMonitor.consoleErrors()).toEqual([]);
  }
});
