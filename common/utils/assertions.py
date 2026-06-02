from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect


def assert_url_contains(page: Page, expected_fragment: str) -> None:
    expect(page).to_have_url(re.compile(f".*{re.escape(expected_fragment)}.*"))


def assert_text_visible(locator: Locator, expected_text: str) -> None:
    expect(locator).to_be_visible()
    expect(locator).to_contain_text(expected_text)


def assert_toast_contains(page: Page, message: str) -> None:
    toast = page.get_by_role("alert").or_(page.locator(".toast, .Toastify__toast, [data-testid*='toast']").first)
    expect(toast).to_be_visible()
    expect(toast).to_contain_text(message)
