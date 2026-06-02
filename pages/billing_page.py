from __future__ import annotations

"""Page object for customer billing workflows."""

from playwright.sync_api import expect

from pages.base_page import BasePage


class BillingPage(BasePage):
    """Purpose: Encapsulates billing page navigation, tabs, and usage checks."""

    def open(self) -> None:
        """Open Billing and verify the page heading; returns None."""
        self.goto("/billing")
        expect(self.page.get_by_role("heading", name="Billing")).to_be_visible()

    def switch_to_plans(self) -> None:
        """Switch to the Plans tab for billing-plan validation; returns None."""
        self.page.get_by_role("button", name="Plans").click()

    def switch_to_payments(self) -> None:
        """Switch to the Payments tab for payment-history validation; returns None."""
        self.page.get_by_role("button", name="Payments").click()

    def expect_usage_metrics(self) -> None:
        """Assert core billing metrics are visible; raises via Playwright on mismatch."""
        expect(self.page.get_by_text("Total Cost", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Total Calls", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Minutes Used", exact=True)).to_be_visible()
