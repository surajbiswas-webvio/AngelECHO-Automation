from __future__ import annotations

"""Page object for customer compliance document workflows."""

from playwright.sync_api import expect

from pages.base_page import BasePage


class CompliancePage(BasePage):
    """Purpose: Encapsulates compliance page navigation and upload-form checks."""

    def open(self) -> None:
        """Open Compliance and verify the page heading; returns None."""
        self.goto("/compliance")
        expect(self.page.get_by_role("heading", name="Compliance")).to_be_visible()

    def open_upload_document_dialog(self) -> None:
        """Open the upload dialog used to validate required document controls."""
        self.page.get_by_role("button", name="Upload document").click()
        expect(self.page.get_by_role("dialog", name="Upload compliance document")).to_be_visible()

    def expect_upload_form_fields(self) -> None:
        """Assert required upload form fields and actions are visible; returns None."""
        expect(self.page.get_by_placeholder("e.g. Acme Inc. Articles of Incorporation")).to_be_visible()
        expect(self.page.get_by_placeholder("Anything the reviewer should know")).to_be_visible()
        expect(self.page.get_by_role("button", name="Choose File")).to_be_visible()
        expect(self.page.get_by_role("button", name="Upload")).to_be_visible()

    def expect_documents_empty_state(self) -> None:
        """Assert the no-documents empty state is visible for onboarding clarity."""
        expect(self.page.get_by_text("You haven't uploaded any compliance documents yet.", exact=True)).to_be_visible()
