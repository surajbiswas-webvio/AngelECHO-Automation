import { expect, type Page } from '@playwright/test';
import { BasePage } from './BasePage';
import { envConfig } from '../config/env';

export class LoginPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  async open(): Promise<void> {
    await this.goto('/sign-in');
  }

  async login(email = envConfig.customerEmail, password = envConfig.customerPassword): Promise<void> {
    await this.open();
    await this.page.locator("input[type='email'], input[name='email'], input[placeholder*='Email' i]").first().fill(email);
    await this.page.locator("input[type='password'], input[name='password'], input[placeholder*='Password' i]").first().fill(password);
    await this.page.getByRole('button', { name: /sign in/i }).click();
    await expect(this.page.getByText("New Customer's Workspace", { exact: false }).first()).toBeVisible();
  }

  async expectRejectedLogin(): Promise<void> {
    await expect(this.page).toHaveURL(/sign-in/);
  }
}
