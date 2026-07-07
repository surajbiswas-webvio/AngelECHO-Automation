import { expect, type Locator, type Page } from '@playwright/test';

export abstract class BasePage {
  protected constructor(protected readonly page: Page) {}

  async goto(path = ''): Promise<void> {
    await this.page.goto(path, { waitUntil: 'domcontentloaded' });
    await this.waitForReady();
  }

  async waitForReady(): Promise<void> {
    await this.page.waitForLoadState('domcontentloaded');
  }

  async expectVisible(locator: Locator): Promise<void> {
    await expect(locator.first()).toBeVisible();
  }

  async clickByRole(name: string | RegExp): Promise<void> {
    const control = this.page.getByRole('button', { name }).or(this.page.getByRole('link', { name })).first();
    await expect(control).toBeVisible();
    await control.click();
  }
}
