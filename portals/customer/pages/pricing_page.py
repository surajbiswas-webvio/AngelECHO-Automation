from __future__ import annotations

from playwright.sync_api import expect

from common.base_pages.base_page import BasePage


class PricingPage(BasePage):
    def open(self) -> None:
        self.goto("/pricing")
        expect(self.page.get_by_role("heading", name="Cost Calculator")).to_be_visible()

    def expect_calculator_loaded(self) -> None:
        expect(self.page.get_by_text("Estimated Total", exact=True)).to_be_visible()
        expect(self.page.get_by_text("components active", exact=False)).to_be_visible()

    def open_detailed_pricing(self) -> None:
        self.page.get_by_role("button", name="Detailed Pricing").click()
        expect(self.page.get_by_text("Deepgram", exact=False).first).to_be_visible()
