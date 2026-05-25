from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class PhoneNumbersPage(BasePage):
    def open(self) -> None:
        self.goto("/phone-numbers")
        expect(self.page.get_by_role("heading", name="Phone Numbers")).to_be_visible()

    def open_buy_number_dialog(self) -> None:
        self.page.get_by_role("button", name="Buy Number").click()
        expect(self.page.get_by_role("dialog", name="Phone Number")).to_be_visible()

    def expect_purchase_requires_selection(self) -> None:
        expect(self.page.get_by_role("button", name="Purchase Number")).to_be_disabled()

    def select_first_suggested_number(self) -> None:
        dialog = self.page.get_by_role("dialog", name="Phone Number")
        dialog.locator("input[type='checkbox']").nth(0).check()
        expect(self.page.get_by_role("button", name="Purchase Number")).to_be_enabled()

    def search_numbers(self, value: str) -> None:
        self.page.get_by_placeholder("Search numbers...").fill(value)
        self.page.wait_for_timeout(300)
