from __future__ import annotations

from pathlib import Path

from playwright.sync_api import expect

from common.base_pages.base_page import BasePage


class VendorSupportPage(BasePage):
    def open(self) -> None:
        self.goto("/vendor/support")
        expect(self.page.get_by_text("Support", exact=True).first).to_be_visible()

    def search(self, value: str) -> None:
        self.page.get_by_placeholder("Search tickets...").fill(value)
        self.page.wait_for_timeout(300)

    def open_new_ticket(self) -> None:
        self.page.get_by_role("button", name="New Ticket").click()
        expect(self.page.get_by_placeholder("Brief summary of your issue")).to_be_visible()

    def fill_ticket(self, subject: str, description: str) -> None:
        self.page.get_by_placeholder("Brief summary of your issue").fill(subject)
        self.page.get_by_placeholder("Describe your issue in detail...").fill(description)

    def attach_file(self, path: Path) -> None:
        self.page.locator("input[type='file']").set_input_files(str(path))

    def expect_submit_ready(self) -> None:
        expect(self.page.get_by_role("button", name="Submit Ticket")).to_be_enabled()

    def expect_required_validation(self) -> None:
        self.open()
        self.open_new_ticket()
        self.page.get_by_role("button", name="Submit Ticket").click()
        expect(self.page.get_by_placeholder("Brief summary of your issue")).to_be_visible()
        expect(self.page.get_by_role("button", name="Submit Ticket")).to_be_visible()

    def open_first_ticket_details(self) -> None:
        details = self.page.get_by_role("button", name="Details").or_(self.page.get_by_text("Details", exact=True))
        expect(details.first).to_be_visible()
        details.first.click()
        expect(self.page.get_by_role("button", name="Back to Support")).to_be_visible()
        expect(self.page.get_by_text("Conversation", exact=False)).to_be_visible()
