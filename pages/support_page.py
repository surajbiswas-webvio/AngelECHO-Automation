from __future__ import annotations

"""Page object for customer support ticket workflows."""

from playwright.sync_api import expect

from pages.base_page import BasePage


class SupportPage(BasePage):
    """Purpose: Encapsulates support page search, ticket dialog, and form checks."""

    def open(self) -> None:
        """Open Support and verify the page heading; returns None."""
        self.goto("/support")
        expect(self.page.get_by_role("heading", name="Support")).to_be_visible()

    def open_new_ticket_dialog(self) -> None:
        """Open the new-ticket dialog and verify it is displayed."""
        self.page.get_by_role("button", name="New Ticket").click()
        expect(self.page.get_by_role("dialog", name="Create New Ticket")).to_be_visible()

    def fill_ticket_summary(self, subject: str, description: str) -> None:
        """Fill required ticket subject and description fields; returns None."""
        self.page.get_by_placeholder("Brief summary of your issue").fill(subject)
        self.page.get_by_placeholder("Describe your issue in detail...").fill(description)

    def expect_ticket_ready_for_submission(self) -> None:
        """Assert a completed ticket form can be submitted and upload UI is present."""
        expect(self.page.get_by_role("button", name="Submit Ticket")).to_be_enabled()
        expect(self.page.get_by_text("Choose a file or drag & drop it here", exact=True)).to_be_visible()

    def search_tickets(self, value: str) -> None:
        """Search tickets by value and wait for client-side filtering."""
        self.page.get_by_placeholder("Search tickets...").fill(value)
        self.page.wait_for_timeout(300)

    def expect_empty_state(self) -> None:
        """Assert the support ticket empty-state message is visible."""
        expect(self.page.get_by_text("No tickets found", exact=True)).to_be_visible()
