from __future__ import annotations

"""Base page-object utilities shared by all UI workflow pages.

The BasePage class provides navigation, locator, assertion, dialog, and
screenshot helpers so concrete page objects can describe business workflows
instead of repeating low-level Playwright operations.
"""

import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from config.settings import Settings
from utils.logger import get_logger
from utils.screenshot import capture_screenshot


class BasePage:
    """
    Purpose:
        Common parent for AngelECHO Playwright page objects.

    Why Needed:
        Centralizes page access, settings, logging, default timeouts, and
        shared UI actions.

    Args:
        page: Playwright page controlled by the test.
        settings: Runtime automation configuration.

    Returns:
        Page-object instances expose reusable UI helper methods.

    Notes:
        Concrete page classes should layer domain-specific workflows on top of
        these primitives.
    """

    def __init__(self, page: Page, settings: Settings) -> None:
        """
        Purpose:
            Initializes common page-object state.

        Why Needed:
            Every page object needs the Playwright page, runtime settings, and
            a consistent default timeout.

        Args:
            page: Playwright page instance.
            settings: Runtime automation settings.

        Returns:
            None.

        Notes:
            The timeout is applied directly to the page for all later actions.
        """
        self.page = page
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        self.page.set_default_timeout(settings.default_timeout_ms)

    def goto(self, path: str = "") -> None:
        """
        Purpose:
            Navigates to an application route and waits for initial readiness.

        Why Needed:
            Page objects should use one URL-building path for consistent
            environment behavior.

        Args:
            path: Route path relative to the configured base URL.

        Returns:
            None.

        Notes:
            Uses `domcontentloaded` to avoid waiting forever on long-polling
            application traffic.
        """
        url = self.settings.url_for(path)
        self.logger.info("Navigating to %s", url)
        self.page.goto(url, wait_until="domcontentloaded")
        self.wait_for_page_ready()

    def wait_for_page_ready(self) -> None:
        """
        Purpose:
            Waits for the page's DOM to be available.

        Why Needed:
            Provides a reusable synchronization point after navigation or save
            actions.

        Args:
            None.

        Returns:
            None.

        Notes:
            The method intentionally avoids network-idle for apps with
            background requests.
        """
        self.page.wait_for_load_state("domcontentloaded")

    def locator(self, selector: str) -> Locator:
        """
        Purpose:
            Creates a Playwright locator from a CSS selector.

        Why Needed:
            Gives concrete page objects a concise wrapper through the base
            page abstraction.

        Args:
            selector: CSS selector string.

        Returns:
            Playwright Locator for the selector.

        Notes:
            No waiting is performed until the locator is acted on.
        """
        return self.page.locator(selector)

    def click(self, target: str | Locator) -> None:
        """
        Purpose:
            Clicks the first visible and enabled locator target.

        Why Needed:
            Reusable click behavior reduces duplicated visibility/enabled
            assertions before interactions.

        Args:
            target: CSS selector or existing Playwright Locator.

        Returns:
            None.

        Notes:
            Only the first matched element is clicked to keep ambiguous
            selectors deterministic.
        """
        locator = target if isinstance(target, Locator) else self.page.locator(target)
        first = locator.first
        expect(first).to_be_visible()
        expect(first).to_be_enabled()
        first.click()

    def fill(self, selector: str, value: str) -> None:
        """
        Purpose:
            Fills the first visible field matched by a selector.

        Why Needed:
            Page objects repeatedly need safe text-entry behavior.

        Args:
            selector: CSS selector for the field.
            value: Text value to enter.

        Returns:
            None.

        Notes:
            Visibility is asserted before filling to produce readable failures.
        """
        field = self.page.locator(selector).first
        expect(field).to_be_visible()
        field.fill(value)

    def select_option(self, selector: str, value: str) -> None:
        """
        Purpose:
            Selects an option in a visible native select field.

        Why Needed:
            Settings and form workflows use dropdown controls repeatedly.

        Args:
            selector: CSS selector for the select element.
            value: Option value to select.

        Returns:
            None.

        Notes:
            Designed for native select elements, not custom combobox widgets.
        """
        field = self.page.locator(selector).first
        expect(field).to_be_visible()
        field.select_option(value=value)

    def click_button(self, name: str) -> None:
        """
        Purpose:
            Clicks a button by accessible name.

        Why Needed:
            Encourages role-based selectors for stable and accessible tests.

        Args:
            name: Accessible button name.

        Returns:
            None.

        Notes:
            Delegates visibility and enabled checks to `click`.
        """
        self.click(self.page.get_by_role("button", name=name))

    def visible_text(self, text: str) -> Locator:
        """
        Purpose:
            Builds a locator for visible text content.

        Why Needed:
            Page assertions often need a reusable text locator.

        Args:
            text: Text fragment to locate.

        Returns:
            Playwright Locator matching text non-exactly.

        Notes:
            Visibility must be asserted separately by callers.
        """
        return self.page.get_by_text(text, exact=False)

    def expect_visible(self, target: str | Locator) -> None:
        """
        Purpose:
            Asserts that a selector or locator is visible.

        Why Needed:
            Creates a common visibility assertion across page objects and tests.

        Args:
            target: CSS selector or Playwright Locator.

        Returns:
            None.

        Notes:
            The first match is used for deterministic behavior.
        """
        locator = target if isinstance(target, Locator) else self.page.locator(target)
        expect(locator.first).to_be_visible()

    def expect_not_visible(self, target: str | Locator) -> None:
        """
        Purpose:
            Asserts that a selector or locator is not visible.

        Why Needed:
            Used for negative validation such as deleted records and hidden
            authentication fields.

        Args:
            target: CSS selector or Playwright Locator.

        Returns:
            None.

        Notes:
            The first match is checked to mirror `expect_visible`.
        """
        locator = target if isinstance(target, Locator) else self.page.locator(target)
        expect(locator.first).not_to_be_visible()

    def expect_url_contains(self, fragment: str) -> None:
        """
        Purpose:
            Asserts that the current URL contains a literal fragment.

        Why Needed:
            Navigation flows often need route verification.

        Args:
            fragment: URL fragment expected in the current page URL.

        Returns:
            None.

        Notes:
            Escapes the fragment before converting it to a regular expression.
        """
        expect(self.page).to_have_url(re.compile(f".*{re.escape(fragment)}.*"))

    def open_combobox_by_text(self, text: str) -> None:
        """
        Purpose:
            Opens a custom combobox or menu trigger by exact visible text.

        Why Needed:
            Some application controls are rendered as buttons or text triggers
            instead of native select elements.

        Args:
            text: Exact trigger text.

        Returns:
            None.

        Notes:
            Option selection is left to the calling workflow.
        """
        self.page.get_by_text(text, exact=True).click()

    def close_dialog(self) -> None:
        """
        Purpose:
            Closes an open modal dialog using Close or Cancel controls.

        Why Needed:
            Workflows that inspect dialogs need a reusable cleanup path before
            continuing with the page.

        Args:
            None.

        Returns:
            None.

        Notes:
            Checks both common button names because dialogs use different
            dismissal labels.
        """
        close = self.page.get_by_role("button", name="Close")
        if close.count() > 0 and close.first.is_visible():
            close.first.click()
            return
        cancel = self.page.get_by_role("button", name="Cancel")
        if cancel.count() > 0 and cancel.first.is_visible():
            cancel.first.click()

    def capture(self, name: str) -> Path:
        """
        Purpose:
            Captures a screenshot for the current page object.

        Why Needed:
            Provides a convenient debugging hook from workflow classes.

        Args:
            name: Human-readable screenshot name.

        Returns:
            Path to the saved screenshot.

        Notes:
            Delegates filename sanitization and directory handling to the
            screenshot utility.
        """
        return capture_screenshot(self.page, name)
