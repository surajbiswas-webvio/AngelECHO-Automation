from __future__ import annotations

from playwright.sync_api import expect

from common.base_pages.base_page import BasePage


class BillingPage(BasePage):
    def open(self) -> None:
        self.goto("/billing")
        expect(self.page.get_by_role("heading", name="Billing")).to_be_visible()

    def switch_to_plans(self) -> None:
        self.page.get_by_role("button", name="Plans").click()

    def switch_to_payments(self) -> None:
        self.page.get_by_role("button", name="Payments").click()

    def expect_usage_metrics(self) -> None:
        expect(self.page.get_by_text("Total Cost", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Total Calls", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Minutes Used", exact=True)).to_be_visible()
