from __future__ import annotations

"""Page object for outbound campaign workflows."""

from playwright.sync_api import expect

from pages.base_page import BasePage


class OutboundPage(BasePage):
    """Purpose: Encapsulates campaign page navigation, search, and validation checks."""

    def open(self) -> None:
        """Open Campaign Calling and verify the page heading; returns None."""
        self.goto("/outbound")
        expect(self.page.get_by_role("heading", name="Campaign Calling")).to_be_visible()

    def open_new_campaign_dialog(self) -> None:
        """Open the campaign creation dialog for form validation; returns None."""
        self.page.get_by_role("button", name="New Campaign").click()
        expect(self.page.get_by_role("dialog", name="Create New Campaign")).to_be_visible()

    def expect_campaign_blocked_without_recipients(self) -> None:
        """Assert campaign creation is blocked when no lead list is available."""
        expect(self.page.get_by_text("No lead lists available", exact=False)).to_be_visible()
        expect(self.page.get_by_role("button", name="Create Campaign")).to_be_disabled()

    def search_campaigns(self, value: str) -> None:
        """Search campaigns by value and wait for client-side filtering."""
        self.page.get_by_placeholder("Search campaigns...").fill(value)
        self.page.wait_for_timeout(300)
