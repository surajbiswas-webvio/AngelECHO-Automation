from __future__ import annotations

"""Reusable assertion helpers for common UI expectations.

These helpers keep tests expressive when the same URL, text, and toast
verification patterns are needed across multiple workflows.
"""

import re

from playwright.sync_api import Locator, Page, expect


def assert_url_contains(page: Page, expected_fragment: str) -> None:
    """
    Purpose:
        Verifies that the current page URL contains an expected fragment.

    Why Needed:
        Route assertions appear across navigation and redirect tests.

    Args:
        page: Playwright page under test.
        expected_fragment: Literal URL fragment expected in the current URL.

    Returns:
        None. Fails through Playwright expect on mismatch.

    Notes:
        Escapes the fragment before building the regular expression.
    """
    expect(page).to_have_url(re.compile(f".*{re.escape(expected_fragment)}.*"))


def assert_text_visible(locator: Locator, expected_text: str) -> None:
    """
    Purpose:
        Confirms that a locator is visible and contains expected text.

    Why Needed:
        Combines two common UI assertions into one reusable helper.

    Args:
        locator: Playwright locator to inspect.
        expected_text: Text expected within the visible locator.

    Returns:
        None. Fails through Playwright expect on mismatch.

    Notes:
        Visibility is asserted before content to produce clearer failures.
    """
    expect(locator).to_be_visible()
    expect(locator).to_contain_text(expected_text)


def assert_toast_contains(page: Page, message: str) -> None:
    """
    Purpose:
        Verifies that a user-facing toast or alert contains a message.

    Why Needed:
        The app may render notifications with different toast containers, so
        tests need one resilient assertion point.

    Args:
        page: Playwright page under test.
        message: Expected notification text.

    Returns:
        None. Fails through Playwright expect on mismatch.

    Notes:
        Uses a union locator that covers ARIA alerts and common toast classes.
    """
    toast = page.get_by_role("alert").or_(page.locator(".toast, .Toastify__toast, [data-testid*='toast']").first)
    expect(toast).to_be_visible()
    expect(toast).to_contain_text(message)
