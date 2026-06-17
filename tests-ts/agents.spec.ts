import { test, expect, envConfig } from '../src/fixtures/baseFixture';
import { AgentsPage } from '../src/pages/AgentsPage';
import { AgentEditorPage } from '../src/pages/AgentEditorPage';
import { agentData } from '../src/data/agentData';

test.describe('@agents Agent management and E2E validation', () => {
  test('validates listing search filters sorting-style controls and details page', async ({ authenticatedPage }) => {
    const agents = new AgentsPage(authenticatedPage);
    await agents.open();
    await agents.expectTable();
    await agents.search(agentData.name);
    await agents.exerciseFilters();
  });

  test('creates voice agent, persists prompt, validates config sections and test module', async ({ authenticatedPage, networkMonitor }) => {
    const agents = new AgentsPage(authenticatedPage);
    await agents.createVoiceAgent(agentData.name);
    await agents.openAgent(agentData.name);

    const editor = new AgentEditorPage(authenticatedPage);
    await editor.setPrompt(agentData.prompt);
    await editor.validateSections();
    await editor.openPromptGenerator();
    await editor.validateTestModule();

    const createOrUpdateCalls = networkMonitor.apiEvents.filter(event =>
      event.url.includes('/agents/create-full') || event.method === 'PUT' || event.method === 'PATCH'
    );
    expect(createOrUpdateCalls.some(event => event.status >= 200 && event.status < 300)).toBeTruthy();

    const failures = envConfig.allowKnownDefects ? networkMonitor.failedApiEvents() : networkMonitor.failedApiEvents({ includeKnown: true });
    expect(failures).toEqual([]);
  });
});
