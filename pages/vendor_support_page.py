from __future__ import annotations

"""Page object for vendor support ticket workflows."""

from pathlib import Path

from playwright.sync_api import expect

from pages.vendor_base_page import VendorBasePage


class VendorSupportPage(VendorBasePage):
    """Purpose: Encapsulates vendor support search, ticket form, upload, and details checks."""

    def open(self) -> None:
        """Open vendor support and verify the support surface is visible."""
        self.goto("/vendor/support")
        expect(self.page.get_by_text("Support", exact=True).first).to_be_visible()

    def search(self, value: str) -> None:
        """Search vendor support tickets by value and wait for filtering."""
        self.page.get_by_placeholder("Search tickets...").fill(value)
        self.page.wait_for_timeout(300)

    def open_new_ticket(self) -> None:
        """Open the new-ticket form and verify the subject field is visible."""
        self.page.get_by_role("button", name="New Ticket").click()
        expect(self.page.get_by_placeholder("Brief summary of your issue")).to_be_visible()

    def fill_ticket(self, subject: str, description: str) -> None:
        """Fill required vendor support ticket fields; returns None."""
        self.page.get_by_placeholder("Brief summary of your issue").fill(subject)
        self.page.get_by_placeholder("Describe your issue in detail...").fill(description)

    def attach_file(self, path: Path) -> None:
        """Attach a file path to the support ticket upload control."""
        self.page.locator("input[type='file']").set_input_files(str(path))

    def expect_submit_ready(self) -> None:
        """Assert the support ticket submit action is enabled."""
        expect(self.page.get_by_role("button", name="Submit Ticket")).to_be_enabled()

    def expect_required_validation(self) -> None:
        """Verify submitting an empty ticket keeps required controls visible."""
        self.open()
        self.open_new_ticket()
        self.page.get_by_role("button", name="Submit Ticket").click()
        expect(self.page.get_by_placeholder("Brief summary of your issue")).to_be_visible()
        expect(self.page.get_by_role("button", name="Submit Ticket")).to_be_visible()

    def open_first_ticket_details(self) -> None:
        """Open the first ticket details view and verify conversation content appears."""
        details = self.page.get_by_role("button", name="Details").or_(self.page.get_by_text("Details", exact=True))
        expect(details.first).to_be_visible()
        details.first.click()
        expect(self.page.get_by_role("button", name="Back to Support")).to_be_visible()
        expect(self.page.get_by_text("Conversation", exact=False)).to_be_visible()
