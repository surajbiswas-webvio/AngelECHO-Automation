from __future__ import annotations

"""Page object for pricing calculator workflows."""

from playwright.sync_api import expect

from pages.base_page import BasePage


class PricingPage(BasePage):
    """Purpose: Encapsulates pricing page loading and detail-panel checks."""

    def open(self) -> None:
        """Open Pricing and verify the cost calculator heading; returns None."""
        self.goto("/pricing")
        expect(self.page.get_by_role("heading", name="Cost Calculator")).to_be_visible()

    def expect_calculator_loaded(self) -> None:
        """Assert calculator summary content is visible; returns None."""
        expect(self.page.get_by_text("Estimated Total", exact=True)).to_be_visible()
        expect(self.page.get_by_text("components active", exact=False)).to_be_visible()

    def open_detailed_pricing(self) -> None:
        """Open detailed pricing and verify provider rate content is visible."""
        self.page.get_by_role("button", name="Detailed Pricing").click()
        expect(self.page.get_by_text("Deepgram", exact=False).first).to_be_visible()
