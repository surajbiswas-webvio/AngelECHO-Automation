import type { Page, Response } from '@playwright/test';

export type ApiEvent = {
  method: string;
  url: string;
  status: number;
  resourceType: string;
};

export type ConsoleEvent = {
  type: string;
  text: string;
};

const knownApiDefects = [
  /\/live-calls\/10$/,
];

const knownConsoleDefects = [
  /CORS policy/i,
  /Failed to load resource/i,
  /WebSocket connection/i,
  /setDeleteLoading is not defined/i,
];

export class NetworkMonitor {
  readonly apiEvents: ApiEvent[] = [];
  readonly consoleEvents: ConsoleEvent[] = [];

  attach(page: Page): void {
    page.on('response', (response: Response) => {
      const url = response.url();
      if (!url.includes('staging-api.angelecho.ai') && !url.includes('/api/')) return;
      this.apiEvents.push({
        method: response.request().method(),
        url,
        status: response.status(),
        resourceType: response.request().resourceType()
      });
    });

    page.on('console', message => {
      if (!['error', 'warning'].includes(message.type())) return;
      this.consoleEvents.push({
        type: message.type(),
        text: message.text()
      });
    });
  }

  failedApiEvents(options: { includeKnown?: boolean } = {}): ApiEvent[] {
    return this.apiEvents.filter(event => {
      if (event.status < 400) return false;
      if (options.includeKnown) return true;
      return !knownApiDefects.some(pattern => pattern.test(event.url));
    });
  }

  consoleErrors(options: { includeKnown?: boolean } = {}): ConsoleEvent[] {
    return this.consoleEvents.filter(event => {
      if (event.type !== 'error') return false;
      if (options.includeKnown) return true;
      return !knownConsoleDefects.some(pattern => pattern.test(event.text));
    });
  }
}
