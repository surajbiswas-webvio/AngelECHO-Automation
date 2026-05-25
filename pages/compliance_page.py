from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class CompliancePage(BasePage):
    def open(self) -> None:
        self.goto("/compliance")
        expect(self.page.get_by_role("heading", name="Compliance")).to_be_visible()

    def open_upload_document_dialog(self) -> None:
        self.page.get_by_role("button", name="Upload document").click()
        expect(self.page.get_by_role("dialog", name="Upload compliance document")).to_be_visible()

    def expect_upload_form_fields(self) -> None:
        expect(self.page.get_by_placeholder("e.g. Acme Inc. Articles of Incorporation")).to_be_visible()
        expect(self.page.get_by_placeholder("Anything the reviewer should know")).to_be_visible()
        expect(self.page.get_by_role("button", name="Choose File")).to_be_visible()
        expect(self.page.get_by_role("button", name="Upload")).to_be_visible()

    def expect_documents_empty_state(self) -> None:
        expect(self.page.get_by_text("You haven't uploaded any compliance documents yet.", exact=True)).to_be_visible()
