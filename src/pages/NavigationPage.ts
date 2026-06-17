import { expect, type Page } from '@playwright/test';
import { BasePage } from './BasePage';

export const primaryModules = [
  { name: 'Dashboard', path: '/', heading: /Live Calls|Dashboard/ },
  { name: 'All Agents', path: '/list', heading: /Agents Management/ },
  { name: 'Knowledge Base', path: '/knowledge-base', heading: /Knowledge Base/ },
  { name: 'Phone Numbers', path: '/phone-numbers', heading: /Phone Numbers/ },
  { name: 'Campaign Calling', path: '/outbound', heading: /Campaign Calling/ },
  { name: 'Live Calls', path: '/live-calls', heading: /Live Calls/ },
  { name: 'Call History', path: '/call-history', heading: /Call History/ },
  { name: 'Campaign History', path: '/campaign-history', heading: /Campaign Call History/ },
  { name: 'Chat History', path: '/chat-history', heading: /Chat History/ },
  { name: 'Analytics', path: '/analytics', heading: /Analytics/ },
  { name: 'Compliance', path: '/compliance', heading: /Compliance/ },
  { name: 'Billing', path: '/billing', heading: /Billing/ },
  { name: 'Pricing', path: '/pricing', heading: /Cost Calculator/ },
  { name: 'Members', path: '/members', heading: /Members/ },
  { name: 'Roles & Permissions', path: '/roles-permissions', heading: /Permissions For Admin/ },
  { name: 'Setup Guides', path: '/setup-guides', heading: /Setup Guides/ },
  { name: 'Support', path: '/support', heading: /Support/ }
] as const;

export class NavigationPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  async expectShell(): Promise<void> {
    await expect(this.page.locator('aside, nav, [data-testid=sidebar]').first()).toBeVisible();
  }

  async openModule(module: (typeof primaryModules)[number]): Promise<void> {
    await this.page.getByRole('link', { name: module.name }).click();
    await this.waitForReady();
    await expect(this.page).toHaveURL(new RegExp(`${module.path.replace('/', '\\/')}$|${module.path.replace('/', '\\/')}`));
    await expect(this.page.getByRole('heading', { name: module.heading }).first()).toBeVisible();
  }
}
