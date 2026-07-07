import { expect, type Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class AgentEditorPage extends BasePage {
  readonly sections = [
    'Functions',
    'Agent Settings',
    'Multi-Language',
    'Knowledge Base',
    'Speech Settings',
    'Call Settings',
    'Post-Call Analysis',
    'Security & Fallback Settings',
    'Safety Restrictions',
    'Webhook Settings',
    'Agent Metadata'
  ];

  constructor(page: Page) {
    super(page);
  }

  async setPrompt(prompt: string): Promise<void> {
    const promptField = this.page
      .locator("textarea[placeholder*='universal prompt' i], textarea[placeholder*='Prompt' i]")
      .last();
    await expect(promptField).toBeVisible();
    await promptField.fill(prompt);
    await this.page.getByRole('button', { name: /Update Agent|Save Agent/i }).click();
    await expect(this.page.getByRole('button', { name: /Update Agent|Save Agent/i })).toBeVisible({ timeout: 20_000 });
  }

  async validateSections(): Promise<void> {
    for (const section of this.sections) {
      const control = this.page.getByRole('button', { name: new RegExp(section, 'i') }).first();
      await expect(control).toBeVisible();
      await control.click();
      await expect(this.page.getByRole('heading', { name: new RegExp(section, 'i') }).first()).toBeVisible();
    }
  }

  async validateTestModule(): Promise<void> {
    await expect(this.page.getByRole('tab', { name: /Web Call/i })).toBeVisible();
    await expect(this.page.getByRole('tab', { name: /Phone Call/i })).toBeVisible();
    await expect(this.page.getByRole('button', { name: /^Start$/i })).toBeVisible();
  }

  async openPromptGenerator(): Promise<void> {
    await this.page.getByRole('button', { name: /Generate Prompt/i }).click();
    await expect(this.page.getByRole('dialog').filter({ hasText: 'Generate System Prompt' })).toBeVisible();
    await this.page.keyboard.press('Escape');
  }
}
