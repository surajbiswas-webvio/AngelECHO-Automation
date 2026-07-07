from __future__ import annotations

"""Page object for phone number purchase workflows."""

from playwright.sync_api import expect

from pages.base_page import BasePage


class PhoneNumbersPage(BasePage):
    """Purpose: Encapsulates phone-number search, dialog, and purchase validation."""

    def open(self) -> None:
        """Open Phone Numbers and verify the page heading; returns None."""
        self.goto("/phone-numbers")
        expect(self.page.get_by_role("heading", name="Phone Numbers")).to_be_visible()

    def open_buy_number_dialog(self) -> None:
        """Open the buy-number dialog for selection validation; returns None."""
        self.page.get_by_role("button", name="Buy Number").click()
        expect(self.page.get_by_role("dialog", name="Phone Number")).to_be_visible()

    def expect_purchase_requires_selection(self) -> None:
        """Assert the purchase action is disabled until a number is selected."""
        expect(self.page.get_by_role("button", name="Purchase Number")).to_be_disabled()

    def select_first_suggested_number(self) -> None:
        """Select the first suggested number and verify purchase becomes enabled."""
        dialog = self.page.get_by_role("dialog", name="Phone Number")
        dialog.locator("input[type='checkbox']").nth(0).check()
        expect(self.page.get_by_role("button", name="Purchase Number")).to_be_enabled()

    def search_numbers(self, value: str) -> None:
        """Search phone numbers by value and wait for client-side filtering."""
        self.page.get_by_placeholder("Search numbers...").fill(value)
        self.page.wait_for_timeout(300)
