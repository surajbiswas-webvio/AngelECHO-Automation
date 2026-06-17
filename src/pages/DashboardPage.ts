import { expect, type Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class DashboardPage extends BasePage {
  readonly widgets = [
    'Live Calls',
    'Total Calls',
    'Avg Duration',
    'Active Agents',
    'Phone Numbers',
    'Daily Calls',
    'Agent Performance',
    'Cost Breakdown'
  ];

  constructor(page: Page) {
    super(page);
  }

  async open(): Promise<void> {
    await this.goto('/');
  }

  async expectLoaded(): Promise<void> {
    await expect(this.page.getByRole('heading', { name: 'Live Calls' }).or(this.page.getByText('Live Calls')).first()).toBeVisible();
  }

  async validateWidgets(): Promise<void> {
    for (const widget of this.widgets) {
      await expect(this.page.getByText(widget, { exact: false }).first()).toBeVisible();
    }
    await expect(this.page.getByRole('table').first()).toBeVisible();
    await expect(this.page.getByRole('button', { name: /Last 30 days/i })).toBeVisible();
  }

  async openDateFilter(): Promise<void> {
    await this.page.getByRole('button', { name: /Last 30 days/i }).click();
    await expect(this.page.getByRole('option').or(this.page.getByText(/Last 7 days|Last 30 days|Custom/i)).first()).toBeVisible();
    await this.page.keyboard.press('Escape');
  }
}
