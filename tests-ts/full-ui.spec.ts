import { test, expect, envConfig } from '../src/fixtures/baseFixture';
import { NavigationPage, primaryModules } from '../src/pages/NavigationPage';
import { captureUiInventory } from '../src/utils/uiInventory';

test.describe('@full-ui Full UI coverage', () => {
  for (const module of primaryModules) {
    test(`opens ${module.name} and validates clickable surface inventory`, async ({ authenticatedPage, networkMonitor }, testInfo) => {
      const nav = new NavigationPage(authenticatedPage);
      await nav.openModule(module);

      const inventory = await captureUiInventory(authenticatedPage);
      await testInfo.attach(`${module.name}-inventory`, {
        body: JSON.stringify(inventory, null, 2),
        contentType: 'application/json'
      });

      expect(inventory.headings.length).toBeGreaterThan(0);
      expect(inventory.links.length).toBeGreaterThan(0);

      for (const buttonName of inventory.buttons.filter(Boolean).slice(0, 8)) {
        if (/Create|Delete|Buy|Upload|Invite|New Ticket|Start|Generate/i.test(buttonName)) continue;
        await authenticatedPage.keyboard.press('Escape');
        const button = authenticatedPage.getByRole('button', { name: buttonName }).first();
        if (await button.isVisible().catch(() => false)) {
          await expect(button).toBeEnabled();
        }
      }

      const failures = envConfig.allowKnownDefects ? networkMonitor.failedApiEvents() : networkMonitor.failedApiEvents({ includeKnown: true });
      expect(failures).toEqual([]);
    });
  }
});
