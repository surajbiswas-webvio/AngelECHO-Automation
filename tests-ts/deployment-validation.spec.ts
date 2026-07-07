import { test, expect } from '../src/fixtures/baseFixture';
import { DashboardPage } from '../src/pages/DashboardPage';
import { NavigationPage, primaryModules } from '../src/pages/NavigationPage';
import { AgentsPage } from '../src/pages/AgentsPage';
import { AgentEditorPage } from '../src/pages/AgentEditorPage';
import { agentData } from '../src/data/agentData';

test('@deployment strict deployment smoke: no API failures and no console errors', async ({ authenticatedPage, networkMonitor }) => {
  await new DashboardPage(authenticatedPage).validateWidgets();

  const nav = new NavigationPage(authenticatedPage);
  await nav.openModule(primaryModules.find(module => module.name === 'All Agents')!);

  const agents = new AgentsPage(authenticatedPage);
  await agents.createVoiceAgent(agentData.name);
  await agents.openAgent(agentData.name);

  const editor = new AgentEditorPage(authenticatedPage);
  await editor.validateTestModule();

  await nav.openModule(primaryModules.find(module => module.name === 'Members')!);
  await nav.openModule(primaryModules.find(module => module.name === 'Support')!);

  expect(networkMonitor.failedApiEvents({ includeKnown: true })).toEqual([]);
  expect(networkMonitor.consoleErrors({ includeKnown: true })).toEqual([]);
});
