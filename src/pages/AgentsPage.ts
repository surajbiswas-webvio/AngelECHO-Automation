import { expect, type Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class AgentsPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  async open(): Promise<void> {
    await this.goto('/list');
    await expect(this.page.getByRole('heading', { name: 'Agents Management' })).toBeVisible();
  }

  async search(name: string): Promise<void> {
    await this.page.locator("input[type='search'], input[placeholder*='Search' i]").first().fill(name);
    await this.page.waitForTimeout(500);
  }

  async expectTable(): Promise<void> {
    await expect(this.page.getByRole('table')).toBeVisible();
    for (const header of ['Agent Name', 'Mode', 'Type', 'Language', 'Actions']) {
      await expect(this.page.getByRole('columnheader', { name: new RegExp(header, 'i') })).toBeVisible();
    }
  }

  async exerciseFilters(): Promise<void> {
    for (const label of ['Mode', 'Type', 'Language', 'Status']) {
      await this.page.getByRole('button', { name: new RegExp(label, 'i') }).click();
      await expect(this.page.getByRole('option').or(this.page.getByRole('menuitem')).first()).toBeVisible();
      await this.page.keyboard.press('Escape');
    }
  }

  async createVoiceAgent(name: string): Promise<void> {
    await this.open();
    await this.search(name);
    if (await this.page.getByRole('row').filter({ hasText: name }).first().isVisible().catch(() => false)) return;

    await this.page.getByRole('button', { name: /Create Agent/i }).click();
    await expect(this.page.getByRole('heading', { name: /Select Template/i })).toBeVisible();
    await this.page.getByText('Start from blank', { exact: true }).click();
    await expect(this.page.getByRole('heading', { name: /Create a new agent/i })).toBeVisible();
    await this.page.getByPlaceholder(/agent name/i).fill(name);
    await this.page.getByRole('button', { name: /^Create$/i }).click();
    await expect(this.page.getByRole('row').filter({ hasText: name }).first()).toBeVisible({ timeout: 20_000 });
  }

  async openAgent(name: string): Promise<void> {
    await this.open();
    await this.search(name);
    const row = this.page.getByRole('row').filter({ hasText: name }).first();
    await expect(row).toBeVisible();
    await row.getByRole('button', { name: /Edit/i }).click();
    await expect(this.page).toHaveURL(/agent-editor/);
    await expect(this.page.getByRole('heading', { name })).toBeVisible();
  }
}
