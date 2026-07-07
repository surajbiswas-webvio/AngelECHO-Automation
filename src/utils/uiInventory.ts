import type { Page } from '@playwright/test';

export type UiInventory = {
  url: string;
  headings: string[];
  links: { text: string; href: string }[];
  buttons: string[];
  inputs: { tag: string; type: string; name: string; placeholder: string; label: string; value: string }[];
  tables: string[][];
  dialogs: string[];
};

export async function captureUiInventory(page: Page): Promise<UiInventory> {
  return page.evaluate(() => {
    const visible = (element: Element) => {
      const htmlElement = element as HTMLElement;
      return Boolean(htmlElement.offsetWidth || htmlElement.offsetHeight || htmlElement.getClientRects().length);
    };
    const text = (element: Element) =>
      (
        (element as HTMLElement).innerText ||
        element.textContent ||
        element.getAttribute('aria-label') ||
        element.getAttribute('placeholder') ||
        ''
      )
        .trim()
        .replace(/\s+/g, ' ');
    const all = (selector: string) => Array.from(document.querySelectorAll(selector)).filter(visible);

    return {
      url: location.href,
      headings: all('h1,h2,h3,[role=heading]').map(text),
      links: all('a').map(element => ({ text: text(element), href: (element as HTMLAnchorElement).href })),
      buttons: all('button,[role=button]').map(text),
      inputs: all('input,textarea,select,[role=combobox]').map(element => ({
        tag: element.tagName,
        type: element.getAttribute('type') || '',
        name: element.getAttribute('name') || '',
        placeholder: element.getAttribute('placeholder') || '',
        label: element.getAttribute('aria-label') || '',
        value: (element as HTMLInputElement).value || ''
      })),
      tables: all('table').map(table => Array.from(table.querySelectorAll('th')).map(text)),
      dialogs: all('[role=dialog], .modal').map(text)
    };
  });
}
