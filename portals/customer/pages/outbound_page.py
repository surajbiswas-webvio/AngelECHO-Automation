from __future__ import annotations

from playwright.sync_api import expect

from common.base_pages.base_page import BasePage


class OutboundPage(BasePage):
    def open(self) -> None:
        self.goto("/outbound")
        expect(self.page.get_by_role("heading", name="Campaign Calling")).to_be_visible()

    def open_new_campaign_dialog(self) -> None:
        self.page.get_by_role("button", name="New Campaign").click()
        expect(self.page.get_by_role("dialog", name="Create New Campaign")).to_be_visible()

    def expect_campaign_blocked_without_recipients(self) -> None:
        expect(self.page.get_by_text("No lead lists available", exact=False)).to_be_visible()
        expect(self.page.get_by_role("button", name="Create Campaign")).to_be_disabled()

    def search_campaigns(self, value: str) -> None:
        self.page.get_by_placeholder("Search campaigns...").fill(value)
        self.page.wait_for_timeout(300)
